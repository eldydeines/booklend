import os
from threading import ThreadError
from flask import Flask, render_template, request, redirect, session, flash, g, jsonify
from flask.typing import TeardownCallable
from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy.exc import IntegrityError
from models import db, connect_db, User, Book, Status, Borrower
from forms import RegisterForm, LoginForm, StatusForm, ProfileForm
from func import Warehouse

#sets up session variable
CURR_USER_KEY = "curr_user"

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
@app.before_request
def add_user_to_g():
    """If we're logged in, add curr user to Flask global."""

    if CURR_USER_KEY in session:
        g.user = User.query.get(session[CURR_USER_KEY])

    else:
        g.user = None

@app.route('/')
def homepage():
    """Show homepage:
    - anonymous users: will be directed to signup
    - logged in users: will see list of books on shelves
    """
    if g.user:
        # I was having trouble using the list of Ids and had to reference the solution for this one. 
        latest_books = (Status
                    .query
                    .filter_by(location="On Shelf")
                    .order_by(Status.timestamp.desc())
                    .limit(10))
        return render_template('home.html', status=latest_books)

    else:
        return render_template('home-anon.html')

#--------------------------------------------------------------------------#
#                   Register, Login, and Logout Routes
#--------------------------------------------------------------------------#

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
        return redirect('/addbooks')

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
#                   API Routes
#--------------------------------------------------------------------------#

@app.route("/addbooks")
def add_books():
    """Render search form"""
    return render_template('books/search_wh.html')

@app.route('/api/search-wh')
def search_wh():
    """ This will get books based on Title and Author"""
    title = request.args['title']
    author = request.args['author']
    
    book_criteria = Warehouse(title, author)

    found_books = book_criteria.findBooksInWH()

    if found_books:
        message = "Here are your results!"
        return (jsonify(found_books),201)
    else: 
        message = "Sorry, but your search turned up empty. Please try again."
        return (jsonify(message))
    

#--------------------------------------------------------------------------#
#                  Book Routes
#--------------------------------------------------------------------------#
@app.route('/book/add-book')
def add_book():
    """ This will add the book to user's library"""
    key = request.args['key']

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")
    
    book_to_add = Book.query.filter_by(key=key).first()
        
    book_to_add.user.append(g.user)
    db.session.commit()      

    return (jsonify("Book Added"),201)

@app.route('/book/<int:book_id>/update', methods=["GET","POST"])
def update_book(book_id):
    """ This will updated specific book for user"""
    
    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    form=StatusForm()

    user_book = Status.query.filter_by(user_id=g.user.user_id,book_id=book_id).one()

    if form.validate_on_submit():
        location = request.form['location']
        condition = request.form['condition']
        user_book.location = location
        user_book.condition = condition
        db.session.add(user_book)
        db.session.commit()
        flash("Book updated.", "success")
        return redirect(f"/user/library")
    return render_template('books/update_bk.html', form=form, book=user_book)

@app.route('/book/<int:book_id>/delete', methods=["POST"])
def delete_book(book_id):
    """ Delete a specific book from user's library"""
    
    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    user_book = Status.query.filter_by(user_id=g.user.user_id,book_id=book_id).one()
    db.session.delete(user_book)
    db.session.commit()
    flash("Book removed from library.", "success")
    return redirect(f"/user/library")

@app.route('/book/<int:book_id>/<int:user_id>/request', methods=["POST"])
def request_book(book_id,user_id):
    """Update database to show this new request for specified book and book owner"""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    user_book = Status.query.filter_by(book_id=book_id,user_id=user_id).one()
    requestor = User.query.get(g.user.user_id)
    new_borrow = Borrower(book_id=user_book.book_id,
                        status_owner_id=user_book.user_id,
                        borrower_id=requestor.user_id)
    user_book.location = "Requested"
    db.session.add(new_borrow)
    db.session.commit()

    flash("Book has been requested.", "success")
    return redirect('/user/requests')

    
@app.route('/book/<int:book_id>/<int:user_id>/approve', methods=["POST"])
def approve_request(book_id,user_id):
    """Book Owner can approve the request and will update status of book"""
    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    user_book = Status.query.filter_by(book_id=book_id,user_id=user_id).one()
    user_book.location = "Checked Out"

    db.session.commit()
    return redirect ('/user/requests')

