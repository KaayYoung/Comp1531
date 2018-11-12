import os
import sys

# Safeguards against incorrect usage
if __name__ == "__main__":
    # stuff only to run when not called via 'import' here
    from run_tests import Colour
    print(Colour.WARNING + "WARNING: Do not run this file directly, use run_tests.py for db safety." + Colour.NORM)
    decision = None
    while decision not in ['y', 'n', "yes", "no"]:
        decision = str(input("Do you wish to execute run_tests.py (y/n)? ")).lower()
    if decision in ['y', 'yes']:
        os.system("python3 run_tests.py")
    else:
        sys.exit()

import unittest
from shutil import copyfile
from pathlib import Path
from datetime import datetime
from sqlite3 import IntegrityError

import config as Config
from app import db as DB
from app.classes.course import Course
from app.classes.offering import Offering
from app.classes.student import Student
from app.classes.staff import Staff
from app.classes.admin import Admin
from app.classes.guest import Guest
from app.classes.enrolment import Enrolment
from app.classes.survey import Survey, Phase
from app.classes.question import Question
from app.classes.surveyQuestion import SurveyQuestion
from app.classes.surveyQuestionMCQ import SurveyQuestionMCQ
from app.classes.surveyQuestionTXT import SurveyQuestionTXT
from app.classes.response import Response
from app.classes.completion import Completion

class TestCourse(unittest.TestCase):

    def setUp(self):
        DB.drop_all()
        DB.create_all()
        self.course = Course("TEST1531")
        DB.add_course(self.course)

    def test_init(self):
        self.assertEqual(self.course.name, "TEST1531")

    def test_duplicate_course(self):
        """
        :pre  : 1 instance of course is in DB
        :post : 1 instance of course is in DB
                That instance has 0 offerings
        """
        with self.assertRaises(IntegrityError):
            DB.add_course(Course(self.course.name))
        self.assertEqual(Course.query.filter_by(name = self.course.name).all(), [self.course])
        course = Course.query.filter_by(name = self.course.name).first()
        self.assertEqual(course.offerings.all(), [])

    def test_add_offering(self):
        """
        :pre  : 1 instance of course is in DB, with 0 offerings
        :post : 1 instance of course is in DB, with 2 offerings
                There are 2 offerings in the database
        """
        # Tries adding with text
        self.course.add_offering("17s1")

        self.assertEqual(len(self.course.offerings.all()), 1)
        self.assertEqual(len(Offering.query.filter_by(course_name = self.course.name).all()), 1)
        self.assertEqual(len(Offering.query.all()), 1)

        # Tries adding with Offering object
        self.course.add_offering(Offering("17s2", self.course.name))

        with self.assertRaises(TypeError):
            self.course.add_offering(1)

        self.assertEqual(len(self.course.offerings.all()), 2)
        self.assertEqual(len(Offering.query.filter_by(course_name = self.course.name).all()), 2)
        self.assertEqual(len(Offering.query.all()), 2)

    def test_add_offering_duplicate(self):
        """
        :pre  : 1 instance of course is in DB, with 0 offerings
        :post : 1 instance of course is in DB, with 1 offering
                There is 1 offering in the database
        """
        # Tries adding with text
        self.course.add_offering("17s1")
        with self.assertRaises(IntegrityError):
            self.course.add_offering("17s1")

        self.assertEqual(len(self.course.offerings.all()), 1)
        self.assertEqual(len(Offering.query.filter_by(course_name = self.course.name).all()), 1)
        self.assertEqual(len(Offering.query.all()), 1)

        # Tries adding with Offering object
        self.course.add_offering("17s2")
        with self.assertRaises(IntegrityError):
            self.course.add_offering(Offering("17s2", self.course.name))

        with self.assertRaises(TypeError):
            self.course.add_offering(1)

        self.assertEqual(len(self.course.offerings.all()), 2)
        self.assertEqual(len(Offering.query.filter_by(course_name = self.course.name).all()), 2)
        self.assertEqual(len(Offering.query.all()), 2)

    def tearDown(self):
        DB.session.remove()
        DB.drop_all()


