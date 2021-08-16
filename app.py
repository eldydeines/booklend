#--------------------------------------------------------------------------#
#  Capstone Project:  BookLandia
#  BookLandia allows people to find and add books to their shelf.  
#  Books have title, author, description, reviews, and more.
#  Users can see available books and can request/approve book requests.
#  Users can also provide ratings on lenders.
#
#  References: 
#  --- Previous projects in GitHub Repository 
#  --- SpringBoard Exercises & Lessons
#  
#  By: Eldy Deines  Date: 8/11/2021
#--------------------------------------------------------------------------#


#--------------------------------------------------------------------------#
#                           Import Necessary Libraries 
#--------------------------------------------------------------------------#
import os
from flask import Flask, render_template, request, redirect, session, flash, g, jsonify
from sqlalchemy.exc import IntegrityError
from sqlalchemy.sql import func
from models import BookRating, db, connect_db, User, Book, Status, Borrower, BookRating, LenderRating
from forms import RegisterForm, LoginForm, StatusForm, ProfileForm, BookReviewForm, LenderReviewForm
from func import Warehouse


#--------------------------------------------------------------------------#
#                           Setup App Configurations & Variables
#--------------------------------------------------------------------------#


# Sets up session variable
CURR_USER_KEY = "curr_user"

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get('DATABASE_URL').replace("://", "ql://", 1)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = True
app.config["SECRET_KEY"] = os.environ.get('SECRET_KEY', 'CKsec123secKC')


#Connect and create database
connect_db(app)

#Add app to debug tool


#--------------------------------------------------------------------------#
#--------------------------------------------------------------------------#
#                           Start Routes 
#--------------------------------------------------------------------------#
#--------------------------------------------------------------------------#

@app.before_request
def add_user_to_g():
    """If we're logged in, add the saved sesssion user to current 
    user to Flask global before app requests start. If not, there is 
    global user is none.
    """

    if CURR_USER_KEY in session:
        g.user = User.query.get(session[CURR_USER_KEY])

    else:
        g.user = None


@app.route('/')
def homepage():
    """Show homepage:
    - Anonymous users: will be directed to signup
    - logged in user: will see list of books on shelves and reviews
    """

    if g.user:
        
        #Get the latest books added to BookLandia by timestamp
        latest_books = (Status
                    .query
                    .filter_by(location="On Shelf")
                    .order_by(Status.timestamp.desc())
                    .limit(10))

        #Get ratings specific to user
        rated_books = (BookRating.query
                    .filter_by(user_rating=g.user.user_id)
                    .all())
        
        #Filter out book ids from ratings and send back as list
        reviews_book_ids = [review.book_rated for review in rated_books]

        #render this template for users that is logged in.
        return render_template('home.html', status=latest_books, reviews=reviews_book_ids)

    else:
        #render this template for users that have not logged in.
        return render_template('home-anon.html')


#--------------------------------------------------------------------------#
#--------------------------------------------------------------------------#
#                   Register, Login, and Logout Routes
#--------------------------------------------------------------------------#
#--------------------------------------------------------------------------#

def do_login(user):
    """Log in user by adding user to session."""
    session[CURR_USER_KEY] = user.user_id


def do_logout():
    """Logout user by deleting the user from the session."""
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
            form.username.errors.append('Sorry, but this username is taken.  Please pick another.')
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
        #authenticates user against saved credentials
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
#--------------------------------------------------------------------------#
#                   API Routes from JavaScript to OpenLibrary
#--------------------------------------------------------------------------#
#--------------------------------------------------------------------------#


@app.route("/addbooks")
def add_books():
    """Render search form"""

    return render_template('books/search_wh.html')

@app.route('/api/search-wh')
def search_wh():
    """ Upon receipt of AJAX request, we save arguments and search the API Warehouse Class.  
    If we find books, those are saved into our Book Table to save the search findings.
    We will also serialize information for JSON response
    If results are empty, we provide the user with JSON message.
    """

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
#--------------------------------------------------------------------------#
#                  Book Routes
#--------------------------------------------------------------------------#
#--------------------------------------------------------------------------#