@app.route('/book/<int:book_id>/<int:user_id>/reject', methods=["POST"])
def reject_request(book_id,user_id):
    """Book Owner can reject the request and remove from Borrower table"""
    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    user_book = Status.query.filter_by(book_id=book_id,user_id=user_id).one()
    user_book.location = "On Shelf"
    db.session.commit()

    user_borrows = Borrower.query.filter_by(book_id=book_id,status_owner_id=user_id).one()
    db.session.delete(user_borrows)
    db.session.commit()

    return redirect ('/user/requests')    

#--------------------------------------------------------------------------#
#                  User Routes
#--------------------------------------------------------------------------#

@app.route('/users/all')
def see_all_users():
    """See a list of all users"""
    users = User.query.all()
    return render_template('users/all.html',users=users)

@app.route('/user/library')
def see_library():
    """For logged in user, show books that they have added to their library"""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")
    
    book_ids = [status.book_id for status in g.user.status]
 
    statuses = (Status.query
            .filter(Status.book_id.in_(book_ids))
            .filter_by(user_id=g.user.user_id)
            .order_by(Status.timestamp.desc()))
    #users_books = (Status.query.filter_by(user_id=g.user.user_id).order_by(Status.book_id.desc()))
    return render_template('users/library.html',statuses=statuses)

@app.route('/user/profile')
def see_profile():
    """For Logged in User, show profile"""
    
    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")
    
    current_user = User.query.get(session[CURR_USER_KEY])
    return render_template('users/profile.html',user=current_user)


@app.route('/user/profile/<int:user_id>')
def see_requestor_profile(user_id):
    """See requestors profile"""
    
    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    requestor = User.query.get(user_id)

    statuses = (Status.query
            .filter_by(user_id=requestor.user_id)
            .order_by(Status.timestamp.desc()))

    return render_template('users/requestor.html',user=requestor,statuses=statuses)


@app.route('/user/profile/update', methods=["GET", "POST"])
def update_profile():
    """For Logged in User, update their profile information"""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    form = ProfileForm()
    current_user = User.query.get(session[CURR_USER_KEY])

    if form.validate_on_submit():
        pword_entered = request.form['password']
        if User.authenticate(current_user.username, pword_entered):

            first_name = request.form['first_name']
            last_name = request.form['last_name']
            address1 = request.form['address1']
            address2 = request.form['address2']
            town = request.form['town']
            state =  request.form['state']
            zip = request.form['zip']
            phone =  request.form['phone']
            email = request.form['email']
            profile = request.form['profile']
            fav_book = request.form['fav_book']
            fav_author = request.form['fav_author']

            
            if first_name: 
                current_user.first_name = first_name
            if last_name: 
                current_user.last_name = last_name
            if address1: 
                current_user.address1 = address1
            if address2: 
                current_user.address2 = address2
            if town: 
                current_user.town = town
            if state:
                current_user.state = state
            if zip: 
                current_user.zip = zip
            if phone: 
                current_user.phone = phone
            if email: 
                current_user.email = email
            if profile: 
                current_user.profile = profile
            if fav_book:
                current_user.fav_book = fav_book
            if fav_author:
                current_user.fav_author = fav_author

            db.session.commit()
            flash("Profile has been updated.","success")
            return redirect(f"/user/profile")

        flash("Password incorrect. Profile updates not saved.","warning")


    return render_template('users/update.html',user=current_user, form=form)

@app.route('/user/requests')
def show_requests():
    """Show all requests that user has made and any requests for their books"""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    user_borrows = Borrower.query.filter(Borrower.borrower_id==g.user.user_id)
    user_books = [book.book_id for book in user_borrows]
    user_users = [user.status_owner_id for user in user_borrows]
    all_requests = (Status.query
                    .filter((Status.location=="Requested") | (Status.location=="Checked Out"))
                    .filter( (Status.user_id==g.user.user_id) | ((Status.book_id.in_(user_books)) & (Status.user_id.in_(user_users))) )
                    .all())
    user_borrows = (Borrower.query
                    .filter((Borrower.borrower_id==g.user.user_id) |(Borrower.status_owner_id==g.user.user_id))
                    .all())
    return render_template('users/requests.html', statuses=all_requests, requestor=user_borrows)