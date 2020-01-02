from django.views.generic import CreateView, DetailView, ListView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse
from django.db.models.base import ObjectDoesNotExist
from django.shortcuts import Http404
import datetime

from .forms import ExamPaperForm, CreateInitialDraftForm, CreateInternalReviewForm, InternalReviewAmendmentsForm, \
    VettingCommitteeForm, VettingCommitteeAmendmentsForm, CreateExternalReviewForm, ExternalReviewAmendmentsForm, \
    CreateExamMarkerReportForm, CreateModuleModeratorReportForm
from .models import ExamPaper, ExamInitialDraft, ExamInternalReview, ExamVettingCommittee, ExamExternalReview, \
    ExamMarkerReport, ExamModuleModeratorReport
from .custom_methods import work_progress, report_progress, creation_stage_numeric
from accounts.models import CustomUser
from teams.models import Team
from teams.custom_methods import get_user_teams, verify_user_in_team, verify_user_exam_setter, \
    verify_user_internal_reviewer


# View displays all exam papers linked to the active user
class UserExamPapers(LoginRequiredMixin, ListView):

    model = ExamPaper
    context_object_name = 'user_exams'
    template_name = 'exam_papers/my_exams.html'

    def get_queryset(self):
        # gets active user id then locates Team model instances where the user is present in a field
        user_teams = get_user_teams(self)

        # searches exam papers identified user team and sorts by year and module
        user_exams = ExamPaper.objects.filter(paper_team_id__in=user_teams).order_by(
            'paper_review_deadlines__academic_start_year',
            'module_exam__module_name',
            '-main_exam'
        )
        return user_exams


class ExamOfficerPapersView(LoginRequiredMixin, ListView):
    model = ExamPaper
    context_object_name = 'exam_papers'
    template_name = 'exam_papers/exam_officer_all_exams.html'

    def get_queryset(self):

        # Response to unauthorised user
        error_response = 'Only the examination officer can access this page'

        # get user object
        user = CustomUser.objects.get(pk=self.request.user.id)

        # check user is exam officer
        if user.is_superuser:
            # ordering by active/inactive, year then module code
            ordered_exams = ExamPaper.objects.order_by(
                'active',
                'paper_review_deadlines__academic_start_year',
                'module_exam'
            )
            return ordered_exams
        # raise error if user is not exam officer
        else:
            raise Http404("%s" % error_response)


# View for creating exam papers
class CreateExamView(LoginRequiredMixin, CreateView):

    form_class = ExamPaperForm
    template_name = 'exam_papers/create_exam.html'
    context_object_name = 'exam'

    def get_success_url(self):
        return reverse('exam_paper:exam-paper-overview', kwargs={'exam_paper_ref': self.object.pk})

    def get_form_kwargs(self):
        kwargs = super(CreateExamView, self).get_form_kwargs()
        kwargs.update({'current_user': self.request.user})
        return kwargs

    # override form to check if paper requires resit
    def form_valid(self, form):
        # gets requires_resit field from user submitted form
        requires_resit = form.cleaned_data['requires_resit_paper']

        # if requires resit
        if requires_resit:
            # get data from user submitted form
            team = form.cleaned_data['paper_team']
            module = form.cleaned_data['module_exam']
            exam_type = form.cleaned_data['exam_paper_type']
            review_deadlines = form.cleaned_data['paper_review_deadlines']

            # create new ExamPaper object for resit
            resit_paper = ExamPaper(
                paper_team=team,
                paper_creation_stage='INITIAL_DRAFT',
                requires_resit_paper=False,
                main_exam=False,
                module_exam=module,
                exam_paper_type=exam_type,
                paper_review_deadlines=review_deadlines
            )

            # save resit then use base form_valid method to save main exam object
            resit_paper.save()
            return super(CreateExamView, self).form_valid(form)

        # if no resit required, use base form_valid method
        else:
            return super(CreateExamView, self).form_valid(form)


