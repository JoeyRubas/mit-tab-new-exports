from random import shuffle
import time
from mittab.apps.tab.models import RoomCheckIn, RoomTag, Round, TabSettings
from mittab.libs import errors, mwmatching, tab_logic
from mittab.libs.tab_logic import team_comp
from django.db.models import Sum
    
def add_rooms():
    function_start_time = time.time()
    no_seeding = TabSettings.get("disable_room_seeding", 0)
    #Clear any existing room assignments
    Round.objects.filter(round_number=TabSettings.get("cur_round") - 1).update(room=None)
    Round.objects.filter(round_number=TabSettings.get("cur_round") - 1).filter(room_warning__isnull=False).update(room_warning=None)
    round_number = TabSettings.get("cur_round") - 1

    rooms = RoomCheckIn.objects.filter(round_number=round_number).select_related("room")
    rooms = sorted((r.room for r in rooms), key=lambda r: r.rank, reverse=True)
    pairings = list(Round.objects.filter(round_number=round_number).prefetch_related(
        "room_tags", "gov_team", "opp_team"
    ))#not using tab settings get pairing function because we don't need the pre-fetches
    
    if no_seeding:
        shuffle(pairings)
    else:
        pairings = sorted(pairings, key=lambda x: team_comp(x, round_number), reverse=True)

    graph_edges = []
    if not pairings or not rooms or len(pairings) > len(rooms):
        raise errors.RoomAssignmentError("Not enough rooms or pairings")
    
    before_graph_time = time.time()
    room_tags_dict = {room.id: set(room.tags.values_list('id', 'priority')) for room in rooms}
    for pairing_i, pairing in enumerate(pairings):
        pairing_tags = set(pairing.room_tags.values_list('id', 'priority'))
        for room_i, room in enumerate(rooms):
            weight = 0
            
            #Unfilled tags penalty
            room_tags = room_tags_dict[room.id]
            unfulfilled_tags = pairing_tags - room_tags
            
            #tag[1] is the priority
            #Multiply by 1000 gaurenteed lower bonuses and pentalties are secondary to tag fulfillment
            weight -= 1000 * sum(tag[1] for tag in unfulfilled_tags) 

            #High seed high room bonus
            if no_seeding == 0:
                weight -= abs(pairing_i - room_i)
            
            #Bad room penalty
            weight -= room.rank
            
            edge = (pairing_i, len(pairings) + room_i, weight)
            graph_edges.append(edge)
            
    after_graph_time = time.time()
    room_assignments = mwmatching.maxWeightMatching(graph_edges, maxcardinality=True)
    after_matching_time = time.time()
    if -1 in room_assignments[:len(pairings)]:
        pairing_list = room_assignments[: len(pairings)]
        bad_pairing = pairings[pairing_list.index(-1)]
        raise errors.RoomAssignmentError(
            "Could not find a room for: %s" % str(bad_pairing)
            )
    round_updates = []
    for pairing_i, pairing in enumerate(pairings):
        room_i = room_assignments[pairing_i] - len(pairings)
        pairing.room = rooms[room_i]
        round_updates.append(pairing)
    Round.objects.bulk_update(round_updates, ['room'])
    after_save_time = time.time()
    print("Graph prep time", before_graph_time - function_start_time)
    print("Graph time: ", after_graph_time - before_graph_time)
    print("Matching time: ", after_matching_time - after_graph_time)
    print("Save time: ", after_save_time - after_matching_time)
    print("Total time: ", after_save_time - function_start_time)