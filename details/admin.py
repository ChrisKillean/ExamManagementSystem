from django.contrib import admin

from .models import ModuleDetail, ExamType, SubmissionDeadlines, GuidelineDocuments
from .forms import SubmissionDeadlineForm, ModuleDetailsForm


class ModuleDetailsAdmin(admin.ModelAdmin):
    model = ModuleDetail
    add_form = ModuleDetailsForm

    list_display = ['module_code', 'module_name', 'active']

    list_filter = ('active',)


class ExamTypeAdmin(admin.ModelAdmin):
    model = ExamType

    list_display = ['type', 'abbreviation', 'active']

    list_filter = ['active']

    # remove ability to delete ExamType objects
    def has_delete_permission(self, request, obj=None):
        return False


class SubmissionDeadlinesAdmin(admin.ModelAdmin):
    model = SubmissionDeadlines
    form = SubmissionDeadlineForm

    list_display = [
        'name', 'academic_start_year', 'initial_draft_submission', 'internal_review_response',
        'internal_review_amendments', 'vetting_committee_response', 'vetting_committee_amendments',
        'external_review_response', 'school_office_submission'
    ]

    list_filter = [
        'active', 'academic_start_year'
    ]

    def get_form(self, request, obj=None, **kwargs):
        if obj:
            kwargs.update({
                'exclude': getattr(kwargs, 'exclude', tuple()) + (
                    'academic_start_year', 'initial_draft_submission', 'internal_review_response',
                    'internal_review_amendments', 'vetting_committee_response', 'vetting_committee_amendments',
                    'external_review_response', 'school_office_submission'
                ),
            })
        return super(SubmissionDeadlinesAdmin, self).get_form(request, obj, **kwargs)


class GuidelineDocumentsAdmin(admin.ModelAdmin):
    model = GuidelineDocuments

    list_display = [
        'name', 'document'
    ]


admin.site.register(ModuleDetail, ModuleDetailsAdmin)
admin.site.register(ExamType, ExamTypeAdmin)
admin.site.register(SubmissionDeadlines, SubmissionDeadlinesAdmin)
admin.site.register(GuidelineDocuments, GuidelineDocumentsAdmin)
