from flask import Blueprint, redirect, url_for, request, render_template, flash
from flask_login import login_required, current_user
import uuid

from app import db as DB
from app.classes.question import Question

questions_blueprint = Blueprint('questions', __name__)

mandatory_options = {True:'Mandatory', False:'Optional'}

@questions_blueprint.route('/questions/', methods=['GET', 'POST'])
@login_required
def questions():
    if not current_user.admin:
        flash(u"Admin access only", 'error')
        return redirect(url_for('index.index'))
    if request.method == "POST":
        question_pool = Question.query.all()
        if 'question-to-delete' in request.form:
            to_delete = request.form.get("question-to-delete")
            question = Question.query.filter(Question.id == to_delete).first()
            if question:
                question.remove_question()
        elif 'question-to-add' in request.form:
            to_add = request.form.get("question-to-add")
            question_mandatory = request.form.get("question_mandatory")
            question = Question(to_add, question_mandatory == "True")
            try:
                question.add_question()
            except:
                pass
        elif 'add-option' in request.form:
            pass
    return render_template('questions.html', questions=Question.query.all(), mandatory_options=mandatory_options)


