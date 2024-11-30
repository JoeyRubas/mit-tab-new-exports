from django.conf.urls import url
from mittab.apps.tab.views import judge_views

urlpatterns = [
    url(r"^judges/", judge_views.public_view_judges, name="public_judges"),
    url(r"^judge/(\d+)/$", judge_views.view_judge, name="view_judge"),
    url(r"^judge/(\d+)/scratches/add/(\d+)/",
        judge_views.add_scratches,
        name="add_scratches"),
    url(r"^judge/(\d+)/scratches/view/",
        judge_views.view_scratches,
        name="view_scratches"),
    url(r"^judge/(\d+)/check_ins/round/(\d+)/$",
        judge_views.judge_check_in,
        name="judge_check_in"),
    url(r"^view_judges/$", judge_views.view_judges, name="view_judges"),
    url(r"^enter_judge/$", judge_views.enter_judge, name="enter_judge"),
    url(r"^batch_checkin/$", judge_views.batch_checkin, name="batch_checkin"),
    ]