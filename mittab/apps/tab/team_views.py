import csv
import json
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import permission_required
from django.shortcuts import render

from mittab.apps.tab.forms import TeamForm, TeamEntryForm, ScratchForm
from mittab.libs.data_import.tab_card import JSONDecimalEncoder, csv_tab_cards, get_all_json_data, get_tab_card_data
from mittab.libs.errors import *
from mittab.apps.tab.helpers import redirect_and_flash_error, \
    redirect_and_flash_success
from mittab.apps.tab.models import *
from mittab.libs import tab_logic, cache_logic
from mittab.libs.tab_logic import TabFlags
from mittab.libs.tab_logic import rankings
from django.http import HttpResponse as HTTPResponse


def public_view_teams(request):
    display_teams = TabSettings.get("teams_public", 0)

    if not request.user.is_authenticated and not display_teams:
        return redirect_and_flash_error(request, "This view is not public", path="/")

    return render(
        request, "public/teams.html", {
            "teams": Team.objects.order_by("-checked_in",
                                           "school__name").all(),
            "num_checked_in": Team.objects.filter(checked_in=True).count()
        })


def view_teams(request):
    def flags(team):
        result = 0
        if team.checked_in:
            result |= TabFlags.TEAM_CHECKED_IN
        else:
            result |= TabFlags.TEAM_NOT_CHECKED_IN
        return result

    c_teams = [(team.id, team.display_backend, flags(team),
                TabFlags.flags_to_symbols(flags(team)))
               for team in Team.objects.all()]
    all_flags = [[TabFlags.TEAM_CHECKED_IN, TabFlags.TEAM_NOT_CHECKED_IN]]
    filters, symbol_text = TabFlags.get_filters_and_symbols(all_flags)
    return render(
        request, "common/list_data.html", {
            "item_type": "team",
            "title": "Viewing All Teams",
            "item_list": c_teams,
            "filters": filters,
            "symbol_text": symbol_text
        })


def view_team(request, team_id):
    team_id = int(team_id)
    try:
        team = Team.with_preloaded_relations_for_tabbing().get(pk=team_id)
        stats = []
        stats.append(("Wins", tab_logic.tot_wins(team)))
        stats.append(("Total Speaks", tab_logic.tot_speaks(team)))
        stats.append(("Govs", tab_logic.num_govs(team)))
        stats.append(("Opps", tab_logic.num_opps(team)))
        stats.append(("Avg. Opp Wins", tab_logic.opp_strength(team)))
        stats.append(("Been Pullup", tab_logic.pull_up_count(team)))
        stats.append(("Hit Pullup", tab_logic.hit_pull_up(team)))
    except Team.DoesNotExist:
        return redirect_and_flash_error(request, "Team not found")
    if request.method == "POST":
        form = TeamForm(request.POST, instance=team)
        if form.is_valid():
            try:
                form.save()
            except ValueError:
                return redirect_and_flash_error(
                    request,
                    "An error occured, most likely a non-existent team")
            return redirect_and_flash_success(
                request, "Team {} updated successfully".format(
                    form.cleaned_data["name"]))
    else:
        form = TeamForm(instance=team)
        links = [("/team/" + str(team_id) + "/scratches/view/",
                  "Scratches for {}".format(team.display_backend))]
        for deb in team.debaters.all():
            links.append(
                ("/debater/" + str(deb.id) + "/", "View %s" % deb.name))
        return render(
            request, "common/data_entry.html", {
                "title": "Viewing Team: %s" % (team.display_backend),
                "form": form,
                "links": links,
                "team_obj": team,
                "team_stats": stats
            })

    return render(request, "common/data_entry.html", {"form": form})


def enter_team(request):
    if request.method == "POST":
        form = TeamEntryForm(request.POST)
        if form.is_valid():
            try:
                team = form.save()
            except ValueError:
                return redirect_and_flash_error(
                    request,
                    "Team name cannot be validated, most likely a duplicate school"
                )
            num_forms = form.cleaned_data["number_scratches"]
            if num_forms > 0:
                return HttpResponseRedirect("/team/" + str(team.pk) +
                                            "/scratches/add/" + str(num_forms))
            else:
                return redirect_and_flash_success(
                    request,
                    "Team {} created successfully".format(
                        team.display_backend),
                    path="/")
    else:
        form = TeamEntryForm()
    return render(request, "common/data_entry.html", {
        "form": form,
        "title": "Create Team"
    })


