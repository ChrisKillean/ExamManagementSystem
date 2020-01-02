from django import forms
from django.core.exceptions import ValidationError

from .models import Team
from accounts.models import CustomUser


class TeamForm(forms.ModelForm):

    class Meta:
        model = Team
        fields = '__all__'
        exclude = ('active', )

        help_texts = {
            'team_name': '<b>Required:</b>'
                         '<b>Team name must be unique. Suggested team name would be the name of the module the <br>'
                         'is responsible for and the academic year</b>',
            'exam_setter': '<b>Required</b>',
            'internal_reviewer': '<b>Required</b>',
            'vetting_committee': '<b>Required</b>',
            'external_examiner': '<b>Required</b>',
            'school_office': '<b>Required</b>',
            'observer': '<b>Optional</b>'
        }

    # called when TeamForm is initiated
    def __init__(self, *args, **kwargs):
        # run base __init__ method
        super(TeamForm, self).__init__(*args, **kwargs)

        # gets all users with EXAM_STAFF role so this query only needs to be run once instead of 4 times
        exam_staff_instance = CustomUser.objects.filter(user_role='EXAM_STAFF')

        # filtering fields based on user_roles from CustomUser model to only show relevant users for positions
        self.fields['exam_setter'].queryset = exam_staff_instance
        self.fields['internal_reviewer'].queryset = exam_staff_instance
        self.fields['vetting_committee'].queryset = exam_staff_instance
        self.fields['external_examiner'].queryset = CustomUser.objects.filter(user_role='EXTERNAL_EXAMINER')
        self.fields['school_office'].queryset = CustomUser.objects.filter(user_role='SCHOOL_OFFICE')
        self.fields['observer'].queryset = exam_staff_instance

    # override base clean method
    def clean(self):
        # Applying base clean method prior to applying custom clean method
        cleaned_data = super(TeamForm, self).clean()

        '''
        declare variables. only need to perform custom clean on these fields as they all have the same user_role,
        clean is ensuring a user doesn't occupy multiple roles in the same team
        '''
        exam_setter = cleaned_data.get('exam_setter')
        internal_reviewer = cleaned_data.get('internal_reviewer')
        vetting_committee = cleaned_data.get('vetting_committee')
        observer = cleaned_data.get('observer')

        # clean exam_setter input
        if exam_setter == internal_reviewer == vetting_committee == observer:
            exam_internal_vetting_observer_response = "Field must be unique. Exam Setter, Internal Reviewer, Vetting " \
                                                      "Committee and Observer are presently all set to the same user"
            raise ValidationError({
                'exam_setter': ["%s" % exam_internal_vetting_observer_response],
                'internal_reviewer': ["%s" % exam_internal_vetting_observer_response],
                'vetting_committee': ["%s" % exam_internal_vetting_observer_response],
                'observer': ["%s" % exam_internal_vetting_observer_response]
            })
        elif exam_setter == internal_reviewer == vetting_committee:
            exam_internal_vetting_response = "Field must be unique. Exam Setter, Internal Reviewer, Vetting " \
                                             "Committee are presently all set to the same user"
            raise ValidationError({
                'exam_setter': ["%s" % exam_internal_vetting_response],
                'internal_reviewer': ["%s" % exam_internal_vetting_response],
                'vetting_committee': ["%s" % exam_internal_vetting_response]
                                   })
        elif exam_setter == internal_reviewer == observer:
            exam_internal_observer_response = "Field must be unique. Exam Setter, Internal Reviewer and Observer are " \
                                     "presently all set to the same user"
            raise ValidationError({
                'exam_setter': ["%s" % exam_internal_observer_response],
                'internal_reviewer': ["%s" % exam_internal_observer_response],
                'observer': ["%s" % exam_internal_observer_response]
            })
        elif exam_setter == vetting_committee == observer:
            exam_vetting_observer_response = "Field must be unique. Exam Setter, Vetting Committee and Observer are " \
                                     "presently all set to the same user"
            raise ValidationError({
                'exam_setter': ["%s" % exam_vetting_observer_response],
                'vetting_committee': ["%s" % exam_vetting_observer_response],
                'observer': ["%s" % exam_vetting_observer_response]
            })
        elif exam_setter == internal_reviewer:
            exam_internal_response = "Field must be unique. Exam Setter and Internal Reviewer are presently set to " \
                                     "the same user"
            raise ValidationError({
                'exam_setter': ["%s" % exam_internal_response],
                'internal_reviewer': ["%s" % exam_internal_response]
            })
        elif exam_setter == vetting_committee:
            exam_vetting_response = "Field must be unique. Exam Setter and Vetting Committee are presently set to " \
                                    "the same user"
            raise ValidationError({
                'exam_setter': ["%s" % exam_vetting_response],
                'vetting_committee': ["%s" % exam_vetting_response]
            })
        elif exam_setter == observer:
            exam_observer_response = "Field must be unique. Exam Setter and Observer are presently set to the same user"

            raise ValidationError({
                'exam_setter': ["%s" % exam_observer_response],
                'observer': ["%s" % exam_observer_response]
            })

        # clean internal_reviewer input
        if internal_reviewer == vetting_committee == observer:
            internal_vetting_observer_response = "Field must be unique. Internal Reviewer, Vetting Committee and " \
                                                 "Observer are presently set to the same user"
            raise ValidationError({
                'internal_reviewer': ["%s" % internal_vetting_observer_response],
                'vetting_committee': ["%s" % internal_vetting_observer_response],
                'observer': ["%s" % internal_vetting_observer_response]
            })
        elif internal_reviewer == vetting_committee:
            internal_vetting_response = "Field must be unique. Internal Reviewer and Vetting Committee are presently " \
                                        "set to the same user"
            raise ValidationError({
                'internal_reviewer': ["%s" % internal_vetting_response],
                'vetting_committee': ["%s" % internal_vetting_response]
            })
        elif internal_reviewer == observer:
            internal_observer_response = "Field must be unique. Internal Reviewer and Observer are presently set to " \
                                         "the same user"
            raise ValidationError({
                'internal_reviewer': ["%s" % internal_observer_response],
                'observer': ["%s" % internal_observer_response]
            })

        # clean vetting_committee input
        if vetting_committee == observer:
            vetting_observer_response = "Field must be unique. Vetting Committee and Observer are presently set to " \
                                        "the same user"
            raise ValidationError({
                'vetting_committee': ["%s" % vetting_observer_response],
                'observer': ["%s" % vetting_observer_response]
                                   })

        # observer field input already cleaned by above processes


class TeamChangeForm(forms.ModelForm):

    class Meta:
        model = Team
        fields = ('team_name', 'active')

        help_texts = {
            'team_name': '<b>Required:</b>'
                         '<b>Team name must be unique. Suggested team name would be the name of the module the <br>'
                         'is responsible for and the academic year</b>',
        }
