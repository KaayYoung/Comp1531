import os
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

import config as Config
from app.utils.file_reader import File_Reader as File_Reader

class Database(SQLAlchemy):
    def __init__(self, server):
        super().__init__(server)

    def init_app(self, server):
        super().init_app(server)

    def load_user(self, user_id):
        from app.classes.user import User
        return User.query.get(user_id)

    def register_user(self, user):
        if user.guest:
            from app.classes.offering import Offering
            if len(Offering.query.filter_by(id = user.offering_request).all()) == 0:
                from sqlite3 import IntegrityError
                raise IntegrityError
        
        from app.classes.user import User
        if len(User.query.filter_by(id = user.id).all()) > 0:
            raise ValueError

        self.session.add(user)
        self.session.commit()

    def remove_user(self, user_id):
        from app.classes.enrolment import Enrolment
        for enrolment in Enrolment.query.filter_by(user_id = user_id).all():
            self.session.delete(enrolment)
        self.session.delete(self.load_user(user_id))
        self.session.commit()

    def add_course(self, course):
        from app.classes.course import Course
        from sqlite3 import IntegrityError
        try:
            if isinstance(course, Course):
                if Course.query.filter(Course.name == course.name).first():
                    raise IntegrityError
                else:
                    self.session.add(course)
            elif isinstance(course, str):
                if Course.query.filter(Course.name == course).first():
                    raise IntegrityError
                else:
                    self.session.add(Course(course))
            else:
                raise TypeError
        except TypeError:
            raise TypeError("Argument must be of type Offering or String")
        except IntegrityError:
            raise IntegrityError("Course already exists")
        else:
            self.session.commit()


    def load_defaults(self):
        from app.classes.admin import Admin
        from app.classes.staff import Staff
        from app.classes.student import Student

        from app.classes.course import Course
        from app.classes.offering import Offering
        from app.classes.enrolment import Enrolment

        try:
            print(" * Building database")

            old_percentage = -1
            percentage = 0
            num_admins = 0
            num_staff = 0
            num_students = 0
            users = File_Reader.read(Config.DB_USERS)
            for user in users:
                percentage = round((num_admins+num_staff+num_students)/len(users)*100)
                if percentage != old_percentage:
                    print("      (1/3) " + str(percentage) + "%                 ", end='\r')
                if user:
                    user_info = user.split(',')
                    zid = user_info[0]
                    password = user_info[1]
                    role = user_info[2]
                    staff = True if role == 'staff' else False
                    admin = True if role == 'admin' else False

                    if role == 'admin':
                        self.session.add(Admin(zid, 'Default' + ' ' + role, password))
                        num_admins += 1
                    elif role == 'staff':
                        self.session.add(Staff(zid, 'Default' + ' ' + role, password))
                        num_staff += 1
                    elif role == 'student':
                        self.session.add(Student(zid, 'Default' + ' ' + role, password))
                        num_students += 1
            print("      {0} admin{3} | {1} staff | {2} student{4}".format(num_admins, num_staff, num_students, '' if num_admins == 1 else 's', '' if num_students == 1 else 's'))

            self.session.commit()

            old_percentage = -1
            percentage = 0
            num_courses = 0
            num_offerings = 0
            courses = File_Reader.read(Config.DB_COURSES)
            for course in courses:
                percentage = round((num_courses+num_offerings)/len(courses)*100)
                if percentage != old_percentage:
                    print("      (2/3) " + str(percentage) + "%                 ", end='\r')
                if course:
                    course_info = course.split(',')
                    course_name = course_info[0]
                    existing_record = self.session.query(Course).filter_by(name = course_name).first()
                    if not existing_record:
                        new_course = Course(course_name)
                        self.session.add(new_course)
                        num_courses += 1

                    semester = course_info[1]
                    new_offering = Offering(semester, course_name)
                    self.session.add(new_offering)
                    num_offerings += 1
            print("      {0} course{2} | {1} offering{3}".format(num_courses, num_offerings, '' if num_courses == 1 else 's', '' if num_offerings == 1 else 's'))

            self.session.commit()

            old_percentage = -1
            percentage = 0
            num_enrolments = 0
            enrolments = File_Reader.read(Config.DB_ENROLEMENT)
            for enrolment in enrolments:
                percentage = round((num_enrolments)/len(enrolments)*100)
                if percentage != old_percentage:
                    print("      (3/3) " + str(percentage) + "%                 ", end='\r')
                if enrolment:
                    enrolment_info = enrolment.split(',')
                    enrolled_id = enrolment_info[0]
                    enrolled_course = enrolment_info[1]
                    enrolled_semester = enrolment_info[2]
                    offering_id = self.session.query(Offering).filter_by(semester = enrolled_semester, course_name = enrolled_course).first().id
                    new_enrolment = Enrolment(offering_id, enrolled_id)
                    self.session.add(new_enrolment)
                    num_enrolments += 1
            print("      {0} enrolment{1}".format(num_enrolments, '' if num_enrolments == 1 else 's'))
            
            self.session.commit()
        except:
            try:
                os.remove(Config.DB)
            except:
                pass
            from run import Colour
            print(Colour.FAIL + "      Build failed!" + Colour.NORM)
