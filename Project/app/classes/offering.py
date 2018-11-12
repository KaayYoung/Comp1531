import datetime
from app import db as DB

class Offering(DB.Model):
    __tablename__ = 'offering'

    id = DB.Column('id', DB.Integer, primary_key = True, nullable = False)
    semester = DB.Column('semester', DB.String, nullable = False)
    course_name = DB.Column('course_name', DB.String, DB.ForeignKey("course.name"), nullable = False)

    enrolments = DB.relationship('Enrolment', backref="offering", lazy="dynamic")
    surveys = DB.relationship('Survey', backref="offering", lazy="dynamic")

    def __init__(self, semester, course_name):
        self.semester = semester
        self.course_name = course_name

    def get_surveys(self, *args, **kwargs):
        from app.classes.survey import Survey

        if kwargs:
            # Checks if arguments are valid
            for attribute in kwargs:
                if not hasattr(Survey, attribute):
                    raise AttributeError(str(attribute) + " is not an attribute of Survey")
            try:
                return self.surveys.filter_by(**kwargs).all()
            except ValueError:
                raise ValueError("Offering retrieval failed")
        else:
            from sqlalchemy.sql.elements import BinaryExpression
            # Checks if arguments are valid
            for binary_expr in args:
                if not isinstance(binary_expr, BinaryExpression):
                    raise TypeError("Arguments need to be of type BinaryExpression")
                if not hasattr(Survey, binary_expr.left.name):
                    raise AttributeError(str(binary_expr.left.name) + " is not an attribute of Survey")
            try:
                return self.surveys.filter(*args).all()
            except ValueError:
                raise ValueError("Offering retrieval failed")

    def add_survey(self, survey):
        from sqlite3 import IntegrityError
        try:
            from app.classes.survey import Survey
            if isinstance(survey, Survey):
                if any(x.offering_id == survey.offering_id for x in self.surveys):
                    raise ValueError
                elif survey.offering_id != self.id:
                    raise AttributeError
                else:
                    self.surveys.append(survey)
            else:
                raise TypeError
        except TypeError:
            raise TypeError("survey must be of type Survey")
        except AttributeError:
            raise AttributeError("survey does not belong to this offering")
        except IntegrityError:
            raise IntegrityError("survey already exists")
        else:
            DB.session.commit()

    def delete_survey(self, survey_id):
        try:
            from app.classes.survey import Survey
            survey = Survey.query.filter_by(id = survey_id).first()
            if survey:
                DB.session.delete(survey)
                DB.session.commit()
            else:
                raise ValueError
        except ValueError:
            raise ValueError("survey_id does not belong to an existing survey")
        else:
            DB.session.commit()

    def enrol_user(self, enrolment):
        from sqlite3 import IntegrityError
        from app.classes.enrolment import Enrolment
        from app.classes.user import User

        if not isinstance(enrolment, Enrolment):
            raise TypeError("enrolment must be of type Enrolment")

        try:
            if any(x.offering_id == enrolment.offering_id and x.user_id == enrolment.user_id for x in self.enrolments):
                raise ValueError
            elif len(User.query.filter_by(_id = enrolment.user_id).all()) == 0:
                raise IntegrityError
            else:
                self.enrolments.append(enrolment)
        except AttributeError:
            raise AttributeError("enrolment does not belong to this Enrolment")
        except IntegrityError:
            raise IntegrityError("enrolment already exists")
        else:
            DB.session.commit()

