from flask import Blueprint, request, render_template, redirect, url_for, flash
from flask_login import login_required, login_user, logout_user, current_user
import time

import config as Config

from app.classes.user import User
from app.classes.enrolment import Enrolment
from app.classes.offering import Offering

lookup_blueprint = Blueprint('lookup', __name__)

lookup_obj = {}

# Set the route and accepted methods
@lookup_blueprint.route('/lookup/', methods=['GET', 'POST'])
def lookup():
    global lookup_obj
    if not Config.debug_features:
        flash(u'Restart server with flag "-df" for feature', 'error')
        return redirect(request.referrer) if request.referrer else redirect(index.index)
    
    t0 = time.time()

    # Avoids recreating lookup object every single time
    if not lookup_obj:
        lookup_obj = {}
        all_offerings = Offering.query.all()
        offerings = []
        for offering in all_offerings:
            query = str(offering.course_name) + ' ' + str(offering.semester)
            # If the enrolment's not in the lookup_obj, create list
            if query not in lookup_obj:
                lookup_obj[query] = []
            # For every enrolment in that course, adds it to the list
            for enrolment in offering.enrolments:
                user = User.query.get(enrolment.user_id)
                if user:
                    lookup_obj[query].append({'name':user.name, 'id':user.id, 'password':user.password, 'url':url_for("login.login", zid=user.id, password=user.password)})
            if not lookup_obj[query]:
                del lookup_obj[query]

    dt = time.time() - t0
    if(dt > 1):
        print(' * Time to generate lookup: ' + str(dt))
    return render_template('lookup.html', lookup=lookup_obj)
