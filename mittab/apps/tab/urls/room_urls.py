from django.conf.urls import url
from mittab.apps.tab.views import room_views

urlpatterns = [
    url(r"^room/(\d+)/$", room_views.view_room, name="view_room"),
    url(r"^view_rooms/$", room_views.view_rooms, name="view_rooms"),
    url(r"^enter_room/$", room_views.enter_room, name="enter_room"),
    url(r"^room/(\d+)/check_ins/round/(\d+)/$",
        room_views.room_check_in,
        name="room_check_in"),
    url(r"^batch_room_checkin/$", room_views.batch_checkin, name="batch_room_checkin"),
    url(r"^room/(\d+)/toggle_tag/(\w+)/$",
        room_views.room_tag_toggle,
        name="room_tag_toggle"),
    
    url(r"^delete_room_tag/(\d+)/$",
        room_views.delete_room_tag,
        name="delete_room_tag"),
    
    url(r"^batch_room_tag/$", room_views.batch_room_tag, name="batch_room_tag"),
    url(r"^add_room_tag/$", room_views.add_room_tag, name="add_room_tag"),
    url(r"^tag/(\d+)/$", room_views.view_tag, name="view_tag"),

]