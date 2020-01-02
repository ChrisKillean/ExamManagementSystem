from django.db.models import Q

from .models import Team


# verifies user is a part of the passed instance of team object
def verify_user_in_team(self, instance):
    if ((self.request.user == instance.exam_setter) or
            (self.request.user == instance.internal_reviewer) or
            (self.request.user == instance.vetting_committee) or
            (self.request.user == instance.external_examiner) or
            (self.request.user == instance.school_office) or
            (self.request.user == instance.observer)):
        return True
    else:
        return False


def get_user_teams(self):
    target_user = self.request.user
    found_teams = Team.objects.filter(
        Q(exam_setter=target_user) | Q(internal_reviewer=target_user) |
        Q(vetting_committee=target_user) | Q(external_examiner=target_user) |
        Q(school_office=target_user) | Q(observer=target_user))
    return found_teams


# Check user is exam setter for provided objects team
def verify_user_exam_setter(self, object_instance):
    if object_instance.paper_team.exam_setter == self.request.user:
        return True
    else:
        return False


# Check user is the internal reviewer for the provided objects team
def verify_user_internal_reviewer(self, object_instance):
    if object_instance.paper_team.internal_reviewer == self.request.user:
        return True
    else:
        return False
