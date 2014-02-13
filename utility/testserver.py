#!/usr/bin/env python
# -*- coding: utf-8 -*-

import datetime
from flask import Flask, render_template, request
from subprocess import call


PASSWORD = 'onigiri'


app = Flask(__name__)


@app.route("/")
def index():
    return render_template("testserver.html")


@app.route("/push", methods=["POST"])
def push():
    if request.method == 'POST':
        if request.form['password'] != PASSWORD:
            return 'not allowed.'

        env_file = None
        if request.form['target'] == 'prod':
            env_file = './push.env.prod'
        elif request.form['target'] == 'dev':
            env_file = './push.env.dev'
        call(["./push.sh", env_file])

        return "pushed.({})".format(datetime.datetime.now())
    return "request method not allowed."


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
