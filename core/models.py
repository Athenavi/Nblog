import markdown
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db import models, transaction
from django.utils import timezone


class PublishedManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(status='Published', hidden=False)


class BlogMeta(models.Model):
    title = models.CharField(max_length=255, null=False, blank=False, verbose_name='文章标题')
    user = models.ForeignKey('auth.User', null=True, blank=True, on_delete=models.SET_NULL, verbose_name='作者用户')
    hidden = models.BooleanField(default=False, verbose_name='是否隐藏')
    views = models.BigIntegerField(default=0, verbose_name='浏览次数')
    likes = models.BigIntegerField(default=0, verbose_name='点赞数')
    status = models.CharField(max_length=20,
                              choices=(('Draft', '草稿'), ('Published', '已发布'), ('Deleted', '已删除')),
                              null=False, default='Draft',
                              blank=True, verbose_name='文章状态')
    # 加密
    locked = models.BooleanField(default=False, verbose_name='加密状态')
    cover_image = models.CharField(max_length=255, null=True, blank=True, verbose_name='封面图片路径')
    article_type = models.CharField(max_length=50, null=True, blank=True, verbose_name='文章类型')
    excerpt = models.TextField(null=True, blank=True, verbose_name='文章摘要')
    is_featured = models.BooleanField(default=False, null=True, blank=True,
                                      verbose_name='是否为推荐文章')  # 推荐文章  0 不是 1 是
    tags = models.CharField(max_length=255, null=False, blank=False, verbose_name='标签')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    def __str__(self):
        return self.title

    STATUS_CHOICES = (
        ('Draft', '草稿'),
        ('Published', '已发布'),
        ('Deleted', '已删除'),
    )

    status = models.CharField(max_length=20, choices=[('Published', 'Published'), ('Draft', 'Draft')])

    objects = models.Manager()
    published = PublishedManager()

    @staticmethod
    def get_article_info_by_id(article_id):
        try:
            article = BlogMeta.objects.get(id=article_id)
            article_info = {
                'id': article.id,
                'title': article.title,
                'user': article.user.username if article.user else None,
                'hidden': article.hidden,
                'views': article.views,
                'likes': article.likes,
                'status': article.status,
                'locked': article.locked,
                'cover_image': article.cover_image,
                'article_type': article.article_type,
                'excerpt': article.excerpt,
                'is_featured': article.is_featured,
                'tags': article.tags,
                'created_at': article.created_at,
                'updated_at': article.updated_at,
            }
            return article_info
        except BlogMeta.DoesNotExist:
            return None

    @staticmethod
    def get_paged_articles(request):
        # 获取请求中的页码，默认为1
        page_number = request.GET.get('page', 1)
        # 获取每页的文章数量，默认为10
        page_size = request.GET.get('page_size', 50)

        # 尝试将 page_number 和 page_size 转换为整数
        try:
            page_number = int(page_number)
        except ValueError:
            page_number = 1

        try:
            page_size = int(page_size)
        except ValueError:
            page_size = 10

        articles = BlogMeta.published.order_by('-created_at')

        # 创建分页器对象
        paginator = Paginator(articles, page_size)

        try:
            # 获取指定页码的文章
            page_obj = paginator.page(page_number)
        except PageNotAnInteger:
            # 如果页码不是整数，返回第一页
            page_obj = paginator.page(1)
        except EmptyPage:
            # 如果页码超出范围，返回最后一页
            page_obj = paginator.page(paginator.num_pages)

        # 将文章信息转换为字典列表
        articles_list = []
        for article in page_obj:
            article_info = {
                'id': article.id,
                'title': article.title,
                'user': article.user.username if article.user else None,
                'hidden': article.hidden,
                'views': article.views,
                'likes': article.likes,
                'status': article.status,
                'locked': article.locked,
                'cover_image': article.cover_image,
                'article_type': article.article_type,
                'excerpt': article.excerpt,
                'is_featured': article.is_featured,
                'tags': article.tags,
                'created_at': article.created_at,
                'updated_at': article.updated_at,
            }
            articles_list.append(article_info)

        return articles_list, paginator.num_pages, page_obj.number, page_size


class BlogContent(models.Model):
    content = models.TextField(null=False, blank=False, verbose_name='<UNK>')
    blog_id = models.ForeignKey(BlogMeta, on_delete=models.CASCADE, db_column='blog_id', verbose_name='所属文章')
    blog_password = models.CharField(max_length=20, null=True, blank=True, verbose_name='文章密码')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    def __str__(self):
        return self.title

    @staticmethod
    def get_pure_content(blog_id):
        try:
            content = BlogContent.objects.get(blog_id=blog_id)
            return content.content
        except BlogContent.DoesNotExist:
            return None

    @staticmethod
    def get_markdown_content(blog_id):
        try:
            is_safe_open = BlogMeta.objects.get(id=blog_id).status == 'Published'
            if not is_safe_open:
                return '<h1>文章无法查看</h1>'
            locked = BlogMeta.objects.get(id=blog_id).locked
            if locked:
                return '<h1>文章已加密</h1>'
            content = BlogContent.objects.get(blog_id=blog_id)
            return markdown.markdown(content.content, extensions=[
                'markdown.extensions.extra',
                'markdown.extensions.codehilite',
                'markdown.extensions.toc',
            ])
        except BlogContent.DoesNotExist:
            return None


