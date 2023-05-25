import math as m
import tkinter as tk
import random as r
#from scipy.spatial import Delaunay, Voronoi, voronoi_plot_2d

def find_supertriangle(P):
    # Find the minimum and maximum x and y coordinates in the point set
    min_x = min(p[0] for p in P)
    max_x = max(p[0] for p in P)
    min_y = min(p[1] for p in P)
    max_y = max(p[1] for p in P)

    # Calculate the width and height of the bounding triangle
    width = max_x - min_x
    height = max_y - min_y

    # Define the vertices of the bounding triangle
    v1 = (min_x - width, min_y - height)
    v2 = (max_x + width, min_y - height)
    v3 = ((min_x + max_x) / 2, max_y + height)

    return v1, v2, v3


def is_in_triangle(p, tri):
    if p in tri:
        return False

    x, y = p
    x1, y1 = tri[0]
    x2, y2 = tri[1]
    x3, y3 = tri[2]

    denom = (y2 - y3) * (x1 - x3) + (x3 - x2) * (y1 - y3)
    if denom == 0:
        return False
    b1 = ((y2 - y3) * (x - x3) + (x3 - x2) * (y - y3)) / denom
    b2 = ((y3 - y1) * (x - x3) + (x1 - x3) * (y - y3)) / denom
    b3 = 1 - b1 - b2

    return 0 <= b1 <= 1 and 0 <= b2 <= 1 and 0 <= b3 <= 1


def find_containing_triangles(p, tris):
    # Returns all triangles that contain the point p on their insides or edges but not vertices.

    r = []
    first = False
    for tri in tris:
        if is_in_triangle(p, tri):
            r.append(tri)
            if first:
                return r # p is on an edge
            else:
                first = True
    return r # p is in a triangle


def angle(p1, p2, p3):
    a = abs(m.degrees(m.atan2(p3[1] - p2[1], p3[0] - p2[0]) - m.atan2(p1[1] - p2[1], p1[0] - p2[0])))
    return a if a < 180 else 360 - a


def legalize_edge(p, ptri, tris):
    for i in range(3):
        if ptri[i] == p:
            common1 = ptri[(i+1) % 3]
            common2 = ptri[(i+2) % 3]

    for tri in tris:
        if common1 in tri and common2 in tri and p not in tri:

            for i in range(3):
                if tri[i] != common1 and tri[i] != common2:
                    last_p = tri[i]

            a1 = angle(common1, p, common2)
            a2 = angle(common1, last_p, common2)

            if (a1 + a2) > 180:
                tris.remove(tri)
                tris.remove(ptri)

                ntri1 = [common1, p, last_p]
                ntri2 = [common2, p, last_p]

                tris.append(ntri1)
                tris.append(ntri2)

                legalize_edge(p, ntri1, tris)
                legalize_edge(p, ntri2, tris)

            break


def add_point(p, tris):

    cont_tris = find_containing_triangles(p, tris)

    if cont_tris:
        if len(cont_tris) == 1: # If p is in a triangle
            cont_tris = cont_tris[0]

            tris.remove(cont_tris)

            new_tris = [
                [cont_tris[0], cont_tris[1], p],
                [cont_tris[1], cont_tris[2], p],
                [cont_tris[2], cont_tris[0], p]
            ]

            tris.extend(new_tris)

            for i in range(3):
                legalize_edge(p, new_tris[i], tris)

        else: # If p in on an edge (Visually, doesn't cause a problem
            #TODO
            pass


def delaunay(points):
    a, b, c = find_supertriangle(points)

    triangulation = [[a,b,c]]

    for p in points:
        add_point(p, triangulation)

    # Return all triangles except the ones that share an edge with the supertriangle
    return [t for t in triangulation if not (a in t or b in t or c in t)]


def triangle_ccc(tri):
    ax, ay = tri[0]
    bx, by = tri[1]
    cx, cy = tri[2]

    d = 2 * (ax * (by - cy) + bx * (cy - ay) + cx * (ay - by))
    ux = ((ax**2 + ay**2) * (by - cy) + (bx**2 + by**2) * (cy - ay) + (cx**2 + cy**2) * (ay - by)) / d
    uy = ((ax**2 + ay**2) * (cx - bx) + (bx**2 + by**2) * (ax - cx) + (cx**2 + cy**2) * (bx - ax)) / d

    return [ux, uy]


