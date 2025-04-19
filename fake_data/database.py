from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import DateTime, Date, LargeBinary

db = SQLAlchemy()


class Game(db.Model):
    __tablename__ = 'GameInfo'
    id = db.Column(db.String(10), primary_key=True)
    name = db.Column(db.Text, nullable=False)
    kp = db.Column(db.Text, nullable=False)
    date = db.Column(db.Integer, nullable=False) # 1 or 2
    session = db.Column(db.String(1), nullable=False) #A 上半 or B 下半
    rule = db.Column(db.Text, nullable=False)
    description = db.Column(db.Text)
    qq = db.Column(db.String(30))
    theme = db.Column(db.String(30))
    table = db.Column(db.String(5)) #
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
    group = db.Column(db.String(10)) #Normal, VIP
    date = db.Column(db.Integer, nullable=False) # 0 or 1 or 2

    @staticmethod
    def fetchAllPhone() -> list:
        phones = db.session.query(User.phone).all()
        return [phone[0] for phone in phones]

    @staticmethod
    def getDate(user: int) -> str:
        return db.session.get(User, user).date

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
    def isCorrect(username: str, password: str) -> bool:
        try:
            # 将输入转换为数据库存储格式
            phone_number = int(username)  # 将字符串转为Integer
            password_str = str(password).strip()  # 转为Text格式

            user = User.query.filter_by(phone=phone_number).first()

            return user and (user.password == password_str)

        except ValueError:
            print("手机号必须为纯数字")
            return False
        except Exception as e:
            print(f"验证错误: {str(e)}")
            return False


class UserToGameId(db.Model):
    __tablename__ = 'Register'
    user_id = db.Column(db.Integer, db.ForeignKey('UserInfo.phone'), primary_key=True)
    game_id = db.Column(db.Integer, db.ForeignKey('GameInfo.id'), primary_key=True)

    @staticmethod
    def getPlayersViaGame(game: int) -> list:
        return [player[0] for player in db.session.query(UserToGameId).filter_by(game_id=game).all()]

    @staticmethod
    def getGamesViaPlayer(user: int) -> list:
        return [player[0] for player in db.session.query(UserToGameId).filter_by(user_id=user).all()]


class Sponsor(db.Model):
    __tablename__ = 'Sponsor'
    id = db.Column(db.String(10), primary_key=True)
    advert_urls = db.Column(db.String(30), nullable=True)
