import random
import time as Time
from mittab.apps.tab.models import Room, RoomCheckIn, RoomTag, Round, TabSettings
from django.core.management import BaseCommand

from mittab.libs import tab_logic

class Command(BaseCommand):
    help = "Assign room tags to all rooms"

    def handle(self, *args, **kwargs):
        """
        Create tags and assign them efficiently
        """
        self.num_tags = 100
        self.tags_per_debater_judge = 10
        self.valid_rooms_per_round = 1
        self.make_tags()
        self.assign_tags()

    def make_tags(self):
        # Delete all existing tags
        RoomTag.objects.all().delete()

        # Clear room tags in rounds
        rounds = Round.objects.all()
        for roundobj in rounds:
            roundobj.room_tags.clear()

        # Bulk create new tags
        tags = [
            RoomTag(tag=f"Tag {i}", priority=random.randint(1, 99), color=f"#{random.randint(0, 0xFFFFFF):06x}")
            for i in range(self.num_tags)
        ]
        RoomTag.objects.bulk_create(tags)

    def assign_tags(self):
        cur_round = TabSettings.get("cur_round") - 1

        # Prefetch related data for efficiency
        rounds = Round.objects.filter(round_number=cur_round).select_related(
            "gov_team", "opp_team", "chair"
        )
        rooms = RoomCheckIn.objects.filter(round_number=cur_round).select_related("room")
        rooms = sorted((r.room for r in rooms), key=lambda r: r.rank, reverse=True)
        all_tags = list(RoomTag.objects.all())
        times = []
        time_keys = ["Selecting random tags", "Assigning tags to teams and judges", "Assigning tags to rooms", "Saving pairings"]
        for pairing in rounds:
            times.append([])
            print(f"Assigning tags to pairing {pairing}")
            times[-1].append(Time.time())  # before_select
            # Select random tags
            random_tags = random.sample(all_tags, self.tags_per_debater_judge)
            #split random tags into three lists with random lengths who's union is random_tags
            idx1 = random.randint(0, len(random_tags)-2)
            idx2 = random.randint(idx1, len(random_tags)-1)
            times[-1].append(Time.time())  # after_select
            
            pairing.gov_team.room_tags.add(*random_tags[:idx1])
            pairing.opp_team.room_tags.add(*random_tags[idx1:idx2])
            pairing.chair.room_tags.add(*random_tags[idx2:])
            times[-1].append(Time.time())  # after_round_assign
            # Assign tags to valid rooms
            for _ in range(self.valid_rooms_per_round-1):
                room = rooms.pop()
                room.tags.add(*random_tags)
                room.save()
            times[-1].append(Time.time())  # after_room_assign
            pairing.save()
            times[-1].append(Time.time())  # after_save
        #Time summary:
        total_time = sum(time[-1] - time[0] for time in times)
        time_by_section = [sum(time[i+1] - time[i] for time in times) for i in range(len(times[0])-1)]
        for i, key in enumerate(time_keys):
            print(f"{key}: {time_by_section[i]/total_time*100:.2f}%")
        
