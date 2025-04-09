from HOTEL.model_objects import User
class Manager(User):
    def __init__(self, discount_amt=0):
        super().__init__(self)
        self.discount_amt = discount_amt
