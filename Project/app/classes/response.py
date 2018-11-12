from app import db as DB

class Response(DB.Model):
    __tablename__ = 'response'
    id = DB.Column('id', DB.Integer, primary_key = True, nullable = False)
    response = DB.Column('response', DB.String, nullable = True)
    option_id = DB.Column('option_id', DB.Integer, DB.ForeignKey('option.id'), nullable = True)
    survey_question_id = DB.Column('survey_question_id', DB.Integer, DB.ForeignKey('survey_question.id'), nullable = False)

    def __init__(self, response, survey_question_id, option_id=None):
        self.response = response
        if option_id:
	        self.option_id = option_id
        self.survey_question_id = survey_question_id
