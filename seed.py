from models import db, connect_db
from app import app

connect_db(app)

db.drop_all()
db.create_all()