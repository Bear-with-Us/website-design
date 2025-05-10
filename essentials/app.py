import json
import logging
from flask import Flask, render_template, url_for, request, session, redirect, jsonify
from sqlalchemy.exc import SQLAlchemyError
from database import db, User, Game, UserToGameId, Sponsor
from sqlalchemy.exc import IntegrityError
from datetime import datetime


logging.basicConfig(level=logging.INFO)
app = Flask('FlaskWeb')
app.config['SECRET_KEY'] = 'mysecretkey123'
#app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///VR3.db'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////home/deployer/app/essentials/VR3.db'
db.init_app(app)


@app.route('/')
def home():
    # First, get the user_id from session
    user_id = session.get('user_id')

    # Query the database for game information
    day1_gamesA = Game.query.filter_by(date=1, session='A').all()
    day2_gamesA = Game.query.filter_by(date=2, session='A').all()
    day1_gamesB = Game.query.filter_by(date=1, session='B').all()
    day2_gamesB = Game.query.filter_by(date=2, session='B').all()
    game_list = Game.query.all()

    # Calculate space reserved for each game
    space_reserved = {}
    for game in game_list:
        space_reserved[game.id] = db.session.query(UserToGameId).filter_by(game_id=game.id).count()

    # Get enrolled games for the logged-in user
    enrolled_game = []
    if user_id:
        enrolled_game = [game.id for game in game_list if game.id in UserToGameId.getGamesViaPlayer(user_id)]

    # Create JSON string for JavaScript
    enrolled_js = json.dumps(enrolled_game)

    return render_template("index.html",
                           day1_gamesA=day1_gamesA,
                           day2_gamesA=day2_gamesA,
                           day1_gamesB=day1_gamesB,
                           day2_gamesB=day2_gamesB,
                           space_reserved=space_reserved,
                           enrolled_game=enrolled_game,
                           enrolled_js=enrolled_js)


@app.route('/admin', methods=['POST', 'GET'])
def admin():
    # Check if user is logged in and has admin privileges
    user_id = session.get('user_id')

    # If not logged in as admin, redirect to home page
    if user_id != 20611741:
        # Option 1: Redirect to home page
        return redirect(url_for('home'))

        # Option 2: Or return an error message
        # return jsonify({"error": "未授权访问管理员页面"}), 403

    # Process file uploads if this is a POST request from an admin
    if request.method == 'POST':
        if "UserData" in request.files:
            user_file = request.files['UserData']
            data = json.load(user_file)
            for item in data:
                new_user = User(**item)
                db.session.add(new_user)
                try:
                    db.session.commit()
                    logging.info("✅ User data committed successfully.")
                except SQLAlchemyError as e:
                    db.session.rollback()
                    logging.info(f"❌ Commit failed: {e}")

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

        if "Register" in request.files:
            reg_file = request.files['Register']
            data = json.load(reg_file)
            for item in data:
                new_pair = UserToGameId(**item)
                db.session.add(new_pair)
                try:
                    db.session.commit()
                    print("✅ Registration data committed successfully.")
                except SQLAlchemyError as e:
                    db.session.rollback()
                    print(f"❌ Commit failed: {e}")

        if "SponsorData" in request.files:
            sponsor_file = request.files['SponsorData']
            data = json.load(sponsor_file)
            for item in data:
                from database import Sponsor  # Import if not already imported
                new_sponsor = Sponsor(**item)
                db.session.add(new_sponsor)
                try:
                    db.session.commit()
                    print("✅ Sponsor data committed successfully.")
                except SQLAlchemyError as e:
                    db.session.rollback()
                    print(f"❌ Commit failed: {e}")

    return render_template("admin.html")


