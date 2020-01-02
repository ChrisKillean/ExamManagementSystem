from django.urls import path
from .views import GuidelineDocumentsView, UploadGuidelineDocumentsView
from django.conf.urls.static import static
from django.conf import settings


app_name = 'details'

urlpatterns = [
    path('guidelines/', GuidelineDocumentsView.as_view(),
         name='guideline-documents'),
    path('upload-guideline-documents/', UploadGuidelineDocumentsView.as_view(),
         name='upload-guidelines')
]

# For dev purposes to control file upload/retrieval on dev server
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)