# View for Exam_Paper specific review page
class ExamPaperOverview(LoginRequiredMixin, DetailView):

    model = ExamPaper
    context_object_name = 'exam_paper_ref'
    template_name = 'exam_papers/exam_paper_overview.html'

    def get_object(self, **kwargs):
        error_response = "You can only access exam papers your team is responsible for"
        # attempts to access exam paper object using pk id passed in url, raises Http404
        try:
            exam_paper_instance = ExamPaper.objects.get(id=self.kwargs['exam_paper_ref'])
            team_ref = exam_paper_instance.paper_team_id
            team_instance = Team.objects.get(id=team_ref)

            # Checks user is a member of team responsible for the exam paper or Local Exam Officer, else raises Http404
            if verify_user_in_team(self, team_instance) or self.request.user.is_superuser:
                return exam_paper_instance
            else:
                raise Http404("%s" % error_response)
        # When user tries to access exam paper that does not exist, the same Http404 response is raised to the user.
        # This is to prevent identifying urls patterns relating to exam papers.
        except ObjectDoesNotExist:
            raise Http404("%s" % error_response)

    # Override function
    def get_context_data(self, **kwargs):

        exam_paper = ExamPaper.objects.get(pk=self.kwargs['exam_paper_ref'])
        deadlines = exam_paper.paper_review_deadlines

        # call base get_context)data
        context = super(ExamPaperOverview, self).get_context_data(**kwargs)

        # Filling context for use in template to assess adherence to deadlines
        context['p_initial'] = work_progress(deadlines.initial_draft_submission,
                                             exam_paper.submission_initial_draft)
        context['p_internal'] = work_progress(deadlines.internal_review_response,
                                              exam_paper.submission_internal_review_response)
        context['p_internal_a'] = work_progress(deadlines.internal_review_amendments,
                                                exam_paper.submission_internal_review_amendments)
        context['p_vetting'] = work_progress(deadlines.vetting_committee_response,
                                             exam_paper.submission_vetting_committee_response)
        context['p_vetting_a'] = work_progress(deadlines.vetting_committee_amendments,
                                               exam_paper.submission_vetting_committee_amendments)
        context['p_external'] = work_progress(deadlines.external_review_response,
                                              exam_paper.submission_external_review_response)
        context['p_school'] = work_progress(deadlines.school_office_submission,
                                            exam_paper.submission_school_office)
        context['p_exam_report'] = report_progress(exam_paper.submission_exam_marker_report)
        context['p_module_report'] = report_progress(exam_paper.submission_moderator_report)

        # additional context for deadlines and team
        context['deadlines_ref'] = exam_paper.paper_review_deadlines
        context['team_ref'] = exam_paper.paper_team
        context['module_ref'] = exam_paper.module_exam
        return context


class ReviewTranscript(LoginRequiredMixin, DetailView):

    model = ExamPaper
    context_object_name = 'exam_paper_ref'
    template_name = 'exam_papers/paper_transcript.html'

    def get_object(self, **kwargs):
        error_response = "You can only view transcripts of papers which your team is responsible for"
        # attempts to access exam paper object using pk id passed in url, raises Http404
        try:
            exam_paper_instance = ExamPaper.objects.get(id=self.kwargs['exam_paper_ref'])
            team_instance = Team.objects.get(id=exam_paper_instance.paper_team_id)

            # Checks user is a member of team responsible for the exam paper or Local Exam Officer, else raises Http404
            if verify_user_in_team(self, team_instance) or self.request.user.is_superuser:
                return exam_paper_instance
            else:
                raise Http404("%s" % error_response)
        # When user tries to access transcript for non-existent paper, the same Http404 response is raised to the user.
        # This is to prevent identifying urls patterns relating to exam papers.
        except ObjectDoesNotExist:
            raise Http404("%s" % error_response)

    # Override base method
    def get_context_data(self, **kwargs):

        exam_paper = ExamPaper.objects.get(pk=self.kwargs['exam_paper_ref'])

        # call base get_context_data
        paper_stage = creation_stage_numeric(exam_paper)

        context = super(ReviewTranscript, self).get_context_data(**kwargs)
        context['paper_stage'] = paper_stage
        context['team_ref'] = exam_paper.paper_team

        # assessing stage paper is at to get additional context for template
        if paper_stage > 1:
            context['initial_draft'] = ExamInitialDraft.objects.get(related_exam_paper=exam_paper)

        if paper_stage > 2:
            context['internal_review'] = ExamInternalReview.objects.get(related_exam_paper=exam_paper)

        if paper_stage > 4:
            context['vetting'] = ExamVettingCommittee.objects.get(related_exam_paper=exam_paper)

        if paper_stage > 6:
            context['external_review'] = ExamExternalReview.objects.get(related_exam_paper=exam_paper)

        return context


