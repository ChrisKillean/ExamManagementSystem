from django.contrib.auth.forms import UserCreationForm, UserChangeForm

from .models import CustomUser


# Custom form for user creation. Used instead of default UserCreationForm
class CustomUserCreationForm(UserCreationForm):

    class Meta(UserCreationForm):
        model = CustomUser
        fields = (
            'username', 'password1', 'password2', 'email', 'user_role', 'first_name', 'last_name'
        )

        exclude = {
            'is_staff', 'user_permissions', 'groups'
        }

        help_texts = {
            'user_role': 'Required:<br>'
                         '<b>Exam Staff for Exam Setters, Internal Reviewers or Exam Vetting Committee members</b>',
            'first_name': 'Required',
            'last_name': 'Required',
            'email': 'Required',
        }


# Custom form for editing existing user details. Used instead of default UserChangeForm
class CustomUserChangeForm(UserChangeForm):

    class Meta(UserChangeForm):
        model = CustomUser
        fields = ('username', 'email', 'user_role')

        help_texts = {
            'user_role': 'Required:<br>'
                         '<b>Exam Staff for Exam Setters, Internal Reviewers or Exam Vetting Committee members</b>',
            'first_name': 'Required',
            'last_name': 'Required',
            'email': 'Required',
        }
