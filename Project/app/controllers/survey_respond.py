import time

from flask import Blueprint, redirect, url_for, request, render_template, flash
from flask_login import login_required, current_user

from app import db as DB
from app.classes.survey import Survey
from app.classes.response import Response
from app.classes.surveyQuestion import SurveyQuestion
from app.classes.option import Option
from app.classes.completion import Completion
from app.classes.enrolment import Enrolment
from app.classes.user import User

survey_respond_blueprint = Blueprint('survey_respond', __name__)

# respond survey link
@survey_respond_blueprint.route('/survey/respond/<id>', methods=['GET', 'POST'])
@login_required
def survey_respond(id):
    # Checks if user has done survey
    if Completion.query.filter_by(user_id = current_user.id, survey_id = id).first() == None:
        survey = Survey.query.filter(Survey.id == id).first()
        # Only shows if survey exists and user is allowed to answer
        if survey:
            if survey.phase != 'open':
                flash(u"Survey not open", 'error')
                return redirect(url_for('index.index'))                                
            if Enrolment.query.filter_by(offering_id = survey.offering_id, user_id = current_user.id).all():
                if current_user.staff:
                    flash(u"Survey offering associated with logged-in staff", 'error')
                    return redirect(url_for('index.index'))
            else:
                if not current_user.staff and not current_user.admin:
                    flash(u"Survey offering not associated with logged-in student", 'error')
                    return redirect(url_for('index.index'))

            if request.method == "POST":
                # Creates responses for each quesion of the survey
                for key, value in request.form.items():
                    if value:
                        # response[key[9:]] = value
                        question = survey.questions.filter(SurveyQuestion.number == key[9:]).first()
                        if question.type == 'TXT':
                            response = Response(value, question.id)
                        elif question.type == 'MCQ':
                            option = question.options.filter(Option.id == value).first()
                            if option is None:
                                continue
                            response = Response(option.option, question.id, option.id)

                        try:
                            survey_question = SurveyQuestion.query.filter_by(id = question.id).first()
                            survey_question.add_response(response)
                        except ValueError:
                            raise ValueError
                
                try:
                    completion = Completion(current_user.id, survey.id)
                    user = User.query.filter_by(_id = current_user.id).first()
                    user.add_completion(completion)
                except ValueError:
                    raise ValueError

                DB.session.commit()

                flash(u'Survey successfully completed', 'done')
                return redirect(url_for('index.index'))
            return render_template('survey-respond.html', survey=survey)
        else:
            flash(u"respond link for survey invalid", 'error')
            return redirect(url_for('index.index'))
    else:
        flash(u"Survey already completed", 'error')
    return redirect(url_for('index.index'))