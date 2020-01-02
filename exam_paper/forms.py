from django import forms

from .models import ExamPaper, ExamInitialDraft, ExamInternalReview, ExamVettingCommittee, ExamExternalReview, \
    ExamMarkerReport, ExamModuleModeratorReport
from teams.models import Team


def submission_checkbox():
    checkbox = forms.BooleanField(
        required=True,
        label='I have checked the information I have provided above',
        help_text='<p style="color:red"><strong><b>Warning!</b> '
                  'You will not be able to resubmit this form after submitting</strong></p>'
    )
    return checkbox


class ExamPaperForm(forms.ModelForm):

    class Meta:
        model = ExamPaper
        fields = ('paper_team', 'requires_resit_paper',  'module_exam', 'exam_paper_type', 'paper_review_deadlines')

        help_texts = {
            'paper_team': '<b>Required:</b> Can only select teams which you are the Exam Setter for',
            'requires_resit_paper': 'If you require a resit paper for this exam, tick this box',
            'module_exam': '<b>Required:</b> Select the module the exam is for',
            'exam_paper_type': '<b>Required:</b>',
            'paper_review_deadlines': '<b>Required:</b>',
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('current_user')
        super(ExamPaperForm, self).__init__(*args, **kwargs)

        # filter paper_team options to teams where user is an exam_setter
        self.fields['paper_team'].queryset = Team.objects.filter(exam_setter=self.user)


class CreateInitialDraftForm(forms.ModelForm):

    # Requires user to check a tick-box before submitting. Displays warning they will be unable to return to this stage
    user_check_submission = submission_checkbox()

    class Meta:
        model = ExamInitialDraft
        fields = ('initial_draft_comments', 'exam_paper', 'marking_scheme')

        help_texts = {
            'initial_draft_comments': '<b>Required</b>: Provide comments on material for internal Reviewer',
            'exam_paper': '<b>Required</b>:',
            'marking_scheme': '<b>Required</b>:',
        }


class CreateInternalReviewForm(forms.ModelForm):

    # Requires user to check a tick-box before submitting
    user_check_submission = submission_checkbox()

    class Meta:
        model = ExamInternalReview
        fields = ('internal_reviewer_feedback',)

        help_texts = {
            'internal_reviewer_feedback': '<b>Required</b>: Provide all feedback on the exam paper here'
        }


class InternalReviewAmendmentsForm(forms.ModelForm):

    # Requires user to check box before submission
    user_check_submission = submission_checkbox()

    class Meta:
        model = ExamInternalReview
        fields = ('exam_setter_response', 'exam_paper', 'marking_scheme')

        help_texts = {
            'exam_setter_response': "Enter response to Internal Reviewers feedback, detailing changes made"
        }

    def clean(self):
        # Applying base clean method prior to applying additional clean method
        cleaned_data = super(InternalReviewAmendmentsForm, self).clean()

        # declare variables to contain cleaned data which custom clean methods will be applied to
        exam_paper = cleaned_data.get('exam_paper')
        marking_scheme = cleaned_data.get('marking_scheme')

        # clean uploaded files
        if exam_paper is None:
            raise forms.ValidationError({'exam_paper': ["Exam Paper needs to be included"]
                                         })
        elif marking_scheme is None:
            raise forms.ValidationError({'marking_scheme': ["Marking Scheme needs to be included"]
                                         })
        else:
            return cleaned_data


class VettingCommitteeForm(forms.ModelForm):

    # Requires user to check box before submission
    user_check_submission = submission_checkbox()

    class Meta:
        model = ExamVettingCommittee
        fields = ('vetting_committee_feedback',)


class VettingCommitteeAmendmentsForm(forms.ModelForm):

    # Requires user to check box before submission
    user_check_submission = submission_checkbox()

    class Meta:
        model = ExamVettingCommittee
        fields = ('exam_setter_response', 'exam_paper', 'marking_scheme')

    def clean(self):
        # Applying base clean method prior to applying additional clean method
        cleaned_data = super(VettingCommitteeAmendmentsForm, self).clean()

        # declare variables to contain cleaned data which custom clean methods will be applied to
        exam_paper = cleaned_data.get('exam_paper')
        marking_scheme = cleaned_data.get('marking_scheme')

        # clean uploaded files
        if exam_paper is None:
            raise forms.ValidationError({'exam_paper': ["Exam Paper needs to be included"]
                                         })
        elif marking_scheme is None:
            raise forms.ValidationError({'marking_scheme': ["Marking Scheme needs to be included"]
                                         })
        else:
            return cleaned_data


class CreateExternalReviewForm(forms.ModelForm):

    # Requires user to check box before submission
    user_check_submission = submission_checkbox()

    class Meta:
        model = ExamExternalReview
        fields = ('external_examiner_feedback',)


class ExternalReviewAmendmentsForm(forms.ModelForm):

    # Requires user to check box before submission
    user_check_submission = submission_checkbox()

    class Meta:
        model = ExamExternalReview
        fields = ('exam_setter_response', 'exam_paper', 'marking_scheme')

    def clean(self):
        # Applying base clean method prior to applying additional clean method
        cleaned_data = super(ExternalReviewAmendmentsForm, self).clean()

        # declare variables to contain cleaned data which custom clean methods will be applied to
        exam_paper = cleaned_data.get('exam_paper')
        marking_scheme = cleaned_data.get('marking_scheme')

        # clean uploaded files, returning errors if no file uploaded
        if exam_paper is None:
            raise forms.ValidationError({'exam_paper': ["Exam Paper needs to be included"]
                                         })
        elif marking_scheme is None:
            raise forms.ValidationError({'marking_scheme': ["Marking Scheme needs to be included"]
                                         })
        else:
            return cleaned_data


# form for creating exam marker report
class CreateExamMarkerReportForm(forms.ModelForm):

    # Requires user to check box before submission
    user_check_submission = submission_checkbox()

    class Meta:
        model = ExamMarkerReport
        fields = (
            'quality_answers', 'areas_answered_well', 'areas_answered_poorly', 'difficulties_wording_paper',
            'difficulties_marking_scheme', 'candidate_literacy_numeracy', 'additional_comments'
        )

        labels = {
            "quality_answers": "General quality of candidate answers",
            "areas_answered_well": "Areas of course candidates answered well",
            "areas_answered_poorly": "Areas of course candidates answered poorly",
            "difficulties_wording_paper": "Difficulties arising from wording of paper",
            "difficulties_marking_scheme": "Difficulties applying marking scheme",
            "candidate_literacy_numeracy": "Level of candidates literacy and numeracy",
            "additional_comments": "Other aspects of marking you wish to inform the course coordinator of"
        }

        help_texts = {
            'quality_answers': '<b>Required</b>',
            'areas_answered_well': '<b>Required</b>',
            'areas_answered_poorly': '<b>Required</b>',
            'difficulties_wording_paper': '<b>Required</b>',
            'difficulties_marking_scheme': '<b>Required</b>',
            'candidate_literacy_numeracy': '<b>Required</b>'
        }


class CreateModuleModeratorReportForm(forms.ModelForm):

    # Requires user to check box before submission
    user_check_submission = submission_checkbox()

    class Meta:
        model = ExamModuleModeratorReport

        fields = (
            'check_addition_and_total_marks', 'moderation_process', 'significant_outcomes'
        )

        labels = {
            "check_addition_and_total_marks": "Checking addition and totals for marks",
            "moderation_process": "The moderation process"
        }

        help_texts = {
            "check_addition_and_total_marks": "<b>Required</b>: Did you check that the marks for the exams were added "
                                              "up correctly? Have you notified the module coordinator of any changes?",
            "moderation_process": "<b>Required</b>: Briefly describe how moderation was conducted including details of "
                                  "how many exam scripts were sampled",
            "significant_outcomes": "<b>Required</b>: Are there any significant outcomes you wish to draw to the "
                                    "attention of the module coordinator?"
        }
