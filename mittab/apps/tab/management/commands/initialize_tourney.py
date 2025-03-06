import os
import sys

from django.core.management import call_command
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from mittab.apps.tab.models import TabSettings
from mittab.libs.backup import backup_round, BEFORE_NEW_TOURNAMENT

class Command(BaseCommand):
    help = "Setup a new tounament and backup the last one"

    def add_arguments(self, parser):
        parser.add_argument(
            "--tab-password",
            dest="tab_password",
            help="Password for the tab user",
            nargs="?",
            default=User.objects.make_random_password(length=8))
        parser.add_argument(
            "--entry-password",
            dest="entry_password",
            help="Password for the entry user",
            nargs="?",
            default=User.objects.make_random_password(length=8))

    def handle(self, *args, **options):
        backup_round(
            btype=BEFORE_NEW_TOURNAMENT)
        self.stdout.write("Clearing data from database")
        try:
            call_command("flush", interactive=False)
        except (IOError, os.error) as why:
            self.stdout.write("Failed to clear database")
            print(why)
            sys.exit(1)

        self.stdout.write("Creating tab/entry users")
        tab = User.objects.create_user("tab", None, options["tab_password"])
        tab.is_staff = True
        tab.is_admin = True
        tab.is_superuser = True
        tab.save()
        User.objects.create_user("entry", None, options["entry_password"])

        self.stdout.write("Setting default tab settings")
        TabSettings.set("tot_rounds", 5)
        TabSettings.set("lenient_late", 0)
        TabSettings.set("cur_round", 1)

        self.stdout.write(
            "Done setting up tournament, after backing up old one. "
            "New tournament information:")
        self.stdout.write(
            "%s | %s" % ("Username".ljust(10, " "), "Password".ljust(10, " ")))
        self.stdout.write(
            "%s | %s" %
            ("tab".ljust(10, " "), options["tab_password"].ljust(10, " ")))
        self.stdout.write(
            "%s | %s" %
            ("entry".ljust(10, " "), options["entry_password"].ljust(10, " ")))
