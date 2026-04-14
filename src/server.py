from flask import Flask

app = Flask(__name__)


@app.route("/")
def root():
    return "Hello, world!"


@app.route("/temperature")
def temperature():
    return "Temperature"


@app.route("/raw")
def raw():
    return "Raw"
