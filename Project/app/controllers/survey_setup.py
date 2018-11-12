from flask import Blueprint, redirect, url_for, request, render_template, flash
from flask_login import login_required, current_user
from app.controllers import survey_manage
from datetime import datetime
from sqlite3 import IntegrityError

from app.classes.survey import Survey
from app.classes.surveyQuestion import SurveyQuestion, QuestionType
from app.classes.surveyQuestionMCQ import SurveyQuestionMCQ
from app.classes.surveyQuestionTXT import SurveyQuestionTXT
from app.classes.question import Question
from app.classes.course import Course
from app.classes.offering import Offering
from app.classes.option import Option
from app import db as DB

survey_setup_blueprint = Blueprint('survey_setup', __name__)

question_types = {'TXT':'Text based', 'MCQ':'Multiple choice'}

# Creates survey
@survey_setup_blueprint.route('/survey/setup/', methods=['GET', 'POST'])
@survey_setup_blueprint.route('/survey/setup/<predetermined_course_name>/<predetermined_course_offering>', methods=['GET', 'POST'])
@login_required
def survey_setup(predetermined_course_name = None, predetermined_course_offering = None):
    if not current_user.admin:
        flash(u"Admin access only", 'error')
        return redirect(url_for('index.index'))
    if request.method == "POST":
        try:
            title = request.form.get('survey_title')
            start_date = datetime.strptime(request.form.get('start_date'), '%d %B, %Y')
            end_date = datetime.strptime(request.form.get('end_date'), '%d %B, %Y')
            course_name = request.form.get('survey_course')
            semester = request.form.get('survey_offering')
            offering = Offering.query.filter_by(course_name = course_name, semester = semester).first()
            
            if offering.get_surveys():
                flash(u'Survey for this offering already exists', 'error')
                return redirect(url_for('index.index'))

            try:
                survey = Survey(title, 'review', start_date, end_date, offering.id)
                offering.add_survey(survey)
            except IntegrityError:
                flash(u'Survey for this course already exists')
                return redirect(url_for('dashboard.dashboard'))
            else:
                survey_id = Survey.query.filter_by(title = title, offering_id = offering.id).first().id
                for question_index, question_key in enumerate(request.form.getlist('question')):
                    question_type = None
                    for type_index, question_type_key in enumerate(request.form.getlist('question_type')):
                        question_type_contents = question_type_key.split('-')
                        if question_key == question_type_contents[0]:
                            question_type = question_type_contents[1]
                            break

                    corresponding_question = Question.query.filter(Question.id == question_key).first()
                    question_text = corresponding_question.question
                    question_is_mandatory = corresponding_question.mandatory

                    if question_type == QuestionType.MCQ:
                        survey_question = SurveyQuestionMCQ(question_text, question_index, question_is_mandatory, survey_id)
                    elif question_type == QuestionType.TXT:
                        survey_question = SurveyQuestionTXT(question_text, question_index, question_is_mandatory, survey_id)

                    try:
                        survey.add_survey_question(survey_question)
                    except ValueError:
                        raise ValueError("Error adding Survey question", ValueError)

                    survey_question_id = SurveyQuestion.query.filter_by(question = question_text, survey_id = survey_id).first().id
                    if question_type == QuestionType.MCQ:
                        try:
                            survey_question.add_options(survey_question_id)
                        except ValueError:
                            raise ValueError("Error Adding Survey Question options", ValueError)
                    
                DB.session.commit()

                flash(u'Survey created', 'done')
                return redirect(url_for('dashboard.dashboard'))
        except ValueError:
            flash(u'Survey creation encountered an error')
            return render_setup(predetermined_course_name, predetermined_course_offering)
                
    else:
        return render_setup(predetermined_course_name, predetermined_course_offering)

def render_setup(predetermined_course_name, predetermined_course_offering):
    offerings = {}
    for course in Course.query.all():
        offerings[course.name] = []
        for offering in course.offerings:
            offerings[course.name].append(offering.semester)

    questions = Question.query.all()
    if len(questions) == 0:
        return redirect(url_for('questions.questions'))

    return render_template('survey-setup.html', questions=questions, courses=Course.query.all(), offerings=offerings, question_types=question_types, predetermined_course_name = predetermined_course_name, predetermined_course_offering = predetermined_course_offering)

