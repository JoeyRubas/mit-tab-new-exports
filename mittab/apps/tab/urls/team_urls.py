from django.conf.urls import url
from mittab.apps.tab.views import team_views

urlpatterns = [
    url(r"^teams/", team_views.public_view_teams, name="public_teams"),
    url(r"^team/(\d+)/$", team_views.view_team, name="view_team"),
    url(r"^team/(\d+)/scratches/add/(\d+)/",
        team_views.add_scratches,
        name="add_scratches"),
    url(r"^team/(\d+)/scratches/view/",
        team_views.view_scratches,
        name="view_scratches_team"),
    url(r"^view_teams/$", team_views.view_teams, name="view_teams"),
    url(r"^enter_team/$", team_views.enter_team, name="enter_team"),
    url(r"^all_tab_cards/$", team_views.all_tab_cards, name="all_tab_cards"),
    url(r"^team/card/(\d+)/$", team_views.tab_card, name="tab_card"),
    url(r"^team/card/(\d+)/pretty/$",
        team_views.pretty_tab_card,
        name="pretty_tab_card"),
    url(r"^team/ranking/$", team_views.rank_teams_ajax,
        name="rank_teams_ajax"),
    url(r"^team/rank/$", team_views.rank_teams, name="rank_teams"),
]