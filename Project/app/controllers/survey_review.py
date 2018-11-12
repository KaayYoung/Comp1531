from flask import Blueprint, redirect, url_for, request, render_template, flash
from flask_login import login_required, current_user
from datetime import datetime

from app import db as DB

from app.classes.survey import Survey
from app.classes.course import Course
from app.classes.offering import Offering
from app.classes.question import Question
from app.classes.surveyQuestion import SurveyQuestion, QuestionType
from app.classes.surveyQuestionMCQ import SurveyQuestionMCQ
from app.classes.surveyQuestionTXT import SurveyQuestionTXT
from app.classes.option import Option

survey_review_blueprint = Blueprint('survey_review', __name__)

question_types = {'TXT':'Text based', 'MCQ':'Multiple choice'}

# Displays selected survey
@survey_review_blueprint.route('/survey/review/<course>/<offering>/<id>', methods=['GET', 'POST'])
@login_required
def survey_review(course, offering, id):
    if not current_user.staff and not current_user.admin:
        flash(u"Admin or staff access only", 'error')
        return redirect(url_for('index.index'))
    survey = Survey.query.filter_by(id = id).first()
    if survey:
        if survey.phase != "review":
            flash(u"Survey not for review", 'error')
            return redirect(url_for('index.index'))
    else:
        flash(u"Invalid survey", 'error')
        return redirect(url_for('index.index'))
    # id is survey id
    if request.method == "POST":
        # try:
        course_name = request.form.get('survey_course')
        semester = request.form.get('survey_offering')
        offering = Offering.query.filter_by(course_name = course_name, semester = semester).first()

        # original_survey_questions = survey.questions.all()
        # for sq in original_survey_questions:
        #     Option.query.filter_by(survey_question_id = sq.id).delete()
        #     SurveyQuestion.query.filter_by(id = sq.id).delete()
        # del(survey.questions)

        # delete unchecked prior questions
        prior_questions_to_keep = request.form.getlist('question_from_before')
        prior_questions_to_delete = []
        for sq in survey.questions:
            checked = False
            for question_obj in prior_questions_to_keep:
                question_contents = question_obj.split("-")
                question_key = question_contents[0]
                question_text = question_contents[1]

                if sq.id == int(question_key):
                    checked = True
            if not checked:
                prior_questions_to_delete.append(sq.id)

        for sq_id in prior_questions_to_delete:
            survey.remove_survey_question(sq_id)

        survey.phase = "open"
        start_index_for_new = len(prior_questions_to_keep) - len(prior_questions_to_delete)
        for question_index, question_obj in enumerate(request.form.getlist('question')):
            question_contents = question_obj.split("-")
            question_key = question_contents[0]
            #question_text = question_contents[1]

            question_type = None
            for type_index, question_type_key in enumerate(request.form.getlist('question_type')):
                question_type_contents = question_type_key.split('-')
                if question_key == question_type_contents[0]:
                    question_type = question_type_contents[1]
                    break

            corresponding_question = Question.query.filter(Question.id == question_key).first()
            question_text = corresponding_question.question
            question_is_mandatory = corresponding_question.mandatory

            question_number = question_index + start_index_for_new
            if question_type == QuestionType.MCQ:
                survey_question = SurveyQuestionMCQ(question_text, question_number, question_is_mandatory, survey.id)
            elif question_type == QuestionType.TXT:
                survey_question = SurveyQuestionTXT(question_text, question_number, question_is_mandatory, survey.id)
            try:
                survey.add_survey_question(survey_question)
            except:
                pass

            # survey_question_id = SurveyQuestion.query.filter_by(question = question_text, survey_id = survey.id).first().id
            if question_type == QuestionType.MCQ:
                survey_question.add_options(survey_question.id)

        DB.session.commit()
        flash(u"Survey successfully reviewed", 'done')
        return redirect(url_for('index.index'))
        # except:
        #     flash(u'Survey review encountered an error', 'error')
        #     return redirect(url_for('dashboard.dashboard'))

    # staff should be able to review the survey and add optional questions
    # admins should be able to do the same as staff
    survey = Survey.query.filter_by(id = id).first()
    if survey:
        course = None
        offering = Offering.query.filter_by(id = survey.offering_id).first()
        course = Course.query.filter_by(name = offering.course_name).first()
        optional_questions = Question.query.filter_by(mandatory = False).all()
        start_date = survey.start_date.strftime("%d %B, %Y")
        end_date = survey.end_date.strftime("%d %B, %Y")
        return render_template('survey-review.html', survey = survey, course = course, offering = offering, questions = optional_questions, question_types=question_types, start_date=start_date, end_date=end_date)
    else:
        flash(u"Public link for survey invalid", 'error')
        return redirect(url_for('index.index'))
    
    return 'not yet implemented'
    