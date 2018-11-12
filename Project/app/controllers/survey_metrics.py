from flask import Blueprint, redirect, url_for, request, render_template, flash
from flask_login import login_required, current_user

# from app.utils import db_handler as DB
from app.classes.survey import Survey, Phase

survey_metrics_blueprint = Blueprint('survey_metrics', __name__)

# Displays selected survey
@survey_metrics_blueprint.route('/metrics/<course>/<offering>/<id>', methods=['GET', 'POST'])
@login_required
def survey_metrics(course, offering, id):
    #survey_questions = query_obj.get_all_questions_of_a_survey(course, offering)
    #survey = DB.surveys[id]
    #return str(survey.title)
    survey = Survey.query.filter(Survey.id == id).first()
    if not survey:
        flash(u"Survey does not exist", 'error')
        return redirect(url_for('index.index'))
    # Checks permissions - if not admin, needs to be closed before viewing results
    if not current_user.admin and survey.phase != Phase.closed:
        flash(u"Survey is not closed yet", 'error')
        return redirect(url_for('index.index'))

    responses = {}
    for question in survey.questions:
        if question.responses:
            responses[question.id] = {}
            for response in question.responses:
                if response.response not in responses[question.id]:
                    responses[question.id][response.response] = 1
                else:
                    responses[question.id][response.response] += 1

    return render_template('survey-metrics.html', survey=survey, responses=responses)
