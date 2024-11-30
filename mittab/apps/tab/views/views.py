from django.contrib.auth.decorators import permission_required
from django.contrib.auth import logout
from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import render, reverse
import yaml

from mittab.apps.tab.archive import ArchiveExporter
from mittab.apps.tab.forms import SchoolForm, UploadDataForm, ScratchForm, \
    SettingsForm
from mittab.apps.tab.helpers import redirect_and_flash_error, \
    redirect_and_flash_success
from mittab.apps.tab.models import *
from mittab.libs import cache_logic
from mittab.libs.data_import import import_judges, import_rooms, import_teams, \
    import_scratches


def index(request):
    school_list = [(school.pk, school.name) for school in School.objects.all()]
    judge_list = [(judge.pk, judge.name) for judge in Judge.objects.all()]
    team_list = [(team.pk, team.display_backend) for team in Team.objects.all()]
    debater_list = [(debater.pk, debater.display)
                    for debater in Debater.objects.all()]
    room_list = [(room.pk, room.name) for room in Room.objects.all()]

    number_teams = len(team_list)
    number_judges = len(judge_list)
    number_schools = len(school_list)
    number_debaters = len(debater_list)
    number_rooms = len(room_list)

    return render(request, "common/index.html", locals())


def tab_logout(request, *args):
    logout(request)
    return redirect_and_flash_success(request,
                                      "Successfully logged out",
                                      path="/")


def render_403(request, *args, **kwargs):
    response = render(request, "common/403.html")
    response.status_code = 403
    return response


def render_404(request, *args, **kwargs):
    response = render(request, "common/404.html")
    response.status_code = 404
    return response


def render_500(request, *args, **kwargs):
    response = render(request, "common/500.html")
    response.status_code = 500
    return response


# View for manually adding scratches
def add_scratch(request):
    if request.method == "POST":
        form = ScratchForm(request.POST)
        if form.is_valid():
            form.save()
        return redirect_and_flash_success(request,
                                          "Scratch created successfully")
    else:
        form = ScratchForm(initial={"scratch_type": 0})
    return render(request, "common/data_entry.html", {
        "title": "Adding Scratch",
        "form": form
    })

#### END SCHOOL ###

@permission_required("tab.scratch.can_delete", login_url="/403/")
def delete_scratch(request, item_id, scratch_id):
    try:
        scratch_id = int(scratch_id)
        scratch = Scratch.objects.get(pk=scratch_id)
        scratch.delete()
    except Scratch.DoesNotExist:
        return redirect_and_flash_error(
            request,
            "This scratch does not exist, please try again with a valid id.")
    return redirect_and_flash_success(request,
                                      "Scratch deleted successfully",
                                      path="/")


def view_scratches(request):
    # Get a list of (id,school_name) tuples
    c_scratches = [(s.team.pk, str(s), 0, "") for s in Scratch.objects.all()]
    return render(
        request, "common/list_data.html", {
            "item_type": "team",
            "title": "Viewing All Scratches for Teams",
            "item_list": c_scratches
        })


def get_settings_from_yaml():
    default_settings = []
    with open(settings.SETTING_YAML_PATH, "r") as stream:
        default_settings = yaml.safe_load(stream)

    to_return = []

    for setting in default_settings:
        tab_setting = TabSettings.objects.filter(key=setting["name"]).first()

        if tab_setting:
            if "type" in setting and setting["type"] == "boolean":
                setting["value"] = tab_setting.value == 1
            else:
                setting["value"] = tab_setting.value

        to_return.append(setting)

    return to_return

### SETTINGS VIEWS ###


@permission_required("tab.tab_settings.can_change", login_url="/403/")
def settings_form(request):
    yaml_settings = get_settings_from_yaml()
    if request.method == "POST":
        _settings_form = SettingsForm(request.POST, settings=yaml_settings)

        if _settings_form.is_valid():
            _settings_form.save()
            return redirect_and_flash_success(
                request,
                "Tab settings updated!",
                path=reverse("settings_form")
            )
        return render(  # Allows for proper validation checking
            request, "tab/settings_form.html", {
                "form": settings_form,
            })

    _settings_form = SettingsForm(settings=yaml_settings)

    return render(
        request, "tab/settings_form.html", {
            "form": _settings_form,
        })


def upload_data(request):
    team_info = {"errors": [], "uploaded": False}
    judge_info = {"errors": [], "uploaded": False}
    room_info = {"errors": [], "uploaded": False}
    scratch_info = {"errors": [], "uploaded": False}

    if request.method == "POST":
        form = UploadDataForm(request.POST, request.FILES)
        if form.is_valid():
            if "team_file" in request.FILES:
                team_info["errors"] = import_teams.import_teams(
                    request.FILES["team_file"])
                team_info["uploaded"] = True
            if "judge_file" in request.FILES:
                judge_info["errors"] = import_judges.import_judges(
                    request.FILES["judge_file"])
                judge_info["uploaded"] = True
            if "room_file" in request.FILES:
                room_info["errors"] = import_rooms.import_rooms(
                    request.FILES["room_file"])
                room_info["uploaded"] = True
            if "scratch_file" in request.FILES:
                scratch_info["errors"] = import_scratches.import_scratches(
                    request.FILES["scratch_file"])
                scratch_info["uploaded"] = True

        if not team_info["errors"] + judge_info["errors"] + \
                room_info["errors"] + scratch_info["errors"]:
            return redirect_and_flash_success(request,
                                              "Data imported successfully")
    else:
        form = UploadDataForm()
    return render(
        request, "common/data_upload.html", {
            "form": form,
            "title": "Upload Input Files",
            "team_info": team_info,
            "judge_info": judge_info,
            "room_info": room_info,
            "scratch_info": scratch_info
        })


def force_cache_refresh(request):
    key = request.GET.get("key", "")

    cache_logic.invalidate_cache(key)

    redirect_to = request.GET.get("next", "/")

    return redirect_and_flash_success(request,
                                      "Refreshed!",
                                      path=redirect_to)


@permission_required("tab.tab_settings.can_change", login_url="/403/")
def generate_archive(request):
    tournament_name = request.META["SERVER_NAME"].split(".")[0]
    filename = tournament_name + ".xml"

    xml = ArchiveExporter(tournament_name).export_tournament()

    response = HttpResponse(xml, content_type="text/xml; charset=utf-8")
    response["Content-Length"] = len(xml)
    response["Content-Disposition"] = "attachment; filename=%s" % filename
    return response
