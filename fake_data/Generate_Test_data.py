from faker import Faker
import random
from database import db, Game, User, UserToGameId, Sponsor
from flask import Flask

# --- Flask setup ---
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'  # Or change to your DB
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

fake = Faker()


def seed_data():
    with app.app_context():
        db.drop_all()
        db.create_all()

        # --- Generate Users ---
        users = []
        phone_numbers = set()
        for _ in range(100):
            phone = fake.random_int(min=13000000000, max=19999999999)
            if phone in phone_numbers:
                continue
            phone_numbers.add(phone)
            date = random.choice([0, 1, 2])  # Random date for user
            group = 'VIP' if date == 0 else random.choice(['Normal', 'VIP'])

            user = User(
                phone=phone,
                password=fake.password(),
                group=group,
                date=date
            )
            users.append(user)
            db.session.add(user)

        # --- Generate Sponsors ---
        for _ in range(10):
            sponsor = Sponsor(
                id=fake.unique.lexify(text='S????'),
                advert_urls=fake.url()
            )
            db.session.add(sponsor)

        # --- Generate Games ---
        games = []
        for _ in range(20):
            game_date = random.choice([1, 2])  # Random date for the game
            game = Game(
                id=fake.unique.lexify(text='G????'),
                name=fake.word(),
                kp=fake.name(),
                date=game_date,
                session=random.choice(['A', 'B']),
                rule=fake.sentence(nb_words=10),
                description=fake.sentence(),
                qq=fake.numerify(text='###########'),
                theme=f"fake_data/test_image/image ({random.randint(1, 20)}).jpg",  # Path to image
                table=str(random.randint(1, 20)),
                max_pl=random.randint(4, 12)  # Max players per game
            )
            games.append(game)
            db.session.add(game)

        db.session.commit()

        # --- Create Random Registrations ---
        game_registrations = {game.id: 0 for game in games}  # Track number of registrations per game

        for user in users:
            available_sessions = ['A', 'B']

            # Users with date == 0 (VIP) can register for both date 1 and date 2 games
            if user.date == 0:
                user_games = [game for game in games if game.date in [1, 2]]
            else:
                # Users with date 1 or 2 can only register for games with the same date
                user_games = [game for game in games if game.date == user.date]

            # For each session, allow the user to register only one game
            for session in available_sessions:
                available_games_for_session = [game for game in user_games if game.session == session]

                if available_games_for_session:
                    # Select one game for the session
                    game = random.choice(available_games_for_session)

                    # Check if the number of registrations exceeds max_pl
                    if game_registrations[game.id] < game.max_pl:
                        reg = UserToGameId(user_id=user.phone, game_id=game.id)
                        db.session.add(reg)
                        game_registrations[game.id] += 1  # Increment the registration count

        db.session.commit()
        print("✅ Test data generated!")


if __name__ == "__main__":
    seed_data()
