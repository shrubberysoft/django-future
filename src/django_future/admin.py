from django.contrib import admin
from django_future.models import ScheduledJob


class ScheduledJobAdmin(admin.ModelAdmin):
    pass


admin.site.register(ScheduledJob, ScheduledJobAdmin)
