import math


class Point:
    def __init__(self, x = 0, y = 0):
        self.x = x
        self.y = y

    # Distance of a point to another point
    def dist_to_point(self, other_p = None):
        if not other_p:
            other_p = Point()

        return ((self.x-other_p.x)**2 + (self.y-other_p.y)**2)**.5

    # Projection of a point on a line that contains the segment
    def projection_on_segment(self, segment):

        segment_vector = Point(segment.end_point.x - segment.start_point.x, segment.end_point.y - segment.start_point.y)
        point_vector = Point(self.x - segment.start_point.x, self.y - segment.start_point.y)
        dot_product = segment_vector.x * point_vector.x + segment_vector.y * point_vector.y

        segment_length_squared = segment.length() ** 2

        if dot_product <= 0:
            projection = segment.start_point
        elif dot_product >= segment_length_squared:
            projection = segment.end_point
        else:
            projection_x = segment.start_point.x + (dot_product / segment_length_squared) * segment_vector.x
            projection_y = segment.start_point.y + (dot_product / segment_length_squared) * segment_vector.y
            projection = Point(projection_x, projection_y)

        return projection


class Segment:
    def __init__(self, start_point, end_point):
        self.start_point = start_point
        self.end_point = end_point

    def length(self):
        return self.start_point.dist_to_point(self.end_point)

    # Angle of a segment to another segment
    def angle_to_segment(self, other_segment):
        vector1 = (self.end_point.x - self.start_point.x, self.end_point.y - self.start_point.y)
        vector2 = (other_segment.end_point.x - other_segment.start_point.x,
                   other_segment.end_point.y - other_segment.start_point.y)

        dot_product = vector1[0] * vector2[0] + vector1[1] * vector2[1]

        length1 = math.sqrt(vector1[0] ** 2 + vector1[1] ** 2)
        length2 = math.sqrt(vector2[0] ** 2 + vector2[1] ** 2)

        cosine = dot_product / (length1 * length2)

        angle = math.acos(cosine)

        sign = math.copysign(1, vector1[0] * vector2[1] - vector1[1] * vector2[0])

        return sign * math.degrees(angle) % 360

    # Angle to the x-axis
    def polar_angle(self):
        pass

s1 = Segment(Point(), Point(5,0))
s2 = Segment(Point(), Point(0,5))
print(s1.angle_to_segment(s2))