from django.contrib import admin
from django_future.models import ScheduledJob


class ScheduledJobAdmin(admin.ModelAdmin):

    list_display = ('time_slot_start', 'status', 'callable_name', 'args', 'kwargs')
    list_filter = ('status', 'callable_name')

# TODO: show (read-only) reprs of args and kwargs in job editor screen.


admin.site.register(ScheduledJob, ScheduledJobAdmin)
