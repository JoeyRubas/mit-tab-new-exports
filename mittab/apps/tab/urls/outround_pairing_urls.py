from django.conf.urls import url
from django.urls import path
from mittab.apps.tab.views import outround_pairing_views

urlpatterns = [
    url(r"break/",
        outround_pairing_views.break_teams,
        name="break"),
    path("outround_pairing/<int:type_of_round>/<int:num_teams>",
         outround_pairing_views.outround_pairing_view,
         name="outround_pairing_view"),
    path("outround_pairing",
         outround_pairing_views.outround_pairing_view,
         name="outround_pairing_view_default"),
    url(r"^outround/(\d+)/alternative_judges/(\d+)/$",
        outround_pairing_views.alternative_judges,
        name="outround_alternative_judges"),
    url(r"^outround/(\d+)/(\d+)/alternative_teams/(gov|opp)/$",
        outround_pairing_views.alternative_teams,
        name="outround_alternative_teams"),
    url(r"^outround/(\d+)/alternative_judges/$",
        outround_pairing_views.alternative_judges,
        name="outround_alternative_judges"),
    url(r"^outround/(\d+)/assign_judge/(\d+)/$",
        outround_pairing_views.assign_judge,
        name="outround_assign_judge"),
    url(r"^outround/pairings/assign_team/(\d+)/(gov|opp)/(\d+)/$",
        outround_pairing_views.assign_team,
        name="outround_assign_team"),
    url(r"^outround/(\d+)/assign_judge/(\d+)/(\d+)/$",
        outround_pairing_views.assign_judge,
        name="outround_swap_judge"),
    url(r"^outround/(\d+)/result/$",
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
    ]