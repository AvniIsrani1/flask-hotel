from ..db import db
from .Enums import YesNo, Locations
from ..model_objects import Ho


class Floor(db.Model):
    id = db.Column(db.Integer, primary_key=True) 
    hid = db.Column(db.Integer, db.ForeignKey('hotel.id'))
    floor_number = db.Column(db.Integer,nullable=False)
    rooms = db.relationship('Room', backref='floor', lazy=True, cascade='all, delete-orphan') #floor is keeping track of rooms

    __table_args__ = (db.UniqueConstraint('hid', 'floor_number', name='hid_floor_number_unique'),)

    @classmethod
    def add_floor(cls, number_floors, hid, base_floor_number):
        floors = []
        for i in range(number_floors):
            floor = cls(hid=hid, floor_number=base_floor_number+i)
            floors.append(floor)
        db.session.add_all(floors)
        db.session.commit()

    #############################################
    
    def create_floor_object(self):
        return Ho(
             id=self.id,hid=self.hid,floor_number=self.floor_number
        ) #does not handle rooms logic!!!
    
    @classmethod
    def create_floors_db(cls, floors):
        floor_rows=[]
        for floor in floors:
            floor_rows.append(
                cls(
                    id=cls.id,hid=cls.hid,floor_number=cls.floor_number
                )
            ) #does not handle floors logic!!!
        return floor_rows

    @classmethod
    def update_floors_db(cls, floor):
        model=cls.query.get(floor.id)
        if model:
            model.hid=floor.hid
            model.floor_number=floor.floor_number
            return True
        return False
