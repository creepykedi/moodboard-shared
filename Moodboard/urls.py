"""Moodboard URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from . import views
from . import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views


urlpatterns = [
    path('', views.index, name="index"),
    path('main', views.index, name="index"),
    path('r<int:img_id>/delete', views.superuser_delete_from_moodboard, name="sup_delete"),
    path('myboards', views.myboards_view, name="myboards"),
    path(r'myboards/<int:board_id>/<int:img_id>/delete', views.delete_from_moodboard, name="delete_from_moodboard"),
    path(r'user/<int:board_id>/delete', views.delete_moodboard, name="delete_moodboard"),
    path(r'user/<int:board_id>/rename', views.rename, name="rename_moodboard"),
    path('new_board', views.new_board_view, name="new_board"),
    path('login', views.login_view, name="login"),
    path('logout', views.logout_view, name="logout"),
    path('signup', views.signup_view, name="signup"),
    path('myadminsite', admin.site.urls),
    path('myprofile/', views.userpage_view, name='userpage'),
    path('discover', views.discover_view, name='discover'),
    path('user/share/', views.generate_share_link, name='share-board'),
    path('user/update/', views.profilechange_view, name='profile_change'),
    path(r'shared/<share_link>/', views.shared_view, name='shared_by_link'),
    path(r'user/share/<int:board_id>', views.generate_share_link, name='generate_url'),
    path('password-reset', auth_views.PasswordResetView.as_view(template_name='users/password_reset.html'),
         name="password_reset"),
    path(r'password-reset-confirm/<uidb64>/<token>',
         auth_views.PasswordResetConfirmView.as_view(template_name='users/password_reset_confirm.html'), name="password_reset_confirm"),
    path('password-reset-complete', auth_views.PasswordResetCompleteView.as_view(template_name='users/password_reset_complete.html'), name="password_reset_complete"),
    path('password-reset/done/',
         auth_views.PasswordResetDoneView.as_view(template_name='users/password_reset_done.html'), name='password_reset_done'),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
