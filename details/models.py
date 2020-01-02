from django.db import models
from django.core.validators import MinLengthValidator


# model for table of different module courses
class ModuleDetail(models.Model):
    module_code = models.CharField(
        'Module Code',
        max_length=7,
        null=False,
        validators=[MinLengthValidator(7)],
        unique=True
    )
    module_name = models.CharField(
        max_length=100,
        null=False,
        unique=True
    )
    active = models.BooleanField(
        null=False,
        editable=True,
        unique=False,
        default=True
    )

    def __str__(self):
        return self.module_name + ' - ' + self.module_code


# model for table of Exam Types
class ExamType(models.Model):
    type = models.CharField(
        max_length=50,
        null=False,
        unique=True
    )
    abbreviation = models.CharField(
        max_length=5,
        null=False,
        unique=True,
    )
    active = models.BooleanField(
        null=False,
        editable=True,
        unique=False,
        default=True,
    )

    def __str__(self):
        return self.type + ' - ' + self.abbreviation


# model for table of Submission Deadlines
class SubmissionDeadlines(models.Model):
    name = models.CharField(
        max_length=50,
        null=False,
        unique=False,
    )
    academic_start_year = models.PositiveIntegerField(
        'Academic Start Year',
        null=False,
        unique=False,
    )
    initial_draft_submission = models.DateField(
        null=False,
        unique=False,
    )
    internal_review_response = models.DateField(
        null=False,
        unique=False,
    )
    internal_review_amendments = models.DateField(
        null=False,
        unique=False
    )
    vetting_committee_response = models.DateField(
        null=False,
        unique=False,
    )
    vetting_committee_amendments = models.DateField(
        null=False,
        unique=False
    )
    external_review_response = models.DateField(
        null=False,
        unique=False,
    )
    school_office_submission = models.DateField(
        null=False,
        unique=False,
    )
    active = models.BooleanField(
        null=False,
        unique=False,
        default=True,
    )

    def __str__(self):
        return self.name + ' - ' + str(self.academic_start_year)


class GuidelineDocuments(models.Model):
    name = models.CharField(
        max_length=100,
        null=False,
        unique=True,
    )
    document = models.FileField(
        upload_to='guideline_documents/docs/'
    )

    def __str__(self):
        return self.name
