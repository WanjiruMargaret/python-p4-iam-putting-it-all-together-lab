# resources.py
from flask import request, session
from flask_restful import Resource
from models import User, Recipe
from app import db

class Signup(Resource):
    def post(self):
        data = request.get_json()
        username = data.get("username")
        password = data.get("password")
        bio = data.get("bio", "")

        if not username or not password:
            return {"error": "Username and password required"}, 422

        user = User(username=username, bio=bio)
        user.set_password(password)

        try:
            db.session.add(user)
            db.session.commit()
        except:
            db.session.rollback()
            return {"error": "Username must be unique"}, 422

        session["user_id"] = user.id
        return user.to_dict(), 201


class CheckSession(Resource):
    def get(self):
        user_id = session.get("user_id")
        if not user_id:
            return {"error": "Unauthorized"}, 401

        user = User.query.get(user_id)
        return user.to_dict(), 200


class Login(Resource):
    def post(self):
        data = request.get_json()
        username = data.get("username")
        password = data.get("password")

        user = User.query.filter_by(username=username).first()
        if user and user.authenticate(password):
            session["user_id"] = user.id
            return user.to_dict(), 200

        return {"error": "Invalid username or password"}, 401


class Logout(Resource):
    def delete(self):
        if "user_id" in session:
            session.pop("user_id")
            return {}, 204
        return {"error": "Unauthorized"}, 401


class RecipeIndex(Resource):
    def get(self):
        user_id = session.get("user_id")
        if not user_id:
            return {"error": "Unauthorized"}, 401

        user = User.query.get(user_id)
        recipes = [recipe.to_dict() for recipe in user.recipes]
        return recipes, 200

    def post(self):
        user_id = session.get("user_id")
        if not user_id:
            return {"error": "Unauthorized"}, 401

        data = request.get_json()
        title = data.get("title")
        instructions = data.get("instructions")
        minutes_to_complete = data.get("minutes_to_complete", 0)

        if not title or not instructions:
            return {"error": "Title and instructions required"}, 422

        user = User.query.get(user_id)
        recipe = Recipe(
            title=title,
            instructions=instructions,
            minutes_to_complete=minutes_to_complete,
            user=user
        )

        db.session.add(recipe)
        db.session.commit()
        return recipe.to_dict(), 201
