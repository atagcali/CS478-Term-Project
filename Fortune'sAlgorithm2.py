import tkinter as tk
import math
import heapq


from DataTypes import Point, Segment 

class PriorityQueue:
    def __init__(self):
        self.pq = []

    def is_empty(self):
        return not self.pq
    
    def put(self, item):
        priority = item.x  # The lower the x-coordinate, the higher the priority. 
        heapq.heappush(self.pq, (priority, item))

    def pop(self):
        return heapq.heappop(self.pq)[1]
    
    def top(self):
        return self.pq[0][1] if self.pq else None

class CircleQueue:
    def __init__(self):
        self.cq = []

    def is_empty(self):
        return not self.cq
    
    def put(self, item):
        eventPoint = item.eventPoint
        self.cq.append((eventPoint.x, item))
        self.cq.sort(key=lambda x: x[0])  # Sort the queue based on x-coordinate.


    def pop(self):
        return self.cq.pop(0)[1] if self.cq else None
    
    def top(self):
        return self.cq[0][1] if self.cq else None


class ArcNode:
    def __init__(self, p, a=None, b=None):
        self.p = p
        self.pprev = a
        self.pnext = b
        self.segment0 = None
        self.segment1 = None

class CircleEvent:
    def __init__(self, center, radius, arc, belowArc, aboveArc):
        self.center = center
        self.radius = radius
        self.arc = arc
        self.belowArc = belowArc
        self.aboveArc = aboveArc
        self.x = center.x
        self.eventPoint = Point(center.x + radius, center.y)

        def __lt__(self, other):
            return self.eventPoint.x < other.eventPoint.x
        
class DrawingApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Drawing App")
        
        self.canvas = tk.Canvas(self.master, width=1600, height=900, bg="white")
        self.canvas.pack()
        
        self.points = []
        self.lines = []
        self.canvas.bind("<Button-1>", self.add_point)
        self.canvas.bind("<Button-2>", self.clear_canvas)
        self.canvas.bind("<Button-3>", self.voronoi)


        #Data For Voronoi Diagram
        self.pointEvent = PriorityQueue() #points
        self.circleEvent = CircleQueue() #events
        self.rootArc = None #root of bst




        self.seenPoints = []
        self.bstLength = 0
        self.voronoiVertices = []
        self.voronoiEdges = []
        self.halfEdges = []
            
    def add_point(self, event):
        x, y = event.x, event.y
        print('x = ', x, ' ,  y = ', y)
        self.points.append((x, y))
        self.canvas.create_oval(x-3, y-3, x+3, y+3, fill="black")
    
    def clear_canvas(self, event):
        self.points = []
        self.lines = []
        self.canvas.delete("all")

    def voronoi(self, event):
        for point in self.points:
            p = Point(point[0], point[1])
            self.pointEvent.put(p)
        
        while not self.pointEvent.is_empty():
            if not self.circleEvent.is_empty() and (self.circleEvent.top().eventPoint.x <= self.pointEvent.top().x):
                self.process_event()
            else:
                self.process_point()
        while not self.circleEvent.is_empty():
            self.process_event()
        # Print Voronoi vertices
        for vertex in self.voronoiVertices:
            x = vertex.x
            y = vertex.y
            print('voronoi vertex x : ', x , ' y : ', y )
            self.canvas.create_oval(x - 3, y - 3, x + 3, y + 3, fill="red")

    def isIntersect(self, p, i):
        # check whether a new parabola at point p intersect with arc i
        if (i is None): return False, None
        if (i.p.x == p.x): return False, None

        a = 0.0
        b = 0.0

        if i.pprev is not None:
            a = (self.intersection(i.pprev.p, i.p, 1.0*p.x)).y
        if i.pnext is not None:
            b = (self.intersection(i.p, i.pnext.p, 1.0*p.x)).y

        if (((i.pprev is None) or (a <= p.y)) and ((i.pnext is None) or (p.y <= b))):
            py = p.y
            px = 1.0 * ((i.p.x)**2 + (i.p.y-py)**2 - p.x**2) / (2*i.p.x - 2*p.x)
            res = Point(px, py)
            return True, res
        return False, None

    def intersection(self, p0, p1, l):
        # get the intersection of two parabolas
        p = p0
        if (p0.x == p1.x):
            py = (p0.y + p1.y) / 2.0
        elif (p1.x == l):
            py = p1.y
        elif (p0.x == l):
            py = p0.y
            p = p1
        else:
            # use quadratic formula
            z0 = 2.0 * (p0.x - l)
            z1 = 2.0 * (p1.x - l)

            a = 1.0/z0 - 1.0/z1;
            b = -2.0 * (p0.y/z0 - p1.y/z1)
            c = 1.0 * (p0.y**2 + p0.x**2 - l**2) / z0 - 1.0 * (p1.y**2 + p1.x**2 - l**2) / z1

            py = 1.0 * (-b-math.sqrt(b*b - 4*a*c)) / (2*a)
            
        px = 1.0 * (p.x**2 + (p.y-py)**2 - l**2) / (2*p.x-2*l)
        res = Point(px, py)
        return res
    
    def calculate_circle(self, p1, p2, p3):
        temp = p2.x * p2.x + p2.y * p2.y
        bc = (p1.x * p1.x + p1.y * p1.y - temp) / 2
        cd = (temp - p3.x * p3.x - p3.y * p3.y) / 2
        det = (p1.x - p2.x) * (p2.y - p3.y) - (p2.x - p3.x) * (p1.y - p2.y)

        # If the determinant is zero, then the points are collinear and no circle can be found.
        if abs(det) < 1.0e-6:
            return None, None
        
        # Center of circle
        cx = (bc*(p2.y - p3.y) - cd*(p1.y - p2.y)) / det
        cy = ((p1.x - p2.x)*cd - (p2.x - p3.x)*bc) / det

        radius = ((cx - p1.x)**2 + (cy - p1.y)**2)**0.5

        return Point(cx, cy), radius

    def check_circle_event(self, arc, sweepLine):
        belowArc = self.find_below_arc(self.rootArc, arc)
        aboveArc = self.find_above_arc(self.rootArc, arc)

        if (belowArc is None) or (aboveArc is None):
            return
        if (arc.site is belowArc.site) or (arc.site is aboveArc.site) or (belowArc.site is aboveArc.site):
            return
        print('below arc point is: ', belowArc.site.x, ' , ', belowArc.site.y)
        print('above Arc point is: ', aboveArc.site.x, ' , ', aboveArc.site.y)

        circle_center, circle_radius = self.calculate_circle(belowArc.site, arc.site, aboveArc.site)
        if (circle_center is None) :
            return
        if(circle_center.x + circle_radius > sweepLine):
            event = CircleEvent(circle_center, circle_radius, arc, belowArc, aboveArc)
            self.circleEvent.put(event)

    def process_point(self):
        site = self.pointEvent.pop()
        self.seenPoints.append(site)

        if(self.rootArc is None):
            self.rootArc = ArcNode(site)
            self.bstLength += 1
        else:
            arc = self.rootArc
            while arc is not None:
                flag, z = self.isIntersect(site, arc)
                if flag:
                    flag, zz = self.isIntersect(arc.pnext)
                    if (arc.pnext is not None) and ( not flag):
                        arc.pnext.pprev = ArcNode(arc.p, arc, arc.pnext)
                        arc.pnext = arc.pnext.pprev
                    else:
                        arc.pnext = ArcNode(arc.p, arc)
                    ##
                    arc.pnext.segment1 = arc.segment1
                    ##
                    arc.pnext.pprev = ArcNode(site, arc, arc.pnext)
                    arc.pnext = arc.pnext.pprev

                    newArc = arc.pnext


                    # check for new circle events around the new arc
                    self.check_circle_event(newArc, site.x)
                    self.check_circle_event(newArc.pprev, site.x)
                    self.check_circle_event(newArc.pnext, site.x)
                    return
                arc = arc.pnext
            
            #if site no isntersect
            arc = self.rootArc
            while arc.pnext is not None:
                arc = arc.pnext
            arc.pnext = ArcNode(site, arc)

    def detect_fake_vertices(self, root, center, radius, fake = []):
        for point in self.seenPoints:
            if round(center.dist_to_point(point), 3) < round(radius, 3):
                fake.append(root)
        return fake

    def process_event(self):
        cevent = self.circleEvent.pop()
        print('circle')
        fake = self.detect_fake_vertices(self.rootArc, cevent.center, cevent.radius)
        print('fake vercite , ', fake )
        if(len(fake) == 0):
            self.voronoiVertices.append(cevent.center)
            self.voronoiEdges.append(Segment(cevent.center, cevent.arc.site.midpoint_to(cevent.aboveArc.site)))
            self.voronoiEdges.append(Segment(cevent.center, cevent.arc.site.midpoint_to(cevent.belowArc.site)))
            self.voronoiEdges.append(Segment(cevent.center, cevent.belowArc.site.midpoint_to(cevent.aboveArc.site)))

            self.delete_arc(self.rootArc, cevent.arc)
            self.bstLength = self.bstLength -1
            self.check_circle_event(cevent.belowArc, cevent.eventPoint.x)
            self.check_circle_event(cevent.aboveArc, cevent.eventPoint.x)
        else:
            self.delete_arc(self.rootArc, cevent.arc)
            self.bstLength = self.bstLength -1

            self.check_circle_event(cevent.belowArc, cevent.eventPoint.x)
            self.check_circle_event(cevent.aboveArc, cevent.eventPoint.x)
