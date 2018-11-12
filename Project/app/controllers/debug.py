from flask import Blueprint, redirect, url_for, request, render_template, flash
from flask_login import login_required, current_user
from random import randint, choice
import datetime
import html

import config as Config
from app.utils import json_handler as JSON
from app.classes.survey import Survey
from app.classes.surveyQuestion import SurveyQuestion, QuestionType
from app.classes.surveyQuestionMCQ import SurveyQuestionMCQ
from app.classes.surveyQuestionTXT import SurveyQuestionTXT

from app.classes.question import Question
from app.classes.course import Course
from app.classes.offering import Offering
from app.classes.option import Option
from app.classes.response import Response
from app import db as DB

debug_blueprint = Blueprint('debug', __name__)

# Place to store random survey source
dictionary = {}

""" Taken from https://stackoverflow.com/questions/553303/generate-a-random-date-between-two-other-dates/8170651#8170651 """
def random_date(start, end):
    """Generate a random datetime between `start` and `end`"""
    return start + datetime.timedelta(
        # Get a random amount of seconds between `start` and `end`
        seconds=randint(0, int((end - start).total_seconds())),
    )

@debug_blueprint.route('/debug/', methods=['GET', 'POST'])
def debug():
    if not Config.debug_features:
        flash(u'Restart server with flag "-df" for feature', 'error')
        return redirect(request.referrer) if request.referrer else redirect(index.index)

    if request.method == "POST":
        # Sample surveys from https://opentdb.com/api.php?amount=50
        global dictionary
        # Ensures that long load only occurs when needed, once during
        # server life
        if not dictionary:
            dictionary = JSON.load_object('rand_survey_src')

        # Processes requests to generate DB objects
        if 's-lo' in request.form:
            try:
                s_lo = round(float(request.form.get("s-lo")))
                s_hi = round(float(request.form.get("s-hi")))
                q_lo = round(float(request.form.get("q-lo")))
                q_hi = round(float(request.form.get("q-hi")))
                r_lo = round(float(request.form.get("r-lo")))
                r_hi = round(float(request.form.get("r-hi")))
            except ValueError:
                flash(u'Parameters to generate invalid', 'error')
                return render_template('debug.html', surveys=Survey.query.all(), questions=Question.query.all())

            if dictionary:
                # Whether or not to delete existing surveys
                overwrite = request.form.get("overwrite")
                if overwrite:
                    Survey.query.delete()
                    SurveyQuestion.query.delete()
                    SurveyQuestionMCQ.query.delete()
                    SurveyQuestionTXT.query.delete()
                    Option.query.delete()
                    Response.query.delete()
                    DB.session.commit()

                courses_valid = {}
                for course in Course.query.all():
                    # Assumes true, course has no surveys
                    offerings_valid = []
                    for offering in course.offerings.all():
                        if offering.get_surveys():
                            continue
                        else:
                            offerings_valid.append(offering)
                    if offerings_valid:
                        courses_valid[course.name] = offerings_valid

                if not courses_valid:
                    flash('All offerings already have surveys', 'error')
                    return render_template('debug.html', surveys=Survey.query.all(), questions=Question.query.all())
                s_generated = 0
                courses = Course.query.all()
                max_num_s = randint(s_lo,s_hi)
                if max_num_s > len(Offering.query.all()):
                    max_num_s = len(Offering.query.all())
                if max_num_s  <= 1:
                    flash('All offerings already have surveys', 'error')
                    return render_template('debug.html', surveys=Survey.query.all(), questions=Question.query.all())
                s_to_gen = range(0,max_num_s)

                old_percentage = -1
                percentage = 0
                total = len(s_to_gen)
                for s_index in s_to_gen:
                    percentage = round(s_generated/total*100)
                    if percentage != old_percentage:
                        print(str(percentage) + "%                 ", end='\r')
                    s_generated += 1

                    title = html.unescape(dictionary[randint(0,len(dictionary)-1)]['question'])
                    if len(courses_valid.keys()) <= 0:
                        break
                    course = list(courses_valid.keys())[randint(0,len(courses_valid.keys())-1)]
                    offerings = courses_valid[course]
                    offering = offerings[randint(0,len(offerings)-1)]
                    courses_valid[course].remove(offering)
                    if len(offerings) == 0:
                        del courses_valid[course]

                    now = datetime.datetime.now()
                    start_date = now
                    end_date = random_date(now, now + datetime.timedelta(days=2))
                    dice = randint(0,2)
                    if dice == 2:
                        survey_phase = 'closed'
                    elif dice == 1:
                        survey_phase = 'open'
                    else:
                        survey_phase = 'review'
                    try:
                        survey = Survey(title, survey_phase, start_date, end_date, offering.id)
                    except:
                        s_generated -= 1
                        total -= 1
                        continue

                    for q_index in range(0,randint(q_lo,q_hi)):
                        d_index = randint(0,len(dictionary)-1)
                        if randint(0,1) == 1:
                            survey_question = SurveyQuestionMCQ(html.unescape(dictionary[d_index]['question']), q_index, True if randint(0,1) == 1 else False, survey.id)
                        else:
                            survey_question = SurveyQuestionTXT(html.unescape(dictionary[d_index]['question']), q_index, True if randint(0,1) == 1 else False, survey.id)

                        if survey_question.type == QuestionType.MCQ:
                            survey_question.options.append(Option(html.unescape(dictionary[d_index]['correct_answer']), survey.id))
                            for option in dictionary[d_index]['incorrect_answers']:
                                survey_question.options.append(Option(html.unescape(option), survey.id))
                        survey.questions.append(survey_question)

                        # Does random responses if it's generated as closed
                        if survey.phase == 'closed':
                            possible_responses = dictionary[d_index]['incorrect_answers']
                            possible_responses.append(dictionary[d_index]['correct_answer'])
                            # Doubles chance of correct answer being the response
                            possible_responses.append(dictionary[d_index]['correct_answer'])
                            for r_index in range(0,randint(r_lo,r_hi)):
                                survey_question.responses.append(Response(possible_responses[randint(0,len(possible_responses)-1)], survey_question.id))
                    offering.surveys.append(survey)

                    # DB.session.add(survey)
                DB.session.commit()
                flash(str(s_generated) + u' surveys generated', 'done')

        elif 'qp-lo' in request.form:
            qp_lo = round(float(request.form.get("qp-lo")))
            qp_hi = round(float(request.form.get("qp-hi")))

            overwrite = request.form.get("overwrite")
            if overwrite:
                Question.query.delete()
                DB.session.commit()

            if dictionary:
                q_generated = 0
                q_to_gen = range(0,randint(qp_lo,qp_hi))
                total = len(q_to_gen)
                for q_index in q_to_gen:
                    print(str(q_generated/total*100) + "%                 ", end='\r')
                    q_generated += 1
                    try:
                        DB.session.add(Question(html.unescape(dictionary[randint(0,len(dictionary)-1)]['question']), True if randint(0,1) == 1 else False))
                    except:
                        q_generated -= 1
                        total -= 1
                        continue

                DB.session.commit()
                flash(str(q_generated) + u' questions generated', 'done')

        elif 'reset-db' in request.form:
            DB.drop_all()
            DB.create_all()
            DB.load_defaults()
            DB.session.commit()
            flash(u'Database reset', 'done')            

        else:
            flash(u'Unknown command', 'error')

    return render_template('debug.html', surveys=Survey.query.all(), questions=Question.query.all())