@app.route('/book/add-book')
def add_book():
    """ Upon seeing API search results on FrontEnd, users can add any books to 
    their shelf which are directly tied from User to Status to Book tables. 
    This allows the append option to work. Note, we use the book key when 
    working with the API results to ensure a unique book.
    """
    
    key = request.args['key']

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")
    
    book_to_add = Book.query.filter_by(key=key).first() 
    book_to_add.user.append(g.user)
    db.session.commit()      

    return (jsonify("Book Added"),201)


@app.route('/search')
def search_booklandia():
    """A user can search the Books Database which will look at the title, author, and description. 
       There is a field in the nav bar that will collect arguments and send to this path.  
       We have to format and the arguments with SQL like arguments i.e. %.
       Upon finding in Book Table, we then filter out books that can be borrowed.
       We serve up those findings on a results page. 
    """
 
    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    term = request.args["term"]
    search_term = "%{}%".format(term) 
   
    findings = (Book.query
            .filter((Book.title.ilike(search_term)) | (Book.author.ilike(search_term)) | (Book.description.ilike(search_term)))
            .order_by(Book.title.desc())
            .all())

    found_books_ids = [book.book_id for book in findings]

    found_books = (Status.query
                    .filter(Status.book_id.in_(found_books_ids))
                    .limit(20))

    return render_template('books/results.html', status=found_books)


@app.route('/book/<int:book_id>')
def book_info(book_id):
    """ Every book has it's own page. You can see details about specific book, requests/owners, and reviews.
    To show necessary information, we query against the book table, the status table, and the book rating table.
    """
    
    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    book = Book.query.filter_by(book_id=book_id).one()
    book_statuses = Status.query.filter_by(book_id=book_id).all()
    book_reviews = BookRating.query.filter_by(book_rated=book_id).all()
    reviews_user_ids = [review.user_rating for review in book_reviews]

    return render_template('books/info.html', book=book, statuses=book_statuses, ratings=book_reviews, user_ids=reviews_user_ids)


@app.route('/book/<int:book_id>/update', methods=["GET","POST"])
def update_book(book_id):
    """ If a user owns a book, they have the ability to update the book's location and condition. Users will 
    not be able to update books that are own by other users. They are presented with a WTForm for these two arguments.
    These values are then committed to the database for the specific book being updated."""
    
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
        return redirect("/user/library")
    return render_template('books/update_bk.html', form=form, book=user_book)


@app.route('/book/<int:book_id>/delete', methods=["POST"])
def delete_book(book_id):
    """ While updating a book that they own, they can delete this from their libarary by committing 
    the delete to the status table. This will not delete the book from the book table.  
    """
    
    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    user_book = Status.query.filter_by(user_id=g.user.user_id,book_id=book_id).one()
    db.session.delete(user_book)
    db.session.commit()
    flash("Book removed from library.", "success")
    return redirect("/user/library")


@app.route('/book/<int:book_id>/<int:user_id>/request', methods=["POST"])
def request_book(book_id,user_id):
    """If a user finds a book where location of book is "On the Shelf", they can request this book.
    Upon hitting the request button, this route is taken. The request is saved in the Borrower Table and 
    will remain there until the owner of the book approves/disapproves the request. 
    The user is redirected to see all requests that they have made and that are requesting his/her book. 
    """

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
    """Book Owner can approve the request that has been made on their book.
       This will update the status of book to "Checked Out".
    """
    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    user_book = Status.query.filter_by(book_id=book_id,user_id=user_id).one()
    user_book.location = "Checked Out"

    db.session.commit()
    return redirect ('/user/requests')

@app.route('/book/<int:book_id>/<int:user_id>/reject', methods=["POST"])
def reject_request(book_id,user_id):
    """Book Owner can reject the request that has been made on their book.
       This will remove the request from the Borrower table and put the book back on the shelf.
    """

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

