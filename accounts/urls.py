from django.urls import path, reverse_lazy
from ExamSystem import views
from django.contrib.auth import views as auth_views


app_name = "accounts"

urlpatterns = [
    path('', views.login_redirect, name='account_home'),
    path('login/', auth_views.LoginView.as_view(
        redirect_authenticated_user=True,
        success_url='general_pages:home',
        template_name='accounts/login.html'),
        name='login'),
    path('logout/', auth_views.LogoutView.as_view(
        template_name='accounts/logout.html'),
        name='logout'),
    path('password-reset/', auth_views.PasswordResetView.as_view(
        template_name='accounts/password_reset_form.html',
        email_template_name='accounts/password_reset_email.html',
        success_url=reverse_lazy('accounts:password_reset_done')),
        name='password_reset'),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(
        template_name='accounts/password_reset_done.html'),
        name='password_reset_done'),
    path('password-reset_<uidb64>_<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='accounts/password_reset_confirm.html',
        success_url=reverse_lazy('accounts:password_reset_complete')),
        name='password_reset_confirm'),
    path('password-reset/complete/', auth_views.PasswordResetCompleteView.as_view(
        template_name='accounts/password_reset_complete.html'),
        name='password_reset_complete'),
]
