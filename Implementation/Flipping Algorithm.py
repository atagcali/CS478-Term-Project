import math as m
import random as r
import tkinter as tk
import time as t

def point_orient(a, b, c):
    return (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])


def slope(a, b):
    if a[0] - b[0]:
        return (a[1] - b[1]) / (a[0] - b[0])
    else:
        return float('inf')


# Clockwise
def convex_hull(P):
    sortedP = sorted(P, key=lambda p: (p[0], p[1]))

    first = sortedP.pop(0)
    hull = [first]

    sortedP.sort(key=lambda p: (slope(p, first), -p[1], p[0]))
    for p in sortedP:
        hull.append(p)
        while len(hull) > 2 and point_orient(hull[-3], hull[-2], hull[-1]) < 0:
            hull.pop(-2)

    return hull


def poly_point_intersect(poly, point):
    valid_vertices = set()
    for i in range(len(poly)):
        if point_orient(poly[i], point, poly[(i + 1) % len(poly)]) > 0:
            valid_vertices.add(i)
            valid_vertices.add((i + 1) % len(poly))

    edges = [[point, poly[v]] for v in valid_vertices]
    return edges


def def_triangulation(P, canvas, root):
    sortedP = sorted(P, key=lambda p: (p[0], p[1]))

    edges = [sortedP[:2], sortedP[1:3], [sortedP[0], sortedP[2]]]
    tris = [sortedP[:3]]

    for i, p in enumerate(sortedP[3:], start=3):
        ch = convex_hull(sortedP[:i])

        new_edges = poly_point_intersect(ch, p)
        edges.extend(new_edges)

        for e1, e2 in zip(new_edges[:len(new_edges) - 1], new_edges[1:]):
            tri = [p, e1[1], e2[1]]
            tri.sort()
            tris.append(tri)

            p1, p2, p3 = tri
            canvas.create_polygon(p1[0], p1[1], p2[0], p2[1], p3[0], p3[1], outline="black", fill='#F0F0F0')
            a, b = (p1[0] + p2[0] + p3[0]) / 3, (p1[1] + p2[1] + p3[1]) / 3
            canvas.create_oval(a - 3, b - 3, a + 3, b + 3, fill="black")

            if delay:
                root.update()
                root.after(delay)

    if not delay:
        root.update()
        root.after(3000)

    return edges, tris


def draw_points(points, canvas):
    for i, (x, y) in enumerate(points):
        canvas.create_oval(x - 3, y - 3, x + 3, y + 3, fill='black')


def draw_lines(lines, canvas, root):
    for p1, p2 in lines:
        canvas.create_line(p1[0], p1[1], p2[0], p2[1], fill='black')
        if delay:
            root.update()
            root.after(delay // 2)

    if not delay:
        root.update()
        root.after(3000)


def draw_tris(tris, canvas):

    for p1, p2, p3 in tris[::-1]:
        canvas.create_polygon(p1[0], p1[1], p2[0], p2[1], p3[0], p3[1], outline="black", fill='#F0F0F0')
        a, b = (p1[0] + p2[0] + p3[0]) / 3, (p1[1] + p2[1] + p3[1]) / 3
        canvas.create_oval(a-3, b-3, a+3, b+3, fill="black")


def distance(p1, p2):
    return ((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2) ** .5


def point_in_circle(p, circ):
    ax, ay = circ[0]
    bx, by = circ[1]
    cx, cy = circ[2]

    d = 2 * (ax * (by - cy) + bx * (cy - ay) + cx * (ay - by))
    if d == 0: # Points of the circle are collinear
        return False

    ux = ((ax**2 + ay**2) * (by - cy) + (bx**2 + by**2) * (cy - ay) + (cx**2 + cy**2) * (ay - by)) / d
    uy = ((ax**2 + ay**2) * (cx - bx) + (bx**2 + by**2) * (ax - cx) + (cx**2 + cy**2) * (bx - ax)) / d

    r = m.sqrt((ux - ax)**2 + (uy - ay)**2)

    px, py = p
    d = m.sqrt((ux - px)**2 + (uy - py)**2)

    return d < r


def flip_edges(edges, tris):
    def locally_delaunay(edge):
        p1, p2 = edge

        tri1, tri2 = None, None
        for tri in tris:
            if p1 in tri and p2 in tri:
                if tri1:
                    tri2 = tri
                    break
                else:
                    tri1 = tri

        p3, p4 = None, None
        if tri1:
            tri1.remove(p1)
            tri1.remove(p2)
            p3 = tri1[0]
        if tri2:
            tri2.remove(p1)
            tri2.remove(p2)
            p4 = tri2[0]

        if p3 and p4:
            if point_in_circle(p3, [p1, p2, p4]) or point_in_circle(p4, [p1, p2, p3]):
                return False
        return True

    def flip(edge):
        p1, p2 = edge
        containing_tris = [tri for tri in tris if (p1 in tri) and (p2 in tri)]

        if len(containing_tris) == 2:
            tri1, tri2 = containing_tris

            for pt in tri1:
                if pt != p1 and pt != p2:
                    p3 = pt
                    break
            for pt in tri2:
                if pt != p1 and pt != p2:
                    p4 = pt
                    break

            edges.remove(edge)

            tris.remove(tri1)
            tris.remove(tri2)

            a = [[p1,p3,p4],[p3,p4,p2]]
            tris.extend(a)

            new_edge = [p3, p4]
            edges.append(new_edge)
            return new_edge

    stack = []

    for edge in edges:
        if not locally_delaunay(edge):
            stack.append(edge)

    while stack:
        next_edge = stack.pop()

        if next_edge in edges:
            new_edge = flip(next_edge)

            if not locally_delaunay(new_edge):
                stack.append(new_edge)


delay = int(input("Delay(ms) between steps (0 for instant): "))
point_count = int(input("Number of points: "))

root = tk.Tk()
root.title("Flipping Algorithm")

screen_size = (root.winfo_screenwidth(), root.winfo_screenheight())

canvas = tk.Canvas(root, width=screen_size[0], height=screen_size[1])
canvas.pack()

random_points = [
    [r.randint(30,screen_size[0]-30), r.randint(30,screen_size[1]-100)]
    for _ in range(point_count)
]

draw_points(random_points, canvas)

edges, tris = def_triangulation(random_points, canvas, root)

root.mainloop()

"""
Commented out since it doesn't finished and doesn't work

flip_edges(edges, tris)
draw_tris(tris)
"""
#draw_tris(tris, canvas, root) Old function