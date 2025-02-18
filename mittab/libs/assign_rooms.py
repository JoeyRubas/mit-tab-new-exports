from random import shuffle
from mittab.apps.tab.models import RoomCheckIn, Round, TabSettings
from mittab.libs import errors, mwmatching, tab_logic
from django.db import transaction

def add_rooms():
    no_seeding = TabSettings.get("disable_room_seeding", 0)
    #Clear any existing room assignments
    Round.objects.filter(round_number=TabSettings.get("cur_round") - 1).update(room=None)
    round_number = TabSettings.get("cur_round") - 1

    rooms = RoomCheckIn.objects.filter(round_number=round_number).select_related("room").prefetch_related("room__tags")
    rooms = sorted((r.room for r in rooms), key=lambda r: r.rank, reverse=True)
    pairings = tab_logic.sorted_pairings(round_number, fetch_room_tags=True)

    if no_seeding:
        shuffle(pairings)

    if not pairings or not rooms or len(pairings) > len(rooms):
        raise errors.RoomAssignmentError("Not enough rooms or pairings")

    graph_edges = []
    unfulfilled_tags_matrix = [[False for _ in range(len(rooms))] for _ in range(len(pairings))]

    room_tags_dict = {
    room.id: {tag for tag in room.tags.all()}
            for room in rooms}

    for pairing_i, pairing in enumerate(pairings):
        pairing_tags = set(pairing.opp_team.room_tags.all()) \
                     | set(pairing.gov_team.room_tags.all()) \
                     | set(tag for judge in pairing.judges.all() for tag in judge.room_tags.all())

        for room_i, room in enumerate(rooms):
            weight = 0

            #Unfilled tags penalty
            room_tags = room_tags_dict[room.id]
            unfulfilled_tags = pairing_tags - room_tags
            if unfulfilled_tags:
                unfulfilled_tags_matrix[pairing_i][room_i] = unfulfilled_tags

                #Multiply by 1000 gaurenteed lower bonuses and pentalties are secondary to tag fulfillment
                weight -= 1000 * sum(tag.priority for tag in unfulfilled_tags) 

            #High seed high room bonus
            if no_seeding == 0:
                weight -= abs(pairing_i - room_i)

            #Bad room penalty
            weight -= room.rank

            edge = (pairing_i, len(pairings) + room_i, weight)
            graph_edges.append(edge)

    room_assignments = mwmatching.maxWeightMatching(graph_edges, maxcardinality=True)

    if -1 in room_assignments[:len(pairings)]:
        pairing_list = room_assignments[: len(pairings)]
        bad_pairing = pairings[pairing_list.index(-1)]
        raise errors.RoomAssignmentError(
            "Could not find a room for: %s" % str(bad_pairing)
            )


    updated_pairings = []
    for pairing_i, pairing in enumerate(pairings):
        room_i = room_assignments[pairing_i] - len(pairings)
        pairing.room = rooms[room_i]
        updated_pairings.append(pairing)

    with transaction.atomic():
        Round.objects.bulk_update(updated_pairings, ['room'])

    for pairing_i, pairing in enumerate(pairings):
        room_i = room_assignments[pairing_i] - len(pairings)
        pairing.room = rooms[room_i]
        pairing.save()