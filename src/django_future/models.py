import datetime
import cPickle
from django.db import models
from django.conf import settings
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType


__all__ = ['ScheduledJob']


END_OF_TIME = datetime.datetime(2047, 9, 14)


class ScheduledJob(models.Model):

    STATUSES = (
        ('scheduled', 'Scheduled'),
        ('running', 'Running'),
        ('failed', 'Failed'),
        ('complete', 'Complete'),
        ('expired', 'Expired'),
    )

    time_slot_start = models.DateTimeField()
    time_slot_end = models.DateTimeField()
    execution_start = models.DateTimeField(blank=True, null=True)
    status = models.CharField(choices=STATUSES, max_length=32,
                              default='scheduled')

    content_type = models.ForeignKey(ContentType, blank=True, null=True)
    object_id = models.PositiveIntegerField(blank=True, null=True)
    content_object = generic.GenericForeignKey()

    callable_name = models.CharField(max_length=255)
    args_pickled = models.TextField()
    kwargs_pickled = models.TextField()

    def _get_args(self):
        return cPickle.loads(str(self.args_pickled))
    def _set_args(self, value):
        self.args_pickled = cPickle.dumps(tuple(value))
    args = property(_get_args, _set_args)

    def _get_kwargs(self):
        return cPickle.loads(str(self.kwargs_pickled))
    def _set_kwargs(self, value):
        self.kwargs_pickled = cPickle.dumps(value)
    kwargs = property(_get_kwargs, _set_kwargs)

    def __repr__(self):
        return '<ScheduledJob (%s) callable=%r>' % (
                    self.status, self.callable_name)

    def run(self):
        # TODO: logging?
        args = self.args
        kwargs = self.kwargs
        if '.' in self.callable_name:
            module_name, function_name = self.callable_name.rsplit('.', 1)
            module = __import__(module_name, fromlist=[function_name])
            callable_func = getattr(module, function_name)
            if self.content_object is not None:
                args = [self.content_object] + list(args)
        else:
            callable_func = getattr(self.content_object, self.callable_name)
        if hasattr(callable_func, 'job_as_parameter'):
            args = [self] + list(args)
        callable_func(*args, **kwargs)

    def reschedule(self, date, callable_name=None, content_object=None,
                   expires='7d', args=None, kwargs=None):
        """Schedule a clone of this job."""
        if callable_name is None:
            callable_name = self.callable_name
        if content_object is None:
            content_object = self.content_object
        if args is None:
            args = self.args
        if kwargs is None:
            kwargs = self.kwargs
        from django_future import schedule_job
        return schedule_job(date, callable_name, content_object=content_object,
                            expires=expires, args=args, kwargs=kwargs)
