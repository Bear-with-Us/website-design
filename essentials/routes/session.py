from flask import Blueprint, jsonify, request, session
from database import db, Game, UserToGameId, User # adjust import if models moved
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from sqlalchemy.exc import IntegrityError
bp = Blueprint("session", url_prefix="/api/session")

@bp.post('/reg_player/<string:game_id>')
def reg_player(game_id: str):
    """
    add a play to a game.
    :param game_id: The unique identifier of the game.
    :return: A dictionary containing:
        - message (str): Report the reason of errors or success confirmation text.
        - ok (bool): Indicates whether the operation was successful.
    """
    current_time = datetime.now(ZoneInfo("Asia/Shanghai"))
    VIP_starting_time = datetime(2026, 1, 8, 20, 0, 0, tzinfo=ZoneInfo("Asia/Shanghai"))
    Normal_starting_time = datetime(2026, 1, 10, 12, 0, 0, tzinfo=ZoneInfo("Asia/Shanghai"))
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"message": "没有登陆呢喵╮(￣▽ ￣)╭刷新一下喵","ok": False}), 401

    # Get objects
    user = db.session.get(User, user_id)
    user_group = User.getGroupViaPlayer(user_id)
    game = db.session.get(Game, game_id)
    enrolled_game = len(UserToGameId.getGamesViaPlayer(user_id))
    if not user or not game:
        return jsonify({"message": "用户或游戏不存在喵"}), 400

    # Prevent Normal user from joining wrong day
    if user.group == "Normal" and user.date != game.date:
        return jsonify({"message": "只能报名你所属日期的团喵(=^-ω-^=)","ok":False}), 400

    # Check if user already registered for the same session on the same day
    existing_games = UserToGameId.getGamesViaPlayer(user_id)
    session_games = db.session.query(Game).filter(Game.id.in_(existing_games)).all()
    for g in session_games:
        if g.date == game.date and g.session == game.session:
            return jsonify({"message": "你已经报名了这个时间段的团喵(๑•́ ₃ •̀๑)","ok":False}), 400

    # Check if game is full
    current_players = db.session.query(UserToGameId).filter_by(game_id=game_id).count()
    if current_players >= game.max_pl:
        return jsonify({"message": "这个团已经满了喵(っ °Д °;)っ","ok":False}), 400

    # Check the max game limit
    if user_group == 'Normal' and enrolled_game >=1:
        db.session.rollback()
        return jsonify({"message": "您的限额到了喵(っ °Д °;)っ","ok":False}), 300
    if user_group == 'VIP' and enrolled_game >= 2:
        db.session.rollback()
        return jsonify({"message": "您的限额到了喵(っ °Д °;)っ","ok":False}), 300

    #Check if current time is the starting time
    if current_time < Normal_starting_time and user_group == 'Normal':
        db.session.rollback()
        return jsonify({"message": "还没到时间呢喵(っ °Д °;)っ","ok":False}), 400
    if current_time < VIP_starting_time and user_group == 'VIP':
        db.session.rollback()
        return jsonify({"message": "还没到时间呢喵(っ °Д °;)っ","ok":False}), 400

    # Register user
    new_register = UserToGameId(game_id=game_id, user_id=user_id)
    try:
        db.session.add(new_register)
        db.session.commit()
        return jsonify({"message": "成功加入喵!φ(≧ω≦*)♪","ok":True},), 200
    except IntegrityError:
        db.session.rollback()
        return jsonify({"message": "已经成功了喵！ヾ(≧∇≦*)ゝ","ok":True}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"服务器错误喵: {str(e)}","ok":False}), 500
@bp.post('/login')
def login():
    data = request.get_json()
    if not data:
        return jsonify({"ok": False, "message": "No data received"}), 400
    try:
        username = int(data.get('username'))
        password = data.get('password')

        print(f"Login attempt for user: {username}")  # Debug

        if User.exist(username):
            if User.isCorrect(username, password):
                session['user_id'] = username
                session['logged_in'] = True
                return jsonify({"ok": True,"message":f"Login successful for user: {username}"})
            print(f"Incorrect password for user: {username}")  # Debug
            return jsonify({"ok": False, "message": "Password incorrect"}), 400

        print(f"User does not exist: {username}")  # Debug
        return jsonify({"ok": False, "message": "User not found"}), 404

    except Exception as e:
        print(f"Login error: {str(e)}")  # Debug
        return jsonify({"message": str(e),"ok":False}), 500
    
@bp.get('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('logged_in', None)
    return jsonify({'message': '登出了喵！(o゜▽゜)o☆[BINGO!]',"ok":True})

