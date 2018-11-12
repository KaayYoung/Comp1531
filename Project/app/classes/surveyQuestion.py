from app import db as DB

class QuestionType():
    TXT = "TXT"
    MCQ = "MCQ"

class SurveyQuestion(DB.Model):
    __tablename__ = 'survey_question'
    id = DB.Column('id', DB.Integer, primary_key = True, nullable = False)
    type = DB.Column('type', DB.String, nullable = False)
    question = DB.Column('question', DB.String, nullable = False)
    number = DB.Column('question_num', DB.Integer, nullable = False)
    mandatory = DB.Column('mandatory', DB.Boolean, nullable = False)
    survey_id = DB.Column('survey_id', DB.Integer, DB.ForeignKey('survey.id'), nullable = False)

    responses = DB.relationship('Response', lazy='dynamic', backref='survey_question')

    __mapper_args__ = {
        'polymorphic_identity':'survey_question',
        'polymorphic_on':type
    }

    def __init__(self, question, number, mandatory, survey_id):
        self.question = question
        self.number = number
        self.mandatory = mandatory
        self.survey_id = survey_id
    
    def add_response(self, response):
        from sqlite3 import IntegrityError
        try:
            from app.classes.response import Response
            from app.classes.option import Option
            if isinstance(response, Response):
                if response.option_id is not None and len(Option.query.filter_by(id = response.option_id).all()) == 0:
                    raise IntegrityError
                elif self.type == QuestionType.MCQ and response.option_id is None:
                    raise IntegrityError
                else:
                    self.responses.append(response)
            else:
                raise TypeError
        except TypeError:
            raise TypeError("response must be of type Response")
        except AttributeError:
            raise AttributeError("response does not belong to this SurveyQuestion")
        except IntegrityError:
            raise IntegrityError("response already exists")
        else:
            DB.session.commit()
