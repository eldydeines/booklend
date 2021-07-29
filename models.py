from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

db = SQLAlchemy()
bcrypt = Bcrypt()

def connect_db(app):
    """Connect to database."""
    db.app = app
    db.init_app(app)

class User(db.Model):

    __tablename__ = 'users'

    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.Text, nullable=False,  unique=True)
    password = db.Column(db.Text, nullable=False)
    first_name = db.Column(db.String(30), nullable=False)
    last_name = db.Column(db.String(30), nullable=False)
    address1 = db.Column(db.Text, nullable=False)
    address2 = db.Column(db.Text)
    town = db.Column(db.Text, nullable=False)
    state = db.Column(db.Text, nullable=False)
    zip = db.Column(db.Text, nullable=False)
    phone = db.Column(db.String(30)) 
    email = db.Column(db.String(50), unique=True, nullable=False)
    profile = db.Column(db.Text)
    fav_book = db.Column(db.Text)
    fav_author = db.Column(db.Text)

    @classmethod
    def register(cls, username, password, email, first_name, last_name, 
                address1, address2, town, state, zip, phone, profile, fav_book, fav_author):
        """Register user w/hashed password & return user."""

        hashed = bcrypt.generate_password_hash(password)
        # turn bytestring into normal (unicode utf8) string
        hashed_utf8 = hashed.decode("utf8")

        # return instance of user w/username and hashed pwd
        return cls(username=username, password=hashed_utf8, email=email, first_name=first_name, last_name=last_name,
                   address1=address1, address2=address2, town=town, state=state, zip=zip, phone=phone, profile=profile, 
                   fav_book=fav_book, fav_author=fav_author)

    @classmethod
    def authenticate(cls, username, password):
        """Searches for a user by decrypting the hash.
        If match, send back authenticated user.
        If no match, it returns False.
        """
        
        user = cls.query.filter_by(username=username).first()

        if user:
            is_auth = bcrypt.check_password_hash(user.password, password)
            if is_auth:
                return user

        return False