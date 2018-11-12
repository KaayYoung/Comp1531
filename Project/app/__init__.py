''' Server app initialiser '''
import sys
import os
import re
import sqlite3
from pathlib import Path
from datetime import datetime
from random import randint

from flask import Flask, redirect, url_for, g, flash
from flask_login import LoginManager

import atexit
def reset_handler():
    pass
atexit.register(reset_handler)

import config as Config
from app.utils.file_reader import File_Reader as File_Reader

from app.classes.database import Database
from app.classes.server import Server

app = Server(__name__)
db = Database(app)

lm = LoginManager(app)
lm.login_view = 'login'

@lm.user_loader
def load_user(user_id):
    return db.load_user(user_id)

@lm.unauthorized_handler
def unauthorized_handler():
    return redirect(url_for('login.login'))


from app.classes.user import User
from app.classes.admin import Admin
from app.classes.staff import Staff
from app.classes.student import Student
from app.classes.guest import Guest

from app.classes.course import Course
from app.classes.offering import Offering
from app.classes.enrolment import Enrolment
from app.classes.survey import Survey
from app.classes.question import Question

from app.classes.surveyQuestion import SurveyQuestion
from app.classes.surveyQuestionMCQ import SurveyQuestionMCQ
from app.classes.surveyQuestionTXT import SurveyQuestionTXT

from app.classes.completion import Completion
from app.classes.response import Response
from app.classes.option import Option


# Checks all tables are created
db.create_all()

# Avoids running everything twice when debug mode is on
if (os.environ.get("WERKZEUG_RUN_MAIN") and os.environ.get("WERKZEUG_RUN_MAIN") == "true") or (os.environ.get("WERKZEUG_RUN_MAIN") == None and Config.debug == False):
    # Only loads from CSVs if asked to via command line argument 1
    # if len(sys.argv) > 1 and (str(sys.argv[1]) == '-ld' or str(sys.argv[1]) == '--load-defaults'):
    if '-ld' in sys.argv or '--load-defaults' in sys.argv:
        if Path(Config.DB).exists() and os.path.getsize(Config.DB) > 0:
            os.remove(Config.DB)
            db.create_all()
        # Needs to be initialised from CSVs
        db.load_defaults()

    if '-q' in sys.argv or '--quick-quit' in sys.argv:
        sys.exit()

@app.context_processor
def inject_now():
     return {'now': datetime.utcnow()}

app.start()
