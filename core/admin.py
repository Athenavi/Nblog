from django.contrib import admin
from django.utils.html import format_html
from .models import BlogMeta


class BlogMetaAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'hidden', 'views', 'likes', 'status', 'locked', 'article_type', 'is_featured',
                    'created_at', 'updated_at']
    list_filter = ['hidden', 'status', 'locked', 'created_at', 'updated_at']
    search_fields = ['title', 'excerpt', 'tags']
    readonly_fields = ['created_at', 'updated_at']
    list_editable = ['hidden', 'status', 'locked', 'is_featured']
    ordering = ['-created_at']

    def user(self, obj):
        return obj.user.username if obj.user else None

    user.short_description = '作者用户'

    def cover_image_tag(self, obj):
        if obj.cover_image:
            return format_html('<img src="{}" width="150" height="150" />', obj.cover_image)
        return None

    cover_image_tag.short_description = '封面图片'
    cover_image_tag.admin_order_field = 'cover_image'

    fieldsets = [
        ('基本信息', {'fields': ['title', 'user', 'cover_image_tag', 'cover_image', 'article_type', 'excerpt', 'tags',
                                 'is_featured']}),
        ('文章状态', {'fields': ['hidden', 'status', 'locked']}),
        ('统计信息', {'fields': ['views', 'likes']}),
        ('时间戳', {'fields': ['created_at', 'updated_at'], 'classes': ['collapse']}),
    ]


admin.site.register(BlogMeta, BlogMetaAdmin)

from django.contrib import admin
from .models import Media, FileHash


class MediaAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'created_at', 'updated_at', 'hash', 'original_filename')
    search_fields = ('original_filename', 'hash')
    list_filter = ('user', 'created_at', 'updated_at')
    readonly_fields = ('created_at', 'updated_at')

    def get_user_username(self, obj):
        return obj.user.username if obj.user else None

    get_user_username.short_description = '上传用户'

    def has_add_permission(self, request):
        # 禁止在后台添加Media对象，视情况调整
        return False

    def has_change_permission(self, request, obj=None):
        # 禁止在后台修改Media对象，视情况调整
        return False

    def has_delete_permission(self, request, obj=None):
        # 禁止在后台删除Media对象，视情况调整
        return False


class FileHashAdmin(admin.ModelAdmin):
    list_display = ('id', 'hash', 'filename', 'created_at', 'reference_count', 'file_size', 'mime_type', 'storage_path')
    search_fields = ('filename', 'hash')
    list_filter = ('created_at', 'reference_count', 'file_size', 'mime_type')
    readonly_fields = ('created_at',)

    def has_add_permission(self, request):
        # 禁止在后台添加FileHash对象，视情况调整
        return False

    def has_change_permission(self, request, obj=None):
        # 禁止在后台修改FileHash对象，视情况调整
        return False

    def has_delete_permission(self, request, obj=None):
        # 禁止在后台删除FileHash对象，视情况调整
        return False


admin.site.register(Media, MediaAdmin)
admin.site.register(FileHash, FileHashAdmin)
