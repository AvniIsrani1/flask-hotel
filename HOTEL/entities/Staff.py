from .User import User
from ..db import db
from sqlalchemy import DateTime, or_
from .Enums import Position


class Staff(User):
    """
    A table for storing staff information. 

    Inherits from the users table. 

    Note:
        Author: Avni Israni
        Documentation: Avni Israni
        Created: April 28, 2025
        Modified: April 28, 2025
    """
    position = db.Column(db.Enum(Position))
    salary = db.Column(db.Integer())
    supervisor_id = db.Column(db.Integer())
    startdate = db.Column(DateTime)

    services = db.relationship('Service', backref='staff', lazy=True, cascade='all, delete-orphan')  

    __mapper_args__ = {
        'polymorphic_identity': 'staff'
    }


    @classmethod
    def get_staff(cls, id):
        """
        Retrieve a staff member by their unique ID.

        Parameters: 
            id (int): The unique ID of the staff member.

        Returns:
            Staff | None: The Staff object if found, else None.
        """
        return cls.query.filter(cls.id==id).first()
    
    def get_assignable_staff(self):
        """
        Retrieve staff members who can be assigned to work under this staff member. 
        
        This includes the staff member themselves and al staff who report directly to this staff member 
        (where this staff member is their supervisor).

        Parameters:
            None
        
        Returns:
            list: A list of Staff objects that can be assigned, or an empty list if none found
        
        """
        return self.__class__.query.filter(or_(self.__class__.supervisor_id==self.id, self.__class__.id==self.id)).all()