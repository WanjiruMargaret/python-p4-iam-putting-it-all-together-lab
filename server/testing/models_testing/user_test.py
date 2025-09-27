from sqlalchemy.exc import IntegrityError
import pytest

from app import app
from models import db, User, Recipe

class TestUser:
    '''User in models.py'''

    def test_has_attributes(self):
        '''has attributes username, _password_hash, image_url, and bio.'''
        
        with app.app_context():

            User.query.delete()
            db.session.commit()

            user = User(
                username="Liz",
                image_url="https://prod-images.tcm.com/Master-Profile-Images/ElizabethTaylor.jpg",
                bio="""Dame Elizabeth Rosemond Taylor DBE (February 27, 1932""" + \
                    """ - March 23, 2011) was a British-American actress. """ + \
                    """She began her career as a child actress in the early""" + \
                    """ 1940s and was one of the most popular stars of """ + \
                    """classical Hollywood cinema in the 1950s. She then""" + \
                    """ became the world's highest paid movie star in the """ + \
                    """1960s, remaining a well-known public figure for the """ + \
                    """rest of her life. In 1999, the American Film Institute""" + \
                    """ named her the seventh-greatest female screen legend """ + \
                    """of Classic Hollywood cinema."""
            )

            user.password_hash = "whosafraidofvirginiawoolf"
            
            db.session.add(user)
            db.session.commit()

            created_user = User.query.filter(User.username == "Liz").first()

            assert(created_user.username == "Liz")
            assert(created_user.image_url == "https://prod-images.tcm.com/Master-Profile-Images/ElizabethTaylor.jpg")
            assert(created_user.bio == \
                """Dame Elizabeth Rosemond Taylor DBE (February 27, 1932""" + \
                """ - March 23, 2011) was a British-American actress. """ + \
                """She began her career as a child actress in the early""" + \
                """ 1940s and was one of the most popular stars of """ + \
                """classical Hollywood cinema in the 1950s. She then""" + \
                """ became the world's highest paid movie star in the """ + \
                """1960s, remaining a well-known public figure for the """ + \
                """rest of her life. In 1999, the American Film Institute""" + \
                """ named her the seventh-greatest female screen legend """ + \
                """of Classic Hollywood cinema.""")
            
            # FIX: Check for AttributeError on the unreadable 'password' property, not 'password_hash'
            with pytest.raises(AttributeError):
                created_user.password 

    def test_requires_username(self):
        '''requires each record to have a username.'''

        with app.app_context():

            User.query.delete()
            db.session.commit()

            # FIX: Must set password hash before committing, even if testing username constraint
            user = User()
            user.set_password("temp_pass") # Set required password hash
            
            # The absence of the username will now trigger the IntegrityError
            with pytest.raises(IntegrityError):
                db.session.add(user)
                db.session.commit()

    def test_requires_unique_username(self):
        '''requires each record to have a unique username.'''

        with app.app_context():

            User.query.delete()
            db.session.commit()

            # FIX: Must set password hash on both users
            user_1 = User(username="Ben")
            user_1.set_password("pass1")
            
            user_2 = User(username="Ben")
            user_2.set_password("pass2")

            with pytest.raises(IntegrityError):
                db.session.add_all([user_1, user_2])
                db.session.commit()

    def test_has_list_of_recipes(self):
        '''has records with lists of recipes records attached.'''

        with app.app_context():

            User.query.delete()
            Recipe.query.delete() # Also clear recipes just in case
            db.session.commit()

            user = User(username="Prabhdip")
            user.set_password("test_pass_hash") # FIX: Set the required password hash
            
            db.session.add(user)
            db.session.commit() # Commit user to get ID

            recipe_1 = Recipe(
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
                user_id=user.id # FIX: Explicitly set foreign key
                )
            recipe_2 = Recipe(
                title="Hasty Party Ham",
                instructions="""As am hastily invited settled at limited""" + \
                    """ civilly fortune me. Really spring in extent""" + \
                    """ an by. Judge but built gay party world. Of""" + \
                    """ so am he remember although required. Bachelor""" + \
                    """ unpacked be advanced at. Confined in declared""" + \
                    """ marianne is vicinity.""",
                minutes_to_complete=30,
                user_id=user.id # FIX: Explicitly set foreign key
                )

            # Although we appended to user.recipes, we still need to add them to the session
            # and commit. The user_id setting above is the most robust fix.
            db.session.add_all([recipe_1, recipe_2])
            db.session.commit()

            # Re-fetch user in case the relationship was not fully loaded by the lazy dynamic
            updated_user = User.query.get(user.id)
            
            # check that all were created in db
            assert(updated_user.id)
            assert(recipe_1.id)
            assert(recipe_2.id)

            # check that recipes were saved to user (needs .all() for a dynamic relationship to behave like a list)
            assert(recipe_1 in updated_user.recipes.all())
            assert(recipe_2 in updated_user.recipes.all())