class ReviewExamMarkerReport(LoginRequiredMixin, DetailView):

    model = ExamMarkerReport
    context_object_name = 'exam_report'
    template_name = 'exam_papers/exam_marker_report.html'

    def get_object(self, **kwargs):
        error_response = "You can only view exam marker reports of papers which your team is responsible for"
        error_no_report = "Exam markers report has not been submitted at this stage"
        # attempts to access exam paper object using pk id passed in url, raises Http404
        try:
            exam_paper_instance = ExamPaper.objects.get(id=self.kwargs['exam_paper_ref'])
            team_instance = Team.objects.get(id=exam_paper_instance.paper_team_id)

            # Checks user is a member of team responsible for the exam paper or Local Exam Officer, else raises Http404
            if verify_user_in_team(self, team_instance) or self.request.user.is_superuser:

                # check exam marker report has been submitted, if not return error
                try:
                    exam_marker_report = ExamMarkerReport.objects.get(related_exam_paper=exam_paper_instance)
                    return exam_marker_report
                except ObjectDoesNotExist:
                    raise Http404("%s" % error_no_report)
        # When user tries to access exam marker report for non-existent paper, the same Http404 response is raised to
        # the user. This is to prevent identifying urls patterns relating to exam papers.
        except ObjectDoesNotExist:
            raise Http404("%s" % error_response)

    # override context to provide exam paper ref to template
    def get_context_data(self, **kwargs):

        # Get details for additional context
        exam_paper = ExamPaper.objects.get(pk=self.kwargs['exam_paper_ref'])

        # call base context then assign additional or template
        context = super(ReviewExamMarkerReport, self).get_context_data(**kwargs)

        context['paper_stage'] = creation_stage_numeric(exam_paper)
        context['exam_setter'] = ExamPaper.objects.get(
            id=self.kwargs['exam_paper_ref']).paper_team.exam_setter.users_name
        context['exam_paper_ref'] = ExamPaper.objects.get(id=self.kwargs['exam_paper_ref'])
        return context


class ReviewModuleModeratorReport(LoginRequiredMixin, DetailView):

    model = ExamModuleModeratorReport
    context_object_name = 'moderator_report'
    template_name = 'exam_papers/module_moderator_report.html'

    def get_object(self, **kwargs):
        error_response = "You can only view module moderator reports of papers which your team is responsible for"
        error_no_report = "Module moderator report has not been submitted at this stage"
        # attempts to access exam paper object using pk id passed in url, raises Http404
        try:
            exam_paper_instance = ExamPaper.objects.get(id=self.kwargs['exam_paper_ref'])
            team_instance = Team.objects.get(id=exam_paper_instance.paper_team_id)

            # Checks user is a member of team responsible for the exam paper or Local Exam Officer, else raises Http404
            if verify_user_in_team(self, team_instance) or self.request.user.is_superuser:

                # check Module Moderator report has been submitted, if not return error
                try:
                    module_moderator_report = ExamModuleModeratorReport.objects.get(
                        related_exam_paper=exam_paper_instance)
                    return module_moderator_report

                except ObjectDoesNotExist:
                    raise Http404("%s" % error_no_report)

        # When user tries to access Module Moderator report for non-existent paper, the same Http404 response is raised
        # to the user. This is to prevent identifying urls patterns relating to exam papers.
        except ObjectDoesNotExist:
            raise Http404("%s" % error_response)

    # override context to provide exam paper ref to template
    def get_context_data(self, **kwargs):
        exam_paper = ExamPaper.objects.get(id=self.kwargs['exam_paper_ref'])
        paper_team = exam_paper.paper_team

        context = super(ReviewModuleModeratorReport, self).get_context_data(**kwargs)
        context['exam_paper_ref'] = exam_paper
        context['module_coordinator'] = paper_team.exam_setter.users_name
        context['moderator'] = paper_team.internal_reviewer.users_name
        return context


