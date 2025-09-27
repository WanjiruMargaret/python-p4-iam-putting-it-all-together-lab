from app import app, db
from models import User, Recipe, DEFAULT_IMAGE_URL

with app.app_context():
    print("Deleting all records...")
    Recipe.query.delete()
    User.query.delete()
    db.session.commit()

    print("Seeding users...")
    users = [
        User(username="alice", bio="I love cooking!", image_url=DEFAULT_IMAGE_URL),
        User(username="bob", bio="Healthy recipes enthusiast", image_url=DEFAULT_IMAGE_URL),
        User(username="charlie", bio="Pasta is life!", image_url=DEFAULT_IMAGE_URL)
    ]

    # Set passwords
    for u in users:
        u.set_password("password123")

    db.session.add_all(users)
    db.session.commit()  # Commit so users have IDs for foreign keys

    print("Seeding recipes...")
    recipes = [
        Recipe(
            title="Pancakes",
            instructions="Mix ingredients thoroughly and cook on a hot griddle until golden brown.",
            minutes_to_complete=15,
            user_id=users[0].id
        ),
        Recipe(
            title="Salad",
            instructions="Chop fresh vegetables and toss them with a light vinaigrette dressing.",
            minutes_to_complete=10,
            user_id=users[1].id
        ),
        Recipe(
            title="Spaghetti",
            instructions="Boil pasta until al dente, prepare a rich tomato sauce, and combine carefully.",
            minutes_to_complete=30,
            user_id=users[2].id
        )
    ]

    db.session.add_all(recipes)
    db.session.commit()

    print("Seeding done!")
