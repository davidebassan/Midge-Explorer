class Coordinates:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

    def __init__(self, x):
        self.x = x.x
        self.y = x.y
        self.z = x.z