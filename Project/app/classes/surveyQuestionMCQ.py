from app import db as DB
from app.classes.surveyQuestion import SurveyQuestion, QuestionType

class SurveyQuestionMCQ(SurveyQuestion):
    __tablename__ = "survey_question_mcq"
    id = DB.Column('id', DB.Integer, DB.ForeignKey('survey_question.id'), primary_key = True, nullable = False)
    options = DB.relationship('Option', lazy='dynamic')

    __mapper_args__ = {
        'polymorphic_identity':QuestionType.MCQ,
    }

    def __init__(self, question, number, mandatory, survey_id):
        super().__init__(question=question, number=number, mandatory=mandatory, survey_id=survey_id)

    def add_options(self, survey_question_id):
        from app.classes.option import Option
        for option in ['Strongly disagree', 'Disagree', 'Neutral', 'Agree', 'Strongly agree']:
            new_option = Option(option, survey_question_id)
            self.options.append(new_option)
            DB.session.add(new_option)

        DB.session.commit()