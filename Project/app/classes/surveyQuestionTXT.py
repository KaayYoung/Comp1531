from app import db as DB
from app.classes.surveyQuestion import SurveyQuestion, QuestionType

class SurveyQuestionTXT(SurveyQuestion):
    __tablename__ = "survey_question_txt"
    id = DB.Column('id', DB.Integer, DB.ForeignKey('survey_question.id'), primary_key = True, nullable = False)

    __mapper_args__ = {
        'polymorphic_identity':QuestionType.TXT,
    }

    def __init__(self, question, number, mandatory, survey_id):
    	super().__init__(question=question, number=number, mandatory=mandatory, survey_id=survey_id)
