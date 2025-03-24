import json
import logging
from flask import Flask, render_template, url_for, request, session, redirect
from sqlalchemy.exc import SQLAlchemyError
from database import db, User, Game, UserToGameId
import flask

from flask_sqlalchemy import SQLAlchemy

logging.basicConfig(level=logging.INFO)
app = Flask('FlaskWeb')
app.config['SECRET_KEY'] = 'mysecretkey123'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///VR3.db'
db.init_app(app)


def initialise_db():
    db.create_all()


@app.route('/')
def home():
    # If user is logged in, greet them; otherwise prompt to log in
    # session is a dictionary containing all information stored by the current user
    if 'user_id' in session:
        return render_template("index.html")
    else:
        # return flask.redirect(url_for('login'))
        return render_template("web.html")


@app.route('/admin', methods=['POST', 'GET'])
def admin():
    """admin page that allows:
    1. upload files to the database
    2. TBD"""

    # Upload the given file to the User table
    if "UserData" in request.files:
        user_file = request.files['UserData']
        data = json.load(user_file)
        for item in data:
            new_user = User(**item)
            db.session.add(new_user)
            try:
                db.session.commit()
                logging.info("✅ Game data committed successfully.")
            except SQLAlchemyError as e:
                db.session.rollback()
                logging.info(f"❌ Commit failed: {e}")

    # Upload the given file to the Game table
    if "GameData" in request.files:
        game_file = request.files['GameData']
        data = json.load(game_file)
        for item in data:
            new_game = Game(**item)
            db.session.add(new_game)
            try:
                db.session.commit()
                print("✅ Game data committed successfully.")
            except SQLAlchemyError as e:
                db.session.rollback()
                print(f"❌ Commit failed: {e}")

    # Upload to the register with data in the given file
    if "Register" in request.files:
        reg_file = request.files['Register']
        data = json.load(reg_file)
        for item in data:
            new_pair = UserToGameId(**item)
            db.session.add(new_pair)
            try:
                db.session.commit()
                print("✅ Game data committed successfully.")
            except SQLAlchemyError as e:
                db.session.rollback()
                print(f"❌ Commit failed: {e}")

    return render_template("admin.html")


@app.route('/day1', methods=['POST', 'GET'])
def day1():
    """This is the page for day1 games"""
    game_list = db.query(Game).all()
    return render_template("day1.html", game_list=game_list)


@app.route('/day2', methods=['POST', 'GET'])
def day2():
    """This is the page for day2 games"""
    return render_template("day2.html")


@app.route('/login', methods=['POST', 'GET'])
def login():
    """Login page"""

    # Check if the user is already signed in
    if 'user_id' in session:
        return render_template("index.html")

    # Login in system
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if username == "123" and password == "123":
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
    with app.app_context():
        initialise_db()

    app.run(debug=True, use_reloader=False)
