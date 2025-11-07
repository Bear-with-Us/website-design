from flask import Blueprint, jsonify, request, session
from database import db, Game, UserToGameId  # adjust import if models moved

bp = Blueprint("game", url_prefix="/api/game")
@bp.get('/display/<int:day_num>/<char:session_num>')
def display(day_num:int, session_num):
    pass
@bp.get('/get_game/<string:game_id>')
def get_game_by_id(game_id):
    """get game by id"""
    pass