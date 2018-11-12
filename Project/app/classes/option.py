from app import db as DB

class Option(DB.Model):
    __tablename__ = 'option'

    id = DB.Column('id', DB.Integer, primary_key = True, nullable = False)
    option = DB.Column('option', DB.String, nullable = False)
    survey_question_id = DB.Column('survey_question_id', DB.Integer, DB.ForeignKey('survey_question.id'), nullable = False)
    
    responses = DB.relationship('Response')

    def __init__(self, option, survey_question_id):
        self.option = option
        self.survey_question_id = survey_question_id
