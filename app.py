import os
from threading import ThreadError
from flask import Flask, render_template, request, redirect, session, flash, g
from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy.exc import IntegrityError
from models import db, connect_db, User
from forms import RegisterForm, LoginForm
from func import Warehouse

#sets up session variable
CURR_USER_KEY = ""

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql:///booklend"
#app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get('DATABASE_URL').replace("://", "ql://", 1)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = True
app.config["SECRET_KEY"] = "CKsec123secKC"
#app.config["SECRET_KEY"] = os.environ.get('SECRET_KEY', 'ed2407')
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

#Connect and create database
connect_db(app)

#Add app to debug tool
toolbar = DebugToolbarExtension(app)

#--------------------------------------------------------------------------#
#                           Start Routes 
#--------------------------------------------------------------------------#

@app.route('/')
def home_page():
    return render_template('index.html')


#--------------------------------------------------------------------------#
#                   Register, Login, and Logout Routes
#--------------------------------------------------------------------------#

@app.before_request
def add_user_to_g():
    """If we're logged in, add curr user to Flask global."""

    if CURR_USER_KEY in session:
        g.user = User.query.get(session[CURR_USER_KEY])

    else:
        g.user = None


def do_login(user):
    """Log in user."""
    session[CURR_USER_KEY] = user.user_id


def do_logout():
    """Logout user."""
    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]
        

@app.route('/register', methods=['GET', 'POST'])
def register_user():
    """Register User: Validate submissions, create a new user, add user to session """
    form = RegisterForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        first_name = form.first_name.data
        last_name = form.last_name.data
        address1 = form.address1.data
        address2 = form.address2.data
        town = form.town.data
        state = form.state.data
        zip = form.zip.data
        phone = form.phone.data
        email = form.email.data
        profile = form.profile.data
        fav_book = form.fav_book.data
        fav_author = form.fav_author.data

        new_user = User.register(username, password, email, first_name, last_name, 
                                 address1, address2, town, state, zip, phone, profile, fav_book, fav_author)
        db.session.add(new_user)
        try:
            db.session.commit()
        except IntegrityError:
            form.username.errors.append('Sorry, but this username is taken.  Please pick another')
            return render_template('register.html', form=form)
        do_login(new_user)
        flash('Welcome! Your Account has been created!', "success")
        return redirect('/')

    return render_template('register.html', form=form)

@app.route('/login', methods=["GET", "POST"])
def login():
    """Handle user login."""

    form = LoginForm()

    if form.validate_on_submit():
        user = User.authenticate(form.username.data,
                                 form.password.data)

        if user:
            do_login(user)
            flash(f"Hello, {user.username}!", "success")
            return redirect("/")

        flash("Invalid credentials.", 'danger')

    return render_template('login.html', form=form)

@app.route('/logout')
def logout():
    """Logout user by removing their username from the session"""
    do_logout()
    flash("You have been logged out.", 'danger')
    return redirect('/login')

#--------------------------------------------------------------------------#
#                   Book Routes
#--------------------------------------------------------------------------#

@app.route("/findbooks")
def find_books():
    """Render search form"""
    return render_template('books/search_wh.html')

@app.route('/api/search-wh')
def search_wh():
    """ This will get books based on Title and Author"""
    title = request.args['title']
    author = request.args['author']
    
    book_criteria = Warehouse(title, author)
    print('******************************')
    print(book_criteria)
    found_books = book_criteria.findBooksInWH()
    return render_template('books/search_wh.html')