class TestOffering(unittest.TestCase):

    def setUp(self):
        DB.drop_all()
        DB.create_all()

        self.course = Course("TEST1531")
        DB.add_course(self.course)
        self.offering = Offering(semester="17s1", course_name=self.course.name)
        self.course.add_offering(self.offering)

    def test_init(self):
        self.assertEqual(self.offering.course_name, "TEST1531")
        self.assertEqual(self.offering.semester, "17s1")

    def test_get_surveys(self):
        self.assertEqual(self.offering.get_surveys(), [])
        survey1 = Survey(title="hey", phase=Phase.closed, start_date=datetime.now(), end_date=datetime.now(), offering_id=self.offering.id)
        self.offering.add_survey(survey1)
        self.assertEqual(self.offering.get_surveys(title="hey"), Survey.query.all())
        self.assertEqual(self.offering.get_surveys(Survey.title == "hey"), Survey.query.all())

        with self.assertRaises(AttributeError):
            self.offering.get_surveys(i_dont_exist="hey")

        with self.assertRaises(AttributeError):
            self.offering.get_surveys(Survey.i_dont_exist == "hey")

        new_offering = self.course.add_offering("17s2")
        survey2 = Survey(title="hey1.5", phase=Phase.closed, start_date=datetime.now(), end_date=datetime.now(), offering_id=new_offering.id)
        new_offering.add_survey(survey2)

        surveys = self.offering.get_surveys()
        self.assertEqual(len(surveys), 1)
        self.assertEqual(surveys[0], survey1)
        self.assertEqual(surveys, Survey.query.filter_by(offering_id = self.offering.id).all())

   
    def test_add_survey(self):
        with self.assertRaises(TypeError):
            self.offering.add_survey(1)

        with self.assertRaises(AttributeError):
            self.offering.add_survey(Survey(title="hey", phase=Phase.closed, start_date=datetime.now(), end_date=datetime.now(), offering_id=2))

    def tearDown(self):
        DB.session.remove()
        DB.drop_all()


class TestEnrolment(unittest.TestCase):

    def setUp(self):
        DB.drop_all()
        DB.create_all()
        self.course = Course("TEST1531")
        DB.add_course(self.course)
        self.offering = Offering(semester="17s1", course_name=self.course.name)
        self.course.add_offering(self.offering)

    def test_enrol_non_existent_user_in_course_offering(self):
        with self.assertRaises(IntegrityError):
            new_enrolment = Enrolment(1, 123)
            self.offering.enrol_user(new_enrolment)

    def test_enrol_user_in_duplicate_enrolment(self):
        new_student = Student('123', 'Default student', 'password')
        DB.register_user(new_student)

        new_enrolment_1 = Enrolment(1, 123)
        self.offering.enrol_user(new_enrolment_1)

        with self.assertRaises(ValueError):
            new_enrolment_2 = Enrolment(1, 123)
            self.offering.enrol_user(new_enrolment_2)

    def test_enrol_user_in_single_course_offering(self):
        new_student = Student('123', 'Default student', 'password')
        DB.register_user(new_student)

        new_enrolment = Enrolment(1, 123)
        self.offering.enrol_user(new_enrolment)

        self.assertEqual(self.offering.enrolments[0], new_enrolment)

    def test_enrol_user_in_multiple_course_offerings(self):
        new_student = Student('123', 'Default student', 'password')
        DB.register_user(new_student)

        new_course_2 = Course("TEST1917")
        DB.add_course(new_course_2)
        new_offering_2 = Offering(semester="16s2", course_name=new_course_2.name)
        
        new_enrolment_1 = Enrolment(1, 123)
        new_enrolment_2 = Enrolment(2, 123)
        self.offering.enrol_user(new_enrolment_1)
        new_offering_2.enrol_user(new_enrolment_2)

        self.assertEqual(self.offering.enrolments[0], new_enrolment_1)
        self.assertEqual(new_offering_2.enrolments[0], new_enrolment_2)

    def tearDown(self):
        DB.session.remove()
        DB.drop_all()


