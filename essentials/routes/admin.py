from flask import Blueprint, jsonify, request, session, current_app
from database import db, Game, UserToGameId, Sponsor, User# adjust import if models moved
from sqlalchemy.exc import SQLAlchemyError
bp = Blueprint("admin", url_prefix="/api/admin")

@bp.post('/user/add_users')
def add_users():
    """add users to database"""
    info = request.get_json(silent=True)
    if not info:
        return jsonify({"message": "空的文件喵", "ok": False}), 400
    if not isinstance(info, list):
        return jsonify({"message": "格式错误喵，应为JSON", "ok": False}), 400
    try:
        new_usr = [User(**item) for item in info]
        db.session.add_all(new_usr)
        db.session.commit()
        return jsonify({
            "message": f"成功添加 {len(new_usr)} 个赞助商喵! φ(≧ω≦*)♪",
            "ok": True
        }), 201
    except SQLAlchemyError as e:
        db.session.rollback()
        current_app.logger.error(f"❌ Commit failed: {e}")
        return jsonify({
            "message": "数据库出错喵(っ °Д °;)っ",
            "ok": False,
            "error": str(e)
        }), 500


@bp.post('/sponsor/add_sponsors/')
def add_sponsors():
    """add sponsors given a json file"""
    info = request.get_json(silent=True)
    if not info:
        return jsonify({"message": "空的文件喵", "ok": False}), 400
    if not isinstance(info, list):
        return jsonify({"message": "格式错误喵，应为JSON", "ok": False}), 400
    try:
        new_sp = [Sponsor(**item) for item in info]
        db.session.add_all(new_sp)
        db.session.commit()
        return jsonify({
            "message": f"成功添加 {len(new_sp)} 个赞助商喵! φ(≧ω≦*)♪",
            "ok": True
        }), 201
    except SQLAlchemyError as e:
        db.session.rollback()
        bp.logger.error(f"❌ Commit failed: {e}")
        return jsonify({
            "message": "数据库出错喵(っ °Д °;)っ",
            "ok": False,
            "error": str(e)
        }), 500

@bp.post('/register/add_register/<int:user_id>/<string:game_id>')
def add_register(user_id:int, game_id:str):
    """
    Adding single connection with a given user and game
    :param game_id:string
    :param user_id:int
    :return: A tuple of dict with state message and status, http status code
    """
    try:
        db.session.add(UserToGameId(user_id=user_id, game_id=game_id))
        db.session.commit()
        return jsonify({"message": "success","ok": True}),  200
    except SQLAlchemyError as e:
        db.session.rollback()
        current_app.logger.error(f"❌ Commit failed: {e}")
        return jsonify({
            "message": "数据库出错喵(っ °Д °;)っ",
            "ok": False,
            "error": str(e)
        }), 500
@bp.post('/register/add_registers')
def add_registers(user_id, game_id):
    """Connect users to games"""
    info = request.get_json(silent=True)
    if not info:
        return jsonify({"message": "空的文件喵", "ok": False}), 400
    if not isinstance(info, list):
        return jsonify({"message": "格式错误喵，应为JSON", "ok": False}), 400
    try:
        new_reg = [UserToGameId(**item) for item in info]
        db.session.add_all(new_reg)
        db.session.commit()
        return jsonify({
            "message": f"成功添加 {len(new_reg)} 个报名关联喵! φ(≧ω≦*)♪",
            "ok": True
        }), 201

    except SQLAlchemyError as e:
        db.session.rollback()
        current_app.logger.error(f"❌ Commit failed: {e}")
        return jsonify({
            "message": "数据库出错喵(っ °Д °;)っ",
            "ok": False,
            "error": str(e)
        }), 500

@bp.post('/game/add_games')
def add_games():
    """
    operations that add games from a json file to the database
    """
    # Parse JSON body
    info = request.get_json(silent=True)
    if not info:
        return jsonify({"message": "空的文件喵", "ok": False}), 400
    # Ensure we got a list of games
    if not isinstance(info, list):
        return jsonify({"message": "格式错误喵，应为JSON", "ok": False}), 400
    try:
        # Convert each dict to a Game object
        new_games = [Game(**item) for item in info]
        db.session.add_all(new_games)
        db.session.commit()
        return jsonify({
            "message": f"成功添加 {len(new_games)} 个游戏喵! φ(≧ω≦*)♪",
            "ok": True
        }), 201

    except SQLAlchemyError as e:
        db.session.rollback()
        current_app.logger.error(f"❌ Commit failed: {e}")
        return jsonify({
            "message": "数据库出错喵(っ °Д °;)っ",
            "ok": False,
            "error": str(e)
        }), 500
