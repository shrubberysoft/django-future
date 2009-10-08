"""Run scheduled jobs."""

import datetime
from django.core.management.base import BaseCommand

from django_future import run_jobs


class Command(BaseCommand):
    help = "Executes any outstanding scheduled jobs."

    def handle(self, *args, **options):
        run_jobs()
