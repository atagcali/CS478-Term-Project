import math
import tkinter as tk

class Point:
    def __init__(self, x = 0, y = 0):
        self.x = x
        self.y = y

    # Distance of a point to another point
    def dist_to_point(self, other_p = None):
        if not other_p:
            other_p = Point()

        return ((self.x-other_p.x)**2 + (self.y-other_p.y)**2)**0.5
    
    def midpoint_to(self, other_p = None):
        if not other_p:
            other_p = Point()

        return Point((self.x + other_p.x) / 2, (self.y + other_p.y) / 2)

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
        x_axis = Segment(Point(), Point(1,0))
        return x_axis.angle_to_segment(self)

    '''
    D > 0: Left
    D = 0: On line
    D < 0: Right
    '''
    def left_test(self, point):
        x0 = self.start_point.x
        x1 = self.end_point.x
        x2 = point.x
        y0 = self.start_point.y
        y1 = self.end_point.y
        y2 = point.y

        return x0*y1 + x2*y0 + x1*y2 - x2*y1 - x0*y2 - x1*y0

    '''
    a>1     : Before the segment
    a=1     : start_point
    1<a<0   : On segment
    a=0     : end_point
    a<0     = After the segment
    '''
    def segment_test(self, point):
        a1 = (point.x - self.end_point.x) / (self.start_point.x - self.end_point.x)
        a2 = (point.y - self.end_point.y) / (self.start_point.y - self.end_point.y)

        if a1 == a2: # Point is on line
            return a1
        
class Vertex:
    def __init__(self, point):
        self.point = point
        self.incident_edge = None

class Edge:
    def __init__(self, origin, destination):
        self.origin = origin
        self.destination = destination
        self.left_face = None
        self.right_face = None
        self.prev_edge_origin = None
        self.prev_edge_destination = None

class Face:
    def __init__(self):
        self.incident_edge = None

class DCEL:
    def __init__(self):
        self.vertices = []
        self.edges = []
        self.faces = []

    def add_vertex(self, point):
        vertex = Vertex(point)
        self.vertices.append(vertex)
        return vertex

    def add_edge(self, origin, destination):
        edge = Edge(origin, destination)
        self.edges.append(edge)
        return edge

    def add_face(self):
        face = Face()
        self.faces.append(face)
        return face

    def set_edge_faces(self, edge, left_face, right_face):
        edge.left_face = left_face
        edge.right_face = right_face

    def set_prev_edges(self, edge, prev_edge_origin, prev_edge_destination):
        edge.prev_edge_origin = prev_edge_origin
        edge.prev_edge_destination = prev_edge_destination

    def set_incident_edge(self, vertex, edge):
        vertex.incident_edge = edge

    def set_incident_edge_face(self, face, edge):
        face.incident_edge = edge

    def draw(self, canvas):
        drawn_vertices = set()

        for edge in self.edges:
            origin = edge.origin.point
            destination = edge.destination.point

            canvas.create_line(origin.x, origin.y, destination.x, destination.y)
            self._draw_vertex(canvas, origin, edge.origin, drawn_vertices)
            self._draw_vertex(canvas, destination, edge.destination, drawn_vertices)

            edge_label_offset_x = 10
            edge_label_offset_y = -10

            edge_label_x = (origin.x + destination.x) / 2 + edge_label_offset_x
            edge_label_y = (origin.y + destination.y) / 2 + edge_label_offset_y
            canvas.create_text(edge_label_x, edge_label_y, text=f"E{self.edges.index(edge)}", anchor="nw")

        for vertex in self.vertices:
            if vertex not in drawn_vertices:
                self._draw_vertex(canvas, vertex.point, vertex, drawn_vertices)

    def _draw_vertex(self, canvas, point, vertex, drawn_vertices):
        if vertex in drawn_vertices:
            return

        canvas.create_oval(point.x - 2, point.y - 2, point.x + 2, point.y + 2, fill='red')
        vertex_label_offset = 5
        canvas.create_text(point.x + vertex_label_offset, point.y + vertex_label_offset, text=f"V{self.vertices.index(vertex)}", anchor="nw")
        drawn_vertices.add(vertex)

class DCELApp:
    def __init__(self, master):
        self.master = master
        self.master.title("DCEL Editor")

        self.canvas = tk.Canvas(self.master, width=300, height=300)
        self.canvas.pack()
        self.canvas.bind("<Button-1>", self.on_canvas_click)

        self.dcel = DCEL()
        v1 = self.dcel.add_vertex(Point(50, 50))
        v2 = self.dcel.add_vertex(Point(250, 50))
        v3 = self.dcel.add_vertex(Point(150, 250))

        e1 = self.dcel.add_edge(v1, v2)
        e2 = self.dcel.add_edge(v2, v3)
        e3 = self.dcel.add_edge(v3, v1)

        self.dcel.set_prev_edges(e1, e3, e2)
        self.dcel.set_prev_edges(e2, e1, e3)
        self.dcel.set_prev_edges(e3, e2, e1)
        self.dcel.draw(self.canvas)


    def on_canvas_click(self, event):
        x, y = event.x, event.y
        new_vertex = self.dcel.add_vertex(Point(x, y))
        self.dcel.draw(self.canvas)


if __name__ == "__main__":
    root = tk.Tk()
    app = DCELApp(root)
    root.mainloop()