"""Run scheduled jobs."""

import datetime
from optparse import make_option
from django.core.management.base import NoArgsCommand

from django_future import run_jobs


class Command(NoArgsCommand):
    option_list = NoArgsCommand.option_list + (
        make_option('--delete-completed', '-d', action='store_true',
                    dest='delete_completed',
                    help='Do not keep entries for completed jobs in the database.'),
    )
    help = "Executes any outstanding scheduled jobs."

    def handle(self, **options):
        delete_completed = bool(options.get('delete_completed', False))
        run_jobs(delete_completed=delete_completed)
