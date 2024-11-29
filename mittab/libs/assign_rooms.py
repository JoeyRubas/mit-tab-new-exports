from mittab.apps.tab.models import RoomCheckIn, RoomTag, Round, TabSettings
from mittab.libs import errors, mwmatching, tab_logic
from mittab.libs.tab_logic import team_comp
from django.db.models import Sum

def calc_weight(room, pairing, room_i, pairing_i):
    # Calculate the sum of the priorities of unfulfilled tags
    unfulfilled_tags = pairing.room_tags.exclude(id__in=room.tags.values_list('id', flat=True))
    unfuffiled_tags_priority = -100 * (unfulfilled_tags.aggregate(sum_weight=Sum("priority"))["sum_weight"] or 0)

    # High seed to high room bonus: prioritize better rooms for better-seeded pairings
    high_seed_high_room_bonus = -abs(pairing_i - room_i)

    # Penalty for rooms with a lower rank
    bad_room_penalty = -room.rank

    return unfuffiled_tags_priority + high_seed_high_room_bonus + bad_room_penalty

    

def add_rooms():
    #Clear any existing room assignments
    Round.objects.filter(round_number=TabSettings.get("cur_round") - 1).update(room=None)
    Round.objects.filter(round_number=TabSettings.get("cur_round") - 1).filter(room_warning__isnull=False).update(room_warning=None)
    round_number = TabSettings.get("cur_round") - 1

    rooms = RoomCheckIn.objects.filter(round_number=round_number).select_related("room")
    rooms = sorted((r.room for r in rooms), key=lambda r: r.rank, reverse=True)
    pairings = Round.objects.filter(round_number=round_number).prefetch_related(
        "room_tags", "gov_team", "opp_team"
    )
    pairings = sorted(pairings, key=lambda x: team_comp(x, round_number), reverse=True)

    graph_edges = []
    if not pairings or not rooms or len(pairings) > len(rooms):
        raise errors.RoomAssignmentError("Not enough rooms or pairings")
    
    for pairing_i, pairing in enumerate(pairings):
        for room_i, room in enumerate(rooms):
            edge = (pairing_i, len(pairings) + room_i, calc_weight(room, pairing, room_i, pairing_i))
            graph_edges.append(edge)

    room_assignments = mwmatching.maxWeightMatching(graph_edges, maxcardinality=True)

    if -1 in room_assignments[:len(pairings)]:
        pairing_list = room_assignments[: len(pairings)]
        bad_pairing = pairings[pairing_list.index(-1)]
        raise errors.RoomAssignmentError(
            "Could not find a room for: %s" % str(bad_pairing)
            )
    print("here")
    print(room_assignments)
    for pairing_i, pairing in enumerate(pairings):
        room_i = room_assignments[pairing_i] - len(pairings)
        pairing.room = rooms[room_i]
        pairing.save()
