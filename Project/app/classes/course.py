from app import db as DB
from app.classes.offering import Offering

class Course(DB.Model):
    __tablename__ = 'course'
    name = DB.Column('name', DB.String, primary_key = True, nullable = False)

    offerings = DB.relationship('Offering', backref='course', lazy='dynamic')

    def __init__(self, name):
        self.name = name

    def __str__(self):
        return '<Course {0}>'.format(self.name)

    def get_offerings(self, *args, **kwargs):
        if kwargs:
            # Checks if arguments are valid
            for attribute in kwargs:
                if not hasattr(Offering, attribute):
                    raise AttributeError(str(attribute) + " is not an attribute of Offering")
            try:
                return self.offerings.filter_by(**kwargs).all()
            except ValueError:
                raise ValueError("Offering retrieval failed")
        else:
            from sqlalchemy.sql.elements import BinaryExpression
            # Checks if arguments are valid
            for binary_expr in args:
                if not isinstance(binary_expr, BinaryExpression):
                    raise TypeError("Arguments need to be of type BinaryExpression")
                if not hasattr(Offering, binary_expr.left.name):
                    raise AttributeError(str(binary_expr.left.name) + " is not an attribute of Offering")
            try:
                return self.offerings.filter(*args).all()
            except ValueError:
                raise ValueError("Offering retrieval failed")

    def add_offering(self, offering):
        from sqlite3 import IntegrityError
        try:
            if isinstance(offering, Offering):
                if Offering.query.filter_by(semester = offering.semester, course_name = offering.course_name).first():
                    raise IntegrityError
                else:
                    to_add = offering
                    self.offerings.append(to_add)
            elif isinstance(offering, str):
                if Offering.query.filter_by(semester = offering, course_name = self.name).first():
                    raise IntegrityError
                else:
                    to_add = Offering(offering, self.name)
                    self.offerings.append(to_add)
            else:
                raise TypeError
        except TypeError:
            raise TypeError("Offering must be of type Offering or String")
        except IntegrityError:
            raise IntegrityError("Offering already exists")
        else:
            DB.session.commit()
            return to_add
