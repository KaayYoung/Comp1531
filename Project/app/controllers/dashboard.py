from datetime import datetime
from flask import Blueprint, redirect, url_for, request, render_template, flash
from flask_login import login_required, current_user

from sqlalchemy.orm import load_only

from app.classes.guest import Guest
from app.classes.survey import Survey
from app.classes.surveyQuestionMCQ import SurveyQuestionMCQ
from app.classes.enrolment import Enrolment
from app.classes.offering import Offering
from app import db as DB

dashboard_blueprint = Blueprint('dashboard', __name__)

# Helpers
def filter_survey(user, survey, type):
    current = datetime.now()
    start = survey.start_date
    end = survey.end_date

    if type is "review":
        # If staff, tries to find survey in the offering that's in review stage
        return (survey.phase == "review")
    elif (type is "open" and user.admin) or type is "open" and (start < current and end > current):
        # If user/admin, tries to find survey in the offering that's in open stage + not completed
        return ((survey.phase == "open") and not user.has_completed(survey)) or ((survey.phase == "open") and user.admin)
    elif type is "closed":
        # Tries to find survey in the offering that's in closed stage
        return (survey.phase == "closed")
    else:
        return None

@dashboard_blueprint.route('/dashboard/', methods=['GET', 'POST'])
@login_required
def dashboard():
    # here do a check on surveys => check for expired ones and make then closed 
    current = datetime.now()
    all_surveys = Survey.query.filter(Survey.end_date <= current).all()
    for survey in all_surveys:
        survey.phase = 'closed'
    DB.session.commit()

    if request.method == "POST":
        if current_user.admin:
            if 'user-to-delete' in request.form:
                to_delete = request.form.get("user-to-delete")
                DB.remove_user(to_delete)
                if to_delete == current_user.id:
                    flash(u'Logged in user deleted', 'error')
                    return redirect(url_for('login.logout'))
                else:
                    flash(u'User deleted', 'done')
            elif 'user-to-promote' in request.form:
                to_promote = request.form.get("user-to-promote")
                guest = Guest.query.get(to_promote)

                if guest.active:
                    for enrolment in Enrolment.query.filter_by(user_id = guest.id).all():
                        DB.session.delete(enrolment)
                else:
                    new_enrolment = Enrolment(guest.offering_request, guest.id)
                    offering = Offering.query.filter_by(id = guest.offering_request).first()
                    offering.enrol_user(new_enrolment)

                guest.active = not guest.active
                DB.session.commit()

            elif 'survey-to-delete' in request.form:
                to_delete = request.form.get("survey-to-delete")
                survey = Survey.query.filter(Survey.id == to_delete).first()
                if survey:
                    for completion in survey.completions:
                        DB.session.delete(completion)
                    for question in survey.questions:
                        if isinstance(question, SurveyQuestionMCQ):
                            for option in question.options:
                                DB.session.delete(option)
                        for response in question.responses:
                            DB.session.delete(response)
                        DB.session.delete(question)
                    DB.session.delete(survey)
                    DB.session.commit()
            elif 'survey-permissions' in request.form:
                to_toggle = request.form.get("survey-permissions")
                survey = Survey.query.filter(Survey.id == to_toggle).first()
                if survey is not None:
                    if survey.phase == "open":
                        survey.close_survey()
                        message_str = "closed"
                    else:
                        survey.open_survey()
                        message_str = "opened"
                    flash(u'Survey successfully ' + message_str, 'done')
                    DB.session.commit()
        else:
            flash(u'Unauthorised', 'error')


    sections = []
    if current_user.admin or current_user.staff:
        review_obj = current_user.get_surveys("review", filter_survey)
        sections.append(("Review surveys", review_obj))
    
    if current_user.admin or not current_user.staff:
        open_obj = current_user.get_surveys("open", filter_survey)
        sections.append(("Open surveys", open_obj))

    closed_obj = current_user.get_surveys("closed", filter_survey)
    sections.append(("Closed surveys", closed_obj))

    if current_user.admin:
        template = 'dashboard-admin.html'
    elif current_user.staff:
        template = 'dashboard-staff.html'
    else:
        template = 'dashboard-student.html'

    return render_template(template, sections=sections, guests=Guest.query.all() if current_user.admin else None)

