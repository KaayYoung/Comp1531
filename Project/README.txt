# COMP1531 Group Assignment
Authors:
* Jeremy Fu
* Tom Little
* Randy Tjang
* Jingshi Yang

This is best viewed as a .md file rather than a .txt as spec requests.

## 1. Dependencies
* click==6.7
* Flask==0.12.2
* Flask-Login==0.4.0
* Flask-SQLAlchemy==2.3.2
* itsdangerous==0.24
* Jinja2==2.9.6
* MarkupSafe==1.0
* SQLAlchemy==1.1.14
* Werkzeug==0.12.2

### Useful commands
To update dependencies: ```pip3 freeze > requirements.txt```

To install dependencies: ```pip3 install -r requirements.txt```

## 2. Run instructions
### Server
#### Auto Setup
```
chmod 744 setup.sh
./setup.sh
```
Run the above to create virtual environment, enter it, install all dependencies and import data from CSVs to the database. For further options with regard to import behaviour, see [Manual Setup](#manual-setup)
then run 
```
python3 run.py
```

#### Manual Setup
If env does not exist, run ```virtualenv env && . env/bin/activate && pip3 install -r requirements.txt```

else run ```source env/bin/activate``` to enter virtual environment.

then run ```python3 run.py``` (**by default doesn't import CSVs**, see below for further information) to activate the server.

It is advised that ```python3 run.py -ld``` is run if server has never been run. One should then stop the server (auto-reloader will reset db (reload from defaults) if a change in the python code is detected during runtime), then ```python3 run.py``` used for further runs.

#### Command-line arguments
Note that ```run.py``` accepts a number of command line arguments:
* ```-ld``` or ```--load-defaults``` resets the database and imports all data from CSVs provided in folder data.
* ```-df``` or ```--debug-features``` enables extra features useful for debugging, such as a user/password lookup via enrolment on the login page as well as a debug page to generate random surveys are varying phases, and random responses for those which are generated as closed
* ```-q``` or ```--quick-quit``` will just run the server then quit it after initialisation - useful if used with ```-ld``` in order to just setup the server then quit
* ```-h``` or ```--help``` will show information on how to use command line arguments with the run.py script

### Access
Visit [```http://127.0.0.1:5001```](http://127.0.0.1:5001) for site access. Note that ```http://localhost:5001``` is equivalent.

## 3. Tests
**Ensure server has been stopped before proceeding.**

**IMPORTANT:**
Move run_tests.py and tests.py inside the same directory as run.py, it is imperative that these files are at the root of the
application directory.

Run ```python3 run_tests.py``` (**not tests.py** as run_tests does handling to prevent production db corruption)

Note that this script first backs up any existing database.db to database.backup.db, runs the tests on a temporary db empty, then
restores the previous database.

(For convenience, the below list can be autoupdated with the command ```python3 update_tests_docs.py```)

The following tests are contained in tests.zip:
* TestCourse
  - test_init
  - test_duplicate_course
  - test_add_offering
  - test_add_offering_duplicate
* TestOffering
  - test_init
  - test_get_surveys
  - test_add_survey
* TestEnrolment
  - test_enrol_non_existent_user_in_course_offering
  - test_enrol_user_in_duplicate_enrolment
  - test_enrol_user_in_single_course_offering
  - test_enrol_user_in_multiple_course_offerings
* TestSurvey
  - test_create_survey_with_0_questions
  - test_create_survey_with_duplicate_questions
  - test_remove_survey_question
  - test_create_survey_with_questions
  - test_create_duplicate_survey_for_same_course_offering
  - test_create_survey_should_be_in_review_phase_once_created
  - test_reviewed_survey_is_set_to_open_phase
  - test_open_survey_is_set_to_close_phase
  - test_delete_survey
* TestQuestion
  - test_create_mandatory_question
  - test_create_optional_question
  - test_create_question_with_empty_text
  - test_create_question_with_invalid_mandatory_or_optional_flag
  - test_create_duplicate_question
  - test_remove_question
* TestUserAuthentication
  - test_check_login_with_correct_credentials
  - test_check_login_with_incorrect_credentials
  - test_check_student_login_associated_with_student_account
  - test_check_staff_login_associated_with_staff_account
  - test_check_admin_login_associated_with_admin_account
  - test_check_guest_login_associated_with_guest_account
  - test_check_guest_registration_with_invalid_offering_association
  - test_register_duplicate_user
* TestResponse
  - test_response_text_with_text_question
  - test_response_option_with_text_question
  - test_response_option_with_mcq_question
  - test_response_text_with_mcq_question
  - test_response_with_all_questions_completed
  - test_response_does_not_have_student_information
  - test_response_successfully_completed_by_student_is_stored_in_completion_table

## 4. Misc
* [User stories and other documentation](https://drive.google.com/drive/folders/0BzeojAacFyyrejJtTFFERXprTmM?usp=sharing)

* Flask flash system usage: ```flash(u'message', 'icon')```

* [Read for styling info for current css used](http://materializecss.com/)

* [JS used for visualisation](http://www.chartjs.org/docs/latest/)

* [Read for drag and drop info](https://supraniti.github.io/Lean-Mean-Drag-and-Drop/)

LMDD Options default values (NOTE SCRIPT MUST BE BEFORE ELEMENT):

```
lmdd.set(document.getElementById('scope-draggable'), {
	containerClass:'lmdd-container',
	draggableItemClass: 'lmdd-draggable',
	handleClass: false,
	dragstartTimeout: 50,
	calcInterval: 200,
	revert: true,
	nativeScroll: false,
	mirrorMinHeight: 100,
	mirrorMaxWidth: 500,
	positionDelay: false,
	dataMode: false
});
```

### ER Diagram generator
#### Method 1 (preferred)
Ensure dot and pylint are installed, then run:
```
pyreverse -o png -p Pyreverse app
```

#### Method 2
Install generator with:
```
brew install eralchemy
```
Then run to generate diagram:
```
eralchemy -i sqlite:///database/database.db -o erd_from_sqlite.pdf
```

### Server keys
NOTE: These are not in use currently


Pass phrase for server.key: ```WayneWobke```

Challenge password for server.cse: ```WayneWobke```

Pass phras for server.key.org: ```WayneWobke```


[Commands](http://kracekumar.com/post/54437887454/ssl-for-flask-local-development):
```
openssl genrsa -des3 -out server.key 1024
openssl req -new -key server.key -out server.csr
cp server.key server.key.org
openssl rsa -in server.key.org -out server.key
openssl x509 -req -days 365 -in server.csr -signkey server.key -out server.crt
```

