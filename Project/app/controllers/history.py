from flask import Blueprint, redirect, url_for, request, render_template
from flask_login import login_required, current_user

history_blueprint = Blueprint('history', __name__)

@history_blueprint.route('/history/')
@login_required
def history():
	return render_template('history.html', past_logins=[])