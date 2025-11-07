from flask import Blueprint, jsonify, request, session
from database import db, Game, UserToGameId  # adjust import if models moved

bp = Blueprint("user", url_prefix="/api/user")
@bp.get('/get_game/')
def get_game_by_user():
    """get games that current user is in"""
    user_id = session.get('user_id')
    pass
@bp.post('/remove_player/<string:game_id>')
def remove_player(game_id: str):
    user_id=session.get('user_id')
    if not user_id:
        return jsonify({"error": "未登录，无法退出喵( •̀ ω •́ )✧刷新一下喵"}), 401
    try:
        entry = UserToGameId.query.filter_by(game_id=game_id, user_id=user_id).first()
        if entry:
            db.session.delete(entry)
            db.session.commit()
            return jsonify({"message": "已成功退出该团喵~┗( T﹏T )┛"}), 200
        else:
            return jsonify({"message": "你还没有加入这个团喵ฅ(＾・ω・＾ฅ)"}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "服务器错误喵(╥﹏╥)"}), 500
