"""Run scheduled jobs."""

import datetime
from optparse import make_option
from django.core.management.base import NoArgsCommand, CommandError

from django_future import run_jobs


class Command(NoArgsCommand):
    option_list = NoArgsCommand.option_list + (
        make_option('--delete-completed', '-d', action='store_true',
                    dest='delete_completed',
                    help='Do not keep entries for completed jobs in the database.'),
        make_option('--ignore-errors', '-i', action='store_true',
                    dest='ignore_errors',
                    help='Do not abort if a job handler raises an error.'),
    )
    help = "Executes any outstanding scheduled jobs."

    def handle(self, **options):
        delete_completed = bool(options.get('delete_completed', False))
        ignore_errors = bool(options.get('ignore_errors', False))
        try:
            run_jobs(delete_completed=delete_completed,
                     ignore_errors=ignore_errors)
        except ValueError, e:
            raise CommandError(e)
