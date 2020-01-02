from django import forms
from datetime import timedelta, date
import datetime

from .models import SubmissionDeadlines, ModuleDetail
from .custom_methods import validate_deadlines


# custom form for adding Submission Deadlines
class SubmissionDeadlineForm(forms.ModelForm):

    class Meta:
        model = SubmissionDeadlines
        fields = '__all__'

        # displays text to user when they are creating Submission Deadlines
        help_texts = {
            'name': '<b>Required:</b>, name of deadline',
            'academic_start_year': '<b>Required:</b> format yyyy',
            'initial_draft_submission': '<b>Required:</b> format dd/mm/yyyy',
            'internal_review_response': '<b>Required:</b> format dd/mm/yyyy',
            'internal_review_amendments': '<b>Required:</b> format dd/mm/yyyy',
            'vetting_committee_response': '<b>Required:</b> format dd/mm/yyyy',
            'vetting_committee_amendments': '<b>Required:</b> format dd/mm/yyyy',
            'external_review_response': '<b>Required:</b> format dd/mm/yyyy',
            'school_office_submission': '<b>Required:</b> format dd/mm/yyyy',
        }

    # override base clean method
    def clean(self):
        # Applying base clean method prior to applying additional clean method
        cleaned_data = super(SubmissionDeadlineForm, self).clean()

        # declare variables to contain cleaned data which custom clean methods will be applied to
        academic_start_year = cleaned_data.get('academic_start_year')
        initial_draft_submission = cleaned_data.get('initial_draft_submission')
        internal_review_response = cleaned_data.get('internal_review_response')
        internal_review_amendments = cleaned_data.get('internal_review_amendments')
        vetting_committee_response = cleaned_data.get('vetting_committee_response')
        vetting_committee_amendments = cleaned_data.get('vetting_committee_amendments')
        external_review_response = cleaned_data.get('external_review_response')
        school_office_submission = cleaned_data.get('school_office_submission')

        # setting date variables and minimum days between deadlines
        academic_input_converted = date(day=int(1), month=int(1), year=int(academic_start_year))
        today = date.today()
        min_days_between = 2

        error_date_nonexistent = "Inputted date does not exist"

        # clean academic_start_year input
        if academic_input_converted.year < today.year-1:
            raise forms.ValidationError({'academic_start_year': ["Academic Start Year cannot be more than 1 year in "
                                                                 "the past"]
                                         })
        elif academic_input_converted.year > today.year+5:
            raise forms.ValidationError({'academic_start_year': ["Academic start year cannot be more than 5 years "
                                                                 "later than the present year"]
                                         })

        # clean initial_draft_deadline input
        if initial_draft_submission is None:
            raise forms.ValidationError({'initial_draft_submission': ["%s" % error_date_nonexistent]
                                         })
        elif initial_draft_submission < academic_input_converted:
            raise forms.ValidationError({'initial_draft_submission': ["Initial Draft deadline cannot be earlier than "
                                                                      "the Academic Start Year"]
                                         })
        elif initial_draft_submission < today + timedelta(days=min_days_between):
            raise forms.ValidationError({'initial_draft_submission': ["Initial Draft deadline must be at least %s days "
                                                                      "later than today" % min_days_between]
                                         })
        elif initial_draft_submission > datetime.date(day=1, month=6, year=int(academic_start_year+1)):
            raise forms.ValidationError({'initial_draft_submission': ["Initial Draft deadline cannot be later than 1st "
                                                                      "June %s"
                                                                      % str(academic_start_year+1)]
                                         })

        internal_response_validate = validate_deadlines(internal_review_response, initial_draft_submission,
                                                        academic_input_converted, min_days_between)
        if internal_response_validate == 1:
            raise forms.ValidationError({'internal_review_response': ["%s" % error_date_nonexistent]
                                         })
        elif internal_response_validate == 2:
            raise forms.ValidationError({'internal_review_response': ["Internal Review Amendments deadline must be at "
                                                                      "least %s days later than the Internal Review"
                                                                      % min_days_between]
                                         })
        elif internal_response_validate == 3:
            raise forms.ValidationError({'internal_review_response': ["Internal Review deadline cannot be later than "
                                                                      "1st June %s" % str(academic_start_year+1)]
                                         })

        internal_amendments_validate = validate_deadlines(internal_review_amendments, internal_review_response,
                                                          academic_input_converted, min_days_between)
        if internal_amendments_validate == 1:
            raise forms.ValidationError({'internal_review_amendments': ["%s" % error_date_nonexistent]
                                         })
        elif internal_amendments_validate == 2:
            raise forms.ValidationError({'internal_review_amendments': ["Internal Review Amendments deadline must be "
                                                                        "at least %s days later than the Initial Draft"
                                                                        % min_days_between]
                                         })
        elif internal_amendments_validate == 3:
            raise forms.ValidationError({'internal_review_amendments': ["Internal Review Amendments deadline cannot be "
                                                                        "later than 1st June %s"
                                                                        % str(academic_start_year+1)]
                                         })

        vetting_response_validate = validate_deadlines(vetting_committee_response, internal_review_amendments,
                                                       academic_input_converted, min_days_between)
        if vetting_response_validate == 1:
            raise forms.ValidationError({'vetting_committee_response': ["%s" % error_date_nonexistent]
                                         })
        elif vetting_response_validate == 2:
            raise forms.ValidationError({'vetting_committee_response': ["Vetting Committee Response deadline must be "
                                                                        "at least %s days later than Internal Review "
                                                                        "Amendments" % min_days_between]
                                         })
        elif vetting_response_validate == 3:
            raise forms.ValidationError({'vetting_committee_response': ["Vetting Committee Response deadline cannot be "
                                                                        "later than 1st June %s"
                                                                        % str(academic_start_year+1)]
                                         })

        vetting_amendments_validate = validate_deadlines(vetting_committee_amendments, vetting_committee_response,
                                                         academic_input_converted, min_days_between)
        if vetting_amendments_validate == 1:
            raise forms.ValidationError({'vetting_committee_amendments': ["%s" % error_date_nonexistent]
                                         })
        elif vetting_amendments_validate == 2:
            raise forms.ValidationError({'vetting_committee_amendments': ["Vetting Committee Amendments deadline must "
                                                                          "be at least %s days later than the Vetting "
                                                                          "Committee" % min_days_between]
                                         })
        elif vetting_amendments_validate == 3:
            raise forms.ValidationError({'vetting_committee_amendments': ["Vetting Committee Amendments deadline "
                                                                          "cannot be later than 1st June %s"
                                                                          % str(academic_start_year+1)]
                                         })

        external_response_validate = validate_deadlines(external_review_response, vetting_committee_amendments,
                                                        academic_input_converted, min_days_between)
        if external_response_validate == 1:
            raise forms.ValidationError({'external_review_response': ["%s" % error_date_nonexistent]
                                         })
        elif external_response_validate == 2:
            raise forms.ValidationError({'external_review_response': ["External Review Response deadline must be at "
                                                                      "least %s days later than Vetting Committee "
                                                                      "Amendments" % min_days_between]
                                         })
        elif external_response_validate == 3:
            raise forms.ValidationError({'external_review_response': ["External Review Response deadline cannot be "
                                                                      "later than 1st June %s"
                                                                      % str(academic_start_year+1)]
                                         })

        school_office_validate = validate_deadlines(school_office_submission, external_review_response,
                                                    academic_input_converted, min_days_between)
        if school_office_validate == 1:
            raise forms.ValidationError({'school_office_submission': ["%s" % error_date_nonexistent]
                                         })
        if school_office_validate == 2:
            raise forms.ValidationError({'school_office_submission': ["School Office Submission deadline must be at "
                                                                      "least %s days later than the External Review"
                                                                      % min_days_between]
                                         })
        elif school_office_validate == 3:
            raise forms.ValidationError({'school_office_submission': ["School Office Submission deadline cannot be "
                                                                      "later than 1st June %s"
                                                                      % str(academic_start_year+1)]
                                         })
        # return cleaned data which will be saved to database
        return cleaned_data


# Form for Module Details
class ModuleDetailsForm(forms.ModelForm):

    class Meta:
        model = ModuleDetail

        exclude = ('active',)
