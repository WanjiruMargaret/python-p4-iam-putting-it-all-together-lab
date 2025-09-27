from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import validates

db = SQLAlchemy()

# Ensure this URL matches what the test is expecting
DEFAULT_IMAGE_URL = "https://cdn.pixabay.com/photo/2017/11/10/05/24/screenshot_4.jpg"

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False, unique=True)
    _password_hash = db.Column(db.String(255), nullable=False)
    bio = db.Column(db.Text, default="")
    image_url = db.Column(db.String(255), default=DEFAULT_IMAGE_URL)
    
    # Use lazy='dynamic'
    recipes = db.relationship('Recipe', backref='user', lazy='dynamic', cascade='all, delete-orphan')

    # Fix for: TestUser.test_has_attributes (DID NOT RAISE <class 'AttributeError'>)
    @property
    def password(self):
        raise AttributeError('Password is not a readable attribute.')

    @hybrid_property
    def password_hash(self):
        return self._password_hash

    @password_hash.setter
    def password_hash(self, password):
        self._password_hash = generate_password_hash(password)

    def set_password(self, password):
        self.password_hash = password

    def authenticate(self, password):
        return check_password_hash(self._password_hash, password)

    # ... (to_dict method)
    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "bio": self.bio,
            "image_url": self.image_url,
            # Use .all() here for the dict to match expected output in tests
            "recipes": [r.to_dict() for r in self.recipes.all()] 
        }

class Recipe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    instructions = db.Column(db.Text, nullable=False)
    minutes_to_complete = db.Column(db.Integer)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    # ... (validation and to_dict methods)
    @validates('title')
    def validate_title(self, key, title):
        if not title or len(title) < 1 or len(title) > 100:
            raise ValueError("Title must be between 1 and 100 characters.")
        return title

    @validates('instructions')
    def validate_instructions(self, key, instructions):
        if len(instructions) < 50:
            raise ValueError("Instructions must be at least 50 characters long.")
        return instructions

    @validates('minutes_to_complete')
    def validate_minutes_to_complete(self, key, minutes):
        if minutes is not None and minutes < 1:
            raise ValueError("Minutes to complete must be a positive number.")
        return minutes

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "instructions": self.instructions,
            "minutes_to_complete": self.minutes_to_complete,
            "user_id": self.user_id
        }