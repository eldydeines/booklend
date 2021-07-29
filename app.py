from flask import Flask, render_template, redirect, session, flash
from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy.exc import IntegrityError
from models import db, connect_db, User
from forms import RegisterForm



app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql:///booklend"
#app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get('DATABASE_URL').replace("://", "ql://", 1)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = True
app.config["SECRET_KEY"] = "abc123"
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
        session['username'] = new_user.username
        flash('Welcome! Your Account has been created!', "success")
        return redirect('/')

    return render_template('register.html', form=form)
