from flask import Flask, redirect, render_template, request, url_for
from server import app, cal
from math import sin, cos, tan, log, sqrt

ACTIONS = [
    "1", "2", "3", "C",
    "4", "5", "6", "+",
    "7", "8", "9", "-",
    "0", "*", "/", "=",
    "(", ")", "sin", "tan",
    "cos", "log", "sqrt", "CE"
]
calculator_display = []

@app.route("/")
def calculator():
    return render_template("calculator.html", actions=ACTIONS, display="".join(calculator_display))

@app.route("/calc_action/<action>")
def calculator_action(action):
    global calculator_display
    if action == "C":
        calculator_display.pop()
    elif action == "CE":
        calculator_display = []
    elif action == "=":
        calculator_display = [str(eval("".join(calculator_display)))]
    else:
        calculator_display.append(action)
    return redirect(url_for("calculator"))



