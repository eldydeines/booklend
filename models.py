#--------------------------------------------------------------------------#
#  Capstone Project:  BookLandia
#  Several models were needed for this project. Troubleshooting using psql.
#  User Model - contains all profile information for user 
#               and class functions for authentication
#  Book Model - contains all book information
#  Status Model- links many books to many users
#  Borrower Model - shows who has requested/borrowed the owner's book
#  BookRating Model - saves all ratings and reviews for many
#               users to many books
#  LenderRating Model - saves all ratings by lender and borrower
#
#  References: 
#  --- SQLAlchemy Documentation Website
#  --- Previous projects in GitHub Repository 
#  --- SpringBoard Exercises & Lessons
#  
#  By: Eldy Deines  Date: 8/11/2021
#--------------------------------------------------------------------------#


#--------------------------------------------------------------------------#
#                           Import Necessary Libraries 
#--------------------------------------------------------------------------#

from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from datetime import datetime

db = SQLAlchemy()
bcrypt = Bcrypt()


#--------------------------------------------------------------------------#
#                           Connect the app to the DB 
#--------------------------------------------------------------------------#

def connect_db(app):
    """Connect to database."""
    db.app = app
    db.init_app(app)

class LenderRating(db.Model):
    """ Connection between lender and borrower """

    __tablename__ = 'lender_ratings'

    user_being_rated_id = db.Column(db.Integer, db.ForeignKey("users.user_id",ondelete="cascade"), primary_key=True)
    user_rating_id = db.Column(db.Integer, db.ForeignKey("users.user_id",ondelete="cascade"), primary_key=True)
    rating = db.Column(db.Integer)
    review = db.Column(db.Text)

class User(db.Model):
    """Table for user profiles. One to Many"""

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
    avg_rating = db.Column(db.Float)

    status = db.relationship('Status')
    borrower = db.relationship('Borrower')

    lender = db.relationship(
        "User",
        secondary="lender_ratings",
        primaryjoin=(LenderRating.user_being_rated_id == user_id),
        secondaryjoin=(LenderRating.user_rating_id == user_id)
    )

    borrow_ee = db.relationship(
        "User",
        secondary="lender_ratings",
        primaryjoin=(LenderRating.user_rating_id == user_id),
        secondaryjoin=(LenderRating.user_being_rated_id == user_id)
    )

    def __repr__(self):
        """show info about user in cmd prompt"""
        u = self
        return f"<USER user_id={u.user_id} username={u.username}>"

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


class Book(db.Model):
    """Table for all books and their details.  One to many """

    __tablename__ = 'books'

    book_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    key = db.Column(db.Text, nullable=False,  unique=True)
    title = db.Column(db.Text, nullable=False)
    author = db.Column(db.Text, nullable=False)
    description = db.Column(db.Text)
    subjects = db.Column(db.Text)
    cover_img_url_m = db.Column(db.Text)
    cover_img_url_s = db.Column(db.Text)
    published_year = db.Column(db.Text)
    avg_rating = db.Column(db.Float)

    user = db.relationship('User', secondary='statuses', backref='books')
    status = db.relationship('Status')

    def __repr__(self):
        """show info about book in cmd prompt"""
        b = self
        return f"<BOOK book_id={b.book_id} key={b.key}> title={b.title}> author={b.author}>"
    
    def calc_avg_rating(cls, avg):
        """cleans up the average received and sends back cleaner version"""

        temp = str(avg)
        temp2 = temp.split("'")
        temp = float(temp2[1])
        book_ratings_avg = '{:,}'.format(round(temp,1))
        average_rating = float(book_ratings_avg)
        
        return average_rating


class Status(db.Model):
    """ Joins together a book with a user. Many to many relationship """

    __tablename__ = "statuses"

    # table columns setup with combination primary key
    book_id = db.Column(db.Integer, db.ForeignKey("books.book_id",ondelete="cascade"), primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.user_id",ondelete="cascade"), primary_key=True)
    location = db.Column(db.String(50), nullable=False, default="On Shelf")
    condition = db.Column(db.String(50), nullable=False, default="Like New")
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow())

    book = db.relationship('Book')
    user = db.relationship('User')
    
    
    def __repr__(self):
        """show info about tag in cmd prompt"""
        s = self
        return f"<STATUS book_id={s.book_id} user_id={s.user_id}>"


class Borrower(db.Model):
    """ Joins together a book with a borrower for ratings and reviews Many to many """

    __tablename__ = "borrowers"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    book_id = db.Column(db.Integer)
    status_owner_id = db.Column(db.Integer)
    borrower_id = db.Column(db.Integer, db.ForeignKey("users.user_id",ondelete="cascade"))

    user = db.relationship('User')

    def __repr__(self):
        """show info about tag in cmd prompt"""
        b = self
        return f"<BORROWER borrower_id={b.borrower_id} book_id={b.book_id} owner_id={b.status_owner_id}>"


class BookRating(db.Model):
    """ Joins together books and users for ratings and reviews. Many to Many """

    __tablename__ = "books_ratings"

    book_rated = db.Column(db.Integer, db.ForeignKey("books.book_id",ondelete="cascade"), primary_key=True)
    user_rating = db.Column(db.Integer, db.ForeignKey("users.user_id",ondelete="cascade"), primary_key=True)
    rating = db.Column(db.Integer)
    review = db.Column(db.Text)

    book = db.relationship('Book')
    user = db.relationship('User')

    def __repr__(self):
        """show info about tag in cmd prompt"""
        b = self
        return f"<BOOKRATING book={b.book_rated} user={b.user_rating}>"