class TestSurvey(unittest.TestCase):

    def setUp(self):    
        DB.drop_all()
        DB.create_all()
        TestSurvey.start = datetime(2000, 1, 31)
        TestSurvey.future = datetime(2100, 1, 31)

        self.course = Course("TEST1531")
        DB.add_course(self.course)
        self.offering = Offering(semester="17s1", course_name=self.course.name)
        self.course.add_offering(self.offering)

    def test_create_survey_with_0_questions(self):
        new_survey = Survey("Title_mock", "review", TestSurvey.start, TestSurvey.future, 1)

        self.offering.add_survey(new_survey)

        self.assertEqual(Survey.query.all()[0], new_survey)

    def test_create_survey_with_duplicate_questions(self):
        question = Question("question_mock", True)
        question.add_question()
        new_survey = Survey("Title_mock", "review", TestSurvey.start, TestSurvey.future, 1)
        self.offering.add_survey(new_survey)

        survey_question_1 = SurveyQuestion("question_mock", 1, True, 1)
        new_survey.add_survey_question(survey_question_1)

        with self.assertRaises(ValueError):
            survey_question_2 = SurveyQuestion("question_mock", 1, True, 1)
            new_survey.add_survey_question(survey_question_2)

    def test_remove_survey_question(self):
        question = Question("question_mock", True)
        question.add_question()

        new_survey = Survey("Title_mock", "review", TestSurvey.start, TestSurvey.future, 1)
        self.offering.add_survey(new_survey)

        survey_question_1 = SurveyQuestion("question_mock", 1, True, 1)
        new_survey.add_survey_question(survey_question_1)

        self.assertEqual(len(SurveyQuestion.query.all()), 1)
        new_survey.remove_survey_question(SurveyQuestion.query.first().id)

        self.assertEqual(len(SurveyQuestion.query.all()), 0)

    def test_create_survey_with_questions(self):
        new_survey = Survey("Title_mock", "review", TestSurvey.start, TestSurvey.future, 1)
        self.offering.add_survey(new_survey)
        question_1 = Question("question_mock", True)
        question_2 = Question("question_mock_2", True)
        question_1.add_question()
        question_2.add_question()

        survey_question_1 = SurveyQuestion("question_mock", 1, True, 1)
        survey_question_2 = SurveyQuestion("question_mock_2", 1, True, 1)
        new_survey.add_survey_question(survey_question_1)
        new_survey.add_survey_question(survey_question_2)

        self.assertEqual(new_survey.questions[0], survey_question_1)
        self.assertEqual(new_survey.questions[1], survey_question_2)

    @unittest.expectedFailure
    def test_create_duplicate_survey_for_same_course_offering(self):
        new_survey_1 = Survey("Title_mock", "review", TestSurvey.start, TestSurvey.future, 1)
        self.offering.add_survey(new_survey_1)

        new_survey_2 = Survey("Title_mock_2", "review", TestSurvey.start, TestSurvey.future, 1)
        with self.assertRaises(IntegrityError):
            self.offering.add_survey(new_survey_2)

    def test_create_survey_should_be_in_review_phase_once_created(self):
        new_survey_1 = Survey("Title_mock", "review", TestSurvey.start, TestSurvey.future, 1)
        self.offering.add_survey(new_survey_1)

        self.assertEqual(Survey.query.first().phase, "review")

    def test_reviewed_survey_is_set_to_open_phase(self):
        new_survey_1 = Survey("Title_mock", "review", TestSurvey.start, TestSurvey.future, 1)
        self.offering.add_survey(new_survey_1)
        self.assertEqual(Survey.query.first().phase, "review")
        
        new_survey_1.open_survey()

        self.assertEqual(Survey.query.first().phase, "open")

    def test_open_survey_is_set_to_close_phase(self):
        new_survey_1 = Survey("Title_mock", "review", TestSurvey.start, TestSurvey.future, 1)
        self.offering.add_survey(new_survey_1)
        self.assertEqual(Survey.query.first().phase, "review")
        new_survey_1.open_survey()
        self.assertEqual(Survey.query.first().phase, "open")

        new_survey_1.close_survey()

        self.assertEqual(Survey.query.first().phase, "closed")

    def test_delete_survey(self):
        new_survey_1 = Survey("Title_mock", "review", TestSurvey.start, TestSurvey.future, 1)
        self.offering.add_survey(new_survey_1)

        self.assertEqual(len(Survey.query.all()), 1)
        self.offering.delete_survey(Survey.query.first().id)

        self.assertEqual(len(Survey.query.all()), 0)

    def tearDown(self):
        DB.session.remove()
        DB.drop_all()

