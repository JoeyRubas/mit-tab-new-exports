
from mittab.apps.tab.models import RoomCheckIn, RoomTag, Round, TabSettings
from mittab.libs import tab_logic
from mittab.libs.tab_logic import team_comp


def add_rooms():
    round_number = TabSettings.get("cur_round") - 1
    rooms = RoomCheckIn.objects.filter(round_number=round_number).select_related("room")
    rooms = sorted((r.room for r in rooms), key=lambda r: r.rank, reverse=True)
    pairings = Round.objects.filter(round_number=round_number).prefetch_related(
        "room_tags", "gov_team", "opp_team"
    )

    for pairing in pairings:
        pairing.populate_room_tags()

    sorted_pairings = sorted(pairings, key=lambda x: (x.room_tag_priority, 
                                                      team_comp(x, round_number)), reverse=True)
    room_tag_set = {room: set(room.tags.all()) for room in rooms}
    
    for pairing in sorted_pairings:
        print("Getting room for pairing: %s" % pairing)
        if not pairing.room_tags.exists():
            pairing.room = rooms.pop(0)
        else:    
            best_room = rooms[0]
            best_room_score = 0
            required_score = pairing.room_tag_priority
            required_tags = set(pairing.room_tags.all())
            for room in rooms:
                room_score = sum(tag.priority for tag in required_tags if tag in room_tag_set[room])
                if room_score == required_score:
                    pairing.room = room
                    rooms.remove(room)
                    break
                elif room_score > best_room_score:
                    best_room = room
                    best_room_score = room_score
            else:
                pairing.room = best_room
                missing_tags = required_tags.difference(room_tag_set[best_room])
                pairing.warning = "Warning: Unmet room tags: " + ", ".join([tag.name for tag in missing_tags])
        pairing.save()
        print("Assigned room: %s" % pairing.room)
