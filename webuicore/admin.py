from django.contrib import admin

from .models import SourceVideo, Monitor, AbnormalClip


@admin.register(SourceVideo)
class SourceVideoAdmin(admin.ModelAdmin):
    list_display = ('title', 'upload_time')
    search_fields = ('title',)


@admin.register(Monitor)
class MonitorAdmin(admin.ModelAdmin):
    list_display = ('monitor_id', 'user_id', 'location')
    search_fields = ('monitor_location',)


@admin.register(AbnormalClip)
class AbnormalVideoAdmin(admin.ModelAdmin):
    list_display = ('abnormal_id', 'source_id', 'title', 'label', 'start_time', 'end_time')
    search_fields = ('title', 'label')
