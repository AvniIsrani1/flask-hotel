class Ho:
    def __init__(self, id=None, location=None, address=None, free_wifi=None, free_breakfast=None, 
                 pool=None, gym=None, golf=None):
        self.id = id
        self.location = location
        self.address = address
        self.free_wifi = free_wifi
        self.free_breakfast = free_breakfast
        self.pool = pool
        self.gym = gym
        self.golf = golf
        self.floors = []
        self.rooms = []
    