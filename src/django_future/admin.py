from django.contrib import admin
from django_future.models import ScheduledJob


class ScheduledJobAdmin(admin.ModelAdmin):

    list_display = ('callable_name', 'time_slot_start', 'status', )
    list_filter = ('status', )

# TODO: show reprs of args and kwargs


admin.site.register(ScheduledJob, ScheduledJobAdmin)
