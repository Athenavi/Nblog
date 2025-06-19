from django.contrib import admin
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
from django.utils.html import format_html
from .models import ShortLink


@admin.register(ShortLink)
class ShortLinkAdmin(admin.ModelAdmin):
    # 列表页显示字段
    list_display = (
        'short_code_display',
        'original_url_display',
        'user',
        'blog_link',
        'is_active',
        'click_count',
        'created_at',
        'expires_at_display'
    )

    # 列表页可编辑字段
    list_editable = ('is_active',)

    # 列表页过滤器
    list_filter = (
        'is_active',
        'user',
        ('expires_at', admin.DateFieldListFilter),
        ('created_at', admin.DateFieldListFilter),
    )

    # 搜索字段
    search_fields = (
        'short_code',
        'original_url',
        'blog__title',
        'user__username'
    )

    # 表单页字段分组布局
    fieldsets = (
        ('基本信息', {
            'fields': (
                'short_code',
                'original_url',
                'is_active',
                'click_count'
            )
        }),
        ('关联信息', {
            'fields': (
                'user',
                'blog',
            ),
            'classes': ('collapse',)
        }),
        ('有效期设置', {
            'fields': ('expires_at',),
            'description': '留空表示永不过期'
        }),
    )

    # 只读字段
    readonly_fields = ('click_count', 'created_at')

    # 自定义方法：在列表页显示简化的URL
    def original_url_display(self, obj):
        return format_html(
            '<a href="{}" target="_blank">{}</a>',
            obj.original_url,
            obj.original_url[:50] + '...' if len(obj.original_url) > 50 else obj.original_url
        )

    original_url_display.short_description = '原始URL'

    # 自定义方法：显示带链接的短码
    def short_code_display(self, obj):
        return format_html(
            '<a href="/s/{}" target="_blank"><b>{}</b></a>',
            obj.short_code,
            obj.short_code
        )

    short_code_display.short_description = '短码'

    # 自定义方法：显示带链接的文章标题
    def blog_link(self, obj):
        if obj.blog:
            return format_html(
                '<a href="/admin/blog/blogmeta/{}/change/">{}</a>',
                obj.blog.id,
                obj.blog.title[:30] + '...' if len(obj.blog.title) > 30 else obj.blog.title
            )
        return '-'

    blog_link.short_description = '关联文章'

    # 自定义方法：格式化过期时间显示
    def expires_at_display(self, obj):
        if obj.expires_at:
            return obj.expires_at.strftime("%Y-%m-%d %H:%M")
        return '永不过期'

    expires_at_display.short_description = '过期时间'

    # 自定义操作：批量启用短链接
    def activate_links(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f"已启用 {updated} 个短链接")

    activate_links.short_description = "✅ 启用选中的短链接"

    # 自定义操作：批量禁用短链接
    def deactivate_links(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f"已禁用 {updated} 个短链接")

    deactivate_links.short_description = "⛔ 禁用选中的短链接"

    # 自定义操作：重置点击计数
    def reset_clicks(self, request, queryset):
        updated = queryset.update(click_count=0)
        self.message_user(request, f"已重置 {updated} 个短链接的点击计数")

    reset_clicks.short_description = "🔄 重置点击计数"

    # 添加自定义操作到管理界面
    actions = [activate_links, deactivate_links, reset_clicks]

    # 添加自定义CSS
    class Media:
        css = {
            'all': ('css/shortlink_admin.css',)
        }