# View for creating Initial Exam object for exam
class CreateInitialDraft(LoginRequiredMixin, CreateView):

    form_class = CreateInitialDraftForm
    template_name = 'exam_papers/create_initial_draft.html'

    # redirect to exam paper overview screen upon creation of initial draft object instance
    def get_success_url(self):
        return reverse('exam_paper:exam-paper-overview', kwargs={'exam_paper_ref': self.object.related_exam_paper.pk})

    # override default get_form_kwargs
    def get_form_kwargs(self):

        # responses for Http404 raise
        error_response = "Only exam setter of team can create initial draft"
        initial_draft_exists_response = "Initial draft has already been submitted"
        try:
            # call base get_form_kwargs and sets relevant exam_paper instance
            kwargs = super(CreateInitialDraft, self).get_form_kwargs()
            exam_paper_instance = ExamPaper.objects.get(pk=self.kwargs['exam_paper_ref'])
            if verify_user_exam_setter(self, exam_paper_instance):
                # checks paper at initial draft stage return kwargs if it is, error if it isn't
                if exam_paper_instance.paper_creation_stage == 'INITIAL_DRAFT':
                    return kwargs
                else:
                    raise Http404("%s" % initial_draft_exists_response)

            else:
                # raise error if user is not exam setter of relevant team
                raise Http404("%s" % error_response)

        # raise error if object does not exist
        except ObjectDoesNotExist:
            raise Http404("%s" % error_response)

    def get_context_data(self, **kwargs):
        # Get academic papers for team the sort by academic year of the paper and its module
        context = super(CreateInitialDraft, self).get_context_data(**kwargs)
        return context

    # overrides default form_valid
    def form_valid(self, form):
        # stops form being submitted initially
        CreateInitialDraftForm.instance = form.save(commit=False)

        # sets ForeignKey to parent exam_paper, updates exam_paper creation stage and call default form_valid
        CreateInitialDraftForm.instance.related_exam_paper = ExamPaper.objects.get(pk=self.kwargs['exam_paper_ref'])
        ExamPaper.objects.filter(pk=self.kwargs['exam_paper_ref']).update(paper_creation_stage='INTERNAL_REVIEW',
                                                                          submission_initial_draft=datetime.date.today()
                                                                          )

        return super(CreateInitialDraft, self).form_valid(form)


# View for Internal Review of exam paper
class CreateInternalReview(LoginRequiredMixin, CreateView):

    form_class = CreateInternalReviewForm
    template_name = 'exam_papers/create_internal_review.html'
    context_object_name = 'internal_review_ref'

    # redirect to exam paper overview screen upon creation of initial draft object instance
    def get_success_url(self):
        return reverse('exam_paper:exam-paper-overview', kwargs={'exam_paper_ref': self.object.related_exam_paper.pk})

    # Setting context data for template
    def get_context_data(self, **kwargs):
        # Get academic papers for team the sort by academic year of the paper and its module
        context = super(CreateInternalReview, self).get_context_data(**kwargs)
        context['initial_draft_ref'] = ExamInitialDraft.objects.get(related_exam_paper=self.kwargs['exam_paper_ref'])
        return context

    # override default get_form_kwargs
    def get_form_kwargs(self):

        # responses for Http404 raise
        error_response = "Only Internal Reviewer of team can submit the Internal Review"
        error_wrong_stage_requested = "Internal Review cannot be submitted at this stage"
        try:

            # Gets related exam_paper object then verifies user is the exam setter for the team
            exam_paper_instance = ExamPaper.objects.get(pk=self.kwargs['exam_paper_ref'])
            if exam_paper_instance.paper_team.internal_reviewer == self.request.user:

                # checks
                if exam_paper_instance.paper_creation_stage == 'INTERNAL_REVIEW':

                    # call default get_form_kwargs and return
                    kwargs = super(CreateInternalReview, self).get_form_kwargs()
                    return kwargs
                else:
                    raise Http404("%s" % error_wrong_stage_requested)

            else:
                # raise error if user is not exam setter of relevant team
                raise Http404("%s" % error_response)

        # raise error if object does not exist
        except ObjectDoesNotExist:
            raise Http404("%s" % error_response)

    # overrides default form_valid
    def form_valid(self, form):
        # stops form being submitted initially
        CreateInternalReviewForm.instance = form.save(commit=False)

        # sets ForeignKey to parent exam_paper, updates exam_paper creation stage
        CreateInternalReviewForm.instance.related_exam_paper = ExamPaper.objects.get(pk=self.kwargs['exam_paper_ref'])
        ExamPaper.objects.filter(pk=self.kwargs['exam_paper_ref']).update(
            paper_creation_stage='INTERNAL_REVIEW_COMPLETE', submission_internal_review_response=datetime.date.today()
                                                                          )
        # calls base form_valid
        return super(CreateInternalReview, self).form_valid(form)


