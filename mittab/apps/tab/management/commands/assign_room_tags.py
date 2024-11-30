import math
import random
from mittab.apps.tab.models import Room, RoomCheckIn, RoomTag, Round, TabSettings
from django.core.management import BaseCommand

from mittab.libs import tab_logic

class Command(BaseCommand):
    help = "Assign room tags to all rooms"

    def add_arguments(self, parser):
        parser.add_argument(
            '--num_tags',
            type=int,
            default=100,
            help='Number of tags to create'
        )
        parser.add_argument(
            '--tags_per_round',
            type=int,
            default=10,
            help='Number of tags to assign per round'
        )
        parser.add_argument(
            '--valid_rooms_per_round',
            type=int,
            default=2,
            help='Number of valid rooms per round'
        )
        parser.add_argument(
            '--randomize',
            type = bool,
            default = True,
            help = 'Randomize the number of tags per round and valid rooms per round'
        )

    def handle(self, *args, **kwargs):
        """
        Create tags and assign them efficiently
        """
        self.num_tags = int(kwargs['num_tags'])
        self.tags_per_round = int(kwargs['tags_per_round'])
        self.valid_rooms_per_round = int(kwargs['valid_rooms_per_round'])
        self.randomize = True
        self.make_tags()
        self.assign_tags()

    def make_tags(self):
        # Delete all existing tags
        RoomTag.objects.all().delete()

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
        all_rooms = sorted((r.room for r in rooms), key=lambda r: r.rank, reverse=True)
        unused_rooms = list(all_rooms)
        all_tags = list(RoomTag.objects.all())
        if self.randomize:
            max_rooms_per_round = math.ceil(len(rooms)/4)

        for pairing in rounds:
            print(f"Assigning tags to pairing {pairing}")

            if self.randomize:
                self.tags_per_round = min(self.num_tags, max(1, int(random.betavariate(2, 5) * self.num_tags)))
            random_tags = random.sample(all_tags, self.tags_per_round)
            #split random tags into three lists with random lengths who's union is random_tags
            idx1 = random.randint(0, len(random_tags)-2)
            idx2 = random.randint(idx1, len(random_tags)-1)

            
            pairing.gov_team.room_tags.add(*random_tags[:idx1])
            pairing.gov_team.save()
            pairing.opp_team.room_tags.add(*random_tags[idx1:idx2])
            pairing.opp_team.save()
            pairing.chair.room_tags.add(*random_tags[idx2:])
            pairing.chair.save()

            # Assign tags to valid rooms
            if self.randomize:
                self.valid_rooms_per_round = random.randint(1, max_rooms_per_round)
            for _ in range(self.valid_rooms_per_round):
                room = unused_rooms.pop()
                if not unused_rooms:
                    unused_rooms = list(all_rooms)
                room.tags.add(*random_tags)
                room.save()
