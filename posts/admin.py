from django.contrib import admin
from .models import Post, Comment


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = (
        'author', 'content_preview', 'created_at', 'updated_at', 
        'image_preview'
    )
    list_filter = ('created_at', 'updated_at')
    search_fields = ('content', 'author__username')
    ordering = ('-created_at',)
    
    def content_preview(self, obj):
        return (
            obj.content[:50] + '...' 
            if len(obj.content) > 50 else obj.content
        )
    
    content_preview.short_description = 'Content'
    
    def image_preview(self, obj):
        if obj.image:
            return f'<img src="{obj.image.url}" width="50" height="50" />'
        return "No image"
    
    image_preview.short_description = 'Image'
    image_preview.allow_tags = True


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('author', 'post', 'content_preview', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('content', 'author__username', 'post__content')
    ordering = ('-created_at',)
    
    def content_preview(self, obj):
        return (
            obj.content[:50] + '...' 
            if len(obj.content) > 50 else obj.content
        )
    
    content_preview.short_description = 'Content' 