# View responsible for exam_setter amendments after internal review
class InternalReviewAmendments(LoginRequiredMixin, UpdateView):
    form_class = InternalReviewAmendmentsForm
    template_name = 'exam_papers/internal_review_amendments.html'
    context_object_name = 'internal_amendments_ref'

    # redirect to exam paper overview screen upon creation of initial draft object instance
    def get_success_url(self):
        return reverse('exam_paper:exam-paper-overview', kwargs={'exam_paper_ref': self.object.related_exam_paper.pk})

    # Gets relevant exam_internal_review object and applies additional user verification
    def get_object(self, **kwargs):
        error_response = "Only the exam setter for the paper can complete a response to the internal review"
        error_amendments_already_submitted = "Amendments to the Internal Review cannot be submitted at this stage"

        # attempts to access exam paper object using pk id passed in url, raises Http404
        try:
            exam_paper_instance = ExamPaper.objects.get(id=self.kwargs['exam_paper_ref'])

            # verify user is relevant exam_setter, then get and returns instance if at internal_review_complete stage
            if verify_user_exam_setter(self, exam_paper_instance):
                if exam_paper_instance.paper_creation_stage == 'INTERNAL_REVIEW_COMPLETE':
                    internal_review_instance = ExamInternalReview.objects.get(
                        related_exam_paper=self.kwargs['exam_paper_ref'])
                    return internal_review_instance
                else:
                    # if present exam paper stage isn't internal_review_complete, give error that its already submitted
                    raise Http404("%s" % error_amendments_already_submitted)
            # invalid user, return error
            else:
                raise Http404("%s" % error_response)
        # return error if object doesnt exist
        except ObjectDoesNotExist:
            raise Http404("%s" % error_response)

    def get_context_data(self, **kwargs):
        # Get context data for html templates
        context = super(InternalReviewAmendments, self).get_context_data(**kwargs)
        context['initial_draft_ref'] = ExamInitialDraft.objects.get(related_exam_paper=self.kwargs['exam_paper_ref'])
        return context

    # override form_valid
    def form_valid(self, form):
        # stops form being saved initially
        InternalReviewAmendmentsForm.instance = form.save(commit=False)

        # updates paper_creation_stage and applies date of submission to exam_paper
        ExamPaper.objects.filter(pk=self.kwargs['exam_paper_ref']).update(
            paper_creation_stage='VETTING_COMMITTEE', submission_internal_review_amendments=datetime.date.today())
        # calls base form_valid
        return super(InternalReviewAmendments, self).form_valid(form)


class VettingCommittee(LoginRequiredMixin, CreateView):
    form_class = VettingCommitteeForm
    template_name = 'exam_papers/create_vetting_committee_review.html'
    context_object_name = 'vetting_ref'

    def get_success_url(self):
        return reverse('exam_paper:exam-paper-overview', kwargs={'exam_paper_ref': self.object.related_exam_paper.pk})

    def get_form_kwargs(self):
        # responses for Http404 raise
        error_response = "Only Vetting Committee of team can submit the Vetting Committee Review"
        error_wrong_stage_requested = "Vetting Committee review cannot be submitted at this stage"
        try:

            # Gets related exam_paper object then verifies user is vetting committee for the team
            exam_paper_instance = ExamPaper.objects.get(pk=self.kwargs['exam_paper_ref'])
            if exam_paper_instance.paper_team.vetting_committee == self.request.user:

                # checks
                if exam_paper_instance.paper_creation_stage == 'VETTING_COMMITTEE':

                    # call default get_form_kwargs and return
                    kwargs = super(VettingCommittee, self).get_form_kwargs()
                    return kwargs
                else:
                    raise Http404("%s" % error_wrong_stage_requested)

            else:
                # raise error if user is not exam setter of relevant team
                raise Http404("%s" % error_response)

        # raise error if object does not exist
        except ObjectDoesNotExist:
            raise Http404("%s" % error_response)

    def get_context_data(self, **kwargs):
        # Get context data for html templates
        context = super(VettingCommittee, self).get_context_data(**kwargs)

        # adding additional context for template
        context['initial_draft_ref'] = ExamInitialDraft.objects.get(related_exam_paper=self.kwargs['exam_paper_ref'])
        context['internal_review_ref'] = ExamInternalReview.objects.get(related_exam_paper=self.kwargs['exam_paper_ref']
                                                                        )
        return context

    def form_valid(self, form):
        # stops form being saved initially
        VettingCommitteeForm.instance = form.save(commit=False)

        # sets FK to exam_paper, updates paper_creation_stage and submission date n exam_paper. Returns base form_valid
        VettingCommitteeForm.instance.related_exam_paper = ExamPaper.objects.get(pk=self.kwargs['exam_paper_ref'])
        ExamPaper.objects.filter(pk=self.kwargs['exam_paper_ref']).update(
            paper_creation_stage='VETTING_COMMITTEE_COMPLETE',
            submission_vetting_committee_response=datetime.date.today())
        return super(VettingCommittee, self).form_valid(form)


