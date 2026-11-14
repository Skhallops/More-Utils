"""
Candidate sprite generator for the More Utils late-game buildings.

Both buildings are drawn from scratch with the same pixel vocabulary as the
vanilla-derived mass drivers in generate_sprites.py:

  * hard-edged 1px outlines, 2-3px bevels, top-left light / bottom-right shade
  * chunky armour plates, rivets, vents, hazard stripes and pipe flanges
  * a deliberately narrow 14-colour grey-steel palette

The 20% sci-fi layer is an Iron-Man-style arc reactor: segmented gold rings,
teal containment rings, a white-hot core and Bayugo crystal inlays.

Outputs candidate sprites plus labelled contact sheets into docs/designs/.
The chosen designs are then copied into sprites/ so the shipped art is always
reproducible from this script.

Usage:  py -3 tools/generate_buildings.py
"""

import math
import os

from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCS = os.path.join(ROOT, "docs", "designs")
SPRITES = os.path.join(ROOT, "sprites")

# ---------------------------------------------------------------------------
# shared 14-colour palette
# ---------------------------------------------------------------------------

K = (39, 48, 56)      # outline
L = (177, 190, 191)   # light steel
D = (64, 76, 84)      # dark panel
d = (91, 105, 112)    # mid-dark
m = (133, 147, 151)   # mid steel
W = (216, 225, 219)   # highlight
T = (37, 105, 111)    # deep teal
G = (211, 180, 94)    # gold
w = (237, 242, 230)   # white
C = (133, 224, 198)   # Bayugo mint
c = (63, 170, 164)    # Bayugo teal
y = (247, 224, 151)   # pale gold
g = (151, 119, 58)    # dark gold
H = (207, 250, 232)   # pale mint

PALETTE = (K, L, D, d, m, W, T, G, w, C, c, y, g, H)


# ---------------------------------------------------------------------------
# primitives
# ---------------------------------------------------------------------------

def octagon(size, inset, cut):
    lo, hi = inset, size - inset
    return [
        (lo + cut, lo), (hi - cut, lo), (hi, lo + cut), (hi, hi - cut),
        (hi - cut, hi), (lo + cut, hi), (lo, hi - cut), (lo, lo + cut),
    ]


def chassis(size, inset=3, cut=16, body=m, floor=D):
    """Rounded-corner armour shell with a recessed floor plate."""
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    draw.polygon(octagon(size, inset, cut), fill=K)
    draw.polygon(octagon(size, inset + 2, max(3, cut - 1)), fill=body)
    draw.polygon(octagon(size, inset + 8, max(3, cut - 6)), fill=floor)

    # outer rim bevel: light top/left, shade bottom/right
    lo, hi = inset + 2, size - inset - 2
    draw.line([(lo + cut - 1, lo), (hi - cut + 1, lo)], fill=L, width=2)
    draw.line([(lo + cut - 1, lo), (lo, lo + cut - 1)], fill=L, width=2)
    draw.line([(lo, lo + cut - 1), (lo, hi - cut + 1)], fill=L, width=2)
    draw.line([(lo + cut - 1, hi), (hi - cut + 1, hi)], fill=D, width=2)
    draw.line([(hi - cut + 1, hi), (hi, hi - cut + 1)], fill=D, width=2)
    draw.line([(hi, lo + cut - 1), (hi, hi - cut + 1)], fill=d, width=2)

    # recessed floor lip: dark at the top/left, lit at the bottom/right
    lo2, hi2 = inset + 8, size - inset - 8
    draw.line([(lo2 + cut - 6, lo2), (hi2 - cut + 6, lo2)], fill=d, width=2)
    draw.line([(lo2 + cut - 6, lo2), (lo2, lo2 + cut - 6)], fill=d, width=2)
    draw.line([(lo2, lo2 + cut - 6), (lo2, hi2 - cut + 6)], fill=d, width=2)
    draw.line([(lo2 + cut - 6, hi2), (hi2 - cut + 6, hi2)], fill=m, width=2)
    draw.line([(hi2 - cut + 6, hi2), (hi2, hi2 - cut + 6)], fill=m, width=2)
    draw.line([(hi2, lo2 + cut - 6), (hi2, hi2 - cut + 6)], fill=m, width=2)

    # top/bottom rivet rows
    for x in range(inset + cut + 8, size - inset - cut - 6, 18):
        bolt(draw, x, inset + 4)
    for x in range(inset + cut + 8, size - inset - cut - 6, 18):
        bolt(draw, x, size - inset - 5)
    return img


def bolt(draw, x, y):
    draw.rectangle([x - 1, y - 1, x + 1, y + 1], fill=K)
    draw.rectangle([x, y, x + 1, y + 1], fill=d)
    draw.point([x, y], fill=W)


def rivet_row(draw, x0, x1, y, step=10):
    for x in range(x0, x1 + 1, step):
        bolt(draw, x, y)


def panel(img, box, fill=m, hi=W, lo=d, edge=K):
    x0, y0, x1, y1 = box
    draw = ImageDraw.Draw(img)
    draw.rectangle([x0 - 1, y0 - 1, x1 + 1, y1 + 1], fill=edge)
    draw.rectangle([x0, y0, x1, y1], fill=fill)
    draw.line([x0, y0, x1, y0], fill=hi)
    draw.line([x0, y0, x0, y1], fill=hi)
    draw.line([x0, y1, x1, y1], fill=lo)
    draw.line([x1, y0, x1, y1], fill=lo)


def inset(img, box, fill=D, hi=d, lo=m, edge=K):
    x0, y0, x1, y1 = box
    draw = ImageDraw.Draw(img)
    draw.rectangle([x0 - 1, y0 - 1, x1 + 1, y1 + 1], fill=edge)
    draw.rectangle([x0, y0, x1, y1], fill=fill)
    draw.line([x0, y0, x1, y0], fill=hi)
    draw.line([x0, y0, x0, y1], fill=hi)
    draw.line([x0, y1, x1, y1], fill=lo)
    draw.line([x1, y0, x1, y1], fill=lo)


