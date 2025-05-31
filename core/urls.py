from django.urls import path
from core.views import index, blog_detail, blog_edit, blog_new, media_route, register, login_view, user_profile, \
    logout_view, login_enter, edit_profile, media_upload

urlpatterns = [
    path('', index, name='index'),
    path('blog/<int:blog_id>/', blog_detail, name='blog_detail'),
    path('blog/edit/<int:blog_id>', blog_edit, name='blog_edit'),
    path('blog/new/', blog_new, name='blog_new'),
    path('media', media_route, name='media_route'),
    path('register/', register, name='register'),
    path('accounts/login/', login_view, name='login_view'),
    path('login/', login_enter, name='login_view'),
    path('profile/', user_profile, name='user_profile'),
    path('logout/', logout_view, name='logout'),
    path('profile/edit', edit_profile, name='edit_profile'),
    path('api/media/upload', media_upload, name='media_upload'),
]
