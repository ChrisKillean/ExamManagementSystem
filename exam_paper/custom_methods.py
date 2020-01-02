import datetime


# compares submission date to deadlines and returns appropriate response to populate context
def work_progress(deadline, submission):
    # assesses if stage has been submitted
    if submission is None:
        if deadline < datetime.date.today():
            return 'overdue'
        else:
            return 'fine'

    elif deadline < submission:
        return 'submitted late'
    else:
        return 'on time'


# Confirms if report object has been submitted
def report_progress(submission):
    # assesses if stage has been submitted
    if submission is None:
        return False
    else:
        return True


def creation_stage_numeric(exam_obj):

    if exam_obj.paper_creation_stage == 'REPORTS_COMPLETED':
        return 10
    elif exam_obj.paper_creation_stage == 'EXAM_REPORT':
        return 9
    elif exam_obj.paper_creation_stage == 'PAPER_FINALISED':
        return 8
    elif exam_obj.paper_creation_stage == 'EXTERNAL_REVIEW_COMPLETE':
        return 7
    elif exam_obj.paper_creation_stage == 'EXTERNAL_REVIEW':
        return 6
    elif exam_obj.paper_creation_stage == 'VETTING_COMMITTEE_COMPLETE':
        return 5
    elif exam_obj.paper_creation_stage == 'VETTING_COMMITTEE':
        return 4
    elif exam_obj.paper_creation_stage == 'INTERNAL_REVIEW_COMPLETE':
        return 3
    elif exam_obj.paper_creation_stage == 'INTERNAL_REVIEW':
        return 2
    else:
        return 1
