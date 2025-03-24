from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import DateTime, Date, LargeBinary

db = SQLAlchemy()


class Game(db.Model):
    __tablename__ = 'GameInfo'
    id = db.Column(db.Text, primary_key=True)
    name = db.Column(db.Text, nullable=False)
    kp = db.Column(db.Text, nullable=False)
    type = db.Column(db.String(10), nullable=False)
    time = db.Column(db.DateTime, nullable=False)
    rule = db.Column(db.Text, nullable=False)
    description = db.Column(db.Text)
    QR_code = db.Column(db.Text)
    max_pl = db.Column(db.Integer, nullable=False)

    @staticmethod
    def getGamesViaType(cls):
        """Returns a list of tuple: [(id, name, kp, type, time, description, QR_code)]"""
        return db.session.query(Game).filter_by(type=cls).all()

    @staticmethod
    def isClashedDate(id1, id2) -> bool:
        return db.session.get(Game, id1).type == db.session.get(Game, id2).type

    @staticmethod
    def isClashedTime(id1, id2) -> bool:
        return db.session.get(Game, id1).time == db.session.get(Game, id2).time

class User(db.Model):
    __tablename__ = 'UserInfo'
    phone = db.Column(db.Integer, primary_key=True)
    password = db.Column(db.Text, nullable=False)
    group = db.Column(db.Integer)

    @staticmethod
    def fetchAllPhone() -> list:
        phones = db.session.query(User.phone).all()
        return [phone[0] for phone in phones]

    @staticmethod
    def exist(name) -> bool:
        return db.session.query(User.phone).filter_by(phone=name).all() is not None

    @staticmethod
    def getGroupViaPlayer(user: int) -> int:
        player = db.session.get(User, user)
        return player.group if player else None

    @staticmethod
    def getAllPlayersViaGroup(grp: int) -> list:
        players = db.session.query(User.phone).filter_by(group=grp).all()
        return [player[0] for player in players]

    @staticmethod
    def removePlayer(user: int) -> None:
        player = db.session.get(User, user)
        if player:
            db.session.delete(player)
            db.session.commit()

    @staticmethod
    def isCorrect(username, password) -> bool:
        """Validate the password given the username"""
        return password == db.session(User.password).filter_by(phone=username)


class UserToGameId(db.Model):
    __tablename__ = 'Resgister'
    user_id = db.Column(db.Integer, db.ForeignKey('UserInfo.phone'), primary_key=True)
    game_id = db.Column(db.Integer, db.ForeignKey('GameInfo.game_id'), primary_key=True)

    @staticmethod
    def getPlayersViaGame(game: int) -> list:
        return [player[0] for player in db.session.query(UserToGameId).filter_by(game_id=game).all()]

    @staticmethod
    def getGamesViaPlayer(user: int) -> list:
        return [player[0] for player in db.session.query(UserToGameId).filter_by(user_id=user).all()]
