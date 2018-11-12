from app import db as DB

class Completion(DB.Model):
    __tablename__ = 'completion'
    id = DB.Column('id', DB.Integer, primary_key = True, nullable = False)
    user_id = DB.Column('user_id', DB.Integer, DB.ForeignKey('user.id'), nullable = False)
    survey_id = DB.Column('survey_id', DB.Integer, DB.ForeignKey('survey.id'), nullable = False)

    def __init__(self, user_id, survey_id):
        self.user_id = user_id
        self.survey_id = survey_id

