class Coordinates:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

    def __init__(self, x):
        self.x = x.x
        self.y = x.y
        self.z = x.z

    def __init__(self):
        self.x = 0
        self.y = 0
        self.z = 0