@app.route('/get_block')
def get_block():
    user_id = session.get('user_id')
    logged_in = session.get('logged_in')

    print(f"get_block called: user_id={user_id}, logged_in={logged_in}")  # Debug

    if user_id is None or not logged_in:
        return jsonify({"html": render_template('guest.html')})

    user = db.session.get(User, user_id)
    if not user:
        print(f"User not found for id: {user_id}")  # Debug
        return jsonify({"html": render_template('guest.html')})

    date_val = User.getDate(user_id)
    group_val = User.getGroupViaPlayer(user_id)

    print(f"User details: id={user_id}, date={date_val}, group={group_val}")  # Debug

    if group_val == 'Normal' and date_val == 1:
        return jsonify({"html": render_template("Day1-normal.html", user=user)})
    elif group_val == 'Normal' and date_val == 2:
        return jsonify({"html": render_template("Day2-normal.html", user=user)})
    else:  # VIP case or date == 0
        return jsonify({"html": render_template("VIP.html", user=user)})


@app.route('/add_player', methods=['GET', 'POST'])
def add_player():
    # Get game_id from either query parameters (GET) or request body (POST)
    game_id = request.args.get('game_id')
    user_id = session.get('user_id')

    if not user_id:
        return jsonify({"error": "没有登陆呢喵╮(￣▽ ￣)╭刷新一下喵"}), 401

    # Get objects
    user = db.session.get(User, user_id)
    user_group = User.getGroupViaPlayer(user_id)
    game = db.session.get(Game, game_id)
    enrolled_game = len(UserToGameId.getGamesViaPlayer(user_id))
    if not user or not game:
        return jsonify({"error": "用户或游戏不存在喵"}), 400

    # Prevent Normal user from joining wrong day
    if user.group == "Normal" and user.date != game.date:
        return jsonify({"error": "只能报名你所属日期的团喵(=^-ω-^=)"}), 400

    # Check if user already registered for the same session on the same day
    existing_games = UserToGameId.getGamesViaPlayer(user_id)
    session_games = db.session.query(Game).filter(Game.id.in_(existing_games)).all()
    for g in session_games:
        if g.date == game.date and g.session == game.session:
            return jsonify({"error": "你已经报名了这个时间段的团喵(๑•́ ₃ •̀๑)"}), 400

    # Check if game is full
    current_players = db.session.query(UserToGameId).filter_by(game_id=game_id).count()
    if current_players >= game.max_pl:
        return jsonify({"error": "这个团已经满了喵(っ °Д °;)っ"}), 400

    # Check the max game limit
    if user_group == 'Normal' and enrolled_game > 0:
        return jsonify({"error": "您的限额到了喵(っ °Д °;)っ"}), 300
    if user_group == 'Vip' and enrolled_game >= 2:
        return jsonify({"error": "您的限额到了喵(っ °Д °;)っ"}), 300

    # Register user
    new_register = UserToGameId(game_id=game_id, user_id=user_id)
    try:
        db.session.add(new_register)
        db.session.commit()
        return jsonify({"message": "成功加入喵!φ(≧ω≦*)♪"}), 200
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "已经成功了喵！ヾ(≧∇≦*)ゝ"}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"服务器错误喵: {str(e)}"}), 500


@app.route('/remove_player', methods=['GET', 'POST'])
def remove_player():
    game_id = request.args.get('game_id')
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
    

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    if not data:
        return jsonify({"success": False, "error": "No data received"}), 400

    try:
        username = int(data.get('username'))
        password = data.get('password')

        print(f"Login attempt for user: {username}")  # Debug

        if username == 20611741 and password == "space.bilibili.com/20611741?spm_id_from=333.1387.follow.user_card.click":
            session['user_id'] = username
            session['logged_in'] = True
            return jsonify({"success": True, "redirect": url_for('admin')})

        if User.exist(username):
            if User.isCorrect(username, password):
                session['user_id'] = username
                session['logged_in'] = True
                print(f"Login successful for user: {username}")  # Debug
                return jsonify({"success": True})
            print(f"Incorrect password for user: {username}")  # Debug
            return jsonify({"success": False, "error": "Password incorrect"})

        print(f"User does not exist: {username}")  # Debug
        return jsonify({"success": False, "error": "User not found"})

    except Exception as e:
        print(f"Login error: {str(e)}")  # Debug
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/logout', methods=['GET'])
def logout():
    session.pop('user_id', None)
    session.pop('logged_in', None)
    return jsonify({'message': '登出了喵！(o゜▽゜)o☆[BINGO!]'})

if __name__ == "__main__":
    with app.app_context():
        db.create_all()

    app.run(debug=True, use_reloader=False)
