class Point:
    def __init__(self, x_1, y_1):
        self.x_1 = x_1
        self.y_1 = y_1

    def dist(self, p):
        if isinstance(p, Point):
            return ((self.x_1 - p.x_1) ** 2 + (self.y_1 - p.y_1) ** 2) ** 0.5
        return None
