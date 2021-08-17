#--------------------------------------------------------------------------#
#  Capstone Project:  BookLandia
#  Utilized seed file to create tables in Heroku Environment
#  
#  By: Eldy Deines  Date: 8/17/2021
#--------------------------------------------------------------------------#


from models import db, connect_db
from app import app

connect_db(app)

db.drop_all()
db.create_all()