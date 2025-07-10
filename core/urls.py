from django.urls import path

from core.views import index, blog_detail, blog_edit, blog_new, media_route, register, login_view, user_profile, \
    logout_view, login_enter, edit_profile, media_upload, media_preview, comment_add, my_blog_list, blog_restore, \
    blog_delete, comment_list, media_delete, short_link_redirect, create_short_link_view, web_create_short_link, \
    user_short_links_view, ShortLinkCreateAPIView, UserShortLinkListAPIView, ShortLinkDetailAPIView

urlpatterns = [
    path('', index, name='index'),
    path('blog/<int:blog_id>/', blog_detail, name='blog_detail'),
    path('blog/edit/<int:blog_id>', blog_edit, name='blog_edit'),
    path('blog/<int:blog_id>/comment/', comment_add, name='comment_add'),
    path('blog/new/', blog_new, name='blog_new'),
    path('media', media_route, name='media_route'),
    path('media-delete/<int:media_id>', media_delete, name='media_delete'),
    path('register/', register, name='register'),
    path('accounts/login/', login_view, name='login_view'),
    path('login/', login_enter, name='login_view'),
    path('profile/', user_profile, name='user_profile'),
    path('logout/', logout_view, name='logout'),
    path('profile/edit', edit_profile, name='edit_profile'),
    path('api/media/upload', media_upload, name='media_upload'),
    path('media/preview/<str:media_hash>/<str:media_original_filename>',
         media_preview,
         name='media_preview'),
    path('i/posts', my_blog_list, name='my_blog_list'),
    path('blog/restore/<int:blog_id>', blog_restore, name='blog_restore'),
    path('blog/delete/<int:blog_id>', blog_delete, name='blog_delete'),
    path('api/comments/<int:aid>', comment_list, name='comment_list'),
    path('s/<str:short_code>', short_link_redirect, name='short-link-redirect'),
    path('api/short-links/', ShortLinkCreateAPIView.as_view(), name='api_short_links_create'),
    path('api/short-links/user/', UserShortLinkListAPIView.as_view(), name='user_short_links_api'),
    path('api/short-links/<str:short_code>/', ShortLinkDetailAPIView.as_view(), name='short_link_detail_api'),

    path('sURL/', create_short_link_view, name='short_link_create'),
    path('web-api/create/', web_create_short_link, name='web_short_links_create'),
    path('my-links/', user_short_links_view, name='short_link_list')
]