class VettingCommitteeAmendments(LoginRequiredMixin, UpdateView):
    form_class = VettingCommitteeAmendmentsForm
    template_name = 'exam_papers/vetting_committee_amendments.html'
    context_object_name = 'vetting_ref'

    # redirect to exam paper overview screen upon creation of initial draft object instance
    def get_success_url(self):
        return reverse('exam_paper:exam-paper-overview', kwargs={'exam_paper_ref': self.object.related_exam_paper.pk})

    # Gets relevant exam_internal_review object and applies additional user verification
    def get_object(self, **kwargs):
        error_response = "Only the exam setter for the paper can complete a response to the Vetting Committee"
        error_amendments_already_submitted = "Amendments to the Vetting Committee response cannot be submitted at " \
                                             "this stage"

        # attempts to access exam paper object using pk id passed in url, raises Http404
        try:
            exam_paper_instance = ExamPaper.objects.get(id=self.kwargs['exam_paper_ref'])

            # verify user is relevant exam_setter, then get and returns instance if at internal_review_complete stage
            if verify_user_exam_setter(self, exam_paper_instance):
                if exam_paper_instance.paper_creation_stage == 'VETTING_COMMITTEE_COMPLETE':
                    vetting_object = ExamVettingCommittee.objects.get(related_exam_paper=self.kwargs['exam_paper_ref'])
                    return vetting_object
                else:
                    # if present exam paper stage isn't internal_review_complete, give error that its already submitted
                    raise Http404("%s" % error_amendments_already_submitted)
            # invalid user, return error
            else:
                raise Http404("%s" % error_response)
        # return error if object doesnt exist
        except ObjectDoesNotExist:
            raise Http404("%s" % error_response)

    def get_context_data(self, **kwargs):
        # Get context data for html templates
        context = super(VettingCommitteeAmendments, self).get_context_data(**kwargs)
        context['initial_draft_ref'] = ExamInitialDraft.objects.get(
            related_exam_paper=self.kwargs['exam_paper_ref'])
        context['internal_review_ref'] = ExamInternalReview.objects.get(
            related_exam_paper=self.kwargs['exam_paper_ref'])
        return context

    # override form_valid
    def form_valid(self, form):
        # stops form being saved initially
        VettingCommitteeAmendmentsForm.instance = form.save(commit=False)

        # updates paper_creation_stage and applies date of submission to exam_paper
        ExamPaper.objects.filter(pk=self.kwargs['exam_paper_ref']).update(
            paper_creation_stage='EXTERNAL_REVIEW', submission_vetting_committee_amendments=datetime.date.today())
        # calls base form_valid
        return super(VettingCommitteeAmendments, self).form_valid(form)


# View for creating the External Review
class CreateExternalReview(LoginRequiredMixin, CreateView):

    form_class = CreateExternalReviewForm
    template_name = 'exam_papers/create_external_review.html'
    context_object_name = 'external_review_ref'

    # redirect to exam paper overview screen upon creation of object instance
    def get_success_url(self):
        return reverse('exam_paper:exam-paper-overview', kwargs={'exam_paper_ref': self.object.related_exam_paper.pk})

    # Setting context data for template
    def get_context_data(self, **kwargs):
        # Getting past stages and setting context
        context = super(CreateExternalReview, self).get_context_data(**kwargs)
        context['initial'] = ExamInitialDraft.objects.get(
            related_exam_paper=self.kwargs['exam_paper_ref'])
        context['internal'] = ExamInternalReview.objects.get(
            related_exam_paper=self.kwargs['exam_paper_ref'])
        context['vetting'] = ExamVettingCommittee.objects.get(
            related_exam_paper=self.kwargs['exam_paper_ref'])
        return context

    # override default get_form_kwargs
    def get_form_kwargs(self):

        # responses for Http404 raise
        error_response = "Only the External Examiner of team can submit the External Review"
        error_wrong_stage_requested = "External Review cannot be submitted at this stage"
        try:

            # Gets related exam_paper object then verifies user is the exam setter for the team
            exam_paper_instance = ExamPaper.objects.get(pk=self.kwargs['exam_paper_ref'])
            if exam_paper_instance.paper_team.external_examiner == self.request.user:

                # checks
                if exam_paper_instance.paper_creation_stage == 'EXTERNAL_REVIEW':

                    # call default get_form_kwargs and return
                    kwargs = super(CreateExternalReview, self).get_form_kwargs()
                    return kwargs
                else:
                    raise Http404("%s" % error_wrong_stage_requested)

            else:
                # raise error if user is not exam setter of relevant team
                raise Http404("%s" % error_response)

        # raise error if object does not exist
        except ObjectDoesNotExist:
            raise Http404("%s" % error_response)

    # overrides default form_valid
    def form_valid(self, form):
        # stops form being submitted initially
        CreateExternalReviewForm.instance = form.save(commit=False)

        # sets ForeignKey to parent exam_paper, updates exam_paper creation stage and submission date
        CreateExternalReviewForm.instance.related_exam_paper = ExamPaper.objects.get(pk=self.kwargs['exam_paper_ref'])
        ExamPaper.objects.filter(pk=self.kwargs['exam_paper_ref']).update(
            paper_creation_stage='EXTERNAL_REVIEW_COMPLETE', submission_external_review_response=datetime.date.today()
        )
        # calls base form_valid
        return super(CreateExternalReview, self).form_valid(form)