# # Test surveys (THIS USES A DIFFERENT METHOD TO ONE ABOVE)
# # Note: this deletes existing surveys
# DB.surveys = {}
# DB.survey_lookup = {}
# from random import randint, choice
# dictionary = DB.load_object('webster_dictionary')
# for s_index in range(0,100):
#     survey = DB.Survey()

#     survey.title = str(dictionary[choice(list(dictionary.keys()))])[:100]
#     # survey.title = DB.gen_id()
#     survey.course = DB.courses[randint(0,len(DB.courses)-1)]
#     survey.offering = DB.offerings[survey.course][randint(0,len(DB.offerings[survey.course])-1)]
#     for q_index in range(0,randint(1,9)):
#         question = DB.Question(q_index)
#         question.question = str(dictionary[choice(list(dictionary.keys()))])#q_index#DB.gen_id()
#         for o_index in range(0,randint(2,6)):
#             question.options.append(str(choice(list(dictionary.keys()))))#DB.gen_id())
#         survey.questions[q_index] = question
#     DB.surveys[survey.id] = survey

#     # STRUCTURE:
#     # --------------------------
#     # course {
#     #   offering [
#     #       each survey's unique id, generated by DB.gen_id()
#     #   ]
#     # }
#     if survey.course not in DB.survey_lookup:
#         DB.survey_lookup[survey.course] = {}
#     if survey.offering not in DB.survey_lookup[survey.course]:
#         DB.survey_lookup[survey.course][survey.offering] = []

#     # Adds the index of the survey in DB.surveys into survey_lookup
#     DB.survey_lookup[survey.course][survey.offering].append(survey.id)