# init.py

# import os
from flask import Flask
from flask_bootstrap import Bootstrap
from flask_login import LoginManager
from flask import session
from datetime import datetime, timedelta
from random import randint, choice, choices, sample
from faker import Faker

# LOCAL IMPORTS
from .models import Admin, User, Status, Reviews, db
from .views import page_not_found

# Initialize the Faker object
fake = Faker()


def create_app():
    app = Flask(__name__)
    app.static_folder = "static"
    app.config.from_object("config")
    Bootstrap(app)

    db.init_app(app)

    login_manager = LoginManager()
    login_manager.login_view = "auth.login"
    login_manager.init_app(app)

    from .models import User

    create_database(app)
    create_admin(app)
    create_test_users(app)
    create_test_reviews(app)

    @login_manager.user_loader
    def load_user(user_id):
        # since the user_id is just the primary key of our user table, use it in the query for the user
        return User.query.get(int(user_id))

    # page not found
    app.register_error_handler(404, page_not_found)

    # blueprint for auth routes in our app
    from .auth import auth as auth_blueprint

    app.register_blueprint(auth_blueprint)

    # blueprint for admin routes in our app
    from .admin import admin as admin_blueprint

    app.register_blueprint(admin_blueprint)

    # blueprint for non-auth parts of app
    from .views import views as views_blueprint

    app.register_blueprint(views_blueprint)
    return app


def create_database(app):
    with app.app_context():
        db.create_all()


def create_admin(app):
    with app.app_context():
        # Check if needs to add a default admin
        is_there_any_admins = Admin.query.all()
        if len(is_there_any_admins) > 0:
            return

        # add new user to the database
        user_data = {
            "username": "admin",
            "password": "eK9HIEXwVNin8d2AYeIlS8f",
            "name": "admin",
            "lastname": "admin",
            "image_data": None,
            "image_filename": "default.png",
        }
        user = User(**user_data)
        db.session.add(user)
        db.session.commit()

        user = User.query.filter_by(username=user.username).first()

        status_data = {
            "user_id": user.id,
            "status": 0,
            "register_date": datetime.today(),
            "last_deactivate_date": None,
        }
        status = Status(**status_data)
        db.session.add(status)
        db.session.commit()

        new_admin = Admin(user_id=1)

        # Add the new admin entry to the session
        db.session.add(new_admin)

        # Commit the session to save the changes to the database
        db.session.commit()


def random_date() -> datetime:
    """
    Generates a random date between two given dates.

    :return: A random date between start and end.
    """
    start = datetime(2024, 5, 1)
    end = datetime.today()
    delta = end - start
    random_days = randint(0, delta.days)
    return start + timedelta(days=random_days)


def create_test_users(app):
    with app.app_context():
        for i in range(383):
            Faker.seed(randint(0, 100000))
            fake = Faker("en")

            name = fake.first_name()
            lastname = fake.last_name()
            username = f"{name}_{lastname}_{randint(0, 999)}"
            password = "123456"

            # add new user to the database
            user_data = {
                "username": username,
                "password": password,
                "name": name,
                "lastname": lastname,
                "image_data": None,
                "image_filename": "default.png",
            }
            user = User(**user_data)
            db.session.add(user)
            db.session.commit()

            user = User.query.filter_by(username=user.username).first()

            status_data = {
                "user_id": user.id,
                "status": randint(0, 1),
                "register_date": random_date(),
                "last_deactivate_date": None,
            }
            status = Status(**status_data)
            db.session.add(status)
            db.session.commit()


