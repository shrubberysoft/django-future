import datetime
import cPickle
from django.db import models
from django.conf import settings
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import ugettext_lazy as _

from picklefield import PickledObjectField

from django_future.utils import parse_timedelta


__all__ = ['ScheduledJob']


END_OF_TIME = datetime.datetime(2047, 9, 14)


class ScheduledJob(models.Model):

    STATUSES = (
        ('scheduled', _('Scheduled')),
        ('running', _('Running')),
        ('failed', _('Failed')),
        ('complete', _('Complete')),
        ('expired', _('Expired')),
    )

    time_slot_start = models.DateTimeField(_('time slot start'))
    time_slot_end = models.DateTimeField(_('time slot end'))
    execution_start = models.DateTimeField(_('execution start'), blank=True, null=True)
    status = models.CharField(_('status'), choices=STATUSES, max_length=32,
                              default='scheduled')

    content_type = models.ForeignKey(ContentType, blank=True, null=True, verbose_name=_('content type'))
    object_id = models.PositiveIntegerField(_('object ID'), blank=True, null=True)
    content_object = generic.GenericForeignKey()

    callable_name = models.CharField(_('callable name'), max_length=255,
        help_text=_('The callable to be executed may be specified in two ways: '
        'Set the callable name to an identifier (mypackage.myapp.some_function). '
        'Or specify an instance of a model as the content object and set '
        'the callable name to a method name (do_job).'))
    args = PickledObjectField(_('args'))
    kwargs = PickledObjectField(_('kwargs'))
    error = models.TextField(_('error'), blank=True, null=True)
    return_value = models.TextField(_('return value'), blank=True, null=True)

    class Meta:
        verbose_name = _('scheduled job')
        verbose_name_plural = _('scheduled jobs')
        get_latest_by = 'time_slot_start'
        ordering = ['time_slot_start']

    def __repr__(self):
        return '<ScheduledJob (%s) callable=%r>' % (
                    self.status, self.callable_name)

    def __unicode__(self):
        return self.callable_name

    def run(self):
        # TODO: logging?
        args = self.args or []
        kwargs = self.kwargs or {}
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
        return callable_func(*args, **kwargs)

    def reschedule(self, date, callable_name=None, content_object=None,
                   expires='7d', args=None, kwargs=None):
        """Schedule a clone of this job."""
        # Resolve date relative to the expected start of the current job.
        if isinstance(date, basestring):
            date = parse_timedelta(date)
        if isinstance(date, datetime.timedelta):
            date = self.time_slot_start + date

        if callable_name is None:
            callable_name = self.callable_name
        if content_object is None:
            content_object = self.content_object
        if args is None:
            args = self.args or []
        if kwargs is None:
            kwargs = self.kwargs or {}
        from django_future import schedule_job
        return schedule_job(date, callable_name, content_object=content_object,
                            expires=expires, args=args, kwargs=kwargs)
