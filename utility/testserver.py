#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import Flask, render_template, request
from subprocess import call


app = Flask(__name__)


@app.route("/")
def index():
    return render_template("testserver.html")


@app.route("/push", methods=["POST"])
def push():
    if request.method == 'POST':
        call(["./push.sh"])
        return "pushed."
    return "request method not allowed."


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
