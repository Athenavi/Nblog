from django.contrib.auth.decorators import login_required
from django.http import Http404, JsonResponse, HttpResponseForbidden
from django.shortcuts import render, get_object_or_404, redirect
from django.utils.http import urlencode

from .models import BlogMeta, BlogContent, Media


def index(request):
    articles, total_pages, current_page = BlogMeta.get_paged_articles(request)

    if request.method == 'POST':
        # 处理搜索请求
        # print(articles)
        return JsonResponse({"articles": articles})
    # 将文章信息传递给模板
    context = {
        'articles': articles,
        'total_pages': total_pages,
        'current_page': current_page,
    }
    return render(request, 'index.html', context)


def blog_detail(request, blog_id):
    meta = BlogMeta.objects.get(id=blog_id)
    locked = meta.locked
    if locked is True:
        if meta.user == request.user:
            return HttpResponseForbidden('blog is locked but you are the author.')
        else:
            return HttpResponseForbidden('blog is locked but you are not the author.')
    content = BlogContent.get_markdown_content(blog_id=blog_id)
    if not content:
        raise Http404("No such blog content")
    # 将文章内容传递给模板
    context = {
        'content': content,
        'meta': meta
    }
    # print(context)
    return render(request, 'blog_detail.html', context)


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
    media_list = Media.get_media_info_by_user(request)
    context = {
        'media_list': media_list,
        'file_types': {'image', 'document', 'video', 'audio'},
    }
    print(context)
    return render(request, 'blog_media.html', context)


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
            return render(request, 'register.html', {'form': form})
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
