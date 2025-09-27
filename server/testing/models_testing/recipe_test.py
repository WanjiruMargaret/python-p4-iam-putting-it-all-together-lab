import pytest
from sqlalchemy.exc import IntegrityError

from app import app
from models import db, Recipe, User # <-- Added User import

class TestRecipe:
    '''Recipe Model Tests'''

    def test_has_attributes(self):
        '''has attributes title, instructions, and minutes_to_complete.'''
        
        with app.app_context():

            Recipe.query.delete()
            
            # Setup dummy user to satisfy the foreign key constraint
            User.query.delete()
            user = User(username="temp_test_user_1")
            user.set_password("password123")
            db.session.add(user)
            db.session.commit()
            
            recipe = Recipe(
                    title="Delicious Shed Ham",
                    instructions="""Or kind rest bred with am shed then. In""" + \
                        """ raptures building an bringing be. Elderly is detract""" + \
                        """ tedious assured private so to visited. Do travelling""" + \
                        """ companions contrasted it. Mistress strongly remember""" + \
                        """ up to. Ham him compass you proceed calling detract.""" + \
                        """ Better of always missed we person mr. September""" + \
                        """ smallness northward situation few her certainty""" + \
                        """ something.""",
                    minutes_to_complete=60,
                    user_id=user.id # <-- Mandatory user_id assignment
                    )

            db.session.add(recipe)
            db.session.commit()

            new_recipe = Recipe.query.filter(Recipe.title == "Delicious Shed Ham").first()

            assert new_recipe.title == "Delicious Shed Ham"
            assert new_recipe.instructions == """Or kind rest bred with am shed then. In""" + \
                        """ raptures building an bringing be. Elderly is detract""" + \
                        """ tedious assured private so to visited. Do travelling""" + \
                        """ companions contrasted it. Mistress strongly remember""" + \
                        """ up to. Ham him compass you proceed calling detract.""" + \
                        """ Better of always missed we person mr. September""" + \
                        """ smallness northward situation few her certainty""" + \
                        """ something."""
            assert new_recipe.minutes_to_complete == 60
            assert new_recipe.user_id == user.id

    def test_requires_title(self):
        '''requires each record to have a title.'''

        with app.app_context():

            Recipe.query.delete()
            db.session.commit()

            # Setup dummy user
            User.query.delete()
            user = User(username="temp_test_user_2")
            user.set_password("password123")
            db.session.add(user)
            db.session.commit()
            
            # Recipe without title, but with valid instructions and user_id to isolate the title error
            recipe = Recipe(
                instructions="""This instruction text is long enough to satisfy the length requirement. It has to be over 50 characters long so that it doesn't trigger the ValueError or IntegrityError for instructions.""",
                user_id=user.id
            )
            
            # The absence of the title will cause an IntegrityError
            with pytest.raises(IntegrityError):
                db.session.add(recipe)
                db.session.commit()

    def test_requires_50_plus_char_instructions(self):
        with app.app_context():

            Recipe.query.delete()
            db.session.commit()

            # Setup dummy user
            User.query.delete()
            user = User(username="temp_test_user_3")
            user.set_password("password123")
            db.session.add(user)
            db.session.commit()

            '''must raise either a sqlalchemy.exc.IntegrityError with constraints or a custom validation ValueError'''
            with pytest.raises( (IntegrityError, ValueError) ):
                recipe = Recipe(
                    title="Generic Ham",
                    instructions="idk lol", # Intentionally short
                    user_id=user.id # <-- Mandatory user_id assignment
                    )
                db.session.add(recipe)
                db.session.commit()
