class Point:
    def __init__(self, x = 0, y = 0):
        self.x = x
        self.y = y

    def dist_to_point(self, other_p = None):
        if not other_p:
            other_p = Point()

        return ((self.x-other_p.x)**2 + (self.y-other_p.y)**2)**.5

    def projection_on_segment(self, segment):
        pass


class Segment:
    def __init__(self, start_point, end_point):
        self.start_point = start_point
        self.end_point = end_point

    def length(self):
        return self.start_point.dist_to_point(self.end_point)

    def angle_to_segment(self, other):
        pass

    def polar_angle(self):
        pass


s = Segment(Point(), Point(5,5))
print(s.length)