# View for exam_setters response to external review
class ExternalReviewAmendments(LoginRequiredMixin, UpdateView):
    form_class = ExternalReviewAmendmentsForm
    template_name = 'exam_papers/external_review_amendments.html'
    context_object_name = 'external'

    # redirect to exam paper overview screen upon creation of initial draft object instance
    def get_success_url(self):
        return reverse('exam_paper:exam-paper-overview', kwargs={'exam_paper_ref': self.object.related_exam_paper.pk})

    # Gets relevant exam_internal_review object and applies additional user verification
    def get_object(self, **kwargs):
        error_response = "Only the exam setter for the paper can complete a response to the External Review"
        error_amendments_already_submitted = "Amendments to the External Review response cannot be submitted at " \
                                             "this stage"

        # attempts to access exam paper object using pk id passed in url, raises Http404
        try:
            exam_paper_instance = ExamPaper.objects.get(id=self.kwargs['exam_paper_ref'])

            # verify user is relevant exam_setter, then get and returns instance if at internal_review_complete stage
            if verify_user_exam_setter(self, exam_paper_instance):
                if exam_paper_instance.paper_creation_stage == 'EXTERNAL_REVIEW_COMPLETE':
                    external_review_object = ExamExternalReview.objects.get(
                        related_exam_paper=self.kwargs['exam_paper_ref'])
                    return external_review_object
                else:
                    # if present exam paper stage isn't internal_review_complete, give error that its already submitted
                    raise Http404("%s" % error_amendments_already_submitted)
            # invalid user, return error
            else:
                raise Http404("%s" % error_response)
        # return error if object doesnt exist
        except ObjectDoesNotExist:
            raise Http404("%s" % error_response)

    def get_context_data(self, **kwargs):
        # Get context data for html templates
        context = super(ExternalReviewAmendments, self).get_context_data(**kwargs)
        context['initial'] = ExamInitialDraft.objects.get(
            related_exam_paper=self.kwargs['exam_paper_ref'])
        context['internal'] = ExamInternalReview.objects.get(
            related_exam_paper=self.kwargs['exam_paper_ref'])
        context['vetting'] = ExamVettingCommittee.objects.get(
            related_exam_paper=self.kwargs['exam_paper_ref'])
        return context

    # override form_valid
    def form_valid(self, form):
        # stops form being saved initially
        ExternalReviewAmendmentsForm.instance = form.save(commit=False)

        # updates paper_creation_stage and applies date of submission to exam_paper
        ExamPaper.objects.filter(pk=self.kwargs['exam_paper_ref']).update(
            paper_creation_stage='PAPER_FINALISED', submission_school_office=datetime.date.today())
        # calls base form_valid
        return super(ExternalReviewAmendments, self).form_valid(form)


