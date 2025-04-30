#menu data base work in progress, not finished 
from ..db import db

class Menu(db.Model):
    
    __FullMenu__ = 'menuItems'  # Name of the table in the database
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)  # Unique id for each user
    picture = db.Column(db.String(150), nullable=False) 
    name = db.Column(db.String(150), nullable=False)  # dish's names
    price = db.Column(db.String(150), unique=True, nullable=False)  # 
    icons = db.Column(db.String(255), nullable=False)  # 
    ingredients = db.Column(db.String(15))
    stats = db.Column(db.String(100))
