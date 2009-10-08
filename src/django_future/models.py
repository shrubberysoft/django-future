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
        ('complete', 'Complete')
    )

    time_slot_start = models.DateTimeField()
    time_slot_end = models.DateTimeField()
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
        self.args_pickled = cPickle.dumps(value)
    args = property(_get_args, _set_args)

    def _get_kwargs(self):
        return cPickle.loads(str(self.kwargs_pickled))
    def _set_kwargs(self, value):
        self.kwargs_pickled = cPickle.dumps(value)
    kwargs = property(_get_kwargs, _set_kwargs)

    def run(self):
        # TODO: logging?
        args = self.args
        kwargs = self.kwargs
        if '.' in self.callable_name:
            module_name, function_name = self.callable_name.rsplit('.', 1)
            module = __import__(module_name, fromlist=[function_name])
            callable_func = getattr(module, function_name)
            if self.content_object is not None:
                callable_func(self.content_object, *args, **kwargs)
            else:
                callable_func(*args, **kwargs)
        else:
            callable_func = getattr(self.content_object, self.callable_name)
            callable_func(*args, **kwargs)
