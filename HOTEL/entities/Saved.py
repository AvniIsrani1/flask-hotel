from ..db import db

class Saved(db.Model):
    """
    Model representing saved room favorites for users.
    
    This class manages the relationship between users and rooms they have saved
    as favorites for future reference.

    Note:
        Author: Avni Israni
        Documentation: Devansh Sharma
        Created: March 20, 2025
        Modified: April 17, 2025
    """
    __tablename__ = 'saved'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    uid = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    rid = db.Column(db.Integer, db.ForeignKey('rooms.id'), nullable=False) 
    user = db.relationship('User', backref=db.backref('saved_u', lazy=True))
    room = db.relationship('Room', backref=db.backref('saved_r', lazy=True))