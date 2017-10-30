from server import app
from flask import render_template, request
from utilities import convert_to_list
from sorts import BubbleSort

@app.route('/', methods=["GET", "POST"])
def index():
    if request.method == "POST":
        numbers = request.form["list"]
        numbers = convert_to_list(numbers)
        all_changes = BubbleSort(numbers)
        return render_template('show.html', all_changes=all_changes)

    return render_template('input.html')

