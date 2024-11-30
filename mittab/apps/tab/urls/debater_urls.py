from django.conf.urls import url

from mittab.apps.tab.views import debater_views

urlpatterns = [
        # Debater related
    url(r"^debater/(\d+)/$", debater_views.view_debater, name="view_debater"),
    url(r"^view_debaters/$", debater_views.view_debaters,
        name="view_debaters"),
    url(r"^enter_debater/$", debater_views.enter_debater,
        name="enter_debater"),
    url(r"^debater/ranking/$",
        debater_views.rank_debaters_ajax,
        name="rank_debaters_ajax"),
    url(r"^debater/rank/$", debater_views.rank_debaters, name="rank_debaters"),

]