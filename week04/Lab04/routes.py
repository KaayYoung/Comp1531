from flask import Flask, redirect, render_template, request, url_for
from server import app
from csv_utilities import *

@app.route('/', methods=["GET", "POST"])
def index():
    if request.method == "POST":
        name = request.form["name"]
        zID = int(request.form["zID"])
        description = request.form["desc"]

        add_entry([name, zID, description])

        return redirect(url_for('hello'))
    return render_template('index.html')

@app.route('/Hello')
def hello():
    return render_template('Hello.html', all_users=get_all_entries())
