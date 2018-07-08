import os
from flask import Flask, redirect, url_for, request, render_template, jsonify, send_file
import json
import requests
import ast
import flask_login
import importlib
import parser
import time
import ssl

# enable SSL for https
context = ssl.SSLContext(ssl.PROTOCOL_SSLv23)
p   = 'keys/'
key = p + 'yelpcsv.key'
crt = p + 'yelpcsv.crt'
context.load_cert_chain(crt, key)

app = Flask(__name__)
app.secret_key = 'somestring'

login_manager = flask_login.LoginManager()

login_manager.init_app(app)

users = {'admin': {'password': 'you should use a database in prod.'}}

class User(flask_login.UserMixin):
    pass


@login_manager.user_loader
def user_loader(email):
    if email not in users:
        return

    user = User()
    user.id = email
    return user


@login_manager.request_loader
def request_loader(request):
    email = request.form.get('email')
    if email not in users:
        return

    user = User()
    user.id = email

    # DO NOT ever store passwords in plaintext and always compare password
    # hashes using constant-time comparison!
    user.is_authenticated = request.form['password'] == users[email][
        'password']

    return user


# TLS cert authority secret link
# replace with your own key or use http and ignore this altogether
sslkey = 'X.txt'
@app.route('/.well-known/pki-validation/%s'%(sslkey))
def sslk():
    return "<SECRET KEY -- THIS IS PRETTY HACKY> comodoca.com <another secret thing>"


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template("login.html")

    email = request.form['email']
    if email not in users:
        print("bad login")
        return render_template("login_bad.html")
    if request.form['password'] == users[email]['password']:
        user = User()
        user.id = email
        flask_login.login_user(user)
        return redirect(url_for('home_page'))

    return redirect(url_for('login'))


@app.route('/data')
def csv(term, location, radius, num):
    # make a csv file to send to the user
    outfile = "temp.csv"

    rawJSON = parser.requestResults(term, location, radius, num)
    outfile = parser.csvResults(outfile, rawJSON)
    return send_file(outfile, mimetype='csv', as_attachment=True, attachment_filename=str(time.time()) + ".csv")


@app.route('/logout')
def logout():
    flask_login.logout_user()
    return redirect(url_for('login'))


@app.route('/protected')
@flask_login.login_required
def protected():
    return 'Logged in as: ' + flask_login.current_user.id


@login_manager.unauthorized_handler
def unauthorized_handler():
    return redirect(url_for('login'))


@app.route('/', methods=['GET', 'POST'])
@flask_login.login_required
def home_page():
    if request.method == 'POST':
        term = request.form['term']
        location = request.form['location']
        radius = int(request.form['radius'])
        num = int(request.form['num'])

        if (request.form['submit'] == "search"):
            res = parser.requestResults(term, location, radius, num)
            return render_template("dashboard.html", _businesses=res['businesses'], term=term, loc=location, radius=radius, num=num)
        elif (request.form['submit'] == "csv"):
            return csv(term, location, radius, num)
    elif (request.method == 'GET'):
        return render_template("dashboard.html")


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=443, debug=True, threaded=True, ssl_context=context) 
    # thanks https://stackoverflow.com/a/28590266