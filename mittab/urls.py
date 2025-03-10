from django.views import i18n
from django.urls import include
from django.urls import path, re_path
from django.contrib import admin
from django.contrib.auth.views import LoginView

import mittab.settings as settings
import mittab.apps.tab.views as views
import mittab.apps.tab.judge_views as judge_views
import mittab.apps.tab.team_views as team_views
import mittab.apps.tab.debater_views as debater_views
import mittab.apps.tab.pairing_views as pairing_views
import mittab.apps.tab.outround_pairing_views as outround_pairing_views


admin.autodiscover()

urlpatterns = [
    path("admin/logout/", views.tab_logout, name="admin_logout"),
    path("accounts/logout/", views.tab_logout, name="logout"),
    re_path(r"^admin/", admin.site.urls, name="admin"),
    path("dynamic-media/jsi18n/", i18n.JavaScriptCatalog.as_view(), name="js18"),
    path("", views.index, name="index"),
    re_path(r"^403/", views.render_403, name="403"),
    re_path(r"^404/", views.render_404, name="404"),
    re_path(r"^500/", views.render_500, name="500"),

    # Account related
    path("accounts/login/",
         LoginView.as_view(template_name="registration/login.html"),
         name="tab_login"),

    # Judge related
    re_path(r"^judges/", judge_views.public_view_judges, name="public_judges"),
    re_path(r"^judge/(\d+)/$", judge_views.view_judge, name="view_judge"),
    re_path(r"^judge/(\d+)/scratches/add/(\d+)/",
            judge_views.add_scratches,
            name="add_scratches"),
    re_path(r"^judge/(\d+)/scratches/view/",
            judge_views.view_scratches,
            name="view_scratches"),
    re_path(r"^judge/(\d+)/check_ins/round/(\d+)/$",
            judge_views.judge_check_in,
            name="judge_check_in"),
    path("view_judges/", judge_views.view_judges, name="view_judges"),
    path("enter_judge/", judge_views.enter_judge, name="enter_judge"),

    # School related
    re_path(r"^school/(\d+)/$", views.view_school, name="view_school"),
    re_path(r"^school/(\d+)/delete/$", views.delete_school, name="delete_school"),
    path("view_schools/", views.view_schools, name="view_schools"),
    path("enter_school/", views.enter_school, name="enter_school"),

    # Room related
    re_path(r"^room/(\d+)/$", views.view_room, name="view_room"),
    path("view_rooms/", views.view_rooms, name="view_rooms"),
    path("enter_room/", views.enter_room, name="enter_room"),
    re_path(r"^room/(\d+)/check_ins/round/(\d+)/$",
            views.room_check_in,
            name="room_check_in"),


    # Scratch related
    re_path(r"^judge/(\d+)/scratches/delete/(\d+)/",
            views.delete_scratch,
            name="delete_scratch_judge"),
    re_path(r"^team/(\d+)/scratches/delete/(\d+)/",
            views.delete_scratch,
            name="delete_scratch_team"),
    re_path(r"^scratches/view/", views.view_scratches, name="view_scratches"),
    re_path(r"^enter_scratch/", views.add_scratch, name="add_scratch"),

    # Team related
    re_path(r"^teams/", team_views.public_view_teams, name="public_teams"),
    re_path(r"^team/(\d+)/$", team_views.view_team, name="view_team"),
    re_path(r"^team/(\d+)/scratches/add/(\d+)/",
            team_views.add_scratches,
            name="add_scratches"),
    re_path(r"^team/(\d+)/scratches/view/",
            team_views.view_scratches,
            name="view_scratches_team"),
    path("view_teams/", team_views.view_teams, name="view_teams"),
    path("enter_team/", team_views.enter_team, name="enter_team"),
    path("all_tab_cards/", team_views.all_tab_cards, name="all_tab_cards"),
    re_path(r"^team/card/(\d+)/$", team_views.tab_card, name="tab_card"),
    re_path(r"^team/card/(\d+)/pretty/$",
            team_views.pretty_tab_card,
            name="pretty_tab_card"),
    path("team/ranking/", team_views.rank_teams_ajax,
         name="rank_teams_ajax"),
    path("team/rank/", team_views.rank_teams, name="rank_teams"),
    re_path(r"^team/(\d+)/check_ins/$",
            team_views.team_check_in,
            name="team_check_in"),

    # Debater related
    re_path(r"^debater/(\d+)/$", debater_views.view_debater, name="view_debater"),
    path("view_debaters/", debater_views.view_debaters,
         name="view_debaters"),
    path("enter_debater/", debater_views.enter_debater,
         name="enter_debater"),
    path("debater/ranking/",
         debater_views.rank_debaters_ajax,
         name="rank_debaters_ajax"),
    path("debater/rank/", debater_views.rank_debaters, name="rank_debaters"),

    # Pairing related
    path("pairings/status/", pairing_views.view_status, name="view_status"),
    path("pairings/view_rounds/",
         pairing_views.view_rounds,
         name="view_rounds"),
    re_path(r"^round/(\d+)/$", pairing_views.view_round, name="view_round"),
    re_path(r"^round/(\d+)/stats/$", pairing_views.team_stats, name="team_stats"),
    re_path(r"^round/(\d+)/result/$",
            pairing_views.enter_result,
            name="enter_result"),
    re_path(r"^round/(\d+)/result/(\d+)/$",
            pairing_views.enter_multiple_results,
            name="enter_multiple_results"),
    re_path(r"^round/(\d+)/alternative_judges/(\d+)/$",
            pairing_views.alternative_judges,
            name="round_alternative_judges"),
    re_path(r"^round/(\d+)/(\d+)/alternative_teams/(gov|opp)/$",
            pairing_views.alternative_teams,
            name="round_alternative_teams"),
    re_path(r"^round/(\d+)/alternative_judges/$",
            pairing_views.alternative_judges,
            name="alternative_judges"),
    re_path(r"^round/(\d+)/assign_judge/(\d+)/$",
            pairing_views.assign_judge,
            name="assign_judge"),
    re_path(r"^pairings/assign_team/(\d+)/(gov|opp)/(\d+)/$",
            pairing_views.assign_team,
            name="assign_team"),
    re_path(r"^round/(\d+)/assign_judge/(\d+)/(\d+)/$",
            pairing_views.assign_judge,
            name="swap_judge"),
    path("pairing/pair_round/", pairing_views.pair_round, name="pair_round"),
    path("pairing/assign_judges/",
         pairing_views.assign_judges_to_pairing,
         name="assign_judges"),
    path("pairing/confirm_start_tourny/",
         pairing_views.confirm_start_new_tourny,
         name="confirm_start_tourny"),
    path("pairing/start_tourny/",
         pairing_views.start_new_tourny,
         name="start_tourny"),
    path("pairings/pairinglist/",
         pairing_views.pretty_pair,
         name="pretty_pair"),
    path("pairings/missing_ballots/",
         pairing_views.missing_ballots,
         name="missing_ballots"),
    path("pairings/pairinglist/printable/",
         pairing_views.pretty_pair_print,
         name="pretty_pair_print"),
    path("pairing/backup/",
         pairing_views.manual_backup,
         name="manual_backup"),
    path("pairing/release/",
         pairing_views.toggle_pairing_released,
         name="toggle_pairing_released"),
    path("pairing/view_backups/",
         pairing_views.view_backups,
         name="view_backups"),
    path("e_ballots/", pairing_views.e_ballot_search,
         name="e_ballot_search"),
    re_path(r"e_ballots/(\S+)/$",
            pairing_views.enter_e_ballot,
            name="enter_e_ballot"),
    path("pairings/simulate_rounds/", views.simulate_round, name="simulate_round"),
    path("batch_checkin/", views.batch_checkin, name="batch_checkin"),

    # Outround related
    re_path(r"break/",
            outround_pairing_views.break_teams,
            name="break"),
    path("outround_pairing/<int:type_of_round>/<int:num_teams>",
         outround_pairing_views.outround_pairing_view,
         name="outround_pairing_view"),
    path("outround_pairing",
         outround_pairing_views.outround_pairing_view,
         name="outround_pairing_view_default"),
    re_path(r"^outround/(\d+)/alternative_judges/(\d+)/$",
            outround_pairing_views.alternative_judges,
            name="outround_alternative_judges"),
    re_path(r"^outround/(\d+)/(\d+)/alternative_teams/(gov|opp)/$",
            outround_pairing_views.alternative_teams,
            name="outround_alternative_teams"),
    re_path(r"^outround/(\d+)/alternative_judges/$",
            outround_pairing_views.alternative_judges,
            name="outround_alternative_judges"),
    re_path(r"^outround/(\d+)/assign_judge/(\d+)/$",
            outround_pairing_views.assign_judge,
            name="outround_assign_judge"),
    re_path(r"^outround/pairings/assign_team/(\d+)/(gov|opp)/(\d+)/$",
            outround_pairing_views.assign_team,
            name="outround_assign_team"),
    re_path(r"^outround/(\d+)/assign_judge/(\d+)/(\d+)/$",
            outround_pairing_views.assign_judge,
            name="outround_swap_judge"),
    re_path(r"^outround/(\d+)/result/$",
            outround_pairing_views.enter_result,
            name="enter_result"),
    path("outround_pairing/pair/<int:type_of_round>/<int:num_teams>/",
         outround_pairing_views.pair_next_outround,
         name="next_outround"),
    path("outround_pairings/pairinglist/<int:type_of_round>/",
         outround_pairing_views.pretty_pair,
         name="outround_pretty_pair"),
    path("outround_pairings/pairinglist/printable/<int:type_of_round>/",
         outround_pairing_views.pretty_pair_print,
         name="outround_pretty_pair_print"),
    path("outround_pairing/release/<int:num_teams>/<int:type_of_round>/",
         outround_pairing_views.toggle_pairing_released,
         name="toggle_outround_pairing_released"),
    path("outround_result/<int:type_of_round>",
         outround_pairing_views.forum_view,
         name="forum_view"),
    path("outround_choice/<int:outround_id>",
         outround_pairing_views.update_choice,
         name="update_choice"),

    # Settings related
    re_path(r"^settings_form",
            views.settings_form,
            name="settings_form"),

    # Backups
    re_path(r"^backup/restore/(.+)/$",
            pairing_views.restore_backup,
            name="restore_backup"),
    re_path(r"^backup/download/(.+)/$",
            pairing_views.download_backup,
            name="download_backup"),
    re_path(r"^backup/(.+)/$", pairing_views.view_backup, name="view_backup"),
    path("upload_backup/", pairing_views.upload_backup,
         name="upload_backup"),

    # Data Upload
    path("import_data/", views.upload_data, name="upload_data"),

    # Tournament Archive
    path("archive/download/", views.generate_archive, name="download_archive"),

    # Cache related
    re_path(r"^cache_refresh", views.force_cache_refresh, name="cache_refresh"),
]

if settings.SILK_ENABLED:
    urlpatterns += [
        # Profiler
        path("silk/", include("silk.urls", namespace="silk"))
    ]

handler403 = "mittab.apps.tab.views.render_403"
handler404 = "mittab.apps.tab.views.render_404"
handler500 = "mittab.apps.tab.views.render_500"
