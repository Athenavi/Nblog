from django.urls import path

from core.views import index, blog_detail, blog_edit, blog_new, media_route, register, login_view, user_profile, \
    logout_view, login_enter, edit_profile, media_upload, media_preview, comment_add, my_blog_list, blog_restore, \
    blog_delete, comment_list, media_delete

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
]
