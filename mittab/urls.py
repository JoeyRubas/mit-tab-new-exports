from django.views import i18n
from django.urls import include, path
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
    path("admin/", admin.site.urls, name="admin"),
    path("dynamic-media/jsi18n/", i18n.JavaScriptCatalog.as_view(), name="js18"),
    path("", views.index, name="index"),
    path("403/", views.render_403, name="403"),
    path("404/", views.render_404, name="404"),
    path("500/", views.render_500, name="500"),
    
    # Account related
    path("accounts/login/", LoginView.as_view(template_name="registration/login.html"), name="tab_login"),
    
    # Judge related
    path("judges/", judge_views.public_view_judges, name="public_judges"),
    path("judge/<int:judge_id>/", judge_views.view_judge, name="view_judge"),
    path("judge/<int:judge_id>/scratches/add/<int:scratch_id>/", judge_views.add_scratches, name="add_scratches"),
    path("judge/<int:judge_id>/scratches/view/", judge_views.view_scratches, name="view_scratches"),
    path("judge/<int:judge_id>/check_ins/round/<int:round_id>/", judge_views.judge_check_in, name="judge_check_in"),
    path("view_judges/", judge_views.view_judges, name="view_judges"),
    path("enter_judge/", judge_views.enter_judge, name="enter_judge"),
    path("batch_checkin/", judge_views.batch_checkin, name="batch_checkin"),
    
    # School related
    path("school/<int:school_id>/", views.view_school, name="view_school"),
    path("school/<int:school_id>/delete/", views.delete_school, name="delete_school"),
    path("view_schools/", views.view_schools, name="view_schools"),
    path("enter_school/", views.enter_school, name="enter_school"),
    
    # Room related
    path("room/<int:room_id>/", views.view_room, name="view_room"),
    path("view_rooms/", views.view_rooms, name="view_rooms"),
    path("enter_room/", views.enter_room, name="enter_room"),
    path("room/<int:room_id>/check_ins/round/<int:round_id>/", views.room_check_in, name="room_check_in"),
    path("batch_room_checkin/", views.batch_checkin, name="batch_room_checkin"),
    
    # Scratch related
    path("judge/<int:judge_id>/scratches/delete/<int:scratch_id>/", views.delete_scratch, name="delete_scratch_judge"),
    path("team/<int:team_id>/scratches/delete/<int:scratch_id>/", views.delete_scratch, name="delete_scratch_team"),
    path("scratches/view/", views.view_scratches, name="view_scratches"),
    path("enter_scratch/", views.add_scratch, name="add_scratch"),
    
    # Team related
    path("teams/", team_views.public_view_teams, name="public_teams"),
    path("team/<int:team_id>/", team_views.view_team, name="view_team"),
    path("team/<int:team_id>/scratches/add/<int:scratch_id>/", team_views.add_scratches, name="add_scratches"),
    path("team/<int:team_id>/scratches/view/", team_views.view_scratches, name="view_scratches_team"),
    path("view_teams/", team_views.view_teams, name="view_teams"),
    path("enter_team/", team_views.enter_team, name="enter_team"),
    path("all_tab_cards/", team_views.all_tab_cards, name="all_tab_cards"),
    path("team/card/<int:team_id>/", team_views.tab_card, name="tab_card"),
    path("team/card/<int:team_id>/pretty/", team_views.pretty_tab_card, name="pretty_tab_card"),
    path("team/ranking/", team_views.rank_teams_ajax, name="rank_teams_ajax"),
    path("team/rank/", team_views.rank_teams, name="rank_teams"),
    
    # Debater related
    path("debater/<int:debater_id>/", debater_views.view_debater, name="view_debater"),
    path("view_debaters/", debater_views.view_debaters, name="view_debaters"),
    path("enter_debater/", debater_views.enter_debater, name="enter_debater"),
    path("debater/ranking/", debater_views.rank_debaters_ajax, name="rank_debaters_ajax"),
    path("debater/rank/", debater_views.rank_debaters, name="rank_debaters"),
    
    # Import Data
    path("import_data/", views.upload_data, name="upload_data"),
    
    # Tournament Archive
    path("archive/download/", views.generate_archive, name="download_archive"),
    
    # Cache related
    path("cache_refresh/", views.force_cache_refresh, name="cache_refresh"),
]

if settings.SILK_ENABLED:
    urlpatterns += [
        path("silk/", include("silk.urls", namespace="silk"))
    ]

handler403 = "mittab.apps.tab.views.render_403"
handler404 = "mittab.apps.tab.views.render_404"
handler500 = "mittab.apps.tab.views.render_500"
