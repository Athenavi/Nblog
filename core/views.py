import re

from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import HttpResponseForbidden, HttpResponse, FileResponse
from django.utils.http import urlencode

from .decorators import increase_blog_views
from .models import BlogMeta, BlogContent


def index(request):
    articles, total_pages, current_page, page_size = BlogMeta.get_paged_articles(request)

    if request.method == 'POST':
        # 处理搜索请求
        # print(articles)
        return JsonResponse({"articles": articles})
    # 将文章信息传递给模板
    context = {
        'articles': articles,
        'total_pages': total_pages,
        'current_page': current_page,
        'next_page': current_page + 1,
        'prev_page': current_page - 1,
        'page_size': page_size,
    }

    return render(request, 'index.html', context)


@increase_blog_views
def blog_detail(request, blog_id):
    meta = BlogMeta.objects.get(id=blog_id)
    locked = meta.locked
    if locked is True:
        if meta.user != request.user:
            return HttpResponseForbidden('当前内容您无权访问。')

    content = BlogContent.get_markdown_content(blog_id=blog_id)
    if not content:
        raise Http404("No such blog content")

    # 获取文章评论
    comments = Comment.objects.filter(article_id=blog_id)

    # 将文章内容和评论信息传递给模板
    context = {
        'content': content,
        'meta': meta,
        'comments': comments
    }
    if request.method == 'POST':
        # 处理评论添加
        return comment_add(request, blog_id)

    return render(request, 'blog_detail.html', context)


@login_required
def comment_add(request, blog_id):
    if request.method == 'POST':
        content = request.POST.get('comment-text')
        user = request.user
        article = get_object_or_404(BlogMeta, id=blog_id)
        user_ip = request.META.get('REMOTE_ADDR')
        user_ua = request.META.get('HTTP_USER_AGENT')
        comment_content_json = {
            "reply_to": request.POST.get('reply-to') or 0,
            "content": content,
            "ip": user_ip,
            "ua": user_ua
        }
        comment = Comment(article=article, user=user, content=comment_content_json)
        comment.save()
        return redirect('blog_detail', blog_id=blog_id)
    else:
        return redirect('blog_detail', blog_id=blog_id)


@login_required
def blog_edit(request, blog_id):
    # 获取文章元数据和内容
    blog_meta = get_object_or_404(BlogMeta, id=blog_id)
    blog_content = get_object_or_404(BlogContent, blog_id=blog_id)
    if blog_meta.user != request.user:
        return HttpResponseForbidden("你没有编辑这篇文章的权限。")

    if request.method == 'POST':
        save_blog(blog_meta, blog_content, request.POST)
        return redirect('blog_detail', blog_id=blog_id)

    tags_list = blog_meta.tags.split(',') if blog_meta.tags else []

    context = {
        'article': blog_meta,
        'content': blog_content,
        'tags_list': tags_list,
        'current_password': blog_content.blog_password,
        'status_choices': BlogMeta.STATUS_CHOICES,
        'article_types': ['技术文章', ],
    }
    return render(request, 'blog_edit.html', context)


@login_required
def blog_new(request):
    if request.method == 'POST':
        blog_meta = BlogMeta(user=request.user)
        blog_content = BlogContent()
        save_blog(blog_meta, blog_content, request.POST)
        return blog_edit(request, blog_meta.id)

    context = {
        'article_types': ['技术文章', ],
    }
    return render(request, 'blog_edit.html', context)


def save_blog(blog_meta, blog_content, post_data):
    blog_meta.title = post_data.get('title')
    blog_meta.status = post_data.get('status')
    blog_meta.cover_image = post_data.get('cover_image')
    blog_meta.article_type = post_data.get('article_type')
    blog_meta.excerpt = post_data.get('excerpt')
    blog_meta.is_featured = post_data.get('is_featured') == 'on'
    blog_meta.hidden = post_data.get('hidden') == 'on'
    blog_meta.locked = post_data.get('locked') == 'on'
    blog_meta.tags = post_data.get('tags')
    blog_meta.save()

    blog_content.blog_id = blog_meta
    blog_content.content = post_data.get('content')
    blog_content.blog_password = post_data.get('blog_password')
    blog_content.save()


@login_required
def media_route(request):
    page = request.GET.get('page', 1)
    media_list, current_page, prev_page, next_page, total_page = Media.get_media_info_by_user(request, page)
    context = {
        'media_list': media_list,
        'file_types': {'image', 'document', 'video', 'audio'},
        'current_page': current_page,
        'prev_page': prev_page,
        'next_page': next_page,
        'total_page': total_page,
    }
    print(context)
    return render(request, 'blog_media.html', context)


