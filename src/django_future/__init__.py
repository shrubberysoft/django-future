"""Django-future -- scheduled jobs in Django."""

import datetime
import traceback
from django.conf import settings
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
    # TODO: allow to pass in a real callable, but check that it's a global
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
    """A decorator for job handlers that take the job as a parameter."""
    f.job_as_parameter = True
    return f


STICKY_JOBS = []


def sticky_job(f):
    """A decorator that ensures that an instance of this job is always queued."""
    STICKY_JOBS.append(f)
    return f


def expire_jobs(dt):
    expired_jobs = ScheduledJob.objects.filter(status='scheduled',
                                               time_slot_end__lt=dt)
    expired_jobs.update(status='expired')


def import_app_jobs():
    """Import the 'jobs' module from all applications.

    This is needed so that the `sticky` decorator has a chance to work.
    """
    for app_name in settings.INSTALLED_APPS:
        try:
            __import__(app_name + '.jobs')
        except ImportError:
            pass # No jobs module.


def schedule_sticky_jobs():
    import_app_jobs()
    for handler in STICKY_JOBS:
        callable_name = '%s.%s' (handler.__module__, handler.__name__)
        scheduled = ScheduledJob.objects.filter(callable_name=callable_name,
                                                status='scheduled')
        if not scheduled.count():
            schedule_job('0d', callable_name)


@transaction.commit_manually
def start_scheduled_jobs(dt, delete_completed, ignore_errors):
    # Get scheduled jobs.
    jobs = ScheduledJob.objects.filter(status='scheduled',
                                       time_slot_start__lte=dt)
    for job in jobs:
        job.status = 'running'
        job.execution_start = datetime.datetime.now()
        job.save()
        transaction.commit()
        try:
            return_value = job.run()
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
                job.return_value = (unicode(return_value)
                                    if return_value is not None else None)
                job.save()
        # Do not commit the transaction here on purpose, so that
        # the next job is marked as active and the current one is marked as
        # complete in the same transaction.

    transaction.commit()


def run_jobs(delete_completed=False, ignore_errors=False, now=None):
    """Run scheduled jobs.

    You may specify a date to be treated as the current time.
    """
    if ScheduledJob.objects.filter(status='running'):
        raise ValueError('jobs in progress found; aborting')
    if now is None:
        now = datetime.datetime.now()

    expire_jobs(now)
    schedule_sticky_jobs()
    start_scheduled_jobs(now, delete_completed, ignore_errors)
