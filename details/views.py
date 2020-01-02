from django.core.files.storage import FileSystemStorage
from django.views.generic import ListView, CreateView
from django.urls import reverse
from django.contrib.auth.mixins import LoginRequiredMixin

from .models import GuidelineDocuments


class UploadGuidelineDocumentsView(LoginRequiredMixin, CreateView):
    model = GuidelineDocuments
    fields = ('name', 'document')
    template_name = 'details/upload_documents.html'

    def get_success_url(self):
        return reverse('details:upload-guidelines')


# View for guideline docs. Available only to active users, only LoginRequiredMixin required for user validation
class GuidelineDocumentsView(LoginRequiredMixin, ListView):
    model = GuidelineDocuments
    template_name = 'details/guidelines_view.html'
    context_object_name = 'guidelines'

    def get_queryset(self):
        # searches exam papers identified user team and sorts by year and module
        guideline_docs = GuidelineDocuments.objects.all().order_by(
            'name'
        )
        return guideline_docs
