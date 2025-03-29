import json
import logging
from flask import Flask, render_template, url_for, request, session, redirect
from sqlalchemy.exc import SQLAlchemyError
from database import db, User, Game, UserToGameId
from sqlalchemy.exc import IntegrityError
from datetime import datetime


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
        return redirect(url_for('login'))



@app.route('/admin', methods=['POST', 'GET'])
def admin():
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

    if "GameData" in request.files:
        game_file = request.files['GameData']
        data = json.load(game_file)
        for item in data:
            item["time"] = datetime.fromisoformat(item['time'])
            new_game = Game(**item)
            db.session.add(new_game)
            try:
                db.session.commit()
                print("✅ Game data committed successfully.")
            except SQLAlchemyError as e:
                db.session.rollback()
                print(f"❌ Commit failed: {e}")

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


@app.route('/Day1', methods=['POST', 'GET'])
def day1():
    game_list = Game.query.filter_by(type='Day2').all()
    #game_list = db.query(Game).filter_by(type='Day1').all()
    space_reserved = {}
    for game in game_list:
        space_reserved[game.id] = db.session.query(UserToGameId).filter_by(game_id=game.id).count()
    logging.info(game_list)
    return render_template("Day1.html", game_list=game_list, space_reserved=space_reserved)


def add_player():
    data = request.get_json()
    game_id = data['id']
    user_id = session.get('user_id')

    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401

    new_register = UserToGameId(game_id=game_id, user_id=user_id)

    try:
        db.session.add(new_register)
        db.session.commit()
        return jsonify({"message": "Successfully registered!"}), 200

    # Now IntegrityError is properly imported and recognized
    except IntegrityError:
        db.session.rollback()
        logging.info("Duplicate game registration attempted")
        return jsonify({"error": "Already registered for this game"}), 400

    except Exception as e:
        db.session.rollback()
        logging.error(f"Error: {str(e)}")
        return jsonify({"error": "Server error"}), 500
@app.route('/Day2', methods=['POST', 'GET'])
def day2():
    return render_template("Day2.html")


@app.route('/login', methods=['POST', 'GET'])
def login():
    if 'user_id' in session:
        return render_template("index.html")

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
    #return render_template("index.html")

@app.route('/logout')
def logout():
    # Clear user session
    session.pop('user_id', None)
    session.pop('username', None)
    return redirect(url_for('login'))


if __name__ == "__main__":
    with app.app_context():
        initialise_db()

    app.run(debug=True, use_reloader=False)