# View for creating the Exam Marker Report
class CreateExamMarkerReport(LoginRequiredMixin, CreateView):
    form_class = CreateExamMarkerReportForm
    template_name = 'exam_papers/create_exam_marker_report.html'
    context_object_name = 'exam_marker_ref'

    # redirect to exam paper overview screen upon creation of object instance
    def get_success_url(self):
        return reverse('exam_paper:exam-paper-overview', kwargs={'exam_paper_ref': self.object.related_exam_paper.pk})

    # Setting context data for template
    def get_context_data(self, **kwargs):
        context = super(CreateExamMarkerReport, self).get_context_data(**kwargs)

        exam_paper = ExamPaper.objects.get(pk=self.kwargs['exam_paper_ref'])
        paper_stage = creation_stage_numeric(exam_paper)

        # adding additional context for template
        context['paper_stage'] = paper_stage
        context['vetting_review_ref'] = ExamVettingCommittee.objects.get(
            related_exam_paper=self.kwargs['exam_paper_ref'])
        return context

    # override default get_form_kwargs
    def get_form_kwargs(self):

        # responses for Http404 raise
        error_response = "Only the Exam Setter of team can submit the Exam Markers Report"
        error_wrong_stage_requested = "Exam Marker Report can not be submitted at this stage"
        try:

            # Gets related exam_paper object then verifies user is the exam setter for the team
            exam_paper_instance = ExamPaper.objects.get(pk=self.kwargs['exam_paper_ref'])
            if verify_user_exam_setter(self, exam_paper_instance):
                if exam_paper_instance.paper_creation_stage == 'PAPER_FINALISED':
                    kwargs = super(CreateExamMarkerReport, self).get_form_kwargs()
                    return kwargs
                else:
                    # if present exam paper stage isn't internal_review_complete, give error that its already submitted
                    raise Http404("%s" % error_wrong_stage_requested)
            # invalid user, return error
            else:
                raise Http404("%s" % error_response)

            # return error if object doesnt exist
        except ObjectDoesNotExist:
            raise Http404("%s" % error_response)

    # overrides default form_valid
    def form_valid(self, form):
        # stops form being submitted initially
        CreateExamMarkerReportForm.instance = form.save(commit=False)

        exam_obj = ExamPaper.objects.get(pk=self.kwargs['exam_paper_ref'])

        # Automatically filling fields in addition to the ones user completes in corresponding form to write to db
        CreateExamMarkerReportForm.instance.related_exam_paper = exam_obj
        CreateExamMarkerReportForm.instance.module_code_and_name = exam_obj.module_exam
        CreateExamMarkerReportForm.instance.report_completed_by = self.request.user

        ExamPaper.objects.filter(pk=self.kwargs['exam_paper_ref']).update(
            paper_creation_stage='EXAM_REPORT', submission_exam_marker_report=datetime.date.today()
        )
        # calls base form_valid
        return super(CreateExamMarkerReport, self).form_valid(form)


# View for submitting the module moderators report
class CreateModuleModeratorReport(LoginRequiredMixin, CreateView):
    form_class = CreateModuleModeratorReportForm
    template_name = 'exam_papers/create_module_moderator_report.html'
    context_object_name = 'moderator_ref'

    # redirect to exam paper overview screen upon creation of object instance
    def get_success_url(self):
        return reverse('exam_paper:exam-paper-overview', kwargs={'exam_paper_ref': self.object.related_exam_paper.pk})

    # Setting context data for template
    '''
    def get_context_data(self, **kwargs):
        # Get academic papers for team the sort by academic year of the paper and its module
        context = super(ModuleModeratorReport, self).get_context_data(**kwargs)
        context['vetting_review_ref'] = ExamVettingCommittee.objects.get(
            related_exam_paper=self.kwargs['exam_paper_ref'])
        return context
    '''

    # override default get_form_kwargs
    def get_form_kwargs(self):

        # responses for Http404 raise
        error_response = "Only the Internal Reviewer of team can submit the Module Moderator Report"
        error_wrong_stage_requested = "Module Moderator Report can not be submitted at this stage"
        try:

            # Gets related exam_paper object then verifies user is the internal reviewer for the team
            exam_paper_instance = ExamPaper.objects.get(pk=self.kwargs['exam_paper_ref'])
            if verify_user_internal_reviewer(self, exam_paper_instance):
                if exam_paper_instance.paper_creation_stage == 'EXAM_REPORT':
                    kwargs = super(CreateModuleModeratorReport, self).get_form_kwargs()
                    return kwargs
                else:
                    # if present exam paper stage isn't internal_review_complete, give error that its already submitted
                    raise Http404("%s" % error_wrong_stage_requested)
            # invalid user, return error
            else:
                raise Http404("%s" % error_response)

            # return error if object doesnt exist
        except ObjectDoesNotExist:
            raise Http404("%s" % error_response)

    # overrides default form_valid
    def form_valid(self, form):
        # stops form being submitted initially
        CreateModuleModeratorReportForm.instance = form.save(commit=False)

        exam_obj = ExamPaper.objects.get(pk=self.kwargs['exam_paper_ref'])

        # Automatically filling fields in addition to the ones user completes in corresponding form to write to db
        CreateModuleModeratorReportForm.instance.related_exam_paper = exam_obj
        CreateModuleModeratorReportForm.instance.module_code_and_name = exam_obj.module_exam
        CreateModuleModeratorReportForm.instance.exam_paper_type = exam_obj.exam_paper_type
        CreateModuleModeratorReportForm.instance.module_moderator = self.request.user
        CreateModuleModeratorReportForm.instance.module_coordinator = exam_obj.paper_team.internal_reviewer

        ExamPaper.objects.filter(pk=self.kwargs['exam_paper_ref']).update(
            paper_creation_stage='REPORTS_COMPLETED', submission_moderator_report=datetime.date.today()
        )
        # calls base form_valid
        return super(CreateModuleModeratorReport, self).form_valid(form)

