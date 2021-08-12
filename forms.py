#--------------------------------------------------------------------------#
#  Capstone Project:  BookLandia
#  I used WTForms to validate input and assign input types for forms.
#
#  Register Form - collects user profile information to register with the app
#  Login Form - collects username and password to login
#  Status Form - collects book location and condition information from user
#  Profile Form - collects profile updates from user
#  BookReview Form - collects book's rating and review from user
#  References: 
#  --- Previous projects in GitHub Repository 
#  --- SpringBoard Exercises & Lessons
#  
#  By: Eldy Deines  Date: 8/11/2021
#--------------------------------------------------------------------------#


#--------------------------------------------------------------------------#
#                           Import Necessary Libraries 
#--------------------------------------------------------------------------#

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, SelectField
from wtforms.validators import InputRequired, DataRequired, Email, Length


#--------------------------------------------------------------------------#
#                           Forms
#--------------------------------------------------------------------------#

class RegisterForm(FlaskForm):
    """Form to register users"""
    username = StringField("Username", validators=[InputRequired()])
    password = PasswordField("Password", validators=[InputRequired(), Length(min=6)])
    first_name = StringField("First Name", validators=[InputRequired()])
    last_name = StringField("Last Name", validators=[InputRequired()])   
    address1 = StringField("Address (Line 1)", validators=[InputRequired()])  
    address2 = StringField("Address (Line 2")  
    town = StringField("City/Town", validators=[InputRequired()])  
    state = StringField("State", validators=[InputRequired()])  
    zip = StringField("Zip", validators=[InputRequired()])
    phone = StringField("Phone", validators=[InputRequired()])  
    email = StringField("Email", validators=[InputRequired(), Email()]) 
    profile = TextAreaField("Profile", description="Brief Description About Yourself")
    fav_book = StringField("Favorite Book") 
    fav_author = StringField("Favorite Author") 


class LoginForm(FlaskForm):
    """Form to login users"""

    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[Length(min=6)])


class StatusForm(FlaskForm):
    """Form for a user to update Book Location and Condition"""

    location = SelectField(u'Location of Book', choices=[('On Shelf'), ('Requested'), ('Checked Out'), ('Off Shelf')])
    condition = SelectField(u'Condition of Book', choices=[('Like New'), ('Worn'), ('Held by Tape')])


class ProfileForm(FlaskForm):
    """ Form to update a user's profile"""
    
    first_name = StringField("First Name")
    last_name = StringField("Last Name")   
    address1 = StringField("Address (Line 1)")  
    address2 = StringField("Address (Line 2")  
    town = StringField("City/Town")  
    state = StringField("State")  
    zip = StringField("Zip")
    phone = StringField("Phone")  
    email = StringField("Email") 
    profile = TextAreaField("Profile", description="Brief Description About Yourself")
    fav_book = StringField("Favorite Book") 
    fav_author = StringField("Favorite Author") 
    password = PasswordField('Please enter your password to save updates.', validators=[InputRequired()])


class BookReviewForm(FlaskForm):
    """Form to review books"""
    
    rating = SelectField(u'Rating', choices=[(5, '5 Stars: Drop Everything and Read Now!'), 
    (4, '4 Stars: Pretty Good, Would Recommend to Friends'), 
    (3, '3 Stars: Eh, In between'), 
    (2,'2 Stars: Struggled to finish'),
    (1, '1 Star: Do Not Bother')])
    review = TextAreaField(u'Book Review',validators=[InputRequired()])