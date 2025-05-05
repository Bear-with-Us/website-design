from faker import Faker
import random
import json
from database import db, Game, User, UserToGameId, Sponsor
from flask import Flask

# --- Flask setup ---
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///VR3.db'  # Or change to your DB
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

fake = Faker()


def seed_data():
    with app.app_context():
        db.drop_all()
        db.create_all()

        # --- Prepare data structures to hold the data we generate ---
        users_data = []
        games_data = []
        registrations_data = []
        sponsors_data = []

        # --- Generate Users ---
        users = []
        phone_numbers = set()
        for _ in range(100):
            phone = fake.random_int(min=13000000000, max=19999999999)
            if phone in phone_numbers:
                continue
            phone_numbers.add(phone)
            date = random.choice([0, 1, 2])  # Random date for user
            group = 'VIP' if date == 0 else 'Normal'

            user = User(
                phone=phone,
                password=fake.password(),
                group=group,
                date=date
            )

            # Add to database
            users.append(user)
            db.session.add(user)

            # Add to our JSON data
            users_data.append({
                'phone': phone,
                'password': user.password,
                'group': group,
                'date': date
            })

        # --- Generate Sponsors ---
        for _ in range(10):
            sponsor_id = fake.unique.lexify(text='S????')
            sponsor_url = fake.url()

            sponsor = Sponsor(
                id=sponsor_id,
                advert_urls=sponsor_url
            )
            db.session.add(sponsor)

            sponsors_data.append({
                'id': sponsor_id,
                'advert_urls': sponsor_url
            })

        # --- Generate Games ---
        games = []
        for _ in range(20):
            game_id = fake.unique.lexify(text='G????')
            game_date = random.choice([1, 2])  # Random date for the game
            game_name = fake.word()
            game_kp = fake.name()
            game_session = random.choice(['A', 'B'])
            game_rule = fake.sentence(nb_words=10)
            game_description = fake.sentence()
            game_qq = fake.numerify(text='###########')
            game_theme = f"image/image ({random.randint(1, 20)}).jpg"
            game_table = str(random.randint(1, 20))
            game_max_pl = random.randint(4, 12)

            game = Game(
                id=game_id,
                name=game_name,
                kp=game_kp,
                date=game_date,
                session=game_session,
                rule=game_rule,
                description=game_description,
                qq=game_qq,
                theme=game_theme,
                table=game_table,
                max_pl=game_max_pl
            )
            games.append(game)
            db.session.add(game)

            games_data.append({
                'id': game_id,
                'name': game_name,
                'kp': game_kp,
                'date': game_date,
                'session': game_session,
                'rule': game_rule,
                'description': game_description,
                'qq': game_qq,
                'theme': game_theme,
                'table': game_table,
                'max_pl': game_max_pl
            })

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

                        registrations_data.append({
                            'user_id': user.phone,
                            'game_id': game.id
                        })

        db.session.commit()

        # --- Save the data to JSON files ---
        with open('users.json', 'w', encoding='utf-8') as f:
            json.dump(users_data, f, indent=4, ensure_ascii=False)

        with open('games.json', 'w', encoding='utf-8') as f:
            json.dump(games_data, f, indent=4, ensure_ascii=False)

        with open('registrations.json', 'w', encoding='utf-8') as f:
            json.dump(registrations_data, f, indent=4, ensure_ascii=False)

        with open('sponsors.json', 'w', encoding='utf-8') as f:
            json.dump(sponsors_data, f, indent=4, ensure_ascii=False)

        print("✅ Test data generated and saved to JSON files!")


if __name__ == "__main__":
    seed_data()
