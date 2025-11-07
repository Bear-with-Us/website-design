
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from database import User, UserToGameId

engine = create_engine("sqlite:////home/deployer/app/instance/VR3.db")

def main():
    with Session(engine) as s:
        unsigned = []
        all_users = s.query(User).all()
        for p in all_users:
            if len(s.query(UserToGameId).filter_by(user_id=p.phone).all()) == 0:
                unsigned.append(p.phone)
        print(unsigned)


if __name__ == "__main__":
    main()