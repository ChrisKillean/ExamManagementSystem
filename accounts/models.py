from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone


# CustomUser model with additional fields as opposed to using default User model.
class CustomUser(AbstractUser):

    # dictionary of possible roles
    USER_ROLE_CHOICES = [
        ('EXAM_STAFF', 'Exam Staff'),
        ('EXTERNAL_EXAMINER', 'External Examiner'),
        ('SCHOOL_OFFICE', 'School Office'),
    ]

    # new fields added to base User model
    user_role = models.CharField(
        choices=USER_ROLE_CHOICES,
        null=False, default='',
        max_length=19
    )
    first_name = models.CharField(
        max_length=40,
        blank=False
    )
    last_name = models.CharField(
        max_length=100,
        blank=False
    )
    email = models.EmailField(
        max_length=100,
        blank=False,
        default='',
        unique=True
    )
    date_joined = models.DateTimeField(
        default=timezone.now
    )
    # gives option to make new users an admin at registration, also sets time user was created
    is_superuser = models.BooleanField(
        default=False
    )
    is_active = models.BooleanField(
        default=True
    )

    # Setting required fields in addition to username and password
    REQUIRED_FIELDS = ['user_role', 'first_name', 'last_name', 'email']

    def __str__(self):
        return self.first_name + ' ' + self.last_name + ': ' + self.email

    def users_name(self):
        return self.first_name + ' ' + self.last_name

    def get_user_role(self):
        return self.user_role
