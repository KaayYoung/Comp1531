from flask_login import UserMixin
from app import db as DB
from app.classes.completion import Completion
from app.classes.enrolment import Enrolment
from app.classes.offering import Offering
from app.classes.course import Course

class User(UserMixin, DB.Model):

    __tablename__ = 'user'
    _id = DB.Column('id', DB.Integer, primary_key = True, nullable = False)
    _password = DB.Column('password', DB.String, nullable = False)
    _name = DB.Column('name', DB.String, nullable = True)
    _type = DB.Column('type', DB.String, nullable = False)

    enrolments = DB.relationship('Enrolment', backref='user', lazy='dynamic', cascade='all,delete')
    completions = DB.relationship('Completion')

    __mapper_args__ = {
        'polymorphic_identity':'user',
        'polymorphic_on':_type
    }

    def __init__(self, password, id=None, name=None):
        # self.id = uuid.uuid4().urn[9:]
        self._password = password
        if id:
            self.id = int(id)
        if name:
            self._name = name

    def __repr__(self):
        return '<User {0} | {1}>'.format(self.id, self.password)

    # UserMixin overrides
    def get_id(self):
        return self._id

    @property
    def is_active(self):
        return True

    @property
    def active(self):
        return True

    def check_login(self, password):
        if password == self._password:
            return True
        else:
            return False

    # Properties
    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, new_id):
        if User.query.get(new_id) == None:
            self._id = new_id
        else:
            raise ValueError('zID {0} taken'.format(new_id))

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, new_name):
        self._name = new_name

    @property
    def password(self):
        return self._password

    @password.setter
    def password(self, new_password):
        self._password = new_password

    @property
    def admin(self):
        return True if self._type == 'admin' else False

    @property
    def staff(self):
        return True if self._type == 'staff' else False

    @property
    def student(self):
        return True if self._type == 'student' else False

    @property
    def guest(self):
        return True if self._type == 'guest' else False

    @property
    def enrolments(self):
        # get all the courses the user is enrolled in 
        enrolments = []
        if self.active and self.admin:
            enrolments = Enrolment.query.all()
        elif self.active:
            enrolments = Enrolment.query.filter_by(user_id = self.id).all()
        return enrolments

    @property
    def enrolled_offerings(self):
        enrolled_ids = list(set(enrolment.offering_id for enrolment in self.enrolments))
        return Offering.query.filter(Offering.id.in_(enrolled_ids)).all()

    @property
    def enrolled_courses(self):
        offerings_names = list(offering.course_name for offering in self.enrolled_offerings)
        return Course.query.filter(Course.name.in_(offerings_names)).all()

    def has_completed(self, survey):
        return False if (Completion.query.filter_by(user_id=self.id, survey_id=survey.id).first()==None) else True

    def get_enrolled_offerings(self):
        """
        Get all the offerings the user is enrolled in 
        """
        offerings = []
        if(self.admin == True):
            offerings = Offering.query.all()
        else:
            enrolment_ids = list(enrolment.offering_id for enrolment in self.enrolments)
            offerings = Offering.query.filter(Offering.id.in_(enrolment_ids)).all()

        return offerings

    def get_surveys(self, type, filter):
        """Creates a hierarchical object containing open surveys organised

        Args:
            type: is element of set {'review', 'open', 'closed'}
            filter: function pointer, returns true or false
                    Args: 
                        survey: survey object to check
                        type: type to filter for
                    Returns:
                        True if check passes, else False


        Returns:
            surveys_obj = {
                           course_name:{
                                        semester:[
                                                  filtered list of survey objects
                                                 ]
                                       }
                          }

        """

        # get the right courses for the user 
        offerings = self.get_enrolled_offerings()

        surveys_obj = {}
        for offering in offerings:
            if offering.course_name not in surveys_obj:
                surveys_obj[offering.course_name] = {}

            # Assumes these are all associated with the user from the prev filtering
            for survey in offering.surveys:
                if filter(self, survey=survey, type=type):
                    if offering.semester not in surveys_obj[offering.course_name]:
                        surveys_obj[offering.course_name][offering.semester] = []
                    surveys_obj[offering.course_name][offering.semester].append(survey)
            # If the surveys_obj entry is still unpopulated, removes that course
            if not surveys_obj[offering.course_name]:
                del surveys_obj[offering.course_name]

        return surveys_obj

    def add_completion(self, completion):
        from sqlite3 import IntegrityError
        try:
            from app.classes.completion import Completion
            if isinstance(completion, Completion):
                if any(x.user_id == completion.user_id and x.survey_id == completion.survey_id for x in self.completions):
                    raise ValueError
                else:
                    self.completions.append(completion)
            else:
                raise TypeError
        except TypeError:
            raise TypeError("completion must be of type Completion")
        except AttributeError:
            raise AttributeError("completion does not belong to this User")
        except IntegrityError:
            raise IntegrityError("completion already exists")
        else:
            DB.session.commit()