from mittab.apps.tab.views import school_views
from django.conf.urls import url

urlpatterns = [
    url(r"^school/(\d+)/$", school_views.view_school, name="view_school"),
    url(r"^school/(\d+)/delete/$", school_views.delete_school, name="delete_school"),
    url(r"^view_schools/$", school_views.view_schools, name="view_schools"),
    url(r"^enter_school/$", school_views.enter_school, name="enter_school"),
]