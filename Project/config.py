''' Config file for the application '''
import os
import sys
# from Crypto.Cipher import AES

config = {}
config["SECRET_KEY"] = "Highly secret key"

basedir = os.path.abspath(os.path.dirname(__file__))
debug = True
port = 5001

SALT = '!?F=-?H%f8g1'
# AES_FUNCTION = AES.MODE_CBC

DB_BASE = basedir + "/database/"
DB = DB_BASE + "database.db"

# Where to import data from 
IMPORT_BASE = basedir + "/data/"
DB_COURSES = IMPORT_BASE + "courses.csv"
DB_COMPLETION = IMPORT_BASE + "completions.csv"
DB_ENROLEMENT = IMPORT_BASE + "enrolments.csv"
DB_OPTIONS = IMPORT_BASE + "options.csv"
DB_QUESTION = IMPORT_BASE + "questions.csv"
DB_USERS = IMPORT_BASE + "passwords.csv"
DB_RESPONSE = IMPORT_BASE + "responses.csv"
DB_SURVEY = IMPORT_BASE + "surveys.csv"
DB_SQUESTIONS = IMPORT_BASE + "survey_questions.csv"

debug_features = True if '-df' in sys.argv or '--debug-features' in sys.argv else False