class TestQuestion(unittest.TestCase):

    def setUp(self):
        DB.drop_all()
        DB.create_all()

    def test_create_mandatory_question(self):
        question = Question("question_mock", True)
        question.add_question()
        self.assertEqual(Question.query.all()[0], question)

    def test_create_optional_question(self):
        question = Question("question_mock", False)
        question.add_question()
        self.assertEqual(Question.query.all()[0], question)

    def test_create_question_with_empty_text(self):
        with self.assertRaises(ValueError):
            question = Question("", True)
            question.add_question()

    def test_create_question_with_invalid_mandatory_or_optional_flag(self):
        with self.assertRaises(TypeError):
            question = Question("question_mock", 'mmmm')
            question.add_question()

    def test_create_duplicate_question(self):
        question_1 = Question("question_mock", True)
        question_1.add_question()

        with self.assertRaises(ValueError):
            question_2 = Question("question_mock", True)
            question_2.add_question()

    def test_remove_question(self):
        question_1 = Question("question_mock", True)
        question_1.add_question()
        self.assertEqual(Question.query.all()[0], question_1)

        question_1.remove_question()
        
        self.assertEqual(len(Question.query.all()), 0)

    def tearDown(self):
        DB.session.remove()
        DB.drop_all()


class TestUserAuthentication(unittest.TestCase):
    
    def setUp(self):
        DB.drop_all()
        DB.create_all()

    def test_check_login_with_correct_credentials(self):
       new_student = Student('123', 'Default student', 'password')
       DB.register_user(new_student)

       student_from_db = DB.load_user(123)
       self.assertEqual(student_from_db.check_login(new_student.password), True)

    def test_check_login_with_incorrect_credentials(self):
        new_student = Student('123', 'Default student', 'password')
        DB.register_user(new_student)

        student_from_db = DB.load_user(123)
        self.assertEqual(student_from_db.check_login('invalid password'), False)

    def test_check_student_login_associated_with_student_account(self):
        new_student = Student('123', 'Default student', 'password')
        DB.register_user(new_student)

        student_from_db = DB.load_user(123)
        self.assertEqual(student_from_db.student, True)
        self.assertEqual(student_from_db.staff, False)
        self.assertEqual(student_from_db.admin, False)
        self.assertEqual(student_from_db.guest, False)

    def test_check_staff_login_associated_with_staff_account(self):
        new_staff = Staff('123', 'Default staff', 'password')
        DB.register_user(new_staff)

        staff_from_db = DB.load_user(123)
        self.assertEqual(staff_from_db.student, False)
        self.assertEqual(staff_from_db.staff, True)
        self.assertEqual(staff_from_db.admin, False)
        self.assertEqual(staff_from_db.guest, False)

    def test_check_admin_login_associated_with_admin_account(self):
        new_admin = Admin('123', 'Default admin', 'password')
        DB.register_user(new_admin)

        admin_from_db = DB.load_user(123)
        self.assertEqual(admin_from_db.student, False)
        self.assertEqual(admin_from_db.staff, False)
        self.assertEqual(admin_from_db.admin, True)
        self.assertEqual(admin_from_db.guest, False)

    def test_check_guest_login_associated_with_guest_account(self):
        self.course = Course("TEST1531")
        DB.add_course(self.course)
        self.offering = Offering(semester="17s1", course_name=self.course.name)
        self.course.add_offering(self.offering)

        new_guest = Guest(id='123', offering_request=1, password='password')
        DB.register_user(new_guest)

        guest_from_db = DB.load_user(123)
        self.assertEqual(guest_from_db.student, False)
        self.assertEqual(guest_from_db.staff, False)
        self.assertEqual(guest_from_db.admin, False)
        self.assertEqual(guest_from_db.guest, True)

    def test_check_guest_registration_with_invalid_offering_association(self):
        new_guest = Guest(id='123', offering_request=1, password='password')
        with self.assertRaises(IntegrityError):
            DB.register_user(new_guest)

    def test_register_duplicate_user(self):
        new_student_1 = Student('123', 'Default student', 'password')
        DB.register_user(new_student_1)

        with self.assertRaises(ValueError):
            new_student_2 = Student('123', 'Default student 2', 'password 2')
            DB.register_user(new_student_2)

    def tearDown(self):
        DB.session.remove()
        DB.drop_all()


