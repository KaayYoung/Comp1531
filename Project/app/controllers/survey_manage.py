from flask import Blueprint, redirect, url_for, request, render_template, flash
from flask_login import login_required, current_user

from app import db as DB
from app.classes.survey import Survey
from app.classes.course import Course
from app.classes.offering import Offering
from app.classes.surveyQuestionMCQ import SurveyQuestionMCQ

survey_manage_blueprint = Blueprint('survey_manage', __name__)

# Displays list of surveys
@survey_manage_blueprint.route('/survey/manage/', methods=['GET', 'POST'])
@login_required
def survey_manage():    
    if not current_user.admin:
        flash(u"Admin access only", 'error')
        return redirect(url_for('index.index'))

    return redirect(url_for('index.index'))

    if request.method == "POST":
        if 'survey-to-delete' in request.form:
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
        elif 'survey-to-respond' in request.form:
            to_respond = request.form.get("survey-to-respond")
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

    return render_template('survey-manage.html', courses=Course.query.all(), surveys=Survey.query.all())
    