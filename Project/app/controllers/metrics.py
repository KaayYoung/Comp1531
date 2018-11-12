from flask import Blueprint, redirect, url_for, request, render_template
from flask_login import login_required, current_user

from app import db as DB
from app.classes.survey import Survey
from app.classes.course import Course
from app.classes.enrolment import Enrolment
from app.classes.offering import Offering

metrics_blueprint = Blueprint('metrics', __name__)

# Displays list of surveys
@metrics_blueprint.route('/metrics/', methods=['GET', 'POST'])
@login_required
def metrics():
    if request.method == "POST":
        if 'survey-to-delete' in request.form:
            to_delete = request.form.get("survey-to-delete")
            survey = Survey.query.filter(Survey.id == to_delete).first()
            if survey:
                try:
                    offering = Offering.query.filter_by(id = survey.offering_id).first()
                    offering.delete_survey(survey.id)
                except:
                    pass
        elif 'survey-to-respond' in request.form:
            to_respond = request.form.get("survey-to-respond")

    # get all the courses the user is enrolled in 
    enrolment_ids = list(set(enrolment.offering_id for enrolment in current_user.enrolments))
    offerings = current_user.enrolled_offerings
    offerings_names = list(offering.course_name for offering in offerings)
    courses = current_user.enrolled_courses

    return render_template('metrics.html', courses=courses, enrolment=enrolment_ids, surveys=Survey.query.all())