def add_scratches(request, team_id, number_scratches):
    try:
        team_id, number_scratches = int(team_id), int(number_scratches)
    except ValueError:
        return redirect_and_flash_error(request, "Received invalid data")
    try:
        team = Team.objects.get(pk=team_id)
    except Team.DoesNotExist:
        return redirect_and_flash_error(request,
                                        "The selected team does not exist")
    if request.method == "POST":
        forms = [
            ScratchForm(request.POST, prefix=str(i))
            for i in range(1, number_scratches + 1)
        ]
        all_good = True
        for form in forms:
            all_good = all_good and form.is_valid()
        if all_good:
            for form in forms:
                form.save()
            return redirect_and_flash_success(
                request, "Scratches created successfully")
    else:
        forms = [
            ScratchForm(
                prefix=str(i),
                initial={
                    "team": team_id,
                    "scratch_type": 0
                }
            ) for i in range(1, number_scratches + 1)
        ]
    return render(
        request, "common/data_entry_multiple.html", {
            "forms": list(zip(forms, [None] * len(forms))),
            "data_type": "Scratch",
            "title": "Adding Scratch(es) for %s" % (team.display_backend)
        })


def view_scratches(request, team_id):
    try:
        team_id = int(team_id)
    except ValueError:
        return redirect_and_flash_error(request, "Received invalid data")
    scratches = Scratch.objects.filter(team=team_id)
    number_scratches = len(scratches)
    team = Team.objects.get(pk=team_id)
    if request.method == "POST":
        forms = [
            ScratchForm(request.POST, prefix=str(i), instance=scratches[i - 1])
            for i in range(1, number_scratches + 1)
        ]
        all_good = True
        for form in forms:
            all_good = all_good and form.is_valid()
        if all_good:
            for form in forms:
                form.save()
            return redirect_and_flash_success(
                request, "Scratches successfully modified")
    else:
        forms = [
            ScratchForm(prefix=str(i), instance=scratches[i - 1])
            for i in range(1,
                           len(scratches) + 1)
        ]
    delete_links = [
        "/team/" + str(team_id) + "/scratches/delete/" + str(scratches[i].id)
        for i in range(len(scratches))
    ]
    links = [("/team/" + str(team_id) + "/scratches/add/1/", "Add Scratch")]
    return render(
        request, "common/data_entry_multiple.html", {
            "forms": list(zip(forms, delete_links)),
            "data_type": "Scratch",
            "links": links,
            "title": "Viewing Scratch Information for %s" % (team.display_backend)
        })


@permission_required("tab.tab_settings.can_change", login_url="/403/")
def all_tab_cards(request):
    all_teams = Team.objects.all()
    return render(request, "tab/all_tab_cards.html", locals())


def pretty_tab_card(request, team_id):
    try:
        team_id = int(team_id)
    except Exception:
        return redirect_and_flash_error(request, "Invalid team id")
    team = Team.objects.get(pk=team_id)
    return render(request, "tab/pretty_tab_card.html", {"team": team})


def tab_card(request, team_id):
    return render(
        request,
        "tab/tab_card.html",
        get_tab_card_data(request, team_id)
    )


def tab_cards_json(request):
    # Serialize the data to JSON
    json_data = json.dumps(
        {"tab_cards": get_all_json_data()}, indent=4, cls=JSONDecimalEncoder)

    # Create the HTTP response with the file download header
    response = HTTPResponse(json_data, content_type="application/json")
    response['Content-Disposition'] = 'attachment; filename="tab_cards.json"'
    return response


def tab_cards_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="tab_cards.csv"'
    writer = csv.writer(response)
    csv_tab_cards(writer)
    return response


def rank_teams_ajax(request):
    return render(request, "tab/rank_teams.html", {"title": "Team Rankings"})


def get_team_rankings(request):
    ranked_teams = tab_logic.rankings.rank_teams()
    teams = []
    for i, team_stat in enumerate(ranked_teams):
        tiebreaker = "N/A"
        if i != len(ranked_teams) - 1:
            next_team_stat = ranked_teams[i + 1]
            tiebreaker_stat = team_stat.get_tiebreaker(next_team_stat)
            if tiebreaker_stat is not None:
                tiebreaker = tiebreaker_stat.name
            else:
                tiebreaker = "Tie not broken"
        teams.append((team_stat.team, team_stat[rankings.WINS],
                      team_stat[rankings.SPEAKS], team_stat[rankings.RANKS],
                      tiebreaker))

    nov_teams = list(filter(
        lambda ts: all(
            map(lambda d: d.novice_status == Debater.NOVICE, ts[0].debaters.
                all())), teams))

    return teams, nov_teams


def rank_teams(request):
    teams, nov_teams = cache_logic.cache_fxn_key(
        get_team_rankings,
        "team_rankings",
        cache_logic.DEFAULT,
        request
    )

    return render(request, "tab/rank_teams_component.html", {
        "varsity": teams,
        "novice": nov_teams,
        "title": "Team Rankings"
    })
