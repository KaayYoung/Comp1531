from flask import Blueprint, redirect, url_for
from flask_login import login_required

index_blueprint = Blueprint('index', __name__)

@index_blueprint.route('/', methods=["GET", "POST"])
@login_required
def index():
	return redirect(url_for('dashboard.dashboard') or url_for('login.login'))