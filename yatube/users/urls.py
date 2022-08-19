from django.contrib.auth.views import PasswordChangeDoneView,\
    PasswordResetDoneView, PasswordResetView, PasswordResetConfirmView,\
    PasswordResetCompleteView, PasswordChangeView, LoginView, LogoutView
from django.urls import path

from . import views

app_name = 'users'

urlpatterns = [
    path('logout/', LogoutView.as_view(
         template_name='users/logged_out.html'),
         name='logged_out'),
    path('signup/', views.SignUp.as_view(),
         name='signup'),
    path('login/', LoginView.as_view(
         template_name='users/login.html'),
         name='login'),
    path('password-change/', PasswordChangeView.as_view(
         template_name='users/password_change_form.html'),
         name='password_change_form'),
    path('password-change/done/', PasswordChangeDoneView.as_view(
         template_name='users/password_change_done.html'),
         name='password_change_done'),
    path('password-reset/', PasswordResetView.as_view(
         template_name='users/password_reset_form.html'),
         name='password_reset_form'),
    path('password_reset/done/', PasswordResetDoneView.as_view(
         template_name='users/password_reset_done.html'),
         name='password_reset_done'),
    path('reset/<uidb64>/<token>/', PasswordResetConfirmView.as_view(
         template_name='users/password_reset_confirm.html'),
         name='password_reset_confirm'),
    path('reset/done/', PasswordResetCompleteView.as_view(
         template_name='users/password_reset_complete.html'),
         name='password_reset_complete'),
]
