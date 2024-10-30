from django.contrib import admin
from .models import VideoClip, ClipComment, SourceVideo

class CommentInline(admin.StackedInline):
    model = ClipComment
    can_delete = False
    verbose_name_plural = 'Comment'

@admin.register(VideoClip)
class VideoClipAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_at')
    search_fields = ('title',)
    inlines = [CommentInline]


    
@admin.register(SourceVideo)
class SourceVideoAdmin(admin.ModelAdmin):
    list_display = ('title', 'uploaded_at')
    search_fields = ('title',)
