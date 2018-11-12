''' DB Query Controller '''
import sqlite3
import config as Config

class Query():
    def __init__(self):
        pass
        # self._connection = sqlite3.connect(Config.DB)
        # self._cursor_obj = self._connection.cursor()
        # TESTING PURPOSES
        # print("GET USER")
        # print(self.get_user(50))
        # print("LOGIN")
        # print(self.check_login(50, "staff670"))
        # print("GET RELEVANT STUDENT SURVEYS")
        # print(self.get_open_surveys_for_user(50))
        # print("GET ALL SURVEYS")
        # print(self.get_all_surveys())
        # print("GET IN REVIEW SURVEYS")
        # print(self.get_in_review_surveys())
        # print("GET ALL QUESTIONS FOR QUESTION POOL")
        # print(self.get_all_questions_from_pool())
        # print("GET QUESTION ID")
        # print(self._get_question_id("Favourite part of the course"))
        # print("GET ALL QUESTIONS OF A SURVEY")
        # print(self.get_all_questions_of_a_survey("SENG4904", "18s1"))
        # print("GET COURSE ID")
        # print(self._get_course_id("SENG2011", "17s2"))
        # print("GET SURVEY ID")
        # print(self._get_survey_id("SENG2011", "17s2"))

    # HELPER PRIVATE FUNCTIONS
    def _get_all_results(self, query):
        conn = sqlite3.connect(Config.DB)
        cur = conn.cursor()
        result = cur.execute(query).fetchall()
        cur.close()
        conn.close()
        return result

    def _get_one_result(self, query):
        conn = sqlite3.connect(Config.DB)
        cur = conn.cursor()
        result = cur.execute(query).fetchone()
        cur.close()
        conn.close()
        return result

    def _make_parameterised_query(self, query, arguments):
        conn = sqlite3.connect(Config.DB)
        cur = conn.cursor()
        cur.execute(query, arguments)
        conn.commit()
        cur.close()
        conn.close()

    # LOGIN FUNCTIONALITY
    def get_user(self, user_id):
        try:
            query = "SELECT * FROM USER WHERE ID = \"%s\";" % user_id
            return self._get_one_result(query)
        except ValueError:
            print("ERROR -  get_user: ", user_id, ValueError)
            return None

    def check_login(self, user_id, password):
        user = self.get_user(user_id)
        if user and user[1] == password:
            return True
        else:
            return False
    
    # DASHBOARD FUNCTIONALITY
    # For student
    def get_open_surveys_for_user(self, user_id):
        try:
            query = ("SELECT * FROM SURVEY " +
                    "WHERE SURVEY.STAGE = 'OPEN' " +
                    "JOIN ENROLMENT ON SURVEY.COURSE_ID = ENROLMENT.COURSE_ID " +
                    "WHERE ENROLMENT.USER_ID = '%s'") % user_id
            return self._get_all_results(query)
        except ValueError:
            print("ERROR -  get_open_surveys_for_user: ", ValueError)

    # For admin
    def get_all_surveys(self):
        try:
            query = ("SELECT NAME, SEMESTER, STAGE, START_DATE, END_DATE " +
                    "FROM SURVEY LEFT JOIN COURSE ON SURVEY.COURSE_ID = COURSE.ID")
            return self._get_all_results(query)
        except ValueError:
            print("ERROR -  get_all_surveys: ", ValueError)

    # For staff
    def get_in_review_surveys(self):
        try:
            query = "SELECT * FROM SURVEY WHERE STAGE = 'REVIEW'"
            return self._get_all_results(query)
        except ValueError:
            print("ERROR -  get_in_review_surveys: ", ValueError)

    # QUESTION POOL FUNCTIONALITY
    def get_all_questions_from_pool(self):
        try:
            query = "SELECT * FROM QUESTION"
            return self._get_all_results(query)
        except ValueError:
            print("ERROR -  get_all_questions_from_pool: ", ValueError)

    def add_question_to_pool(self, question_text, q_type, mandatory):
        try:
            query = "INSERT INTO QUESTION VALUES (?,?,?,?)"
            arguments = (None,) + (question_text, q_type, int(mandatory))
            self._make_parameterised_query(query, arguments)
            return True
        except ValueError:
            print("ERROR -  add_question_to_pool: ", ValueError)
            return False

    def add_option(self, question, option):
        try:
            question_id = self._get_question_id(question)
            query = "INSERT INTO OPTION VALUES(?,?,?)"
            arguments = (None,) + (option, question_id)
            self._make_parameterised_query(query, arguments)
        except ValueError:
            print("ERROR -  add_option: ", ValueError)

    def delete_question_from_pool(self, question):
        try:
            question_id = self._get_question_id(question)
            query = "DELETE FROM QUESTION WHERE ID = ?"
            arguments = (question_id,)
            self._make_parameterised_query(query, arguments)
        except ValueError:
            print("ERROR -  delete_question_from_pool: ", ValueError)

    # CREATE SURVEY FUNCTIONALITY
    def _get_question_id(self, question_text):
        try:
            query = "SELECT ID FROM QUESTION WHERE QUESTION = '%s'" % question_text
            return self._get_one_result(query)[0]
        except ValueError:
            print("ERROR -  _get_question_id: ", ValueError)

    def add_question_to_survey(self, question_text, q_num, course_name, semester):
        try:
            question_id = self._get_question_id(question_text)
            survey_id = self._get_survey_id(course_name, semester)
            query = "INSERT INTO SURVEY_QUESTION VALUES (?,?,?,?)"
            arguments = (None,) + (q_num, survey_id, question_id)
            self._make_parameterised_query(query, arguments)
        except ValueError:
            print("ERROR -  add_question_to_survey: ", ValueError)

    def add_survey(self, course_name, semester, phase, start_date, end_date, questions):
        try:
            #TODO
            query = "INSERT INTO SURVEY VALUES (?,?,?,?,?)"
            course_id = self._get_course_id(course_name, semester)
            arguments = (None,) + (phase, start_date, end_date, course_id)
            self._make_parameterised_query(query, arguments)
            self.add_survey_questions(questions)
            return 1
        except ValueError:
            print("ERROR -  add_survey: ", ValueError)
            return 0

    def get_all_questions_of_a_survey(self, course_name, semester):
        try:
            survey_id = self._get_survey_id(course_name, semester)
            query = ("SELECT QUESTION FROM QUESTION " +
                    "JOIN SURVEY_QUESTION ON QUESTION.ID == SURVEY_QUESTION.QUESTION_ID " +
                    "JOIN SURVEY ON SURVEY_QUESTION.SURVEY_ID == SURVEY.ID WHERE SURVEY_QUESTION.SURVEY_ID == '%s'") % survey_id
            return self._get_all_results(query)
        except ValueError:
            print("ERROR -  get_all_questions_of_a_survey", ValueError)
            return 0

    def _get_course_id(self, course_name, semester):
        try:
            query = ("SELECT ID FROM COURSE " + 
                    "WHERE NAME = '%s' AND SEMESTER = '%s'") % (course_name, semester)
            return self._get_one_result(query)[0]
        except ValueError:
            print("ERROR -  _get_course_id:", ValueError)
            return 0

    def _get_survey_id(self, course_name, semester):
        try:
            query = ("SELECT SURVEY.ID FROM SURVEY " +
                    "JOIN COURSE ON SURVEY.COURSE_ID = COURSE.ID " +
                    "WHERE COURSE.NAME = '%s' AND COURSE.SEMESTER = '%s'") % (course_name, semester)
            return self._get_one_result(query)[0]
        except ValueError:
            print("ERROR -  _get_survey_id: ", ValueError)
            return 0

    def set_stage(self, course_name, semester, stage):
        survey_id = self._get_survey_id(course_name, semester)
        try:
            query = "UPDATE SURVEY SET STAGE = '%s' WHERE ID = '%s'" % (stage, survey_id)
            return self._cursor_obj.execute(query)
        except ValueError:
            print("ERROR -  set_stage: ", ValueError)
            return 0

    def get_responses(self, course_name, semester):
        try:
            survey_id = self._get_survey_id(course_name, semester)
            query = ("SELECT RESPONSE, OPTION_ID FROM RESPONSE " +
                    "JOIN SURVEY_QUESTION ON RESPONSE.SURVEY_QUESTION_ID = SURVEY_QUESTION.ID " +
                    "WHERE SURVEY_QUESTION.SURVEY_ID = '%s'") % survey_id
            return self._get_all_results(query)
        except ValueError:
            print("ERROR -  get_responses: ", ValueError)
            return 0

    def add_response(self, course_name, semester, response):
        #TODO
        try:
            survey_id = self._get_survey_id(course_name, semester)
            query = "INSERT INTO RESPONSE VALUES (?,?,?,?)"
            arguments = (None,) + ()
        except ValueError:
            print("ERROR -  add_response: ", ValueError)
        # response should have question number, and (response text or option value)
        pass

    def set_survey_as_completed_for_user(self, user_id, course_name, semester):
        try:
            survey_id = self._get_survey_id(course_name, semester)
            query = "INSERT INTO COMPLETION VALUES (?,?,?)"
            arguments = (None,) + (user_id, survey_id)
            self._make_parameterised_query(query, arguments)
            return 1
        except ValueError:
            print("ERROR -  set_survey_as_completed_for_user: ", ValueError)
            return 0

    def get_all_course_offerings(self):
        try:
            query = "SELECT * FROM COURSE"
            return self._get_all_results(query)
        except ValueError:
            print("ERROR -  get_all_course_offerings", ValueError)
            return 0

    def add_survey_questions(self, survey_id, questions):
        to_insert = []
        for question in questions:
            to_insert.append((survey_id,) + question)
        try:
            query = "INSERT INTO SURVEY_QUESTION VALUES (?,?,?,?)"
            arguments = (None, to_insert)
            self._make_parameterised_query(query, arguments)
            return 1
        except ValueError:
            print("ERROR -  add_survey_questions:", ValueError)
            return 0