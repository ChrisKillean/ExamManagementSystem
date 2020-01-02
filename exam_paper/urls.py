from django.urls import path
from django.conf.urls.static import static
from django.conf import settings

from .views import UserExamPapers, ExamOfficerPapersView, CreateExamView, CreateInitialDraft, CreateInternalReview, \
    ExamPaperOverview, InternalReviewAmendments, VettingCommittee, VettingCommitteeAmendments, CreateExternalReview, \
    ExternalReviewAmendments, CreateExamMarkerReport, CreateModuleModeratorReport, ReviewTranscript, \
    ReviewExamMarkerReport, ReviewModuleModeratorReport


app_name = "exam_paper"

urlpatterns = [
    path('my-papers/', UserExamPapers.as_view(),
         name='my-exam-papers'),
    path('all-papers/', ExamOfficerPapersView.as_view(),
         name='exam-officer-papers'),
    path('create/', CreateExamView.as_view(),
         name='create-exam'),
    path('overview/<int:exam_paper_ref>/', ExamPaperOverview.as_view(),
         name='exam-paper-overview'),
    path('review-transcript/<int:exam_paper_ref>/', ReviewTranscript.as_view(),
         name='review-transcript'),
    path('review-exam-marker-Report/<int:exam_paper_ref>/', ReviewExamMarkerReport.as_view(),
         name='review-marker-report'),
    path('review-module-moderator-report/<int:exam_paper_ref>/', ReviewModuleModeratorReport.as_view(),
         name='review-moderator-report'),
    path('initial-draft/<int:exam_paper_ref>/', CreateInitialDraft.as_view(),
         name='create-initial-draft'),
    path('internal-review/<int:exam_paper_ref>/', CreateInternalReview.as_view(),
         name='create-internal-review'),
    path('internal-review-amendments/<int:exam_paper_ref>/', InternalReviewAmendments.as_view(),
         name='internal_review_amendments'),
    path('vetting-committee-review/<int:exam_paper_ref>/', VettingCommittee.as_view(),
         name='vetting-committee-review'),
    path('vetting-committee-amendments/<int:exam_paper_ref>/', VettingCommitteeAmendments.as_view(),
         name='vetting-committee-amendments'),
    path('external-review/<int:exam_paper_ref>/', CreateExternalReview.as_view(),
         name='create-external-review'),
    path('external-review-amendments/<int:exam_paper_ref>/', ExternalReviewAmendments.as_view(),
         name='external-review-amendments'),
    path('exam-marker-report/<int:exam_paper_ref>/', CreateExamMarkerReport.as_view(),
         name='exam-marker-report'),
    path('moderator-report/<int:exam_paper_ref>/', CreateModuleModeratorReport.as_view(),
         name='module-moderator-report')
]

# For dev purposes to control file upload/retrieval on dev server
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
