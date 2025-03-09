from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Game(db.model):
    __tablename__ = 'GameInfo'
    game_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), nullable=False)
    reference = db.Column(db.Text, )
    reg = db.relationship("Game", backref='game')

    def getReferenceURL(self, id):
        pass

class User(db.model):
    __tablename__ = 'UserInfo'
    phone = db.Column(db.Integer, primary_key=True)
    password = db.Column(db.Text, nullable=False)
    group = db.Column(db.Integer)
    reg = db.relationship('User', backref='user')

    def fetch_all_phone(self):
        pass

    def getGroupViaPlayer(self, user):
        pass

    def getAllPlayersViaGroup(self, grp):
        pass

    def getPlayerViaPhone(self, user):
        pass

    def removePlayer(self,user):
        pass



class Register(db.model):
    __tablename__ = 'Register'
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    game_id = db.Column(db.Integer, db.ForeignKey('game.id'))

    def getPlayersPerGame(self, game):
        pass

    def getGamesPerPlayer(self, user):
        pass
