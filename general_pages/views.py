from django.shortcuts import render, redirect
from django.views.generic.base import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from accounts.models import CustomUser


# Homepage requiring user is logged in. Redirects to login page if not logged in
class Homepage(LoginRequiredMixin, TemplateView):
    model = CustomUser
    context_object_name = 'user_details'
    template_name = "general_pages/homepage.html"

    def get_name(self, request):
        return request.user.first_name

