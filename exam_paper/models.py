from django.db import models
from django.conf import settings
from django.core.validators import MinLengthValidator

from details.models import SubmissionDeadlines, ExamType, ModuleDetail
from teams.models import Team


# Model for Exam Papers
class ExamPaper(models.Model):
    # Choices for stages exam paper can be at
    Exam_Stages_Options = [
        ('INITIAL_DRAFT', 'Initial Draft'),
        ('INTERNAL_REVIEW', 'Internal Review'),
        ('INTERNAL_REVIEW_COMPLETE', 'Internal Review Complete'),
        ('VETTING_COMMITTEE', 'Vetting Committee'),
        ('VETTING_COMMITTEE_COMPLETE', 'Vetting Committee Review Complete'),
        ('EXTERNAL_REVIEW', 'External Review'),
        ('EXTERNAL_REVIEW_COMPLETE', 'External Review Complete'),
        ('PAPER_FINALISED', 'Paper Finalised'),
        ('EXAM_REPORT', 'Exam Marker Report Submitted'),
        ('REPORTS_COMPLETED', 'Exam Review Complete')
    ]

    paper_team = models.ForeignKey(
        Team,
        null=False,
        on_delete=models.PROTECT,
        related_name='paper_team_set'
    )
    # link to another model to ensure consistency academic_year =
    paper_creation_stage = models.CharField(
        choices=Exam_Stages_Options,
        null=False,
        max_length=30,
        default='INITIAL_DRAFT'
    )
    requires_resit_paper = models.BooleanField(
        default=False
    )
    main_exam = models.BooleanField(
        default=True
    )
    module_exam = models.ForeignKey(
        ModuleDetail,
        null=False,
        on_delete=models.PROTECT,
        related_name='exam_module_set'
    )
    exam_paper_type = models.ForeignKey(
        ExamType,
        null=False,
        on_delete=models.PROTECT,
        related_name='exam_type_set'
    )
    paper_review_deadlines = models.ForeignKey(
        SubmissionDeadlines,
        null=False,
        on_delete=models.PROTECT,
        related_name='paper_deadlines_set'
    )
    # Tracking when individual stages are completed
    submission_initial_draft = models.DateField(
        null=True
    )
    submission_internal_review_response = models.DateField(
        null=True
    )
    submission_internal_review_amendments = models.DateField(
        null=True
    )
    submission_vetting_committee_response = models.DateField(
        null=True
    )
    submission_vetting_committee_amendments = models.DateField(
        null=True
    )
    submission_external_review_response = models.DateField(
        null=True
    )
    submission_school_office = models.DateField(
        null=True
    )
    submission_exam_marker_report = models.DateField(
        null=True
    )
    submission_moderator_report = models.DateField(
        null=True
    )
    active = models.BooleanField(
        null=False,
        default=True
    )

    def get_exam_team(self):
        return str(self.paper_team)


# Model for Initial Draft Stage
class ExamInitialDraft(models.Model):
    related_exam_paper = models.OneToOneField(
        ExamPaper,
        on_delete=models.CASCADE,
        null=False
    )
    initial_draft_comments = models.TextField(
        max_length=1500,
        blank=False,
        validators=[MinLengthValidator(5)]
    )
    exam_paper = models.FileField(
        upload_to='exam_paper/initial_draft/exam_paper',
        null=False
    )
    marking_scheme = models.FileField(
        upload_to='exam_paper/initial_draft/marking_scheme',
        null=False
    )


# Model for Internal Review stage
class ExamInternalReview(models.Model):
    related_exam_paper = models.OneToOneField(
        ExamPaper,
        on_delete=models.CASCADE,
        null=False
    )
    internal_reviewer_feedback = models.TextField(
        max_length=1500,
        blank=False
    )
    exam_setter_response = models.TextField(
        max_length=1000,
        blank=False
    )
    exam_paper = models.FileField(
        upload_to='exam_paper/internal_review/exam_paper',
    )
    marking_scheme = models.FileField(
        upload_to='exam_paper/internal_review/marking_scheme',

    )


# Model for Vetting Committee stage
class ExamVettingCommittee(models.Model):
    related_exam_paper = models.OneToOneField(
        ExamPaper,
        on_delete=models.CASCADE,
        null=False
    )
    vetting_committee_feedback = models.TextField(
        max_length=1500,
        blank=False
    )
    exam_setter_response = models.TextField(
        max_length=1000,
        blank=False
    )
    exam_paper = models.FileField(
        upload_to='exam_paper/vetting/exam_paper',
    )
    marking_scheme = models.FileField(
        upload_to='exam_paper/vetting/marking_scheme',
    )


# Model for external Review stage
class ExamExternalReview(models.Model):
    related_exam_paper = models.OneToOneField(
        ExamPaper,
        on_delete=models.CASCADE,
        null=False
    )
    external_examiner_feedback = models.TextField(
        max_length=1500,
        blank=False
    )
    exam_setter_response = models.TextField(
        max_length=1000,
        blank=False
    )
    exam_paper = models.FileField(
        upload_to='exam_paper/external/exam_paper',
    )
    marking_scheme = models.FileField(
        upload_to='exam_paper/external/marking_scheme',
    )


# Model for Exam Maker Report
class ExamMarkerReport(models.Model):
    related_exam_paper = models.ForeignKey(
        ExamPaper,
        on_delete=models.CASCADE,
        null=False
    )
    module_code_and_name = models.ForeignKey(
        ModuleDetail,
        on_delete=models.PROTECT,
        null=False,
        related_name='module_code_and_name_set'
    )
    report_completed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        null=False,
        related_name='report_completed_by_set'
    )
    quality_answers = models.TextField(
        max_length=1000,
        blank=False
    )
    areas_answered_well = models.TextField(
        max_length=1000,
        blank=False
    )
    areas_answered_poorly = models.TextField(
        max_length=1000,
        blank=False
    )
    difficulties_wording_paper = models.TextField(
        max_length=1000,
        blank=False
    )
    difficulties_marking_scheme = models.TextField(
        max_length=1000,
        blank=False
    )
    candidate_literacy_numeracy = models.TextField(
        max_length=1000,
        blank=False
    )
    additional_comments = models.TextField(
        max_length=1000,
        blank=True
    )


# Model for Exam Moderator Report
class ExamModuleModeratorReport(models.Model):
    related_exam_paper = models.ForeignKey(
        ExamPaper,
        on_delete=models.CASCADE,
        null=False
    )
    module_code_and_name = models.ForeignKey(
        ModuleDetail,
        on_delete=models.PROTECT,
        null=False,
        related_name='module_exam_set'
    )
    exam_paper_type = models.ForeignKey(
        ExamType,
        on_delete=models.PROTECT,
        null=False,
        related_name='exam_paper_type_set'
    )
    # links to internal reviewer
    module_moderator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        null=False,
        related_name='module_moderator_set'
    )
    # links to exam setter
    module_coordinator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        null=False,
        related_name='module_coordinator_set'
    )
    check_addition_and_total_marks = models.TextField(
        max_length=1000,
        null=False
    )
    moderation_process = models.TextField(
        max_length=1000,
        blank=False
    )
    significant_outcomes = models.TextField(
        max_length=1000,
        blank=False
    )
