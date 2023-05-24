import tkinter as tk
import math
import heapq


from DataTypes import Point 

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
        circle_center = item.center  # Assuming center is a Point object with x and y attributes.
        heapq.heappush(self.cq, (circle_center.x, item))  # The lower the x-coordinate, the higher the priority.

    def pop(self):
        return heapq.heappop(self.cq)[1] if self.cq else None
    
    def top(self):
        return self.cq[0][1] if self.cq else None


class ArcNode:
    def __init__(self, site, ordinate ,parent=None, left=None, right=None):
        self.site = site
        self.ordinate = ordinate
        self.parent = parent
        self.left = left
        self.right = right

class CircleEvent:
    def __init__(self, center, radius, arc):
        self.center = center
        self.radius = radius
        self.arc = arc
        self.x = center.x


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
        self.voronoiVertices = []
        #self.dcel = DCEL()
        
    def add_point(self, event):
        x, y = event.x, event.y
        print('x = ', x, ' ,  y = ', y)
        self.points.append((x, y))
        self.canvas.create_oval(x-3, y-3, x+3, y+3, fill="black")
    
    def clear_canvas(self, event):
        self.points = []
        self.lines = []
        self.canvas.delete("all")

    def test(self, event):
        for point in self.points:
            p = Point(point[0], point[1])
            self.pointEvent.put(p)
        
        while not self.pointEvent.is_empty():
            self.process_point()
        
        while not self.circleEvent.is_empty():
            event = self.circleEvent.pop()
            print('circle x = ', event.center.x, ' , y = ', event.center.y)
            self.voronoiVertices.append(event.center)
        
        # Print Voronoi vertices
        for vertex in self.voronoiVertices:
            x = vertex.x
            y = vertex.y
            self.canvas.create_oval(x - 3, y - 3, x + 3, y + 3, fill="red")


    def voronoi(self, event):
        for point in self.points:
            p = Point(point[0], point[1])
            self.pointEvent.put(p)
        
        while not self.pointEvent.is_empty():
            if not self.circleEvent.is_empty() and (self.circleEvent.top().center.x <= self.pointEvent.top().x):
                self.process_event()
            else:
                self.process_point()
        while not self.circleEvent.is_empty():
            self.process_event()
        
        # Print Voronoi vertices
        for vertex in self.voronoiVertices:
            x = vertex.x
            y = vertex.y
            self.canvas.create_oval(x - 3, y - 3, x + 3, y + 3, fill="red")

    def insert(self, bstRoot, site, ordinate, inserted = 0):
        # If the tree is empty, return a new node
        if bstRoot is None:
            inserted = 1
            return ArcNode(site, ordinate), inserted

        newNode = None
        # Otherwise, recur down the tree
        if ordinate < bstRoot.ordinate:
            newNode, inserted = self.insert(bstRoot.left, site, ordinate, inserted)
            if inserted == 1:
                bstRoot.left = newNode
                newNode.parent = bstRoot
                inserted = -1
        else:
            newNode, inserted = self.insert(bstRoot.right, site, ordinate, inserted)
            if inserted == 1:
                bstRoot.right = newNode
                newNode.parent = bstRoot
                inserted = -1
        # Return the new node that was inserted
        return newNode, inserted
    
    def find_inorder_position(self, root, node, position=0):
        if root is None:
            return position, False
        
        position, found = self.find_inorder_position(root.left, node, position)
        
        if found:
            return position, True
        
        if root == node:
            return position+1, True

        return self.find_inorder_position(root.right, node, position+1)
    
    def find_node_by_inorder_position(self, root, position, current_position=0, founded = None):
        if (root is None) and (founded is None):
            return None, current_position
        elif (root is None) and (founded is not None):
            return founded, current_position
        
        founded, current_position = self.find_node_by_inorder_position(root.left, position, current_position, founded)

        current_position += 1

        if current_position == position:
            founded = root
            return founded, current_position
        
        founded, current_position = self.find_node_by_inorder_position(root.right, position, current_position, founded)
        return founded, current_position
    
    def minValueNode(self, node):
        current = node
        # loop down to find the leftmost leaf
        while(current.left is not None):
            current = current.left
        return current

    def delete_arc(self, root, node):
        # If the tree is empty
        if root is None:
            return root

        # If the node to be deleted is smaller than the root, then it lies in the left subtree
        if node.ordinate < root.ordinate or (node.ordinate == root.ordinate and node is not root):
            root.left = self.delete_arc(root.left, node)

        # If the node to be deleted is greater than the root, then it lies in the right subtree
        elif node.ordinate > root.ordinate or (node.ordinate == root.ordinate and node is not root):
            root.right = self.delete_arc(root.right, node)

        # If node is same as root's node, then this is the node to be deleted
        else:
            # Node with only one child or no child
            if root.left is None:
                temp = root.right
                root = None
                return temp
            elif root.right is None:
                temp = root.left
                root = None
                return temp

            # Node with two children: Get the inorder successor (smallest in the right subtree)
            temp = self.minValueNode(root.right)

            # Copy the inorder successor's content to this node
            root.ordinate = temp.ordinate
            root.site = temp.site

            # Delete the inorder successor
            root.right = self.delete_arc(root.right, temp)

        return root


    def find_above_arc(self, root, node):
        position, found = self.find_inorder_position(root,node)
        nextNode, n = self.find_node_by_inorder_position(root, position + 1)
        return nextNode


    def find_below_arc(self, root, node):
        position, found = self.find_inorder_position(root, node)
        beforeNode, n = self.find_node_by_inorder_position(root, position - 1)
        return beforeNode

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

    def check_circle_event(self, arc):
        belowArc = self.find_below_arc(self.rootArc, arc)
        aboveArc = self.find_above_arc(self.rootArc, arc)

        if (belowArc is None) or (aboveArc is None):
            return
        if (arc.site is belowArc.site) or (arc.site is aboveArc.site) or (belowArc.site is aboveArc.site):
            return
        
        circle_center, circle_radius = self.calculate_circle(belowArc.site, arc.site, aboveArc.site)
        if circle_center is None:
            return
        
        event = CircleEvent(circle_center, circle_radius, arc)
        self.circleEvent.put(event)


    def process_point(self):
        print('point')
        site = self.pointEvent.pop()
        if(self.rootArc is None):
            self.rootArc, bool = self.insert(self.rootArc, site, site.y)
        else:
            newArc, bool = self.insert(self.rootArc, site, site.y)

            belowArc = self.find_below_arc(self.rootArc, newArc)
            aboveArc = self.find_above_arc(self.rootArc, newArc)

            
            self.check_circle_event(newArc)
            if belowArc is not None:
                self.check_circle_event(belowArc)
            if aboveArc is not None:
                self.check_circle_event(aboveArc)
    
    def remove_fake_vertices(self, root, center, radius):
        if root is None:
            return
        self.remove_fake_vertices(root.left, center, radius)

        if center.dist_to_point(root.site) < (radius):
            print('delete')
            self.delete_arc(self.rootArc, node=root)
        else:
            self.voronoiVertices.append(center)
        
        self.remove_fake_vertices(root.right, center, radius)

    def process_event(self):
        print('event')
        cevent = self.circleEvent.pop()
        self.remove_fake_vertices(self.rootArc, cevent.center, cevent.radius)
        

    




            







if __name__ == "__main__":
    root = tk.Tk()
    app = DrawingApp(root)
    root.mainloop()