class TestResponse(unittest.TestCase):

    def setUp(self):
        DB.drop_all()
        DB.create_all()

        self.course = Course("TEST1531")
        DB.add_course(self.course)
        self.offering = Offering(semester="17s1", course_name=self.course.name)
        self.course.add_offering(self.offering)

        self.question_1 = Question("question_mock_1", True)
        self.question_1.add_question()
        self.question_2 = Question("question_mock_2", False)
        self.question_2.add_question()

        self.survey = Survey("Title_mock", "review", datetime.now(), datetime.now(), 1)
        self.offering.add_survey(self.survey)

        self.survey_question_1 = SurveyQuestionTXT("survey_question_mock_1", 1, True, 1)
        self.survey.add_survey_question(self.survey_question_1)
        self.survey_question_2 = SurveyQuestionTXT("survey_question_mock_2", 2, False, 1)
        self.survey.add_survey_question(self.survey_question_2)

    def test_response_text_with_text_question(self):
        new_text_sq = SurveyQuestionTXT("survey_question_mock_3", 1, True, 1)
        self.survey.add_survey_question(new_text_sq)

        new_response_1 = Response("response_mock_1", 3)
        new_text_sq.add_response(new_response_1)

        self.assertEqual(new_text_sq.responses[0], new_response_1)
    
    def test_response_option_with_text_question(self):
        new_text_sq = SurveyQuestionTXT("survey_question_mock_3", 1, True, 1)
        self.survey.add_survey_question(new_text_sq)

        new_response_1 = Response("Agree", 3, 1)

        with self.assertRaises(IntegrityError):
            new_text_sq.add_response(new_response_1)

    def test_response_option_with_mcq_question(self):
        new_text_sq = SurveyQuestionMCQ("survey_question_mock_3", 1, True, 1)
        self.survey.add_survey_question(new_text_sq)
        new_text_sq.add_options(SurveyQuestionMCQ.query.first().id)

        new_response_1 = Response("Agree", 3, 3)
        new_text_sq.add_response(new_response_1)

        self.assertEqual(new_text_sq.responses[0], new_response_1)

    def test_response_text_with_mcq_question(self):
        new_text_sq = SurveyQuestionMCQ("survey_question_mock_3", 1, True, 1)
        self.survey.add_survey_question(new_text_sq)
        new_text_sq.add_options(SurveyQuestionMCQ.query.first().id)

        new_response_1 = Response("response_mock_1", 3)

        with self.assertRaises(IntegrityError):
            new_text_sq.add_response(new_response_1)

    def test_response_with_all_questions_completed(self):
        new_response_1 = Response("response_mock_1", 1)
        new_response_2 = Response("response_mock_2", 2)

        self.survey_question_1.add_response(new_response_1)
        self.survey_question_2.add_response(new_response_2)

        self.assertEqual(self.survey_question_1.responses[0], new_response_1)
        self.assertEqual(self.survey_question_2.responses[0], new_response_2)

    def test_response_does_not_have_student_information(self):
        new_student = Student('123', 'Default student', 'password')
        DB.register_user(new_student)
        new_response_1 = Response("response_mock_1", 1)

        self.survey_question_1.add_response(new_response_1)
        new_completion = Completion(123, 1)
        new_student.add_completion(new_completion)

        self.assertEqual(self.survey_question_1.responses[0], new_response_1)

    def test_response_successfully_completed_by_student_is_stored_in_completion_table(self):
        new_student = Student('123', 'Default student', 'password')
        DB.register_user(new_student)
        new_response_1 = Response("response_mock_1", 1)

        self.survey_question_1.add_response(new_response_1)
        new_completion = Completion(123, 1)
        new_student.add_completion(new_completion)

        self.assertEqual(new_student.completions[0], new_completion)

    def tearDown(self):
        DB.session.remove()
        DB.drop_all()
    



def run():
    unittest.main(exit=False, failfast=True)

