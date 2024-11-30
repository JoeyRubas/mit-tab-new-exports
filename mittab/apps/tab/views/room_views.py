from django.http import Http404, JsonResponse
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.contrib.auth.decorators import permission_required
from mittab.apps.tab.forms import RoomForm, RoomTagForm
from mittab.apps.tab.helpers import redirect_and_flash_error, redirect_and_flash_success
from mittab.apps.tab.models import Room, RoomCheckIn, RoomTag, Round, TabSettings
from mittab.libs.tab_logic import TabFlags


def view_rooms(request):
    def flags(room):
        result = 0
        if room.rank == 0:
            result |= TabFlags.ROOM_ZERO_RANK
        else:
            result |= TabFlags.ROOM_NON_ZERO_RANK
        return result

    all_flags = [[TabFlags.ROOM_ZERO_RANK, TabFlags.ROOM_NON_ZERO_RANK]]
    all_rooms = [(room.pk, room.name, flags(room),
                  TabFlags.flags_to_symbols(flags(room)))
                 for room in Room.objects.all()]
    filters, symbol_text = TabFlags.get_filters_and_symbols(all_flags)
    return render(
        request, "common/list_data.html", {
            "item_type": "room",
            "title": "Viewing All Rooms",
            "item_list": all_rooms,
            "symbol_text": symbol_text,
            "filters": filters
        })


def view_room(request, room_id):
    room_id = int(room_id)
    try:
        room = Room.objects.get(pk=room_id)
    except Room.DoesNotExist:
        return redirect_and_flash_error(request, "Room not found")
    if request.method == "POST":
        form = RoomForm(request.POST, instance=room)
        if form.is_valid():
            try:
                form.save()
            except ValueError:
                return redirect_and_flash_error(
                    request,
                    "Room name cannot be validated, most likely a non-existent room"
                )
            return redirect_and_flash_success(
                request, "School {} updated successfully".format(
                    form.cleaned_data["name"]))
    else:
        form = RoomForm(instance=room)
    return render(request, "common/data_entry.html", {
        "form": form,
        "links": [],
        "title": "Viewing Room: %s" % (room.name)
    })

def view_tag(request, tag_id):
    tag_id = int(tag_id)
    try:
        tag = RoomTag.objects.get(pk=tag_id)
    except RoomTag.DoesNotExist:
        return redirect_and_flash_error(request, "Tag not found")
    if request.method == "POST":
        form = RoomTagForm(request.POST, instance=tag)
        if form.is_valid():
            try:
                form.save()
            except ValueError as e:
                print(e)
                return redirect_and_flash_error(
                    request,
                    "Tag name cannot be validated, most likely a non-existent tag"
                )
            return redirect_and_flash_success(
                request, "Tag {} updated successfully".format(
                    form.cleaned_data["tag"]),
                path=reverse("view_tag", args=[tag_id]))
    else:
        form = RoomTagForm(instance=tag)
    return render(request, "common/data_entry.html", {
        "form": form,
        "links": [],
        "tag_obj": tag,
        "title": "Viewing Tag: %s" % (tag.tag)
    })

def delete_room_tag(request, tag_id):
    if request.method == "POST":
        tag_id = request.POST.get("tag_id")
        try:
            rounds = list(Round.objects.filter(room_tags__id=tag_id))
            tag = RoomTag.objects.get(pk=tag_id)
            tag.delete()
            for roundobj in rounds:
                print(roundobj.judges.all())
                roundobj.save()
            return redirect_and_flash_success(request, "Tag deleted successfully", path=reverse("batch_room_tag"))
        except RoomTag.DoesNotExist:
            return redirect_and_flash_error(request, "Tag not found")
    return redirect_and_flash_error(request, "Invalid request")


def enter_room(request):
    if request.method == "POST":
        form = RoomForm(request.POST)
        if form.is_valid():
            try:
                form.save()
            except ValueError:
                return redirect_and_flash_error(
                    request,
                    "Room name cannot be validated, most likely a duplicate room"
                )
            return redirect_and_flash_success(
                request,
                "Room {} created successfully".format(
                    form.cleaned_data["name"]),
                path="/")
    else:
        form = RoomForm()
    return render(request, "common/data_entry.html", {
        "form": form,
        "title": "Create Room"
    })


def batch_checkin(request):
    rooms_and_checkins = []

    round_numbers = list([i + 1 for i in range(TabSettings.get("tot_rounds"))])
    for room in Room.objects.all():
        checkins = []
        for round_number in [0] + round_numbers:  # 0 is for outrounds
            checkins.append(room.is_checked_in_for_round(round_number))
        rooms_and_checkins.append((room, checkins))

    return render(request, "tab/room_batch_checkin.html", {
        "rooms_and_checkins": rooms_and_checkins,
        "round_numbers": round_numbers
    })


@permission_required("tab.tab_settings.can_change", login_url="/403")
def room_check_in(request, room_id, round_number):
    room_id, round_number = int(room_id), int(round_number)

    if round_number < 0 or round_number > TabSettings.get("tot_rounds"):
        # 0 is so that outrounds don't throw an error
        raise Http404("Round does not exist")

    room = get_object_or_404(Room, pk=room_id)
    if request.method == "POST":
        if not room.is_checked_in_for_round(round_number):
            check_in = RoomCheckIn(room=room, round_number=round_number)
            check_in.save()
    elif request.method == "DELETE":
        if room.is_checked_in_for_round(round_number):
            check_ins = RoomCheckIn.objects.filter(room=room,
                                                   round_number=round_number)
            check_ins.delete()
    else:
        raise Http404("Must be POST or DELETE")
    return JsonResponse({"success": True})

def batch_room_tag(request):
    rooms_and_tags = []
    tags = list(RoomTag.objects.order_by("-priority"))
    tag_count = len(tags)   
    for room in Room.objects.prefetch_related("tags").all():
        row = (room, [[tag, False] for tag in tags])
        for tag in room.tags.all():
            row[1][tags.index(tag)][1] = True
        rooms_and_tags.append(row)  
    return render(request, "tab/room_batch_tag.html", {
        "rooms_and_tags": rooms_and_tags,
        "tags": tags
    })


@permission_required("tab.tab_settings.can_change", login_url="/403")
def room_tag_toggle(request, room_id, tag_id):
    room_id, tag_id  = int(room_id), int(tag_id)
    room = get_object_or_404(Room, pk=room_id)
    tag = get_object_or_404(RoomTag, pk=tag_id)
    if not room.is_tagged_with(tag_id):
        room.tags.add(tag)
        room.save()
    elif room.is_tagged_with(tag_id):
        room.tags.remove(tag)
        room.save()
    return JsonResponse({"success": True})
    
def add_room_tag(request):
    if request.method == "POST":
        tag = request.POST.get("tag")
        priority = request.POST.get("priority")

        if not tag or not priority:
            return redirect_and_flash_error(request, "Tag and priority are required fields")

        try:
            priority = int(priority)
            if priority < 0 or priority > 99:
                raise ValueError("Priority must be between 0 and 99")
        except ValueError as e:
            return redirect_and_flash_error(request, str(e))

        RoomTag.objects.create(tag=tag, priority=priority)
        return redirect_and_flash_success(request, "Room tag added successfully")