import os
import hashlib
import magic
from django.core.files.storage import FileSystemStorage
from core.models import FileHash, Media

allowed_size = 10 * 1024 * 1024  # 10MB
allowed_mimes = {
    'image/jpeg',
    'image/png',
    'image/gif',
    'image/webp',
    'application/pdf',
    'application/msword',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    'application/vnd.ms-powerpoint',
    'application/vnd.openxmlformats-officedocument.presentationml.presentation',
    'application/vnd.xmind.workbook',
    'video/mp4',
    'audio/mpeg',
    'audio/wav',
    'audio/mp3'
}

MEDIA_ROOT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'media')
print(MEDIA_ROOT)


@login_required
def media_upload(request):
    if request.method == 'POST':
        uploaded_files = []
        reused_files = 0

        # 使用Django的文件存储系统
        fs = FileSystemStorage()

        for f in request.FILES.getlist('file'):
            filename = f.name  # 在每次循环开始时定义filename变量
            # 校验基础属性
            if f.size > allowed_size:
                return JsonResponse({'message': f'文件大小超出限制: {allowed_size / 1024 / 1024}MB'}, status=413)

            # 读取文件内容并计算哈希
            file_data = f.read()
            file_hash = hashlib.sha256(file_data).hexdigest()
            f.seek(0)  # 重置文件指针

            # 校验MIME类型
            mime_type = magic.from_buffer(file_data, mime=True)
            if mime_type not in allowed_mimes:
                print(f'拒绝: 用户 {request.user.username}, 无效的MIME类型 {mime_type}')
                continue

            # 检查哈希是否已存在
            existing_file = FileHash.objects.filter(hash=file_hash, mime_type=mime_type).first()

            storage_path = None
            if existing_file:
                # 复用已有文件
                storage_path = existing_file.storage_path
                print(f'复用已存在的文件: {storage_path}')
                # 增加引用计数
                existing_file.reference_count += 1
                existing_file.save()
            else:
                # 生成存储路径（哈希分片目录）
                hash_prefix = file_hash[:2]
                hash_subdir = os.path.join(MEDIA_ROOT, 'hashed_files', hash_prefix)
                os.makedirs(hash_subdir, exist_ok=True)

                # 保存文件（示例路径格式：hashed_files/ab/abcdef12345...）
                storage_path = os.path.join(hash_subdir, file_hash)
                with open(storage_path, 'wb') as dest:
                    dest.write(file_data)

                # 插入文件哈希记录
                new_file_hash = FileHash(
                    hash=file_hash,
                    filename=filename,
                    file_size=f.size,
                    mime_type=mime_type,
                    storage_path=storage_path,
                    reference_count=1
                )
                new_file_hash.save()

            # 插入媒体记录（即使文件已存在也需要记录用户关联）
            try:
                media_record = Media(
                    user_id=request.user.id,
                    hash=file_hash,
                    original_filename=filename
                )
                media_record.save()
                uploaded_files.append(filename)
            except Exception as e:
                # 处理同一用户重复上传相同文件
                print(f'插入媒体记录时出错: {e}')
                reused_files += 1
                continue

        return JsonResponse({
            'message': 'success',
            'uploaded': uploaded_files,
            'reused': reused_files
        }, status=200)

    # 如果不是POST请求，则返回上传页面
    return HttpResponse(open('templates/blog_media.html').read())


from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login, authenticate, logout