def vent(img, box, slats=4):
    x0, y0, x1, y1 = box
    inset(img, box, fill=d, hi=K, lo=m)
    draw = ImageDraw.Draw(img)
    span = y1 - y0 - 2
    step = max(3, span // max(1, slats))
    for i in range(slats):
        yy = y0 + 2 + i * step
        if yy + 1 > y1 - 1:
            break
        draw.line([x0 + 2, yy, x1 - 2, yy], fill=K)
        draw.line([x0 + 2, yy + 1, x1 - 2, yy + 1], fill=D)


def hazard(img, box, stripe=7, col=y, dark=g):
    """Diagonal caution stripes, clipped to the box."""
    x0, y0, x1, y1 = box
    width, height = x1 - x0 + 1, y1 - y0 + 1
    tile = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    td = ImageDraw.Draw(tile)
    td.rectangle([0, 0, width - 1, height - 1], fill=dark)
    for i in range(-height, width + height, stripe * 2):
        td.polygon(
            [(i, height), (i + stripe, height), (i + stripe + height, 0), (i + height, 0)],
            fill=col,
        )
    img.alpha_composite(tile, (x0, y0))
    draw = ImageDraw.Draw(img)
    draw.rectangle([x0 - 1, y0 - 1, x1 + 1, y1 + 1], outline=K)
    draw.line([x0, y0, x1, y0], fill=W)
    draw.line([x0, y1, x1, y1], fill=K)


def pipe(img, x0, y0, x1, y1, conduit=False, flanges=True):
    draw = ImageDraw.Draw(img)
    draw.rectangle([x0 - 1, y0 - 1, x1 + 1, y1 + 1], fill=K)
    draw.rectangle([x0, y0, x1, y1], fill=m)
    draw.line([x0, y0, x1, y0], fill=L)
    draw.line([x0, y0, x0, y1], fill=L)
    draw.line([x0, y1, x1, y1], fill=D)
    draw.line([x1, y0, x1, y1], fill=d)
    if conduit:
        mid = (y0 + y1) // 2
        draw.line([x0 + 2, mid, x1 - 2, mid], fill=T)
        for x in range(x0 + 3, x1 - 2, 7):
            draw.line([x, mid - 1, min(x + 2, x1 - 2), mid - 1], fill=C)
    if flanges:
        for x in (x0, x1 - 3):
            draw.rectangle([x, y0 - 2, x + 3, y1 + 2], fill=K)
            draw.rectangle([x, y0 - 1, x + 2, y1 + 1], fill=L)
            draw.line([x, y1, x + 2, y1], fill=d)
            bolt(draw, x + 1, (y0 + y1) // 2)


def vpipe(img, x0, y0, x1, y1, conduit=False, flanges=True):
    draw = ImageDraw.Draw(img)
    draw.rectangle([x0 - 1, y0 - 1, x1 + 1, y1 + 1], fill=K)
    draw.rectangle([x0, y0, x1, y1], fill=m)
    draw.line([x0, y0, x0, y1], fill=L)
    draw.line([x0, y0, x1, y0], fill=L)
    draw.line([x1, y0, x1, y1], fill=d)
    draw.line([x0, y1, x1, y1], fill=D)
    if conduit:
        mid = (x0 + x1) // 2
        draw.line([mid, y0 + 2, mid, y1 - 2], fill=T)
        for yy in range(y0 + 3, y1 - 2, 7):
            draw.line([mid - 1, yy, mid - 1, min(yy + 2, y1 - 2)], fill=C)
    if flanges:
        for yy in (y0, y1 - 3):
            draw.rectangle([x0 - 2, yy, x1 + 2, yy + 3], fill=K)
            draw.rectangle([x0 - 1, yy, x1 + 1, yy + 2], fill=L)
            draw.line([x0 - 1, yy + 2, x1 + 1, yy + 2], fill=d)
            bolt(draw, (x0 + x1) // 2, yy + 1)


def disc(draw, cx, cy, r, fill):
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=fill)


def ring(draw, cx, cy, r_out, r_in, fill, edge=K):
    disc(draw, cx, cy, r_out, edge)
    disc(draw, cx, cy, r_out - 1, fill)
    disc(draw, cx, cy, r_in, edge)
    disc(draw, cx, cy, r_in - 1, fill)


def arc_reactor(img, cx, cy, r, spokes=12, triangle=True):
    """Segmented gold containment ring, teal field rings, white-hot core."""
    draw = ImageDraw.Draw(img)
    disc(draw, cx, cy, r + 3, K)
    disc(draw, cx, cy, r, G)
    disc(draw, cx, cy, r - 2, g)

    # radial segment cuts and bolts between them
    for i in range(spokes):
        a = 2 * math.pi * i / spokes - math.pi / 2
        x0 = cx + round(math.cos(a) * (r - 1))
        y0 = cy + round(math.sin(a) * (r - 1))
        x1 = cx + round(math.cos(a) * (r - 6))
        y1 = cy + round(math.sin(a) * (r - 6))
        draw.line([x0, y0, x1, y1], fill=K)
        b = a + math.pi / spokes
        bx = cx + round(math.cos(b) * (r - 4))
        by = cy + round(math.sin(b) * (r - 4))
        draw.rectangle([bx - 1, by - 1, bx + 1, by + 1], fill=K)
        draw.point([bx, by], fill=W)

    disc(draw, cx, cy, r - 8, K)
    disc(draw, cx, cy, r - 9, T)
    disc(draw, cx, cy, max(1, r - 13), c)
    disc(draw, cx, cy, max(1, r - 17), C)
    disc(draw, cx, cy, max(1, r - 21), H)

    # eight bright spokes across the field ring
    for i in range(8):
        a = 2 * math.pi * i / 8 - math.pi / 2
        x0 = cx + round(math.cos(a) * (r - 20))
        y0 = cy + round(math.sin(a) * (r - 20))
        x1 = cx + round(math.cos(a) * (r - 10))
        y1 = cy + round(math.sin(a) * (r - 10))
        draw.line([x0, y0, x1, y1], fill=T if i % 2 else c)

    if triangle:
        rr = max(4, r * 0.53)
        tri = [
            (cx, cy - rr),
            (cx + round(rr * 0.866), cy + round(rr * 0.5)),
            (cx - round(rr * 0.866), cy + round(rr * 0.5)),
        ]
        draw.polygon([(x, y - 2) for x, y in tri], fill=K)
        draw.polygon([(x, y + 1) for x, y in tri], fill=K)
        draw.polygon(tri, fill=G)
        inner = [(cx + (x - cx) * 0.8, cy + (y - cy) * 0.8) for x, y in tri]
        draw.polygon(inner, fill=w)
        core = [(cx + (x - cx) * 0.5, cy + (y - cy) * 0.5) for x, y in tri]
        draw.polygon(core, fill=H)
    else:
        rr = max(3, r - 27)
        disc(draw, cx, cy, rr + 2, K)
        disc(draw, cx, cy, rr, w)
        disc(draw, cx, cy, max(1, rr - 3), H)

    # top-left glint on the gold ring
    ga = math.radians(225)
    gx = cx + round(math.cos(ga) * (r - 3))
    gy = cy + round(math.sin(ga) * (r - 3))
    draw.line([gx - 3, gy - 1, gx + 1, gy - 4], fill=y, width=1)


def crystal(img, cx, cy, half_w, half_h):
    draw = ImageDraw.Draw(img)
    outer = [
        (cx, cy - half_h),
        (cx + half_w, cy - half_h // 3),
        (cx + half_w * 3 // 5, cy + half_h * 3 // 5),
        (cx, cy + half_h),
        (cx - half_w * 3 // 5, cy + half_h * 3 // 5),
        (cx - half_w, cy - half_h // 3),
    ]
    draw.polygon(outer, fill=K)
    iw, ih = max(1, half_w - 2), max(1, half_h - 2)
    body = [
        (cx, cy - ih),
        (cx + iw, cy - ih // 3),
        (cx + iw * 3 // 5, cy + ih * 3 // 5),
        (cx, cy + ih),
        (cx - iw * 3 // 5, cy + ih * 3 // 5),
        (cx - iw, cy - ih // 3),
    ]
    draw.polygon(body, fill=C)
    # lit left facet + darker right facet
    draw.polygon([body[0], body[5], body[4], (cx, cy + ih // 3)], fill=H)
    draw.polygon([body[0], body[1], body[2], (cx, cy + ih // 3)], fill=c)
    draw.point([cx, cy - ih + 2], fill=w)


def crystal_socket(img, cx, cy, half_w, half_h, socket=True):
    """Bayugo crystal set into a gold ring, used on hulls and injectors."""
    draw = ImageDraw.Draw(img)
    if socket:
        disc(draw, cx, cy, half_w + 5, K)
        disc(draw, cx, cy, half_w + 3, G)
        disc(draw, cx, cy, half_w + 1, T)
        disc(draw, cx, cy, half_w - 1, D)
    crystal(img, cx, cy, half_w, half_h)


def corner_plate(img, box, cap=False):
    panel(img, box, fill=m, hi=W, lo=d)
    x0, y0, x1, y1 = box
    inset(img, [x0 + 4, y0 + 4, x1 - 4, y1 - 4], fill=d, hi=K, lo=m)
    draw = ImageDraw.Draw(img)
    if cap:
        draw.rectangle([x0 + 2, y0 + 2, x1 - 2, y0 + 5], fill=G)
        draw.line([x0 + 2, y0 + 5, x1 - 2, y0 + 5], fill=g)
    for bx, by in ((x0 + 3, y1 - 3), (x1 - 3, y1 - 3), (x0 + 3, y0 + 8), (x1 - 3, y0 + 8)):
        bolt(draw, bx, by)


def hazard_band(img, box, stripe=7):
    hazard(img, box, stripe=stripe)


# ---------------------------------------------------------------------------
# B.B Collider designs (160x160, 5x5)
# ---------------------------------------------------------------------------

BB = 160


def bb_torus():
    img = chassis(BB, cut=18, body=m, floor=D)
    draw = ImageDraw.Draw(img)

    # corner capacitor banks
    for box in ((14, 14, 38, 38), (122, 14, 146, 38), (14, 122, 38, 146), (122, 122, 146, 146)):
        corner_plate(img, box, cap=True)
        cx = (box[0] + box[2]) // 2
        cy = (box[1] + box[3]) // 2
        for yy in range(box[1] + 10, box[3] - 4, 5):
            draw.line([box[0] + 7, yy, box[2] - 7, yy], fill=K)
        draw.point([cx, cy], fill=C)

    # main torus chamber
    arc_reactor(img, 80, 80, 50, spokes=14, triangle=True)

    # four armour clamps reaching toward the ring
    for box in ((40, 22, 64, 34), (96, 22, 120, 34), (40, 126, 64, 138), (96, 126, 120, 138)):
        panel(img, box, fill=m, hi=W, lo=d)
        inset(img, [box[0] + 3, box[1] + 3, box[2] - 3, box[3] - 3], fill=T, hi=K, lo=c)
        draw.line([box[0] + 6, (box[1] + box[3]) // 2, box[2] - 6, (box[1] + box[3]) // 2], fill=C)

    # feed pipes into the chamber
    pipe(img, 8, 74, 29, 86, conduit=True)
    pipe(img, 131, 74, 152, 86, conduit=True)
    vpipe(img, 74, 8, 86, 29, conduit=True)
    vpipe(img, 74, 131, 86, 152, conduit=True)

    # crystal tell-tales in the ring quadrants
    for cx, cy in ((52, 52), (108, 52), (52, 108), (108, 108)):
        crystal_socket(img, cx, cy, 5, 8, socket=False)

    hazard_band(img, [52, 144, 108, 151])
    return img


def bb_twin_rails():
    img = chassis(BB, cut=8, body=m, floor=D)
    draw = ImageDraw.Draw(img)

    # two accelerator rails
    for y0 in (32, 118):
        panel(img, [22, y0, 138, y0 + 12], fill=d, hi=L, lo=K)
        draw.rectangle([22, y0 + 3, 138, y0 + 9], fill=D)
        for x in (30, 62, 94, 126):
            draw.rectangle([x, y0 - 3, x + 7, y0 + 15], fill=K)
            draw.rectangle([x + 1, y0 - 2, x + 6, y0 + 14], fill=G)
            draw.rectangle([x + 2, y0 - 1, x + 4, y0 + 13], fill=g)
            draw.point([x + 2, y0 - 1], fill=y)
        for x in range(26, 136, 8):
            draw.line([x, y0 + 6, min(x + 4, 136), y0 + 6], fill=C)

    # central collision chamber
    cx, cy, r = 80, 80, 40
    draw.polygon([
        (cx + round(math.cos(math.radians(a)) * (r + 4)),
         cy + round(math.sin(math.radians(a)) * (r + 4))) for a in range(0, 360, 45)
    ], fill=K)
    draw.polygon([
        (cx + round(math.cos(math.radians(a)) * r),
         cy + round(math.sin(math.radians(a)) * r)) for a in range(0, 360, 45)
    ], fill=m)
    draw.polygon([
        (cx + round(math.cos(math.radians(a)) * (r - 4)),
         cy + round(math.sin(math.radians(a)) * (r - 4))) for a in range(0, 360, 45)
    ], fill=D)
    draw.polygon([
        (cx + round(math.cos(math.radians(a)) * (r - 10)),
         cy + round(math.sin(math.radians(a)) * (r - 10))) for a in range(0, 360, 45)
    ], fill=T)
    draw.polygon([
        (cx + round(math.cos(math.radians(a)) * (r - 16)),
         cy + round(math.sin(math.radians(a)) * (r - 16))) for a in range(0, 360, 45)
    ], fill=c)
    for a in range(0, 360, 60):
        x0 = cx + round(math.cos(math.radians(a)) * (r - 24))
        y0 = cy + round(math.sin(math.radians(a)) * (r - 24))
        x1 = cx + round(math.cos(math.radians(a)) * (r - 8))
        y1 = cy + round(math.sin(math.radians(a)) * (r - 8))
        draw.line([x0, y0, x1, y1], fill=T)

    # collision flash: four-point star
    star = []
    for i in range(8):
        a = math.radians(i * 45 - 90)
        rad = 24 if i % 2 == 0 else 7
        star.append((cx + round(math.cos(a) * rad), cy + round(math.sin(a) * rad)))
    draw.polygon(star, fill=K)
    star = [(int(x * 0.92 + cx * 0.08), int(y * 0.92 + cy * 0.08)) for x, y in star]
    draw.polygon(star, fill=H)
    draw.polygon([(cx + (x - cx) * 0.55, cy + (y - cy) * 0.55) for x, y in star], fill=w)

    for a in range(0, 360, 45):
        bx = cx + round(math.cos(math.radians(a)) * (r - 1))
        by = cy + round(math.sin(math.radians(a)) * (r - 1))
        bolt(draw, bx, by)

    # pistons tying the rails to the chamber
    for x in (58, 94):
        panel(img, [x, 44, x + 8, 52], fill=L, hi=W, lo=D)
        panel(img, [x, 108, x + 8, 116], fill=L, hi=W, lo=D)

    # crystal injectors on the flanks
    for cx2 in (18, 142):
        panel(img, [cx2 - 8, 62, cx2 + 8, 98], fill=m, hi=W, lo=d)
        inset(img, [cx2 - 5, 67, cx2 + 5, 93], fill=D, hi=K, lo=m)
        crystal(img, cx2, 80, 7, 12)

    hazard_band(img, [52, 146, 108, 153])
    return img


def bb_hex():
    img = chassis(BB, cut=24, body=m, floor=D)
    draw = ImageDraw.Draw(img)

    cx, cy, r = 80, 80, 56

    def hexagon(radius):
        return [
            (cx, cy - radius),
            (cx + round(radius * 0.866), cy - radius // 2),
            (cx + round(radius * 0.866), cy + radius // 2),
            (cx, cy + radius),
            (cx - round(radius * 0.866), cy + radius // 2),
            (cx - round(radius * 0.866), cy - radius // 2),
        ]

    draw.polygon(hexagon(r + 3), fill=K)
    draw.polygon(hexagon(r), fill=L)
    draw.polygon(hexagon(r - 3), fill=m)
    draw.polygon(hexagon(r - 9), fill=K)
    draw.polygon(hexagon(r - 11), fill=D)
    draw.polygon(hexagon(r - 24), fill=K)
    draw.polygon(hexagon(r - 26), fill=T)
    draw.polygon(hexagon(r - 33), fill=c)
    draw.polygon(hexagon(r - 39), fill=C)
    draw.polygon(hexagon(r - 44), fill=H)

    # layered seams and bolts
    for i in range(6):
        a = math.radians(i * 60 - 90)
        x0 = cx + round(math.cos(a) * (r - 12))
        y0 = cy + round(math.sin(a) * (r - 12))
        x1 = cx + round(math.cos(a) * (r - 22))
        y1 = cy + round(math.sin(a) * (r - 22))
        draw.line([x0, y0, x1, y1], fill=K)
        bx = cx + round(math.cos(a) * (r - 6))
        by = cy + round(math.sin(a) * (r - 6))
        bolt(draw, bx, by)

    # bright collision core with a crystal shard suspended inside
    disc(draw, cx, cy, 18, K)
    disc(draw, cx, cy, 16, G)
    disc(draw, cx, cy, 13, T)
    disc(draw, cx, cy, 10, C)
    crystal(img, cx, cy, 6, 11)

    # six clamp arms around the hex
    for a in (0, 60, 120, 180, 240, 300):
        ang = math.radians(a - 90)
        x0 = cx + round(math.cos(ang) * (r - 2))
        y0 = cy + round(math.sin(ang) * (r - 2))
        x1 = cx + round(math.cos(ang) * (r - 18))
        y1 = cy + round(math.sin(ang) * (r - 18))
        draw.line([x0, y0, x1, y1], fill=g, width=5)
        draw.line([x0, y0, x1, y1], fill=G, width=3)
        draw.point([x1, y1], fill=y)

    # top manifold and bottom drain
    for x in (62, 78, 94):
        vpipe(img, x, 8, x + 8, 24, conduit=True)
    hazard_band(img, [58, 145, 102, 152])

    # flank crystal cells
    for cx2 in (18, 142):
        inset(img, [cx2 - 7, 66, cx2 + 7, 94], fill=D, hi=K, lo=m)
        crystal(img, cx2, 80, 6, 10)
    return img


def bb_crossfire():
    img = chassis(BB, cut=6, body=m, floor=D)
    draw = ImageDraw.Draw(img)

    # armoured mount around a circular reaction chamber
    panel(img, [42, 42, 118, 118], fill=L, hi=W, lo=d)
    inset(img, [48, 48, 112, 112], fill=D, hi=K, lo=m)
    disc(draw, 80, 80, 30, K)
    disc(draw, 80, 80, 27, T)
    disc(draw, 80, 80, 23, c)
    disc(draw, 80, 80, 19, C)
    disc(draw, 80, 80, 15, H)
    for a in range(45, 360, 90):
        bx = 80 + round(math.cos(math.radians(a)) * 25)
        by = 80 + round(math.sin(math.radians(a)) * 25)
        bolt(draw, bx, by)

    # crossing energy blades
    for a in (0, 90):
        if a == 0:
            draw.polygon([(58, 76), (102, 76), (102, 84), (58, 84)], fill=K)
            draw.polygon([(60, 78), (100, 78), (100, 82), (60, 82)], fill=w)
        else:
            draw.polygon([(76, 58), (84, 58), (84, 102), (76, 102)], fill=K)
            draw.polygon([(78, 60), (82, 60), (82, 100), (78, 100)], fill=w)

    # suspended crystal at the crossing point
    crystal(img, 80, 80, 8, 14)

    # four emitters aimed at the chamber
    emitters = (
        (74, 12, 86, 44, "v"),
        (74, 116, 86, 148, "v"),
        (12, 74, 44, 86, "h"),
        (116, 74, 148, 86, "h"),
    )
    for x0, y0, x1, y1, axis in emitters:
        panel(img, [x0, y0, x1, y1], fill=m, hi=W, lo=d)
        if axis == "v":
            inset(img, [x0 + 4, y0 + 5, x1 - 4, y1 - 3], fill=D, hi=K, lo=m)
            draw.rectangle([x0 + 2, y1 - 8, x1 - 2, y1 - 3], fill=K)
            draw.rectangle([x0 + 3, y1 - 8, x1 - 3, y1 - 5], fill=G)
            draw.rectangle([x0 + 4, y1 - 8, x1 - 4, y1 - 6], fill=y)
            for yy in range(y0 + 8, y1 - 10, 6):
                draw.line([x0 + 6, yy, x1 - 6, yy], fill=T)
                draw.line([x0 + 6, yy, x1 - 8, yy], fill=C)
        else:
            inset(img, [x0 + 5, y0 + 4, x1 - 3, y1 - 4], fill=D, hi=K, lo=m)
            draw.rectangle([x1 - 8, y0 + 2, x1 - 3, y1 - 2], fill=K)
            draw.rectangle([x1 - 8, y0 + 3, x1 - 5, y1 - 3], fill=G)
            draw.rectangle([x1 - 8, y0 + 4, x1 - 6, y1 - 4], fill=y)
            for xx in range(x0 + 8, x1 - 10, 6):
                draw.line([xx, y0 + 6, xx, y1 - 6], fill=T)
                draw.line([xx, y0 + 6, xx, y1 - 8], fill=C)

    # corner capacitor blocks
    for box in ((12, 12, 36, 36), (124, 12, 148, 36), (12, 124, 36, 148), (124, 124, 148, 148)):
        corner_plate(img, box, cap=False)
        vent(img, [box[0] + 7, box[1] + 8, box[2] - 7, box[3] - 9], slats=3)
        cx = (box[0] + box[2]) // 2
        crystal_socket(img, cx, box[1] + 5, 4, 4, socket=False)

    hazard_band(img, [52, 148, 108, 154], stripe=6)
    return img


def bb_monolith():
    img = chassis(BB, cut=12, body=m, floor=D)
    draw = ImageDraw.Draw(img)

    # central pressure column
    panel(img, [52, 20, 108, 140], fill=m, hi=W, lo=d)
    inset(img, [57, 26, 103, 134], fill=D, hi=K, lo=m)

    # gold top cap with a pair of crystal indicators
    panel(img, [55, 17, 105, 29], fill=G, hi=y, lo=g)
    draw.line([57, 25, 103, 25], fill=g)
    for cx in (72, 88):
        crystal_socket(img, cx, 23, 4, 6, socket=False)

    # stacked collar bands
    for y0 in (38, 96):
        panel(img, [49, y0, 111, y0 + 8], fill=L, hi=W, lo=d)
        for x in range(54, 108, 9):
            bolt(draw, x, y0 + 4)

    # main reactor lens
    arc_reactor(img, 80, 67, 22, spokes=10, triangle=True)

    # lower collision port: hazard throat with a mint glow
    inset(img, [62, 108, 98, 130], fill=K, hi=K, lo=d)
    draw.rectangle([66, 112, 94, 126], fill=T)
    draw.rectangle([70, 115, 90, 123], fill=C)
    draw.rectangle([74, 117, 86, 121], fill=H)
    for x in range(64, 98, 8):
        draw.line([x, 108, x + 4, 114], fill=y)
        draw.line([x, 130, x + 4, 124], fill=y)

    # side flywheels
    for cx in (28, 132):
        disc(draw, cx, 80, 21, K)
        disc(draw, cx, 80, 18, G)
        disc(draw, cx, 80, 15, g)
        disc(draw, cx, 80, 12, m)
        disc(draw, cx, 80, 5, K)
        disc(draw, cx, 80, 3, T)
        for a in range(0, 360, 45):
            x0 = cx + round(math.cos(math.radians(a)) * 6)
            y0 = 80 + round(math.sin(math.radians(a)) * 6)
            x1 = cx + round(math.cos(math.radians(a)) * 14)
            y1 = 80 + round(math.sin(math.radians(a)) * 14)
            draw.line([x0, y0, x1, y1], fill=d)
        # link pipe to column
        if cx < 80:
            pipe(img, cx + 18, 76, 58, 84, conduit=True, flanges=False)
        else:
            pipe(img, 102, 76, cx - 18, 84, conduit=True, flanges=False)

    # exhaust stacks
    for x in (60, 88):
        vpipe(img, x, 8, x + 12, 20, conduit=False)

    # bottom corner vents
    vent(img, [16, 126, 42, 146], slats=3)
    vent(img, [118, 126, 144, 146], slats=3)
    hazard_band(img, [60, 146, 100, 153], stripe=6)
    return img


# ---------------------------------------------------------------------------
# Core Link designs (224x224, 7x7)
# ---------------------------------------------------------------------------

CL = 224


def cl_arc_terminal():
    img = chassis(CL, inset=4, cut=20, body=m, floor=D)
    draw = ImageDraw.Draw(img)

    # corner pylons
    for box in ((24, 24, 54, 54), (170, 24, 200, 54), (24, 170, 54, 200), (170, 170, 200, 200)):
        corner_plate(img, box, cap=True)
        vent(img, [box[0] + 6, box[1] + 9, box[2] - 6, box[3] - 7], slats=3)

    # four radial trunk conduits to edge terminals
    pipe(img, 8, 104, 42, 120, conduit=True)
    pipe(img, 182, 104, 216, 120, conduit=True)
    vpipe(img, 104, 8, 120, 42, conduit=True)
    vpipe(img, 104, 182, 120, 216, conduit=True)

    for cx, cy in ((17, 112), (207, 112), (112, 17), (112, 207)):
        panel(img, [cx - 10, cy - 10, cx + 10, cy + 10], fill=m, hi=W, lo=d)
        inset(img, [cx - 6, cy - 6, cx + 6, cy + 6], fill=T, hi=K, lo=c)
        draw.rectangle([cx - 2, cy - 2, cx + 2, cy + 2], fill=H)

    # the chest piece
    arc_reactor(img, 112, 112, 72, spokes=18, triangle=True)

    # segmented armour struts radiating from the ring
    for a in range(45, 360, 90):
        ang = math.radians(a)
        x0 = 112 + round(math.cos(ang) * 73)
        y0 = 112 + round(math.sin(ang) * 73)
        x1 = 112 + round(math.cos(ang) * 91)
        y1 = 112 + round(math.sin(ang) * 91)
        draw.line([x0, y0, x1, y1], fill=K, width=7)
        draw.line([x0, y0, x1, y1], fill=G, width=4)
        draw.line([x0, y0, x1, y1], fill=y, width=1)

    # ring of crystal indicators
    for a in range(0, 360, 45):
        ang = math.radians(a)
        cx = 112 + round(math.cos(ang) * 84)
        cy = 112 + round(math.sin(ang) * 84)
        crystal_socket(img, cx, cy, 4, 6, socket=False)

    hazard_band(img, [82, 198, 142, 205], stripe=6)
    return img


def cl_hex_vault():
    img = chassis(CL, inset=4, cut=16, body=m, floor=D)
    draw = ImageDraw.Draw(img)
    cx, cy = 112, 108

    def hexagon(radius):
        return [
            (cx, cy - radius),
            (cx + round(radius * 0.866), cy - radius // 2),
            (cx + round(radius * 0.866), cy + radius // 2),
            (cx, cy + radius),
            (cx - round(radius * 0.866), cy + radius // 2),
            (cx - round(radius * 0.866), cy - radius // 2),
        ]

    draw.polygon(hexagon(88), fill=K)
    draw.polygon(hexagon(85), fill=L)
    draw.polygon(hexagon(82), fill=m)
    draw.polygon(hexagon(73), fill=K)
    draw.polygon(hexagon(70), fill=D)
    draw.polygon(hexagon(60), fill=K)
    draw.polygon(hexagon(58), fill=d)

    # mint seams between the vault layers
    for i in range(6):
        a = math.radians(i * 60 - 90)
        for radius in (82, 70, 58):
            x0 = cx + round(math.cos(a) * (radius - 1))
            y0 = cy + round(math.sin(a) * (radius - 1))
            x1 = cx + round(math.cos(a) * (radius - 8))
            y1 = cy + round(math.sin(a) * (radius - 8))
            draw.line([x0, y0, x1, y1], fill=C)
        bx = cx + round(math.cos(a) * 76)
        by = cy + round(math.sin(a) * 76)
        bolt(draw, bx, by)

    # three gold locking bars
    for x in (78, 108, 138):
        panel(img, [x, 48, x + 8, 168], fill=G, hi=y, lo=g)
        draw.line([x + 2, 52, x + 2, 164], fill=g)
        draw.line([x + 5, 52, x + 5, 164], fill=y)
        for y0 in (54, 160):
            bolt(draw, x + 4, y0)

    # central reactor
    arc_reactor(img, cx, cy, 26, spokes=12, triangle=True)

    # edge ports
    for px, py in ((112, 16), (112, 200), (16, 108), (208, 108)):
        panel(img, [px - 12, py - 8, px + 12, py + 8], fill=m, hi=W, lo=d)
        inset(img, [px - 7, py - 4, px + 7, py + 4], fill=T, hi=K, lo=c)
        draw.rectangle([px - 2, py - 2, px + 2, py + 2], fill=H)

    # corner anchor blocks
    for box in ((18, 18, 48, 48), (176, 18, 206, 48), (18, 168, 48, 198), (176, 168, 206, 198)):
        corner_plate(img, box, cap=False)
        vent(img, [box[0] + 6, box[1] + 7, box[2] - 6, box[3] - 8], slats=3)

    hazard_band(img, [84, 198, 140, 205], stripe=6)
    return img


def cl_portal():
    img = chassis(CL, inset=4, cut=14, body=m, floor=D)
    draw = ImageDraw.Draw(img)

    # heavy portal frame
    for box in ((38, 38, 186, 186),):
        panel(img, box, fill=L, hi=W, lo=d)
        inset(img, [box[0] + 6, box[1] + 6, box[2] - 6, box[3] - 6], fill=m, hi=K, lo=W)
        inset(img, [box[0] + 12, box[1] + 12, box[2] - 12, box[3] - 12], fill=D, hi=K, lo=m)

    # field aperture
    draw.rectangle([55, 55, 169, 169], fill=K)
    draw.rectangle([60, 60, 164, 164], fill=T)
    for y0 in range(64, 164, 7):
        draw.line([65, y0, 159, y0], fill=c)
        draw.line([65, y0 + 2, 159, y0 + 2], fill=C)
    disc(draw, 112, 112, 42, C)
    disc(draw, 112, 112, 32, H)
    crystal(img, 112, 112, 18, 34)
    crystal(img, 84, 108, 7, 13)
    crystal(img, 140, 115, 6, 11)

    # frame segmentation and bolts
    for x in (58, 84, 112, 140, 166):
        bolt(draw, x, 45)
        bolt(draw, x, 179)
    for yy in (58, 84, 112, 140, 166):
        bolt(draw, 45, yy)
        bolt(draw, 179, yy)
    for x in (70, 112, 154):
        panel(img, [x - 4, 36, x + 4, 46], fill=G, hi=y, lo=g)
        panel(img, [x - 4, 178, x + 4, 188], fill=G, hi=y, lo=g)
    for yy in (70, 112, 154):
        panel(img, [36, yy - 4, 46, yy + 4], fill=G, hi=y, lo=g)
        panel(img, [178, yy - 4, 188, yy + 4], fill=G, hi=y, lo=g)

    # corner claws
    for bx, by in ((26, 26), (198, 26), (26, 198), (198, 198)):
        panel(img, [bx - 9, by - 9, bx + 9, by + 9], fill=m, hi=W, lo=d)
        draw.rectangle([bx - 5, by - 5, bx + 5, by + 5], fill=K)
        draw.polygon([(bx - 3, by - 3), (bx + 6, by), (bx, by + 6)], fill=G)

    # radial feeds
    pipe(img, 10, 106, 36, 118, conduit=True)
    pipe(img, 188, 106, 214, 118, conduit=True)
    vpipe(img, 106, 10, 118, 36, conduit=True)
    vpipe(img, 106, 188, 118, 214, conduit=True)

    hazard_band(img, [78, 198, 146, 205], stripe=6)
    return img


def cl_twin_reactor():
    img = chassis(CL, inset=4, cut=18, body=m, floor=D)
    draw = ImageDraw.Draw(img)

    # corner banks
    for box in ((22, 22, 50, 50), (174, 22, 202, 50), (22, 174, 50, 202), (174, 174, 202, 202)):
        corner_plate(img, box, cap=True)
        vent(img, [box[0] + 6, box[1] + 8, box[2] - 6, box[3] - 8], slats=3)

    # central crystal spine first, so the twin rings sit proud of it
    panel(img, [100, 44, 124, 180], fill=m, hi=W, lo=d)
    inset(img, [104, 50, 120, 174], fill=D, hi=K, lo=m)
    draw.line([112, 56, 112, 168], fill=T, width=3)
    for yy in range(60, 168, 8):
        draw.line([109, yy, 115, yy], fill=C)
    crystal(img, 112, 92, 7, 15)
    crystal(img, 112, 132, 6, 12)

    # twin reactors, tangent to the spine
    arc_reactor(img, 62, 112, 34, spokes=12, triangle=True)
    arc_reactor(img, 162, 112, 34, spokes=12, triangle=True)

    # edge feeds running into the outer reactor rings
    pipe(img, 10, 104, 26, 120, conduit=True)
    pipe(img, 198, 104, 214, 120, conduit=True)

    # top and bottom node plates
    for y0, y1 in ((20, 44), (180, 204)):
        panel(img, [92, y0, 132, y1], fill=m, hi=W, lo=d)
        inset(img, [97, y0 + 5, 127, y1 - 5], fill=T, hi=K, lo=c)
        draw.rectangle([106, y0 + 9, 118, y1 - 9], fill=D)
        crystal_socket(img, 112, (y0 + y1) // 2, 5, 8, socket=False)

    hazard_band(img, [80, 200, 144, 207], stripe=6)
    return img


def cl_octagon_hub():
    img = chassis(CL, inset=4, cut=26, body=m, floor=D)
    draw = ImageDraw.Draw(img)
    cx, cy = 112, 110

    def octa(radius):
        return [
            (cx + round(math.cos(math.radians(a)) * radius),
             cy + round(math.sin(math.radians(a)) * radius))
            for a in range(22, 360, 45)
        ]

    draw.polygon(octa(90), fill=K)
    draw.polygon(octa(87), fill=L)
    draw.polygon(octa(84), fill=m)
    draw.polygon(octa(74), fill=K)
    draw.polygon(octa(72), fill=D)
    draw.polygon(octa(58), fill=K)
    draw.polygon(octa(56), fill=d)

    # eight radial ports
    for i in range(8):
        ang = math.radians(i * 45 + 22)
        x0 = cx + round(math.cos(ang) * 56)
        y0 = cy + round(math.sin(ang) * 56)
        x1 = cx + round(math.cos(ang) * 92)
        y1 = cy + round(math.sin(ang) * 92)
        draw.line([x0, y0, x1, y1], fill=K, width=11)
        draw.line([x0, y0, x1, y1], fill=G, width=7)
        draw.line([x0, y0, x1, y1], fill=g, width=3)
        # mint port light at the rim
        px = cx + round(math.cos(ang) * 86)
        py = cy + round(math.sin(ang) * 86)
        draw.rectangle([px - 3, py - 3, px + 3, py + 3], fill=K)
        draw.rectangle([px - 2, py - 2, px + 2, py + 2], fill=C)
        draw.point([px, py], fill=w)

    # rim bolts
    for i in range(16):
        ang = math.radians(i * 22.5)
        bx = cx + round(math.cos(ang) * 79)
        by = cy + round(math.sin(ang) * 79)
        bolt(draw, bx, by)

    # central reactor
    arc_reactor(img, cx, cy, 36, spokes=14, triangle=True)

    # corner braces in the four open corners
    for bx, by in ((24, 24), (200, 24), (24, 196), (200, 196)):
        panel(img, [bx - 12, by - 12, bx + 12, by + 12], fill=m, hi=W, lo=d)
        inset(img, [bx - 7, by - 7, bx + 7, by + 7], fill=D, hi=K, lo=m)
        bolt(draw, bx - 4, by - 4)
        bolt(draw, bx + 4, by + 4)

    hazard_band(img, [82, 200, 142, 207], stripe=6)
    return img


# ---------------------------------------------------------------------------
# contact sheets
# ---------------------------------------------------------------------------

def load_font(size):
    for path in (
        "C:/Windows/Fonts/consola.ttf",
        "C:/Windows/Fonts/arial.ttf",
        "C:/Windows/Fonts/segoeui.ttf",
    ):
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size)
            except OSError:
                pass
    return ImageFont.load_default()


def checker(width, height, cell=14):
    img = Image.new("RGBA", (width, height), (26, 31, 39, 255))
    draw = ImageDraw.Draw(img)
    for y in range(0, height, cell):
        for x in range(0, width, cell):
            if (x // cell + y // cell) % 2 == 0:
                draw.rectangle([x, y, x + cell - 1, y + cell - 1], fill=(30, 36, 46, 255))
    return img


def contact_sheet(title, subtitle, items, path, scale=1, gap=22, pad=28):
    tiles = []
    for letter, name, img in items:
        if scale != 1:
            img = img.resize((img.width * scale, img.height * scale), Image.NEAREST)
        tiles.append((letter, name, img))

    font_title = load_font(22)
    font_label = load_font(15)
    font_small = load_font(12)

    label_h = 42
    max_h = max(t[2].height for t in tiles)
    inner_w = sum(t[2].width for t in tiles) + gap * (len(tiles) - 1)
    width = max(inner_w + pad * 2, 760)
    height = pad * 2 + 34 + 22 + max_h + label_h

    sheet = Image.new("RGBA", (width, height), (20, 24, 31, 255))
    draw = ImageDraw.Draw(sheet)
    draw.text((pad, pad - 4), title, font=font_title, fill=(232, 240, 235, 255))
    draw.text((pad, pad + 26), subtitle, font=font_small, fill=(148, 162, 166, 255))

    x = (width - inner_w) // 2
    y = pad + 58
    for letter, name, img in tiles:
        backdrop = checker(img.width, img.height)
        backdrop.alpha_composite(img)
        sheet.alpha_composite(backdrop, (x, y))
        draw = ImageDraw.Draw(sheet)
        draw.rectangle([x - 1, y - 1, x + img.width, y + img.height], outline=(58, 70, 78, 255))
        draw.text((x + 2, y + img.height + 8), f"{letter}  {name}", font=font_label, fill=(206, 217, 211, 255))
        x += img.width + gap

    os.makedirs(os.path.dirname(path), exist_ok=True)
    sheet.convert("RGB").save(path)
    print(f"wrote {os.path.relpath(path, ROOT)}")


# ---------------------------------------------------------------------------
# design registry
# ---------------------------------------------------------------------------

BB_DESIGNS = [
    ("A", "Torus Reactor", bb_torus),
    ("B", "Twin Rails", bb_twin_rails),
    ("C", "Hex Chamber", bb_hex),
    ("D", "Crossfire", bb_crossfire),
    ("E", "Monolith", bb_monolith),
]

CL_DESIGNS = [
    ("A", "Arc Terminal", cl_arc_terminal),
    ("B", "Hex Vault", cl_hex_vault),
    ("C", "Portal Frame", cl_portal),
    ("D", "Twin Reactor", cl_twin_reactor),
    ("E", "Octagon Hub", cl_octagon_hub),
]

# Final in-game art. Change these to swap designs; run the script to reinstall.
CHOSEN = {
    "bb-collider": "A",
    "core-link": "B",
}


def audit(name, img):
    px = img.load()
    allowed = set(PALETTE)
    opaque = 0
    unknown = set()
    for y in range(img.height):
        for x in range(img.width):
            r, g, b, a = px[x, y]
            if a:
                opaque += 1
                if a != 255 or (r, g, b) not in allowed:
                    unknown.add((r, g, b, a))
    frac = opaque / (img.width * img.height)
    status = "ok" if not unknown and frac > 0.70 else "CHECK"
    print(f"  {name:16s} {img.width}x{img.height} opaque={frac:.2f} colors+={len(unknown)} {status}")
    return not unknown


def main():
    os.makedirs(DOCS, exist_ok=True)
    os.makedirs(SPRITES, exist_ok=True)
    ok = True

    built = {}
    for letter, label, factory in BB_DESIGNS:
        img = factory()
        ok &= audit(f"bb-{letter}", img)
        out = os.path.join(DOCS, f"bb-collider-{letter.lower()}.png")
        img.save(out)
        built[("bb-collider", letter)] = img

    for letter, label, factory in CL_DESIGNS:
        img = factory()
        ok &= audit(f"cl-{letter}", img)
        out = os.path.join(DOCS, f"core-link-{letter.lower()}.png")
        img.save(out)
        built[("core-link", letter)] = img

    for name, letter in CHOSEN.items():
        img = built[(name, letter)]
        img.save(os.path.join(SPRITES, name + ".png"))
        print(f"installed sprites/{name}.png <- design {letter}")

    bb_items = [(l, n, f()) for l, n, f in BB_DESIGNS]
    cl_items = [(l, n, f()) for l, n, f in CL_DESIGNS]

    contact_sheet(
        "B.B Collider - design candidates",
        "5x5 factory  /  80% vanilla industrial shell, 20% arc-reactor sci-fi  /  grey + Bayugo mint & gold",
        bb_items,
        os.path.join(DOCS, "bb-collider-designs.png"),
        scale=2,
        gap=20,
    )
    contact_sheet(
        "Core Link - design candidates",
        "7x7 terminal  /  80% vanilla industrial shell, 20% arc-reactor sci-fi  /  grey + Bayugo mint & gold",
        cl_items,
        os.path.join(DOCS, "core-link-designs.png"),
        scale=1,
        gap=20,
    )

    print("palette clean" if ok else "PALETTE / COVERAGE PROBLEM")


if __name__ == "__main__":
    main()
