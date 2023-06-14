import tkinter as tk
import heapq
import itertools
import math
import random
import time


class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def dist_to_point(self, other_p=None):
        if not other_p:
            other_p = Point()

        return ((self.x - other_p.x) ** 2 + (self.y - other_p.y) ** 2) ** 0.5

    def midpoint_to(self, other_p=None):
        if not other_p:
            other_p = Point()

        return Point((self.x + other_p.x) / 2, (self.y + other_p.y) / 2)


class Event:
    def __init__(self, x, p, a):
        self.x = x
        self.p = p
        self.a = a
        self.valid = True


class Arc:
    def __init__(self, p, a=None, b=None):
        self.p = p
        self.pprev = a
        self.pnext = b
        self.e = None
        self.s0 = None
        self.s1 = None


class Segment:
    def __init__(self, p):
        self.start = p
        self.end = None
        self.done = False

    def finish(self, p):
        if self.done: return
        self.end = p
        self.done = True


class PriorityQueue:
    def __init__(self):
        self.pq = []
        self._index = 0

    def is_empty(self):
        return not self.pq

    def push(self, item):
        heapq.heappush(self.pq, (item.x, self._index, item))
        self._index += 1

    def pop(self):
        if self.is_empty():
            return None
        return heapq.heappop(self.pq)[-1]

    def top(self):
        if self.is_empty():
            return None
        return self.pq[0][-1]

    def empty(self):
        return not self.pq


class DrawingApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Drawing App")

        self.canvas = tk.Canvas(self.master, width=1600, height=900, bg="white")
        self.canvas.pack()

        self.points = []
        self.canvas.bind("<Button-1>", self.add_point)
        self.canvas.bind("<Button-2>", self.clear_canvas)
        self.canvas.bind("<Button-3>", self.runVoronoi)

        self.canvas.grid(row=1, column=0, columnspan=3)

        # Add textfield and button horizontally
        self.point_num_entry = tk.Entry(self.master)
        self.point_num_entry.grid(row=0, column=0)

        self.add_points_button = tk.Button(self.master, text="Add Random Points", command=self.add_random_points)
        self.add_points_button.grid(row=0, column=1)

        # initialize boundary box
        self.x0 = 0.0
        self.x1 = 0.0
        self.y0 = 0.0
        self.y1 = 0.0

        self.output = []
        self.vertices = []
        self.arc = None

        self.events = PriorityQueue()

    def add_random_points(self):
        try:
            num_points = int(self.point_num_entry.get())
        except ValueError:
            print("Invalid integer. Please enter a valid number.")
            return

        for _ in range(num_points):
            x, y = random.randint(0, 1600), random.randint(0, 900)
            self.points.append((x, y))
            self.canvas.create_oval(x - 3, y - 3, x + 3, y + 3, fill="black")

        self.voronoi()

    def add_point(self, event):
        x, y = event.x, event.y
        print('x = ', x, ' ,  y = ', y)
        self.points.append((x, y))
        self.canvas.create_oval(x - 3, y - 3, x + 3, y + 3, fill="black")

    def clear_canvas(self, event=None):
        self.points = []
        self.x0 = 0.0
        self.x1 = 0.0
        self.y0 = 0.0
        self.y1 = 0.0
        self.output = []
        self.vertices = []
        self.arc = None
        self.pointEvents = PriorityQueue()
        self.event = PriorityQueue()
        self.canvas.delete("all")

    def runVoronoi(self, event):
        self.voronoi()

    def drawOutput(self):
        for o in self.output:
            p0 = o.start
            p1 = o.end
            if (p0 is not None) and (p1 is not None):
                self.canvas.create_line(p0.x, p0.y, p1.x, p1.y, fill='blue')

        for vertex in self.vertices:
            x = vertex.x
            y = vertex.y
            self.canvas.create_oval(x - 3, y - 3, x + 3, y + 3, fill="red")

    def process_point_event(self, site_event):
        if self.arc is None:
            self.arc = Arc(site_event)
        else:
            current_arc = self.arc
            while current_arc is not None:
                intersection_point = self.check_parabola_intersection(site_event, current_arc)

                if intersection_point is not None:
                    next_intersection_point = self.check_parabola_intersection(site_event, current_arc.pnext)

                    if (current_arc.pnext is not None) and (next_intersection_point is None):
                        current_arc.pnext.pprev = Arc(current_arc.p, current_arc, current_arc.pnext)
                        current_arc.pnext = current_arc.pnext.pprev
                    else:
                        current_arc.pnext = Arc(current_arc.p, current_arc)
                    current_arc.pnext.s1 = current_arc.s1

                    current_arc.pnext.pprev = Arc(site_event, current_arc, current_arc.pnext)
                    current_arc.pnext = current_arc.pnext.pprev

                    new_arc = current_arc.pnext

                    new_segment = Segment(intersection_point)
                    self.output.append(new_segment)
                    new_arc.pprev.s1 = new_arc.s0 = new_segment

                    new_segment = Segment(intersection_point)
                    self.output.append(new_segment)
                    new_arc.pnext.s0 = new_arc.s1 = new_segment

                    # Check for new circle events around the new arc
                    self.check_circle_event(new_arc)
                    self.check_circle_event(new_arc.pprev)
                    self.check_circle_event(new_arc.pnext)

                    return

                current_arc = current_arc.pnext

            # If site_event never intersects an arc, append it to the list
            current_arc = self.arc
            while current_arc.pnext is not None:
                current_arc = current_arc.pnext
            current_arc.pnext = Arc(site_event, current_arc)

            # Insert new segment between site_event and current_arc
            x_coordinate = self.x0
            y_coordinate = (current_arc.pnext.p.y + current_arc.p.y) / 2.0
            start_point = Point(x_coordinate, y_coordinate)

            new_segment = Segment(start_point)
            current_arc.s1 = current_arc.pnext.s0 = new_segment
            self.output.append(new_segment)

    def process_circle_event(self, circle_event):
        if circle_event.valid:
            # Start new Voronoi edge
            voronoi_edge = Segment(circle_event.p)
            self.output.append(voronoi_edge)
            self.vertices.append(circle_event.p)

            # Remove associated arc (parabola)
            associated_arc = circle_event.a
            if associated_arc.pprev is not None:
                associated_arc.pprev.pnext = associated_arc.pnext
                associated_arc.pprev.s1 = voronoi_edge
            if associated_arc.pnext is not None:
                associated_arc.pnext.pprev = associated_arc.pprev
                associated_arc.pnext.s0 = voronoi_edge

            # Finalize the Voronoi edges before and after associated arc
            if associated_arc.s0 is not None:
                associated_arc.s0.finish(circle_event.p)
            if associated_arc.s1 is not None:
                associated_arc.s1.finish(circle_event.p)

            # Recheck circle events on either side of current point
            if associated_arc.pprev is not None:
                self.check_circle_event(associated_arc.pprev)
            if associated_arc.pnext is not None:
                self.check_circle_event(associated_arc.pnext)

    def check_circle_event(self, parabola_arc):
        if (parabola_arc.e is not None) and (parabola_arc.e.x != self.x0):
            parabola_arc.e.valid = False
        parabola_arc.e = None

        if (parabola_arc.pprev is None) or (parabola_arc.pnext is None):
            return

        center, point1, point2 = parabola_arc.pprev.p, parabola_arc.p, parabola_arc.pnext.p
        if ((point1.x - center.x) * (point2.y - center.y) - (point2.x - center.x) * (point1.y - center.y)) > 0:
            return

        if (2 * ((point1.x - center.x) * (point2.y - point1.y) - (point1.y - center.y) * (
                point2.x - point1.x)) == 0): return  # Points are co-linear

        circle_center_x = 1.0 * ((point2.y - center.y) * (
                    (point1.x - center.x) * (center.x + point1.x) + (point1.y - center.y) * (center.y + point1.y)) - (
                                             point1.y - center.y) * (
                                             (point2.x - center.x) * (center.x + point2.x) + (point2.y - center.y) * (
                                                 center.y + point2.y))) / (2 * (
                    (point1.x - center.x) * (point2.y - point1.y) - (point1.y - center.y) * (point2.x - point1.x)))
        circle_center_y = 1.0 * ((point1.x - center.x) * (
                    (point2.x - center.x) * (center.x + point2.x) + (point2.y - center.y) * (center.y + point2.y)) - (
                                             point2.x - center.x) * (
                                             (point1.x - center.x) * (center.x + point1.x) + (point1.y - center.y) * (
                                                 center.y + point1.y))) / (2 * (
                    (point1.x - center.x) * (point2.y - point1.y) - (point1.y - center.y) * (point2.x - point1.x)))
        radius = math.sqrt((center.x - circle_center_x) ** 2 + (center.y - circle_center_y) ** 2)
        max_x = circle_center_x + radius
        circle_center = Point(circle_center_x, circle_center_y)

        if max_x > self.x0:
            parabola_arc.e = Event(max_x, circle_center, parabola_arc)
            self.events.push(parabola_arc.e)

    def calculate_intersection(self, point1, point2, directrix):
        parabola_focus = point1
        if (point1.x == point2.x):
            intersection_y = (point1.y + point2.y) / 2.0
        elif (point2.x == directrix):
            intersection_y = point2.y
        elif (point1.x == directrix):
            intersection_y = point1.y
            parabola_focus = point2
        else:
            z1 = 2.0 * (point1.x - directrix)
            z2 = 2.0 * (point2.x - directrix)

            coef_a = 1.0 / z1 - 1.0 / z2
            coef_b = -2.0 * (point1.y / z1 - point2.y / z2)
            coef_c = 1.0 * (point1.y ** 2 + point1.x ** 2 - directrix ** 2) / z1 - 1.0 * (
                        point2.y ** 2 + point2.x ** 2 - directrix ** 2) / z2

            intersection_y = 1.0 * (-coef_b - math.sqrt(coef_b * coef_b - 4 * coef_a * coef_c)) / (2 * coef_a)

        intersection_x = 1.0 * (parabola_focus.x ** 2 + (parabola_focus.y - intersection_y) ** 2 - directrix ** 2) / (
                    2 * parabola_focus.x - 2 * directrix)
        return Point(intersection_x, intersection_y)

    def check_parabola_intersection(self, new_point, parabola_arc):
        if (parabola_arc is None) or (parabola_arc.p.x == new_point.x):
            return None
        intersection_a_y = 0.0
        intersection_b_y = 0.0
        if parabola_arc.pprev is not None:
            intersection_a_y = self.calculate_intersection(parabola_arc.pprev.p, parabola_arc.p, 1.0 * new_point.x).y
        if parabola_arc.pnext is not None:
            intersection_b_y = self.calculate_intersection(parabola_arc.p, parabola_arc.pnext.p, 1.0 * new_point.x).y

        if (((parabola_arc.pprev is None) or (intersection_a_y <= new_point.y)) and (
                (parabola_arc.pnext is None) or (new_point.y <= intersection_b_y))):
            point_y = new_point.y
            point_x = 1.0 * ((parabola_arc.p.x) ** 2 + (parabola_arc.p.y - point_y) ** 2 - new_point.x ** 2) / (
                        2 * parabola_arc.p.x - 2 * new_point.x)
            return Point(point_x, point_y)

        return None

    def finalize_edges(self):
        max_distance = self.x1 + (self.x1 - self.x0) + (self.y1 - self.y0)
        current_arc = self.arc

        while current_arc.pnext is not None:
            if current_arc.s1 is not None:
                intersection_point = self.calculate_intersection(current_arc.p, current_arc.pnext.p, max_distance * 2.0)
                current_arc.s1.finish(intersection_point)
            current_arc = current_arc.pnext

    def voronoi(self):
        # insert points to site event
        for pts in self.points:
            point = Point(pts[0], pts[1])
            self.events.push(point)
            # keep track of bounding box size
            if point.x < self.x0:
                self.x0 = point.x
            if point.y < self.y0:
                self.y0 = point.y
            if point.x > self.x1:
                self.x1 = point.x
            if point.y > self.y1:
                self.y1 = point.y

        # add margins to the bounding box
        self.x0 = self.x0 - 1000
        self.x1 = self.x1 + 1000
        self.y0 = self.y0 - 1000
        self.y1 = self.y1 + 1000

        start = time.time() * 1000.0

        while not self.events.empty():
            event = self.events.pop()
            if (isinstance(event, Point)):
                self.process_point_event(event)
            else:
                self.process_circle_event(event)

        self.finalize_edges()

        self.drawOutput()

        end = time.time() * 1000.0

        print(end - start)


if __name__ == "__main__":
    root = tk.Tk()
    app = DrawingApp(root)
    root.mainloop()