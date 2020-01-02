from django.contrib import admin

from .models import Team
from .forms import TeamForm, TeamChangeForm


class TeamAdmin(admin.ModelAdmin):
    model = Team

    list_display = [
        'team_name', 'active', 'exam_setter', 'internal_reviewer', 'vetting_committee', 'external_examiner',
        'school_office', 'observer'
    ]

    list_filter = ('active',)

    # override get form method to display different forms depending on if user is adding or editing Team
    def get_form(self, request, obj=None, **kwargs):
        # if object doesnt exist, display TeamForm, otherwise display TeamChangeForm
        if obj is None:
            return TeamForm
        else:
            return TeamChangeForm


admin.site.register(Team, TeamAdmin)
