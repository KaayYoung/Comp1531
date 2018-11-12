from app import db as DB
from app.classes.question import Question
from sqlalchemy.orm.exc import NoResultFound
from sqlite3 import IntegrityError
from sqlalchemy import and_

class Phase():
    # Phase definitions
    review = "review"
    open = "open"
    closed = "closed"

class Survey(DB.Model):

    __tablename__ = 'survey'
    id = DB.Column('id', DB.Integer, primary_key = True, nullable = False)
    title = DB.Column('title', DB.String, nullable = False)
    phase = DB.Column('phase', DB.String, nullable = False)
    start_date = DB.Column('start_date', DB.DateTime, nullable = False)
    end_date = DB.Column('end_date', DB.DateTime, nullable = False)
    offering_id = DB.Column('offering_id', DB.Integer, DB.ForeignKey('offering.id'), nullable = False)

    questions = DB.relationship('SurveyQuestion', lazy='dynamic')
    completions = DB.relationship('Completion', lazy='dynamic')

    def __init__(self, title, phase, start_date, end_date, offering_id):
        # check if the survey id has questions associated with it 
        try:
            # check that there are questions available 
            Question.query.first()
        except NoResultFound:
            raise ValueError("No Questions are currently stored in DB")

        try:
            # check if this course already has a survey 
            surveys = Survey.query.filter(self.offering_id == offering_id).all()
            if len(surveys) != 0:
                raise IntegrityError

            self.title = title
            self.phase = phase
            self.start_date = start_date
            self.end_date = end_date
            self.offering_id = offering_id
        except IntegrityError:
            raise IntegrityError("A Survey for this course already exists")
            

    def add_survey_question(self, survey_question):
        from sqlite3 import IntegrityError
        try:
            from app.classes.surveyQuestion import SurveyQuestion
            if isinstance(survey_question, SurveyQuestion):
                if any(x.type == survey_question.type and x.question == survey_question.question 
                    and x.mandatory == survey_question.mandatory and x.survey_id == survey_question.survey_id 
                    for x in self.questions):
                    raise ValueError
                else:
                    self.questions.append(survey_question)
            else:
                raise TypeError
        except TypeError:
            raise TypeError("survey_question must be of type SurveyQuestion")
        except AttributeError:
            raise AttributeError("survey_question contains attribute that does not belong to SurveyQuestion")
        except IntegrityError:
            raise IntegrityError("survey_question already exists")
        else:
            DB.session.commit()

    def remove_survey_question(self, sq_id):
        try:
            from app.classes.surveyQuestion import SurveyQuestion
            from app.classes.option import Option
            Option.query.filter_by(survey_question_id = sq_id).delete()
            SurveyQuestion.query.filter_by(id = sq_id).delete()
        except:
            pass

    def open_survey(self):
        self.phase = "open"
        DB.session.commit()

    def close_survey(self):
        self.phase = "closed"
        DB.session.commit()
