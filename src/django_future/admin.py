from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from django_future.models import ScheduledJob


class ScheduledJobAdmin(admin.ModelAdmin):
    """Admin customization for ScheduledJob model."""

    status_colors = {
        'default': '#000',
        'running': '#356AA0',
        'failed': '#B02B2C',
        'complete': '#006E2E',
        'expired': '#888'
    }

    def colorful_status(self, obj):
        color = self.status_colors['default']
        if obj.status in self.status_colors:
            color = self.status_colors[obj.status]
        return '<strong style="color: %s">%s</strong>' % (color, obj.get_status_display())
    colorful_status.short_description = 'Status'
    colorful_status.allow_tags = True

    list_display = ('time_slot_start', 'colorful_status', 'callable_name', 'args', 'kwargs', 'return_value')
    list_filter = ('status',)
    date_hierarchy = 'time_slot_start'
    fieldsets = (
        (None, {
            'fields': ('status',)
        }),
        (_('Schedule'), {
            'fields': ('time_slot_start', 'time_slot_end', 'execution_start')
        }),
        (_('Job'), {
            'fields': ('callable_name', ('content_type', 'object_id'), 'error', 'return_value'),
        }),
    )


# TODO: show (read-only) reprs of args and kwargs in job editor screen.


admin.site.register(ScheduledJob, ScheduledJobAdmin)
