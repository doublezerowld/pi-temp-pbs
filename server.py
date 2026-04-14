from flask import Flask

app = Flask("pi-temp")


@app.route("/")
def root():
    return "Hello, world!"
