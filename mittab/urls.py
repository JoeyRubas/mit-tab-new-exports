from django.views import i18n
from django.conf.urls import url, include
from django.contrib import admin
from django.contrib.auth.views import LoginView

import mittab.settings as settings
from mittab.apps.tab.views import views
from mittab.apps.tab.urls import debater_urls, judge_urls, outround_pairing_urls, pairing_urls, room_urls, school_urls, team_urls


admin.autodiscover()

urlpatterns = [
    url(r"^admin/logout/$", views.tab_logout, name="admin_logout"),
    url(r"^accounts/logout/$", views.tab_logout, name="logout"),
    url(r"^admin/", admin.site.urls, name="admin"),
    url(r"^dynamic-media/jsi18n/$", i18n.JavaScriptCatalog.as_view(), name="js18"),
    url(r"^$", views.index, name="index"),
    url(r"^403/", views.render_403, name="403"),
    url(r"^404/", views.render_404, name="404"),
    url(r"^500/", views.render_500, name="500"),

    # Account related
    url(r"^accounts/login/$",
        LoginView.as_view(template_name="registration/login.html"),
        name="tab_login"),


    # Scratch related
    url(r"^judge/(\d+)/scratches/delete/(\d+)/",
        views.delete_scratch,
        name="delete_scratch_judge"),
    url(r"^team/(\d+)/scratches/delete/(\d+)/",
        views.delete_scratch,
        name="delete_scratch_team"),
    url(r"^scratches/view/", views.view_scratches, name="view_scratches"),
    url(r"^enter_scratch/", views.add_scratch, name="add_scratch"),

    # Settings related
    url(r"^settings_form",
        views.settings_form,
        name="settings_form"),

    # Data Upload
    url(r"^import_data/$", views.upload_data, name="upload_data"),

    # Tournament Archive
    url(r"^archive/download/$", views.generate_archive, name="download_archive"),

    # Cache related
    url(r"^cache_refresh", views.force_cache_refresh, name="cache_refresh"),
]

if settings.SILK_ENABLED:
    urlpatterns += [
        # Profiler
        url(r"^silk/", include("silk.urls", namespace="silk"))
    ]

urlpatterns += debater_urls.urlpatterns
urlpatterns += judge_urls.urlpatterns
urlpatterns += outround_pairing_urls.urlpatterns
urlpatterns += pairing_urls.urlpatterns
urlpatterns += room_urls.urlpatterns
urlpatterns += school_urls.urlpatterns
urlpatterns += team_urls.urlpatterns


handler403 = "mittab.apps.tab.views.views.render_403"
handler404 = "mittab.apps.tab.views.views.render_404"
handler500 = "mittab.apps.tab.views.views.render_500"