def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('/login')
        else:
            # 处理表单验证失败的情况
            # 将错误信息传递给模板
            return render(request, 'reg.html', {'form': form})
    else:
        form = UserCreationForm()
    return render(request, 'reg.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            # 从 GET 请求中获取 next 参数
            next_url = request.GET.get('next')
            if next_url:
                return redirect(next_url)  # 登录成功后重定向到 next 页面
            return redirect('/')  # 登录成功后重定向到 index 页面
        else:
            # 如果登录失败，仍然从 GET 请求中获取 next 参数以便在模板中显示
            next_url = request.GET.get('next')
            return render(request, 'login.html', {'error': '用户名或密码错误', 'next': next_url})
    else:
        # 如果不是 POST 请求，则直接渲染登录页面，并从 GET 请求中获取 next 参数
        next_url = request.GET.get('next')
        return render(request, 'login.html', {'next': next_url})


@login_required
def user_profile(request):
    return render(request, 'user_profile.html', {'user': request.user})


def logout_view(request):
    logout(request)
    return redirect('/')  # 注销成功后重定向到index页面


def login_enter(request):
    # 假设你想传递一个next参数
    next_url = request.GET.get('next', '/')  # 从请求中获取next参数，如果没有则默认为根目录
    query_string = urlencode({'next': next_url})
    return redirect(f'/accounts/login?{query_string}')


from .forms import UserProfileForm


@login_required
def edit_profile(request):
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('user_profile')
    else:
        form = UserProfileForm(instance=request.user)
    return render(request, 'user_profile_edit.html', {'form': form})


@login_required
def media_preview(request, media_hash, media_original_filename):
    # 获取文件信息
    file_hash = get_object_or_404(FileHash, hash=media_hash)
    file_path = file_hash.storage_path
    file_type = file_hash.mime_type

    # 判断是否支持预览
    previewable_types = [
        'image/jpeg', 'image/png', 'image/gif',
        'video/mp4', 'video/webm', 'video/quicktime',
        'audio/mpeg', 'audio/wav', 'application/pdf'
    ]

    as_attachment = file_type not in previewable_types

    # 提供文件响应
    if os.path.exists(file_path):
        response = FileResponse(open(file_path, 'rb'), content_type=file_type)
        response['Content-Disposition'] = 'attachment; filename="{}"'.format(
            media_original_filename) if as_attachment else 'inline'
        return response
    raise Http404("文件不存在")


@login_required
def my_blog_list(request):
    # 获取筛选条件
    status_filter = request.GET.get('status', 'all')
    search_query = request.GET.get('q', '')
    sort = request.GET.get('sort', '-created_at')

    # 获取当前用户文章
    blogs = BlogMeta.objects.filter(user=request.user)

    # 状态筛选
    if status_filter != 'all':
        blogs = blogs.filter(status=status_filter)

    # 搜索
    if search_query:
        blogs = blogs.filter(title__icontains=search_query)

    # 排序
    blogs = blogs.order_by(sort)

    # 计算各状态数量
    counts = {
        'total': BlogMeta.objects.filter(user=request.user).count(),
        'draft': BlogMeta.objects.filter(user=request.user, status='Draft').count(),
        'published': BlogMeta.objects.filter(user=request.user, status='Published').count(),
        'deleted': BlogMeta.objects.filter(user=request.user, status='Deleted').count(),
    }

    # 分页
    paginator = Paginator(blogs, 10)  # 每页10篇文章
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'blogs': page_obj.object_list,
        'page_obj': page_obj,
        'status_filter': status_filter,
        'status_filter_display': dict(BlogMeta.STATUS_CHOICES).get(status_filter, '所有'),
        'counts': counts,
        'sort': sort.lstrip('-') if sort.startswith('-') else sort,
    }
    return render(request, 'my_blog_list.html', context)


@login_required
def blog_restore(request, blog_id):
    # 获取文章元数据和内容
    blog_meta = get_object_or_404(BlogMeta, id=blog_id)
    # blog_content = get_object_or_404(BlogContent, blog_id=blog_id)
    if blog_meta.user != request.user:
        return HttpResponseForbidden("你没有编辑这篇文章的权限。")

    if blog_meta.status == 'Deleted':
        blog_meta.status = 'Draft'
        blog_meta.save()
        return redirect('my_blog_list')
    else:
        return redirect('my_blog_list')


@login_required
def blog_delete(request, blog_id):
    # 获取文章元数据和内容
    blog_meta = get_object_or_404(BlogMeta, id=blog_id)
    blog_content = get_object_or_404(BlogContent, blog_id=blog_id)  # 取消注释以获取博客内容对象

    if blog_meta.user != request.user:
        return HttpResponseForbidden("你没有编辑这篇文章的权限。")

    # 从数据库中彻底删除博客元数据和内容
    blog_content.delete()  # 删除博客内容对象
    blog_meta.delete()

    return redirect('my_blog_list')


from rest_framework.decorators import api_view
from rest_framework.response import Response  # 使用 DRF 的 Response 类
from .models import Comment
from .serializers import CommentSerializer


@api_view(['GET'])
def comment_list(request, aid):
    """根据文章ID过滤评论"""
    try:
        comments = Comment.objects.filter(article_id=aid)
        # 在这里传递 context 给序列化器
        serializer = CommentSerializer(comments, many=True, context={'request': request})
        print(serializer.data)
        # 返回 Response 对象，不需要再次传递 context
        return Response(serializer.data)
    except Exception as e:
        # 返回一个错误响应
        return Response({'error': str(e)}, status=500)


