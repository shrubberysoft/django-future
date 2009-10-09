"""Django-future -- scheduled jobs in Django."""

import datetime
import traceback
from django.db import transaction
from django_future.models import ScheduledJob
from django_future.utils import parse_timedelta


__all__ = ['schedule_job', 'job_as_parameter']


def schedule_job(date, callable_name, content_object=None, expires='7d',
                 args=(), kwargs={}):
    """Schedule a job.

    `date` may be a datetime.datetime or a datetime.timedelta.

    The callable to be executed may be specified in two ways:
     - set `callable_name` to an identifier ('mypackage.myapp.some_function').
     - specify an instance of a model as content_object and set
       `callable_name` to a method name ('do_job')

    The scheduler will not attempt to run the job if its expiration date has
    passed.

    """
    assert callable_name and isinstance(callable_name, str), callable_name
    if isinstance(date, basestring):
        date = parse_timedelta(date)
    if isinstance(date, datetime.timedelta):
        date = datetime.datetime.now() + date
    job = ScheduledJob(callable_name=callable_name, time_slot_start=date)
    if expires:
        if isinstance(expires, basestring):
            expires = parse_timedelta(expires)
        if isinstance(expires, datetime.timedelta):
            expires = date + expires
        job.time_slot_end = expires
    if content_object:
        job.content_object = content_object
    job.args = args
    job.kwargs = kwargs
    job.save()
    return job


def job_as_parameter(f):
    f.job_as_parameter = True
    return f


@transaction.commit_manually
def run_jobs(delete_completed=False, ignore_errors=False, now=None):
    """Run scheduled jobs.

    You may specify a date to be treated as the current time.
    """
    if ScheduledJob.objects.filter(status='running'):
        raise ValueError('jobs in progress found; aborting')
    if now is None:
        now = datetime.datetime.now()
    # Expire jobs.
    expired_jobs = ScheduledJob.objects.filter(status='scheduled',
                                               time_slot_end__lt=now)
    for job in expired_jobs:
        job.status = 'expired'
        job.save()
    # Get scheduled jobs.
    jobs = ScheduledJob.objects.filter(status='scheduled',
                                       time_slot_start__lte=now)
    for job in jobs:
        job.status = 'running'
        job.execution_start = datetime.datetime.now()
        job.save()
        transaction.commit()
        try:
            job.run()
        except Exception:
            exc_text = traceback.format_exc()
            transaction.rollback()
            job.error = exc_text
            job.status = 'failed'
            job.save()
            if not ignore_errors:
                transaction.commit()
                raise
        else:
            transaction.commit()
            if delete_completed:
                job.delete()
            else:
                job.status = 'complete'
                job.save()
        # Do not commit the transaction here on purpose, so that
        # the next job is marked as active and the current one is marked as
        # complete in the same transaction.

    transaction.commit()
