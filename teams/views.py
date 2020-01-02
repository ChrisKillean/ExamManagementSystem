from django.shortcuts import Http404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView
from django.db.models.base import ObjectDoesNotExist

from .models import Team
from .custom_methods import get_user_teams, verify_user_in_team
from exam_paper.models import ExamPaper


# View which displays all of an individual users teams. Redirects unregistered/in_active users to login
class DisplayUserTeams(LoginRequiredMixin, ListView):
    model = Team
    context_object_name = 'user_teams'
    template_name = "teams/user_teams.html"

    def get_queryset(self):
        # gets active user id then locates Team model instances where the user is present in a field
        return get_user_teams(self).order_by('team_name')


# View for individual team homepages. Redirects unregistered/in_active users to login screen
class TeamOverview(LoginRequiredMixin, DetailView):
    model = Team
    context_object_name = 'team_overview'
    template_name = 'teams/team_homepage.html'

    def get_context_data(self, **kwargs):

        error_response = "You can only access teams of which you are a member"
        try:
            team_instance = Team.objects.get(id=self.kwargs['pk'])
            # Checks user is a member of the team by checking each field, if not raises Http404
            if verify_user_in_team(self, team_instance):

                context = super(TeamOverview, self).get_context_data(id=self.kwargs['pk'])

                # sorting papers by academic year, module name, then exam type
                context['team_exam_papers'] = ExamPaper.objects.filter(paper_team_id=self.kwargs['pk']).order_by(
                    'paper_review_deadlines__academic_start_year',
                    'module_exam__module_name',
                    '-main_exam'
                )
                return context
            else:
                raise Http404("%s" % error_response)
        # When user tries to access team that does not exist, the same Http404 response is raised to the user.
        # This is to prevent finding urls patterns relating to teams.
        except ObjectDoesNotExist:
            raise Http404("%s" % error_response)
