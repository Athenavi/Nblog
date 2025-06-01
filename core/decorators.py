# decorators.py
from django.core.cache import cache
from django.shortcuts import get_object_or_404

from core.models import BlogMeta


def increase_blog_views(view_func):
    def _wrapped_view(request, blog_id, *args, **kwargs):
        # 使用缓存存储浏览量队列
        cache_key = f'blog_views:{blog_id}'
        views_count = cache.get(cache_key, 0)

        # 增加浏览量
        views_count += 1

        # 每达到100次浏览量，更新数据库中的浏览量
        if views_count >= 100:
            blog_meta = get_object_or_404(BlogMeta, id=blog_id)
            blog_meta.views += views_count
            blog_meta.save()
            cache.set(cache_key, 0)  # 重置浏览量计数
        else:
            cache.set(cache_key, views_count, timeout=None)  # 持久化浏览量计数

        return view_func(request, blog_id, *args, **kwargs)

    return _wrapped_view
