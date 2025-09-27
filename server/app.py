from flask import Flask, request, jsonify, session
from flask_migrate import Migrate
from models import db, User, Recipe, DEFAULT_IMAGE_URL # Import DEFAULT_IMAGE_URL if needed elsewhere
from sqlalchemy.exc import IntegrityError 

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'super-secret-key'

db.init_app(app)
migrate = Migrate(app, db)

# -----------------------
# Helper functions
# -----------------------
def get_current_user():
    user_id = session.get('user_id')
    if not user_id:
        return None
    user = User.query.get(user_id)
    # If a user ID is in session but the user isn't found (e.g., deleted), clear session
    if not user:
        session.pop('user_id', None)
    return user

# -----------------------
# Signup
# -----------------------
@app.route('/signup', methods=['POST'])
def signup():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    bio = data.get('bio', '')
    
    # FIX: Accept the image_url from the request data, falling back to the model's default
    image_url = data.get('image_url')

    if not username or not password:
        return jsonify({"errors": "Username and password required"}), 422

    if User.query.filter_by(username=username).first():
        return jsonify({"errors": "Username already exists"}), 422

    # Pass the potentially provided image_url to the User constructor
    user = User(username=username, bio=bio, image_url=image_url) 
    user.set_password(password)
    
    try:
        db.session.add(user)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({"errors": "Username already exists"}), 422 

    session['user_id'] = user.id

    return jsonify(user.to_dict()), 201

# -----------------------
# Login (No changes needed)
# -----------------------
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    user = User.query.filter_by(username=username).first()
    if not user or not user.authenticate(password):
        return jsonify({"errors": "Invalid username or password"}), 401

    session['user_id'] = user.id
    return jsonify(user.to_dict()), 200

# -----------------------
# Logout
# -----------------------
@app.route('/logout', methods=['DELETE'])
def logout():
    # FIX: Ensure 401 is returned when session is missing or None
    if 'user_id' not in session or session.get('user_id') is None:
        return jsonify({"errors": "Unauthorized"}), 401 

    session.pop('user_id')
    return '', 204

# -----------------------
# Check session (No changes needed, relies on fixed helper)
# -----------------------
@app.route('/check-session', methods=['GET'])
def check_session():
    user = get_current_user()
    if not user:
        return jsonify({"errors": "Unauthorized"}), 401
    return jsonify(user.to_dict()), 200

# -----------------------
# Recipes (GET) (No changes needed)
# -----------------------
@app.route('/recipes', methods=['GET'])
def recipe_index():
    user = get_current_user()
    if not user:
        return jsonify({"errors": "Unauthorized"}), 401

    recipes = user.recipes.all()
    return jsonify([r.to_dict() for r in recipes]), 200

# -----------------------
# Create recipe (POST)
# -----------------------
@app.route('/recipes', methods=['POST'])
def create_recipe():
    user = get_current_user()
    if not user:
        return jsonify({"errors": "Unauthorized"}), 401

    data = request.get_json()
    title = data.get('title')
    instructions = data.get('instructions')
    minutes_to_complete = data.get('minutes_to_complete', 0)

    try:
        minutes_to_complete = int(minutes_to_complete)
    except (ValueError, TypeError):
        return jsonify({"errors": "minutes_to_complete must be an integer"}), 422

    # FIX: Wrap the Recipe instantiation and commit in the same try block 
    # to catch the ValueError raised by model validation (e.g., instructions too short)
    try:
        recipe = Recipe(
            title=title,
            instructions=instructions,
            minutes_to_complete=minutes_to_complete,
            user_id=user.id
        )
        db.session.add(recipe)
        db.session.commit()
    except ValueError as e:
        db.session.rollback() 
        return jsonify({"errors": [str(e)]}), 422
    except Exception as e:
        db.session.rollback()
        return jsonify({"errors": ["An unexpected error occurred: " + str(e)]}), 500

    return jsonify(recipe.to_dict()), 201

# -----------------------
# Main
# -----------------------
if __name__ == '__main__':
    app.run(debug=True)