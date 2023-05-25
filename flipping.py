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

    sortedP.sort(key=lambda p: (slope(p,first), -p[1], p[0]))
    for p in sortedP:
        hull.append(p)
        while len(hull) > 2 and point_orient(hull[-3],hull[-2],hull[-1]) < 0:
            hull.pop(-2)

    return hull


def poly_point_intersect(poly, point):
    valid_vertices = set()
    for i in range(len(poly)):
        if point_orient(poly[i], point, poly[(i+1) % len(poly)]) > 0:
            valid_vertices.add(i)
            valid_vertices.add((i+1) % len(poly))

    edges = [[point, poly[v]] for v in valid_vertices]
    return edges


def def_triangulation(P):
    sortedP = sorted(P, key=lambda p: (p[0], p[1]))

    edges = [sortedP[:2], sortedP[1:3], [sortedP[2], sortedP[0]]]
    tris = [sortedP[:3]]

    for i, p in enumerate(sortedP[3:], start=3):
        ch = convex_hull(sortedP[:i])

        new_edges = poly_point_intersect(ch, p)
        edges.extend(new_edges)

        for e1, e2 in zip(new_edges[:len(new_edges)-1], new_edges[1:]):
            tris.append([p, e1[1], e2[1]])

    return edges, tris


def draw_points(points):
    root = tk.Tk()
    canvas = tk.Canvas(root, width=1600, height=900)
    canvas.pack()

    for i, (x, y) in enumerate(points):
        canvas.create_oval(x - 3, y - 3, x + 3, y + 3, fill='black')
        canvas.create_text(x, y - 15, text=str(i), fill='black')

    root.mainloop()

def draw_lines(lines):
    root = tk.Tk()
    canvas = tk.Canvas(root, width=1600, height=900)
    canvas.pack()

    for p1, p2 in lines:
        canvas.create_line(p1[0], p1[1], p2[0], p2[1], fill='black')

    root.mainloop()


def draw_tris(tris):
    root = tk.Tk()
    canvas = tk.Canvas(root, width=1600, height=900)
    canvas.pack()

    for p1, p2, p3 in tris[::-1]:
        canvas.create_polygon(p1[0], p1[1], p2[0], p2[1], p3[0], p3[1], outline="black", fill='#F0F0F0')

    root.mainloop()


def distance(p1, p2):
    return ((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2) ** .5


def flipping(edges, tris):
    pass


a = [[r.randint(100, 1500), r.randint(100, 800)] for _ in range(31)]
draw_points(a)
b, c = def_triangulation(a)
draw_lines(b)
#draw_tris(c)

