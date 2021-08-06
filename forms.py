from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, SelectField
from wtforms.validators import InputRequired, DataRequired, Email, Length

class RegisterForm(FlaskForm):
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
    """Login form."""

    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[Length(min=6)])

class StatusForm(FlaskForm):
    """Update Book Location and Condition"""

    location = SelectField(u'Location of Book', choices=[('On Shelf'), ('Requested'), ('On Loan'), ('Off Shelf')])
    condition = SelectField(u'Condition of Book', choices=[('Like New'), ('Worn'), ('Held by Tape')])