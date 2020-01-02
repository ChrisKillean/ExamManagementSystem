from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import Group

from .models import CustomUser
from .forms import CustomUserCreationForm, CustomUserChangeForm


class CustomUserAdmin(UserAdmin):

    # setting forms for user creation/editing
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = CustomUser

    # set fields for display in admin dashboard
    list_display = [
        'username', 'user_role', 'first_name', 'last_name', 'email', 'is_superuser', 'is_active'
    ]

    # set filter options
    list_filter = (
        'user_role', 'is_active', 'is_superuser'
    )

    # removes ability to edit
    readonly_fields = ('date_joined', 'last_login',)

    # fieldsets for user admin
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('User Information'), {'fields': ('user_role', 'first_name', 'last_name', 'email')}),
        (_('Permissions'), {'fields': ('is_active', 'is_superuser')}),
    )

    # fieldsets for adding users
    add_fieldsets = (
        (None, {'fields': ('username', 'password1', 'password2')}),
        (_('User Information'), {'fields': ('user_role', 'first_name', 'last_name', 'email')}),
        (_('Permissions'), {'fields': ('is_active', 'is_superuser')}),
    )


# registering CustomUser model to CustomUserAdmin
admin.site.register(CustomUser, CustomUserAdmin)

# removed base groups page
admin.site.unregister(Group)

# setting title and header of admin pages
admin.site.site_title = "Exam Setting Administration"
admin.site.site_header = "Exam Setting Administration"