@app.route('/book/<int:book_id>/<int:user_id>/review', methods=["GET","POST"])
def review_book(book_id,user_id):
    """Logged in user can write a review and provide a rating on any book. We first query to get the 
    specific book object. Upon validating WTForm, we create a new rating record in the BookRating table.
    With the added rating, we need to update the Avg Rating for the book in question. We perform a 
    SQL func avg call that groups all ratings for that one book and save to variable. Because the average
    comes back as a dictionary and decimal, we need to do some formatting and type conversion before
    committing to the Book Column "avg_rating".
    """
    
    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    form=BookReviewForm()

    book_under_review = Book.query.get(book_id)
    user = User.query.get(user_id)

    if form.validate_on_submit():
        rating = request.form['rating']
        review = request.form['review']
        new_rating = BookRating(book_rated=book_under_review.book_id, 
                    user_rating=user.user_id,rating=rating,review=review)
        db.session.add(new_rating)
        db.session.commit()

       
        average_rating = (BookRating.query.with_entities(func.avg(BookRating.rating))
                        .filter(BookRating.book_rated==book_id).group_by(BookRating.book_rated).all())
        book_under_review.avg_rating = book_under_review.calc_avg_rating(average_rating)
        db.session.commit()

        flash("Rating and review added.", "success")
        return redirect("/")

    return render_template('books/review.html', form=form, book=book_under_review)


@app.route('/book/<int:book_id>/<int:user_id>/review/update', methods=["GET","POST"])
def update_book_review(book_id,user_id):
    """If a user has an existing review on specific book, they can update the rating and review in this route.
    Because they may have changed their rating value, we need to ensure the avg_rating is updated.
    """
        
    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")
    
    book_under_review = Book.query.get(book_id)

    form=BookReviewForm()

    if form.validate_on_submit():
        rating = request.form['rating']
        review = request.form['review']

        current_review = BookRating.query.filter_by(book_rated=book_id,user_rating=user_id).one()
        current_review.rating = rating
        current_review.review = review

        average_rating = (BookRating.query.with_entities(func.avg(BookRating.rating))
                        .filter(BookRating.book_rated==book_id).group_by(BookRating.book_rated).all())
        book_under_review.avg_rating = book_under_review.calc_avg_rating(average_rating)
        db.session.commit()

        flash("Rating and review updated.", "success")
        return redirect("/")
    
    return render_template('books/update_rv.html', form=form, book=book_under_review)


#--------------------------------------------------------------------------#
#--------------------------------------------------------------------------#
#                  User Routes
#--------------------------------------------------------------------------#
#--------------------------------------------------------------------------#


@app.route('/user/all')
def see_all_users():
    """Render a list of all users only if you are a logged in user"""
    
    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    users = User.query.all()
    lender_ratings = LenderRating.query.filter_by(user_rating_id=g.user.user_id)
    ratings = [lender.user_being_rated_id for lender in lender_ratings]

 
    return render_template('users/all.html',users=users,ratings=ratings)


@app.route('/user/library')
def see_library():
    """For logged in user, show books that they have added to their library.
       This will also render buttons to update status and update reviews so this will
       query status table and book ratings table as well.
    """

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")
    
    book_ids = [status.book_id for status in g.user.status]
 
    statuses = (Status.query
            .filter(Status.book_id.in_(book_ids))
            .filter_by(user_id=g.user.user_id)
            .order_by(Status.timestamp.desc()))
    
    rated_books = (BookRating.query
                    .filter_by(user_rating=g.user.user_id)
                    .all())
    reviews_book_ids = [review.book_rated for review in rated_books]

    return render_template('users/library.html',statuses=statuses, reviews=reviews_book_ids)


@app.route('/user/profile')
def see_profile():
    """For Logged in User, show the user's profile by querying the user table."""
    
    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")
    
    current_user = User.query.get(session[CURR_USER_KEY])
    return render_template('users/profile.html',user=current_user)


@app.route('/user/profile/<int:user_id>')
def see_requestor_profile(user_id):
    """This routes shows a profile of another user not the logged in user.
       Queries the status to show which books they own.  Queries the book rating table
       to show what books they have rated with the rating and review. 
    """
    
    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    requestor = User.query.get(user_id)

    statuses = (Status.query
            .filter_by(user_id=requestor.user_id)
            .order_by(Status.timestamp.desc()))
    
    rated_books = (BookRating.query
                    .filter_by(user_rating=user_id)
                    .all())

    return render_template('users/requestor.html',user=requestor,statuses=statuses,ratings=rated_books)


