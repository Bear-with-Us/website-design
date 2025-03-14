from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Game(db.Model):
    __tablename__ = 'GameInfo'
    game_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), nullable=False)
    reference = db.Column(db.String(255))  # URL-friendly size

    def getReferenceURL(self, id: int) -> str:
        game = db.session.get(Game, id)
        return game.reference if game and game.reference else None

class User(db.Model):
    __tablename__ = 'UserInfo'
    phone = db.Column(db.Integer, primary_key=True)
    password = db.Column(db.Text, nullable=False)
    group = db.Column(db.Integer)

    def fetch_all_phone(self) -> list:
        phones = db.session.query(User.phone).all()
        return [phone[0] for phone in phones]

    def getGroupViaPlayer(self, user: int) -> int:
        player = db.session.get(User, user)
        return player.group if player else None

    def getAllPlayersViaGroup(self, grp: int) -> list:
        players = db.session.query(User.phone).filter_by(group=grp).all()
        return [player[0] for player in players]

    def removePlayer(self, user: int) -> None:
        player = db.session.get(User, user)
        if player:
            db.session.delete(player)
            db.session.commit()

class Register(db.Model):
    __tablename__ = 'Register'
    user_id = db.Column(db.Integer, db.ForeignKey('UserInfo.phone'), primary_key=True)  # ✅ Corrected
    game_id = db.Column(db.Integer, db.ForeignKey('GameInfo.game_id'), primary_key=True)  # ✅ Corrected

    def getPlayersPerGame(self, game: int) -> int:
        return db.session.query(Register).filter_by(game_id=game).count()

    def getGamesPerPlayer(self, user: int) -> int:
        return db.session.query(Register).filter_by(user_id=user).count()