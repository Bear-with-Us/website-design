import json
import logging
from flask import Flask, render_template, url_for, request, session, redirect, jsonify
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
    urls = [f"static/banner/image{i}.png" for i in range(1, 4)]
    day1_gamesA = Game.query.filter_by(type='Day1', session='A').all()
    day2_gamesA = Game.query.filter_by(type='Day2', session='A').all()
    day1_gamesB = Game.query.filter_by(type='Day1', session='B').all()
    day2_gamesB = Game.query.filter_by(type='Day2', session='B').all()
    game_list = Game.query.all()
    space_reserved = {}
    for game in game_list:
        space_reserved[game.id] = db.session.query(UserToGameId).filter_by(game_id=game.id).count()
    return render_template("index.html", urls=urls, day1_gamesA=day1_gamesA, day2_gamesA=day2_gamesA,day1_gamesB=day1_gamesB, day2_gamesB=day2_gamesB, space_reserved=space_reserved)

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


@app.route('/add_player', methods=['POST'])
def add_player():
    data = request.get_json()
    game_id = data['id']
    user_id = session.get('user_id')

    if not user_id:
        return jsonify({"error": "没有登陆呢喵╮(￣▽ ￣)╭刷新一下喵"}), 401

    new_register = UserToGameId(game_id=game_id, user_id=user_id)

    try:
        db.session.add(new_register)
        db.session.commit()
        return jsonify({"message": "成功加入喵!φ(≧ω≦*)♪"}), 200

    # Now IntegrityError is properly imported and recognized
    except IntegrityError:
        db.session.rollback()
        logging.info("Duplicate game registration attempted")
        return jsonify({"error": "已经成功了喵！ヾ(≧∇≦*)ゝ"}), 400

    except Exception as e:
        db.session.rollback()
        logging.error(f"Error: {str(e)}")
        return jsonify({"error": "服务器没连上喵╥﹏╥..."}), 500

@app.route('/remove_player', methods=['POST'])
def remove_player():
    data = request.get_json()
    game_id = data['id']
    user_id = session.get('user_id')

    if not user_id:
        return jsonify({"error": "未登录，无法退出喵( •̀ ω •́ )✧刷新一下喵"}), 401

    try:
        entry = UserToGameId.query.filter_by(game_id=game_id, user_id=user_id).first()
        if entry:
            db.session.delete(entry)
            db.session.commit()
            return jsonify({"message": "已成功退出该团喵~┗( T﹏T )┛"}), 200
        else:
            return jsonify({"error": "你还没有加入这个团喵ฅ(＾・ω・＾ฅ)"}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "服务器错误喵(╥﹏╥)"}), 500

@app.route('/Day2', methods=['POST', 'GET'])
def day2():
    return render_template("Day2.html")


@app.route('/login', methods=['POST', 'GET'])
def login():
    next_page = request.args.get('next')  # <-- track original destination

    if 'user_id' in session:
        return redirect(next_page or url_for('home'))  # Go to original or home

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if username == "space.bilibili.com/20611741?spm_id_from=333.1387.follow.user_card.click" and password == "20611741":
            session['user_id'] = username
            return redirect(next_page or url_for('admin'))

        if User.exist(username):
            if User.isCorrect(username=username, password=password):
                session['user_id'] = username
                return redirect(next_page or url_for('home'))
            else:
                return redirect(url_for('login', next=next_page))
        else:
            return redirect(url_for('login', next=next_page))

    return render_template("Sign in.html")

@app.route('/logout', methods=['GET'])
def logout():
    session.pop('user_id', None)
    session.pop('username', None)
    return jsonify({'message': '登出了喵！(o゜▽゜)o☆[BINGO!]'})

if __name__ == "__main__":
    with app.app_context():
        initialise_db()

    app.run(debug=True, use_reloader=False)