from django.http import JsonResponse
from django.contrib.auth.decorators import login_required


@login_required
def media_delete(request, media_id):
    user = request.user
    try:
        if Media.delete_media_by_id(user_id=user.id, media_id=media_id):
            return JsonResponse({'message': '删除成功'})
        else:
            return JsonResponse({'message': '删除失败'}, status=500)
    except Exception as e:
        # 返回一个错误响应
        return JsonResponse({'error': str(e)}, status=500)


# views.py
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.utils import timezone
from django.views.decorators.cache import never_cache
from .models import ShortLink


@never_cache
def short_link_redirect(request, short_code):
    """
    短链接重定向视图
    根据短码查找对应的原始URL并进行重定向（区分大小写）
    """
    try:
        # 检查短码长度和是否包含特殊字符
        if not (6 <= len(short_code) <= 12) or re.search(r'[^a-zA-Z0-9]', short_code):
            return render_link_not_found(request, short_code)

        # 获取短链接对象（区分大小写）
        link = get_object_or_404(ShortLink, short_code=short_code)

        # 检查链接是否有效
        if not link.is_active:
            return render_link_inactive(request, link)

        # 检查是否过期
        if link.expires_at and link.expires_at < timezone.now():
            return render_link_expired(request, link)

        # 增加点击计数
        link.click_count += 1
        link.save(update_fields=['click_count'])

        # 重定向到原始URL
        return HttpResponseRedirect(link.original_url)

    except Http404:
        # 短码不存在
        return render_link_not_found(request, short_code)


# 错误处理辅助函数
def render_link_inactive(request, link):
    """链接已禁用视图"""
    context = {
        'title': '链接已禁用',
        'message': f'短链接 {link.short_code} 已被管理员禁用',
        'created_at': link.created_at,
        'expires_at': link.expires_at,
        'error_code': 410
    }
    return render(request, 'shortlink/error.html', context, status=410)


def render_link_expired(request, link):
    """链接已过期视图"""
    context = {
        'title': '链接已过期',
        'message': f'短链接 {link.short_code} 已于 {link.expires_at.strftime("%Y-%m-%d")} 过期',
        'created_at': link.created_at,
        'expires_at': link.expires_at,
        'error_code': 410
    }
    return render(request, 'shortlink/error.html', context, status=410)


def render_link_not_found(request, short_code):
    """链接不存在视图"""
    context = {
        'title': '链接不存在',
        'message': f'短链接 {short_code} 不存在或已被删除',
        'suggestions': [
            {'text': '检查拼写是否正确', 'icon': 'search'},
            {'text': '联系网站管理员', 'icon': 'support'}
        ],
        'error_code': 404
    }
    return render(request, 'shortlink/error.html', context, status=404)


from rest_framework import generics, permissions, status
from rest_framework.response import Response
from .models import ShortLink
from .serializers import ShortLinkCreateSerializer
from django.urls import reverse


class ShortLinkCreateAPIView(generics.CreateAPIView):
    """
    登录用户创建短链接接口
    POST /api/short-links/
    参数:
      - original_url (必填): 原始URL
      - short_code (可选): 自定义短码
      - expires_at (可选): 过期时间
    """
    queryset = ShortLink.objects.all()
    serializer_class = ShortLinkCreateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        short_link = serializer.save()

        # 构建完整的短链接URL
        short_url = request.build_absolute_uri(
            reverse('short-link-redirect', kwargs={'short_code': short_link.short_code})
        )

        # 构建响应数据
        response_data = {
            'id': short_link.id,
            'short_code': short_link.short_code,
            'short_url': short_url,
            'original_url': short_link.original_url,
            'expires_at': short_link.expires_at.strftime('%Y-%m-%d %H:%M') if short_link.expires_at else None,
            'created_at': short_link.created_at.strftime('%Y-%m-%d %H:%M'),
            'message': '短链接创建成功'
        }

        headers = self.get_success_headers(serializer.data)
        return Response(response_data, status=status.HTTP_201_CREATED, headers=headers)


class UserShortLinkListAPIView(generics.ListAPIView):
    """获取当前用户的短链接列表"""
    serializer_class = ShortLinkCreateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return ShortLink.objects.filter(user=self.request.user).order_by('-created_at')


class ShortLinkDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    """短链接详情管理"""
    queryset = ShortLink.objects.all()
    serializer_class = ShortLinkCreateSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'short_code'

    def get_queryset(self):
        return super().get_queryset().filter(user=self.request.user)