class Media(models.Model):
    user = models.ForeignKey(
        'auth.User',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        verbose_name='上传用户',
        db_index=True
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='创建时间',

    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='更新时间',
    )
    hash = models.CharField(
        max_length=64,
        verbose_name='文件哈希',
    )
    original_filename = models.CharField(
        max_length=255,
        verbose_name='原始文件名'
    )

    def __str__(self):
        return self.original_filename

    @staticmethod
    def get_media_info_by_id(media_id):
        try:
            media = Media.objects.get(id=media_id)
            return {
                'id': media.id,
                'user': media.user.username if media.user else None,
                'created_at': media.created_at,
                'updated_at': media.updated_at,
                'hash': media.hash,
                'original_filename': media.original_filename,
            }
        except Media.DoesNotExist:
            return None

    @staticmethod
    def get_media_info_by_user(request, page=1):
        try:
            media_list = Media.objects.filter(user=request.user).order_by('-id')
            paginator = Paginator(media_list, 75)  # 每页最多75个
            current_page_media = paginator.get_page(page)
            media_info = []
            for media in current_page_media:
                media_info.append({
                    'id': media.id,
                    'user': media.user.username if media.user else None,
                    'created_at': media.created_at,
                    'updated_at': media.updated_at,
                    'hash': media.hash,
                    'file_size': FileHash.objects.get(hash=media.hash).file_size,
                    'mime_type': FileHash.objects.get(hash=media.hash).mime_type,
                    'original_filename': media.original_filename
                })

            # 计算分页信息
            current_page = current_page_media.number
            prev_page = current_page_media.previous_page_number() if current_page_media.has_previous() else None
            next_page = current_page_media.next_page_number() if current_page_media.has_next() else None
            total_page = paginator.num_pages

            return media_info, current_page, prev_page, next_page, total_page
        except Exception as e:
            print(f"An error occurred: {e}")
        return None, None, None, None, None

    @staticmethod
    def delete_media_by_id(user_id, media_id):
        try:
            with transaction.atomic():
                media = Media.objects.get(id=media_id, user_id=user_id)
                file_hash_obj = FileHash.objects.filter(hash=media.hash).first()  # 获取文件哈希对象
                if file_hash_obj:
                    # 减少文件的引用次数
                    file_hash_obj.reference_count -= 1
                    if file_hash_obj.reference_count == 0:
                        # 如果引用次数为0，则删除文件哈希对象
                        file_hash_obj.delete()
                    else:
                        # 否则，只更新引用次数
                        file_hash_obj.save()
                # 删除媒体对象
                media.delete()
                return True
        except Media.DoesNotExist:
            print(f"Media with id {media_id} does not exist.")
        except Exception as e:
            print(f"An error occurred while deleting media: {e}")

        return False


class FileHash(models.Model):
    id = models.BigAutoField(primary_key=True)
    hash = models.CharField(
        max_length=64,
        unique=True,
        verbose_name='文件哈希',
        db_index=True  # 显式声明索引
    )
    filename = models.CharField(
        max_length=255,
        verbose_name='原始文件名'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='创建时间'
    )
    reference_count = models.IntegerField(
        default=1,
        verbose_name='引用次数'
    )
    file_size = models.BigIntegerField(
        verbose_name='文件大小（字节）',
    )
    mime_type = models.CharField(
        max_length=100,
        verbose_name='MIME 类型',
    )
    storage_path = models.CharField(
        max_length=255,
        verbose_name='实际存储路径'
    )

    def __str__(self):
        return self.filename

    @staticmethod
    def get_file_info_by_hash(file_hash):
        try:
            return FileHash.objects.get(hash=file_hash)
        except FileHash.DoesNotExist:
            return None


class Comment(models.Model):
    id = models.BigAutoField(primary_key=True)
    article = models.ForeignKey(BlogMeta, on_delete=models.CASCADE, db_column='article_id', verbose_name='关联的文章ID')
    user = models.ForeignKey('auth.User', null=True, blank=True, on_delete=models.SET_NULL, verbose_name='评论者用户ID')
    content = models.TextField(null=False, blank=False, verbose_name='评论内容')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='评论时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    @staticmethod
    def get_comments_by_article_id(article_id):
        try:
            comments = Comment.objects.filter(article_id=article_id)
            return comments
        except Comment.DoesNotExist:
            return None


class ShortLink(models.Model):
    """
    短链接模型，用于将长URL映射为短码
    """
    # 短码（唯一标识，6-12个字符）
    short_code = models.CharField(
        max_length=12,
        unique=True,
        db_index=True,
        verbose_name='短码标识'
    )

    # 原始完整URL
    original_url = models.URLField(
        max_length=2048,
        verbose_name='原始URL'
    )

    # 关联的用户（可选）
    user = models.ForeignKey(
        'auth.User',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        verbose_name='创建用户'
    )

    # 关联的文章（可选）
    blog = models.ForeignKey(
        BlogMeta,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        verbose_name='关联文章'
    )

    # 创建时间
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='创建时间'
    )

    # 过期时间（可选）
    expires_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='过期时间'
    )

    # 点击计数
    click_count = models.PositiveIntegerField(
        default=0,
        verbose_name='点击次数'
    )

    # 是否启用
    is_active = models.BooleanField(
        default=True,
        verbose_name='是否启用'
    )

    class Meta:
        verbose_name = '短链接'
        verbose_name_plural = '短链接管理'
        indexes = [
            models.Index(fields=['short_code']),
            models.Index(fields=['expires_at']),
        ]
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.short_code} → {self.original_url[:50]}"

    def increment_click(self):
        """增加点击计数"""
        self.click_count = models.F('click_count') + 1
        self.save(update_fields=['click_count'])

    def is_valid(self):
        """检查链接是否有效"""
        now = timezone.now()
        return self.is_active and (self.expires_at is None or self.expires_at > now)