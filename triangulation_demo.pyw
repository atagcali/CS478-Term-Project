import tkinter as tk
import itertools

class DrawingApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Drawing App")
        
        self.canvas = tk.Canvas(self.master, width=500, height=500, bg="white")
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        self.points = []
        self.lines = []
        self.canvas.bind("<Button-1>", self.add_point)
        self.canvas.bind("<Button-2>", self.clear_canvas)
        self.canvas.bind("<Button-3>", lambda event: self.connect_points(event))
        
    def add_point(self, event):
        x, y = event.x, event.y
        self.points.append((x, y))
        self.canvas.create_oval(x-3, y-3, x+3, y+3, fill="black")
    
    def clear_canvas(self, event):
        self.points = []
        self.lines = []
        self.canvas.delete("all")
        
    def connect_points(self, event):
        if len(self.points) < 2:
            return
        
        # Get all possible pairs of points
        pairs = list(itertools.combinations(self.points, 2))
        
        # Sort pairs by distance
        sorted_pairs = sorted(pairs, key=lambda p: ((p[0][0]-p[1][0])**2 + (p[0][1]-p[1][1])**2)**0.5)
        
        # Connect each pair of points, checking for intersections
        for pair in sorted_pairs:
            intersect = False
            for line in self.lines:
                if self.do_lines_intersect(pair, line):
                    intersect = True
                    break
            if not intersect:
                self.lines.append(pair)
                self.canvas.create_line(*pair, fill="black")
                
    def do_lines_intersect(self, line1, line2):
        # Check if two lines intersect
        x1, y1 = line1[0]
        x2, y2 = line1[1]
        x3, y3 = line2[0]
        x4, y4 = line2[1]
        
        den = (y4-y3)*(x2-x1) - (x4-x3)*(y2-y1)
        if den == 0:
            return False
        
        ua = ((x4-x3)*(y1-y3) - (y4-y3)*(x1-x3)) / den
        ub = ((x2-x1)*(y1-y3) - (y2-y1)*(x1-x3)) / den
        
        if ua > 0 and ua < 1 and ub > 0 and ub < 1:
            return True
        
        return False
        
if __name__ == "__main__":
    root = tk.Tk()
    app = DrawingApp(root)
    root.mainloop()
