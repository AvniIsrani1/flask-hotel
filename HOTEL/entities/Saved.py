from ..db import db

class Saved(db.Model):
    __tablename__ = 'saved'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    uid = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    rid = db.Column(db.Integer, db.ForeignKey('room.id'), nullable=False) 
    user = db.relationship('Users', backref=db.backref('saved_u', lazy=True))
    room = db.relationship('Room', backref=db.backref('saved_r', lazy=True)) 