def draw_delaunay(triangles):
    root = tk.Tk()
    canvas = tk.Canvas(root, width=1920, height=1080)
    canvas.pack()

    for triangle in triangles:
        x1, y1 = triangle[0]
        x2, y2 = triangle[1]
        x3, y3 = triangle[2]

        canvas.create_polygon(x1, y1, x2, y2, x3, y3, outline='blue', fill='')

    root.mainloop()


"""def circ_intersect(tri1, tri2):
    cc1, cr1 = find_cc(tri1)
    cc2, cr2 = find_cc(tri2)

    dx = cc2[0] - cc1[0]
    dy = cc2[1] - cc1[1]
    d = m.sqrt(dx**2 + dy**2)

    return d < cr1 + cr2"""


def common_edge(tri1, tri2):
    e1 = sorted([sorted([tri1[0], tri1[1]]), sorted([tri1[1], tri1[2]]), sorted([tri1[2], tri1[0]])])
    e2 = sorted([sorted([tri2[0], tri2[1]]), sorted([tri2[1], tri2[2]]), sorted([tri2[2], tri2[0]])])

    for a in e1:
        for b in e2:
            if a == b:
                return a

    return None


def p_line(S, B):
    width = 1920
    height = 1080

    # Compute the slope of line B
    slope_B = (B[1][1] - B[0][1]) / (B[1][0] - B[0][0])

    # Compute the slope of the perpendicular line
    if slope_B == 0:
        slope = float('inf')  # Vertical line
    else:
        slope = -1 / slope_B

    # Determine the endpoint of the perpendicular line on the bounding box
    if slope == float('inf'):
        # Perpendicular line is vertical
        endpoint = (S[0], height)
    else:
        x = width  # x-coordinate at the right side of the bounding box
        y = S[1] + (x - S[0]) * slope  # Compute y-coordinate using slope
        if y > height:
            y = height
            x = S[0] + (y - S[1]) / slope
        endpoint = (x, y)

    return S, endpoint


def voronoi(tris):
    tri_ccs = [triangle_ccc(tri) for tri in tris]

    cells = []
    lines = []

    for i, tri in enumerate(tris):
        neighbors = [j for j, o_tri in enumerate(tris) if i != j and common_edge(tri, o_tri)]
        cells.append({"center": tri_ccs[i], "neighbors": neighbors})

    for cell in cells:
        for o_cell in cell["neighbors"]:
            lines.append([cell["center"], cells[o_cell]["center"]])

        if len(cell["neighbors"]) < 3:
            pass # TODO: Triangle with less than 3 neighbors

    return lines

def draw_points(points,canvas, root):
    for i, (x, y) in enumerate(points):
        canvas.create_oval(x - 3, y - 3, x + 3, y + 3, fill='black')
        canvas.create_text(x, y - 15, text=str(i), fill='black')

    root.mainloop()



def draw_both(triangles, lines, points):
    root = tk.Tk()
    canvas = tk.Canvas(root, width=1920, height=1080, background="white")
    canvas.pack()

    for triangle in triangles:
        x1, y1 = triangle[0]
        x2, y2 = triangle[1]
        x3, y3 = triangle[2]

        canvas.create_polygon(x1, y1, x2, y2, x3, y3, outline='blue', fill='')

    for line in lines:
        start_x, start_y = line[0]
        end_x, end_y = line[1]

        canvas.create_line(start_x, start_y, end_x, end_y, fill='green')

    draw_points(points,canvas,root)
    root.mainloop()


def draw_voronoi(lines):
    root = tk.Tk()
    canvas = tk.Canvas(root, width=1920, height=1080, background="white")
    canvas.pack()

    for line in lines:
        start_x, start_y = line[0]
        end_x, end_y = line[1]

        canvas.create_line(start_x, start_y, end_x, end_y, fill='green')

    root.mainloop()


random_points = [
    [r.randint(50,1870), r.randint(50,980)]
    for _ in range(10)
]


triangulation = delaunay(random_points)
#draw_delaunay(triangulation)
voronoi = voronoi(triangulation)
draw_both(triangulation, voronoi,random_points)
#draw_voronoi(voronoi)
