from django.contrib import admin

from .models import ExamPaper
from .forms import ExamPaperForm


class ExamPaperAdmin(admin.ModelAdmin):
    model = ExamPaper
    form = ExamPaperForm

    list_display = [
        'main_exam', 'module_exam', '' 'paper_creation_stage', 'exam_paper_type', 'active'
    ]

    list_filter = ('active', 'main_exam', 'module_exam', 'exam_paper_type')

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


admin.site.register(ExamPaper, ExamPaperAdmin)
