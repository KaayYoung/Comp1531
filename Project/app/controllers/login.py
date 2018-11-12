from flask import Blueprint, request, render_template, redirect, url_for, flash
from flask_login import login_required, login_user, logout_user, current_user
import math
from app.classes.user import User
from app.classes.guest import Guest
from app.classes.course import Course
from app.classes.offering import Offering

from app import db as DB

import time
import sys

login_blueprint = Blueprint('login', __name__)

# Set the route and accepted methods
@login_blueprint.route('/login/', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(request.args.get('next') or url_for('index.index'))

    offerings = {}
    for course in Course.query.all():
        offerings[course.name] = []
        for offering in course.offerings:
            offerings[course.name].append(offering.semester)

    if request.method == "POST":
        # Determines action for inputted zID/password
        if 'login' in request.form:
            zID = request.form["zID"]
            password = request.form["password"]
            try:
                process_login(zID, password)
            except ValueError:
                flash(u'Log in failed', 'error')
                return redirect(url_for('login.login', zid=zID))
            else:
                flash(u'Log in successful', 'done')
                return redirect(request.args.get('next') or url_for('index.index'))

        elif 'register' in request.form:
            password = request.form["password-reg"]
            course_name = request.form["course"]
            semester = request.form["offering"]
            offering_request = Offering.query.filter_by(course_name = course_name, semester = semester).first()

            zID = request.form["zID-reg"]
            if int(zID) > (math.pow(2, 32) - 1):
                flash(u'Invalid Username', 'error')
                return redirect(url_for('login.login', zid_reg=zID, course=course_name, semester=semester))

            try:
                DB.register_user(Guest(id=zID, password=password, offering_request=offering_request.id, name='Guest ' + zID))
            except ValueError:
                flash(u'Username taken', 'error')
                return redirect(url_for('login.login', zid_reg=zID, course=course_name, semester=semester))
            else:
                flash(u'Awaiting account activation', 'done')
                # Redirects back to index for an admin account to log in
                return redirect(request.args.get('next') or url_for('index.index'))

    return render_template('login.html', zid=request.args.get('zid'), password=request.args.get('password'), zid_reg=request.args.get('zid_reg'), password_reg=request.args.get('password_reg'), offerings=offerings, courses=Course.query.all(), predetermined_course_name=request.args.get('course'), predetermined_course_offering=request.args.get('semester'))

def process_login(id, password):
    user = User.query.filter(User._id == int(id)).first()

    valid = False
    if user:
        valid = user.check_login(password)
    
    if valid:
        # Does actual login with flask.login_manager
        login_user(user)
    else:
        # Raises exception
        raise ValueError('Login details invalid', str(id), password)

@login_blueprint.route('/logout/', methods=['GET'])
@login_required
def logout():
    logout_user()
    flash(u'Logged out', 'done')
    return redirect(request.args.get('next') or url_for('index.index'))