@app.route('/user/profile/update', methods=["GET", "POST"])
def update_profile():
    """For Logged in User, they can update their profile if they can enter their password correctly.
       If password incorrect, they will have to keep trying or move to another page. They will have 
       the ability to update all fields except username and password."""

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
            return redirect("/user/profile")

        flash("Password incorrect. Profile updates not saved.","warning")


    return render_template('users/update.html',user=current_user, form=form)

@app.route('/user/requests')
def show_requests():
    """For logged in user, this will query the borrowers table to see what has been 
    "borrowed/requested" by user. Additionally, we show all books owned by user and those
    statuses.  We end up showing what is relevant for that particular user. 
    """

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
                    .filter((Borrower.borrower_id==g.user.user_id) | (Borrower.status_owner_id==g.user.user_id))
                    .all())
    return render_template('users/requests.html', statuses=all_requests, requestor=user_borrows)

@app.route('/user/<int:user_id>/review', methods=["GET","POST"])
def review_lender(user_id):
    """Logged in user can write a review and provide a rating someone who has lended a book to them. 
    We first query Borrower to make sure their is at least one instance of a borrow. 
    Upon validating WTForm, we create a new rating record in the LenderRating table.
    With the added rating, we need to update the Avg Rating for the user in question. We perform a 
    SQL func avg call that groups all ratings for that one userk and save to variable. Because the average
    comes back as a dictionary and decimal, we need to do some formatting and type conversion before
    committing to the "avg_rating" to the User.
    """
    
    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")
    lender_under_review = User.query.get(user_id)
    form=LenderReviewForm()
    has_borrowed = (Borrower.query
                    .filter((Borrower.status_owner_id==user_id),(Borrower.borrower_id==g.user.user_id))
                    .first())
    if has_borrowed:
        
        if form.validate_on_submit():
            rating = request.form['rating']
            review = request.form['review']
            new_rating = LenderRating(user_being_rated_id=lender_under_review.user_id, user_rating_id=g.user.user_id,rating=rating,review=review)
            db.session.add(new_rating)
            db.session.commit()
            average_rating = (LenderRating.query.with_entities(func.avg(LenderRating.rating))
                        .filter(LenderRating.user_being_rated_id==lender_under_review.user_id)
                        .group_by(LenderRating.user_being_rated_id).all())
            lender_under_review.avg_rating = lender_under_review.calc_avg_rating(average_rating)
            db.session.commit()

            flash("Rating and review added.", "success")
            return redirect("/user/all")
    else:
        flash("Rating not added as you need to have borrowed previously from user.", "danger")
        return redirect("/user/all")

    return render_template('users/review.html', form=form, lender=lender_under_review)


@app.route('/user/<int:user_id>/review/update', methods=["GET","POST"])
def update_user_review(user_id):
    """If a user has an existing review on a user, they can update the rating and review in this route.
    Because they may have changed their rating value, we need to ensure the avg_rating is updated 
    for the specified user.
    """
        
    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")
    
    lender_under_review = User.query.get(user_id)

    form=LenderReviewForm()

    if form.validate_on_submit():
        rating = request.form['rating']
        review = request.form['review']

        current_review = LenderRating.query.filter_by(user_being_rated_id=user_id,user_rating_id=g.user.user_id).one()
        current_review.rating = rating
        current_review.review = review

        average_rating = (LenderRating.query.with_entities(func.avg(LenderRating.rating))
                        .filter(LenderRating.user_being_rated_id==lender_under_review.user_id)
                        .group_by(LenderRating.user_being_rated_id).all())

        lender_under_review.avg_rating = lender_under_review.calc_avg_rating(average_rating)
        db.session.commit()

        flash("Rating and review updated.", "success")
        return redirect("/user/all")
    
    return render_template('users/update_rv.html', form=form, user=lender_under_review)