def generate_random_review():
    """
    Generates a random review with title, content, and stars based on the star rating group.

    :return: A dictionary with title, content, and star rating.
    """
    # Titles categorized by star rating groups
    titles = {
        "bad": [
            "Not worth the money",
            "Very disappointing",
            "Regret buying",
            "Waste of money",
            "Poor quality",
            "Terrible experience",
            "Product broke quickly",
            "False advertising",
            "Not as described",
            "Horrible service",
            "Disappointing results",
            "Wouldn't recommend",
            "Very low quality",
            "Frustrating purchase",
            "Not worth the hype",
            "Overpriced garbage",
            "Worst purchase ever",
            "Complete letdown",
            "Not durable at all",
            "Avoid this product",
        ],
        "good": [
            "Quite satisfied",
            "Better than expected",
            "Good, but could improve",
            "Decent product",
            "Worth the price",
            "Happy with the purchase",
            "Meets expectations",
            "Solid quality",
            "Good value for money",
            "Pleasant surprise",
            "Performs well",
            "Would buy again",
            "Useful and practical",
            "Does the job",
            "Satisfactory performance",
            "Reasonable quality",
            "Good, but some issues",
            "Works as expected",
            "Happy overall",
            "Pretty good purchase",
        ],
        "excellent": [
            "Fantastic product!",
            "Exceeded expectations",
            "Best purchase ever!",
            "Perfect in every way",
            "Incredible quality",
            "Highly recommend",
            "Top-notch product",
            "Absolutely love it",
            "Impressive results",
            "Amazing experience",
            "Worth every penny",
            "Best decision ever",
            "Can't live without it",
            "Superior quality",
            "Outstanding performance",
            "Perfect choice",
            "Thrilled with this product",
            "Couldn't be happier",
            "Five stars all the way",
            "Must-have item",
        ],
    }

    # Contents categorized by star rating groups
    contents = {
        "bad": [
            "This product really let me down. Wouldn't recommend.",
            "The quality was poor and didn't meet expectations.",
            "A complete waste of money. I regret buying this.",
            "It broke after just a week. Very disappointed.",
            "Terrible experience overall. Not what I expected.",
            "False advertising, the product doesn't work as described.",
            "I had high hopes but was sorely disappointed.",
            "The material is cheap and flimsy.",
            "Not worth even half the price.",
            "Bad customer service and bad product.",
            "It stopped working after a few uses.",
            "Definitely wouldn't buy this again.",
            "Overhyped and under-delivered.",
            "Extremely dissatisfied with this purchase.",
            "The product arrived damaged and wasn't usable.",
            "Poor quality control. It's full of defects.",
            "Feels cheaply made and didn't last.",
            "It's unusable. Complete failure.",
            "Very frustrating to use. A total waste.",
            "Avoid this product at all costs!",
        ],
        "good": [
            "The product is decent for its price. Satisfied with the performance.",
            "Pretty good overall. Some minor issues.",
            "Better than expected. I'm quite happy with it.",
            "Does what it promises, though there's room for improvement.",
            "Worth the money for what it offers.",
            "Solid performance and generally happy with it.",
            "I had a good experience, though it could be improved in some areas.",
            "Performs well for the price.",
            "Happy with the purchase, though not perfect.",
            "The product does its job without any major problems.",
            "Good value for money, does what it's supposed to.",
            "I am content with the results.",
            "Works well for most tasks, but could be better.",
            "It’s solid overall with a few minor issues.",
            "Good product but I’ve seen better.",
            "Overall, a decent buy. Would consider buying again.",
            "For the price, this is pretty good.",
            "Performs adequately for its cost.",
            "Quite happy with how it turned out.",
            "Good quality, though there are some improvements that could be made.",
        ],
        "excellent": [
            "Absolutely fantastic! Best purchase I've made.",
            "Exceeded all expectations. Very pleased with this.",
            "This is the best product I've used in a long time.",
            "It performs incredibly well. Highly recommend it.",
            "Perfect! Couldn't ask for more.",
            "Amazing quality and great value.",
            "I'm extremely happy with this product. It works flawlessly.",
            "Superb build and functionality.",
            "Impressed by the attention to detail and performance.",
            "Five stars for sure. Worth every penny.",
            "One of the best purchases I've ever made.",
            "Can't imagine living without this now.",
            "Superb experience from start to finish.",
            "Couldn't be happier with how this turned out.",
            "Highly recommend to everyone! It's perfect.",
            "Outstanding quality and great design.",
            "Completely satisfied with this purchase.",
            "Top-tier performance and quality.",
            "This product is a game changer.",
            "Best decision I've ever made. Highly recommend!",
        ],
    }

    # Generate a random star rating (1 to 5)
    stars = choices(
        [1, 2, 3, 4, 5],  # Star ratings
        weights=[1, 1, 2, 3, 8],  # Corresponding odds (more weight = more likely)
        k=1,  # Number of items to choose
    )[0]

    # Decide which type of review to generate based on the stars
    if stars in [1, 2]:
        review_type = "bad"
    elif stars in [3, 4]:
        review_type = "good"
    else:  # stars == 5
        review_type = "excellent"

    # Pick a random title and content from the appropriate group
    title = choice(titles[review_type])
    content = choice(contents[review_type])

    return title, content, stars


def create_test_reviews(app):
    with app.app_context():
        # Fetch all user IDs from the User model
        user_ids = db.session.query(User.id).all()
        
        # Flatten the list of tuples into a list of IDs
        user_ids = [user_id[0] for user_id in user_ids]

        # Return the specified number of random user IDs
        amount = randint(20, 53)
        user_ids_sample = sample(user_ids, amount)
        
        for i in range(amount):
            current_user = User.query.get(int(user_ids_sample[i]))
            
            status = Status.query.get(int(user_ids_sample[i]))
            delta = datetime.today() - status.register_date
            random_days = randint(0, delta.days)

            title, content, stars = generate_random_review()
            
            review = Reviews(
                title=title,
                content=content,
                stars=stars,
                user_id=None if randint(0, 1) == 0 else current_user.id,
                submitted_at=status.register_date + timedelta(days=random_days)
            )
            db.session.add(review)
            db.session.commit()
