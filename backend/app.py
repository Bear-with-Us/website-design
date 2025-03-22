from flask import Flask, render_template, url_for, request, session, redirect
from database import db, User, Game, UserToGameId
import flask
from werkzeug.security import check_password_hash
from flask_sqlalchemy import SQLAlchemy

app = Flask('FlaskWeb')
app.config['SECRET_KEY'] = 'mysecretkey123'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///VR3.db'


@app.route('/')
def home():
    # If user is logged in, greet them; otherwise prompt to log in
    # session is a dictionary containing all information stored by the current user
    if 'user_id' in session:
        return render_template("index.html")
    else:
        #return flask.redirect(url_for('login'))
        return render_template("index.html")


@app.route('/admin', methods=['POST', 'GET'])
def admin():
    return render_template("admin.html")


@app.route('/day1', methods=['POST', 'GET'])
def day1():
    return render_template("day1.html")


@app.route('/day2', methods=['POST', 'GET'])
def day2():
    return render_template("day2.html")


@app.route('/login', methods=['POST', 'GET'])
def login():
    if 'user_id' in session:
        return render_template("index.html")

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if username == " " and password == " ":
            return redirect("admin")
        if User.exist(username):
            if User.isCorrect(username=username, password=password):
                session['user_id'] = username
                return render_template("index.html")
            else:
                return redirect('login', 401, "密码错误")
        else:
            return redirect("login", 404, "用户名错误")
    return render_template("Sign in.html")


@app.route('/logout')
def logout():
    # Clear user session
    session.pop('user_id', None)
    session.pop('username', None)
    return flask.redirect(url_for('login'))


if __name__ == "__main__":
    app.run(debug=True)
