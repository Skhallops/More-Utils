"""
Sprite generator for the More-Utils mod.

Both buildings are derived from real vanilla Mindustry sprites instead of being
drawn from scratch, so their silhouette, pixel density and shading language
match the base game exactly:

  * B.B Collider (5x5)  - vanilla Core: Nucleus shell re-coloured with the
                          vanilla Distributor palette, with a heavy industrial
                          accelerator housing built into the centre. No crystal
                          detail: the collider only *makes* crystals.
  * Core Link  (7x7)    - a Distributor-styled reinforced platform carrying a
                          Nexus-style core module, with Bayugo crystal windows in
                          the apron and a crystal vault at the centre.

Every grey is sampled from a vanilla sprite, so nothing can drift off-model:
distributor.png gives #4a4b53 / #6e7080 / #989aa4, core-nucleus.png adds the
lighter #b0bac0 bevel. Crystal and heat accents reuse the palette of the block
effects and of the Bayugo Crystal item icon (teal body, gold facet).

Usage:  py -3 tools/generate_buildings.py [--ascii]
"""

import math
import os
import sys

from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VANILLA = os.path.join(ROOT, "tools", "vanilla")
DOCS = os.path.join(ROOT, "docs", "designs")
SPRITES = os.path.join(ROOT, "sprites")

# ---------------------------------------------------------------------------
# palette - every entry copied from a vanilla sprite or from the mod effects
# ---------------------------------------------------------------------------

# distributor.png (exact):  outline, body, highlight
# core-nucleus.png (exact): adds the lighter bevel tone
EDGE = (74, 75, 83)      # 4a4b53  distributor outline
DARK = (110, 112, 128)   # 6e7080  distributor body / nucleus shadow
MID = (152, 154, 164)    # 989aa4  distributor highlight / nucleus body
LIGHT = (176, 186, 192)  # b0bac0  nucleus highlight

# Bayugo Crystal - matches the item icon (teal body, gold facet)
C_DEEP = (37, 105, 111)    # 25696f
C_DARK = (63, 170, 164)    # 3faaa4
C_MID = (133, 224, 198)    # 85e0c6
C_HI = (207, 250, 232)     # cffae8

# collider heat - matches the craftEffect golds
A_DEEP = (151, 119, 58)    # 97773a
A_MID = (211, 180, 94)     # d3b45e
A_HOT = (247, 224, 151)    # f7e097
A_WHITE = (253, 246, 223)

PALETTE = (EDGE, DARK, MID, LIGHT, C_DEEP, C_DARK, C_MID, C_HI,
           A_DEEP, A_MID, A_HOT, A_WHITE)

# core-nucleus.png uses these three flat tones
NUCLEUS = [(110, 112, 128), (152, 154, 164), (176, 186, 192)]

BB = 160   # 5x5 blocks
CL = 224   # 7x7 blocks

# ---------------------------------------------------------------------------
# vanilla helpers
# ---------------------------------------------------------------------------


def load_vanilla(name):
    return Image.open(os.path.join(VANILLA, name + ".png")).convert("RGBA")


def restyle(img, src, dst):
    """Snap a vanilla sprite onto another palette.

    Vanilla block art uses a handful of flat tones, so a nearest-colour remap
    preserves every pixel of the original shading and only changes the hues.
    """
    out = Image.new("RGBA", img.size, (0, 0, 0, 0))
    sp = img.load()
    dp = out.load()
    for y in range(img.height):
        for x in range(img.width):
            r, g, b, a = sp[x, y]
            if a < 20:
                continue
            idx = min(
                range(len(src)),
                key=lambda i: (src[i][0] - r) ** 2 + (src[i][1] - g) ** 2 + (src[i][2] - b) ** 2,
            )
            dp[x, y] = dst[idx] + (255,)
    return out


def octagon(cx, cy, r, fill, cut=None):
    cut = r * 0.42 if cut is None else cut
    return [
        (cx - r + cut, cy - r), (cx + r - cut, cy - r),
        (cx + r, cy - r + cut), (cx + r, cy + r - cut),
        (cx + r - cut, cy + r), (cx - r + cut, cy + r),
        (cx - r, cy + r - cut), (cx - r, cy - r + cut),
    ]


def octo(img, cx, cy, r, fill, cut=None):
    ImageDraw.Draw(img).polygon(octagon(cx, cy, r, fill, cut), fill=fill)


def bevel(img, box, radius, hi, lo):
    """Top-left lit / bottom-right shadowed edge, the vanilla lighting rule."""
    x0, y0, x1, y1 = box
    d = ImageDraw.Draw(img)
    d.line([(x0 + radius, y0), (x1 - radius, y0)], fill=hi, width=2)
    d.line([(x0, y0 + radius), (x0, y1 - radius)], fill=hi, width=2)
    d.line([(x0 + radius, y1), (x1 - radius, y1)], fill=lo, width=2)
    d.line([(x1, y0 + radius), (x1, y1 - radius)], fill=lo, width=2)
    d.arc([x0, y0, x0 + 2 * radius, y0 + 2 * radius], 180, 270, fill=hi, width=2)
    d.arc([x1 - 2 * radius, y1 - 2 * radius, x1, y1], 0, 90, fill=lo, width=2)


def bolt(img, cx, cy, r=3, face=MID, dark=EDGE):
    d = ImageDraw.Draw(img)
    d.rectangle([cx - r, cy - r, cx + r, cy + r], fill=dark)
    d.rectangle([cx - r + 1, cy - r + 1, cx + r - 1, cy + r - 1], fill=face)
    d.point([cx - r + 1, cy - r + 1], fill=LIGHT)


def panel(img, box, radius=0, face=DARK, hi=MID, lo=EDGE):
    x0, y0, x1, y1 = box
    d = ImageDraw.Draw(img)
    if radius:
        d.rounded_rectangle(box, radius=radius, fill=EDGE)
        d.rounded_rectangle([x0 + 2, y0 + 2, x1 - 2, y1 - 2], radius=max(1, radius - 2), fill=face)
        bevel(img, (x0 + 2, y0 + 2, x1 - 2, y1 - 2), max(1, radius - 2), hi, lo)
    else:
        d.rectangle(box, fill=EDGE)
        d.rectangle([x0 + 2, y0 + 2, x1 - 2, y1 - 2], fill=face)
        d.line([x0 + 2, y0 + 2, x1 - 2, y0 + 2], fill=hi, width=2)
        d.line([x0 + 2, y0 + 2, x0 + 2, y1 - 2], fill=hi, width=2)
        d.line([x0 + 2, y1 - 2, x1 - 2, y1 - 2], fill=lo, width=2)
        d.line([x1 - 2, y0 + 2, x1 - 2, y1 - 2], fill=lo, width=2)


def amber_rail(img, x0, x1, y, on=6, off=3, thick=2):
    """Dashed energy rail (horizontal)."""
    d = ImageDraw.Draw(img)
    x = x0
    while x <= x1:
        xe = min(x + on - 1, x1)
        d.rectangle([x, y, xe, y + thick - 1], fill=A_DEEP)
        if xe >= x + 2:
            d.rectangle([x + 1, y, xe - 1, y + thick - 2], fill=A_MID)
            d.line([x + 1, y, xe - 1, y], fill=A_HOT)
        elif xe > x:
            d.rectangle([x, y, xe, y + thick - 2], fill=A_MID)
        x += on + off


def coil(img, x0, x1, y):
    d = ImageDraw.Draw(img)
    d.line([x0, y, x1, y], fill=A_DEEP, width=2)
    d.line([x0, y, x1, y], fill=A_MID)
    d.line([x0 + 1, y - 1, x1 - 1, y - 1], fill=A_HOT)


def shard(img, cx, base, w, h, lean=0):
    """Faceted Bayugo shard, lit from the upper left like vanilla art."""
    d = ImageDraw.Draw(img)
    tip = (cx + lean, base - h)
    pts = [
        tip,
        (cx + w, base - h * 0.40),
        (cx + w * 0.58, base),
        (cx - w * 0.58, base),
        (cx - w, base - h * 0.40),
    ]
    d.polygon(pts, fill=C_MID)
    d.polygon([tip, (cx + w, base - h * 0.40), (cx + w * 0.58, base), (cx, base)], fill=C_DARK)
    d.polygon([tip, (cx - w, base - h * 0.40), (cx - w * 0.40, base), (cx, base)], fill=C_HI)
    d.line(pts + [pts[0]], fill=C_DEEP)
    d.line([tip, (cx, base)], fill=C_DEEP)


def gold_shard(img, cx, base, w, h, lean=0):
    """Gold-faceted shard - the Bayugo Crystal item icon has one of these."""
    d = ImageDraw.Draw(img)
    tip = (cx + lean, base - h)
    pts = [
        tip,
        (cx + w, base - h * 0.40),
        (cx + w * 0.58, base),
        (cx - w * 0.58, base),
        (cx - w, base - h * 0.40),
    ]
    d.polygon(pts, fill=A_MID)
    d.polygon([tip, (cx + w, base - h * 0.40), (cx + w * 0.58, base), (cx, base)], fill=A_DEEP)
    d.polygon([tip, (cx - w, base - h * 0.40), (cx - w * 0.40, base), (cx, base)], fill=A_HOT)
    d.line(pts + [pts[0]], fill=A_DEEP)
    d.line([tip, (cx, base)], fill=A_DEEP)
    d.point([tip[0], tip[1] + 1], fill=A_WHITE)


# ---------------------------------------------------------------------------
# B.B Collider - 5x5, no crystals
# ---------------------------------------------------------------------------


def bb_base():
    img = restyle(load_vanilla("core-nucleus"), NUCLEUS, [EDGE, DARK, MID])
    d = ImageDraw.Draw(img)
    # distributor-style sockets on the four edges
    for box in ((66, 6, 94, 16), (66, 143, 94, 153), (6, 66, 16, 94), (143, 66, 153, 94)):
        d.rectangle(box, fill=EDGE)
        x0, y0, x1, y1 = box
        d.rectangle([x0 + 2, y0 + 2, x1 - 2, y1 - 2], fill=DARK)
        d.line([x0 + 2, y0 + 2, x1 - 2, y0 + 2], fill=MID)
    # corner clamps
    for cx, cy in ((22, 22), (137, 22), (22, 137), (137, 137)):
        bolt(img, cx, cy, 3, face=MID)
    # status lamps
    for cx, cy in ((80, 24), (80, 135), (24, 80), (135, 80)):
        d.rectangle([cx - 2, cy - 2, cx + 2, cy + 2], fill=EDGE)
        d.rectangle([cx - 1, cy - 1, cx + 1, cy + 1], fill=A_MID)
        d.point([cx - 1, cy - 1], fill=A_WHITE)
    return img


def bb_housing(img):
    """Heavy accelerator frame, bolted into the vanilla nucleus centre."""
    d = ImageDraw.Draw(img)
    # diagonal struts, so the frame reads as part of the vanilla structure
    for sx, sy in ((1, 1), (-1, 1), (1, -1), (-1, -1)):
        x0, y0 = 80 + sx * 30, 80 + sy * 30
        x1, y1 = 80 + sx * 63, 80 + sy * 63
        d.line([x0, y0, x1, y1], fill=EDGE, width=13)
        d.line([x0, y0, x1, y1], fill=DARK, width=9)
        d.line([x0 - 1, y0 - 1, x1 - 1, y1 - 1], fill=MID, width=2)
        bolt(img, x1, y1, 3, face=MID)
    panel(img, (28, 28, 131, 131), radius=10, face=DARK, hi=MID, lo=EDGE)
    # inner recess
    d.rectangle([38, 38, 121, 121], fill=EDGE)
    d.rectangle([40, 40, 119, 119], fill=DARK)
    d.line([40, 40, 119, 40], fill=EDGE, width=1)
    d.line([40, 40, 40, 119], fill=EDGE, width=1)
    # corner bolts
    for cx, cy in ((33, 33), (126, 33), (33, 126), (126, 126)):
        bolt(img, cx, cy, 2, face=MID)
    return img


def bb_cap(img, box, stripes=5):
    x0, y0, x1, y1 = box
    panel(img, box, face=DARK, hi=MID, lo=EDGE)
    for i in range(stripes):
        y = y0 + 6 + i * ((y1 - y0 - 10) // max(1, stripes - 1))
        coil(img, x0 + 4, x1 - 4, y)


def bb_beam_press():
    """A - Beam Press: two capped bores driving a beam into a focal gap."""
    img = bb_base()
    bb_housing(img)
    d = ImageDraw.Draw(img)
    bb_cap(img, (40, 50, 58, 109), stripes=5)
    bb_cap(img, (101, 50, 119, 109), stripes=5)
    # accelerator barrels facing the gap
    for x0, x1 in ((58, 70), (89, 101)):
        d.rectangle([x0, 72, x1, 88], fill=EDGE)
        d.rectangle([x0 + 1, 73, x1 - 1, 87], fill=MID)
        d.rectangle([x0 + 2, 75, x1 - 2, 85], fill=DARK)
        d.line([x0 + 2, 75, x1 - 2, 75], fill=LIGHT)
        d.line([x0 + 2, 75, x0 + 2, 85], fill=LIGHT)
    # focal gap
    d.rectangle([70, 70, 89, 90], fill=EDGE)
    d.rectangle([72, 72, 87, 88], fill=DARK)
    amber_rail(img, 72, 87, 79, on=4, off=2, thick=2)
    d.line([79, 72, 79, 88], fill=A_HOT)
    d.line([74, 80, 85, 80], fill=A_HOT)
    d.rectangle([78, 79, 80, 81], fill=A_WHITE)
    for px, py in ((77, 78), (81, 82), (77, 82), (81, 78)):
        d.point([px, py], fill=A_WHITE)
    return img


def bb_twin_bore():
    """B - Twin Bore: two vertical accelerator bores bridged at the waist."""
    img = bb_base()
    bb_housing(img)
    d = ImageDraw.Draw(img)
    for bx in (56, 103):
        d.rectangle([bx - 11, 46, bx + 11, 113], fill=EDGE)
        d.rectangle([bx - 9, 48, bx + 9, 111], fill=MID)
        d.rectangle([bx - 7, 50, bx + 7, 109], fill=DARK)
        d.rectangle([bx - 5, 52, bx + 5, 107], fill=EDGE)
        d.rectangle([bx - 2, 54, bx + 2, 105], fill=A_DEEP)
        d.rectangle([bx - 1, 54, bx + 1, 105], fill=A_HOT)
        for y in (58, 70, 82, 94, 104):
            d.rectangle([bx - 8, y, bx + 8, y + 2], fill=EDGE)
            d.line([bx - 7, y + 1, bx + 7, y + 1], fill=A_MID)
    # bridge chamber
    panel(img, (64, 71, 95, 89), face=DARK, hi=MID, lo=EDGE)
    d.rectangle([74, 75, 85, 85], fill=EDGE)
    d.rectangle([76, 77, 83, 83], fill=A_DEEP)
    d.rectangle([78, 78, 81, 82], fill=A_WHITE)
    return img


def bb_cyclotron():
    """C - Cyclotron: quadruple magnet ring around a hot focus."""
    img = bb_base()
    bb_housing(img)
    d = ImageDraw.Draw(img)
    octo(img, 80, 80, 40, EDGE)
    octo(img, 80, 80, 36, MID)
    octo(img, 80, 80, 33, DARK)
    octo(img, 80, 80, 28, EDGE)
    octo(img, 80, 80, 25, DARK)
    # lit rim, upper left only
    pts = octagon(80, 80, 36, MID)
    for a, b in ((0, 1), (1, 2), (7, 0)):
        d.line([pts[a], pts[b]], fill=LIGHT, width=1)
    # magnets
    for ang in (0, 90, 180, 270):
        a = math.radians(ang)
        mx = int(80 + 34 * math.cos(a))
        my = int(80 + 34 * math.sin(a))
        if ang in (0, 180):
            d.rectangle([mx - 6, my - 12, mx + 6, my + 12], fill=EDGE)
            d.rectangle([mx - 4, my - 10, mx + 4, my + 10], fill=MID)
            d.rectangle([mx - 3, my - 8, mx + 3, my + 8], fill=DARK)
            for yy in range(my - 6, my + 7, 5):
                d.line([mx - 2, yy, mx + 2, yy], fill=A_MID)
        else:
            d.rectangle([mx - 12, my - 6, mx + 12, my + 6], fill=EDGE)
            d.rectangle([mx - 10, my - 4, mx + 10, my + 4], fill=MID)
            d.rectangle([mx - 8, my - 3, mx + 8, my + 3], fill=DARK)
            for xx in range(mx - 6, mx + 7, 5):
                d.line([xx, my - 2, xx, my + 2], fill=A_MID)
    # focus
    d.rectangle([72, 72, 87, 87], fill=EDGE)
    d.rectangle([74, 74, 85, 85], fill=A_DEEP)
    d.rectangle([76, 76, 83, 83], fill=A_MID)
    d.rectangle([78, 78, 81, 81], fill=A_WHITE)
    return img


def bb_press():
    """D - Anvil Press: guide columns and a hot vertical compression gap."""
    img = bb_base()
    bb_housing(img)
    d = ImageDraw.Draw(img)
    for x0 in (50, 100):
        panel(img, (x0, 44, x0 + 10, 116), face=DARK, hi=MID, lo=EDGE)
        for y in range(50, 112, 12):
            d.rectangle([x0 + 2, y, x0 + 8, y + 2], fill=EDGE)
            d.line([x0 + 3, y + 1, x0 + 7, y + 1], fill=A_MID)
    for y0, y1 in ((50, 71), (89, 110)):
        panel(img, (62, y0, 99, y1), face=MID, hi=LIGHT, lo=EDGE)
        d.rectangle([66, y0 + 4, 95, y1 - 4], fill=DARK)
        d.line([66, y0 + 4, 95, y0 + 4], fill=MID)
    # pistons
    panel(img, (74, 42, 86, 50), face=DARK, hi=MID, lo=EDGE)
    panel(img, (74, 110, 86, 118), face=DARK, hi=MID, lo=EDGE)
    # heat gap
    d.rectangle([63, 74, 98, 86], fill=EDGE)
    d.rectangle([65, 76, 96, 84], fill=A_DEEP)
    amber_rail(img, 67, 94, 79, on=4, off=2, thick=2)
    d.rectangle([76, 75, 83, 84], fill=A_HOT)
    d.rectangle([78, 77, 81, 82], fill=A_WHITE)
    return img


def bb_crossfire():
    """E - Crossfire: four corner emitters converging on a single impact."""
    img = bb_base()
    bb_housing(img)
    d = ImageDraw.Draw(img)
    for ex, ey, sx, sy in ((50, 50, 1, 1), (109, 50, -1, 1),
                           (50, 109, 1, -1), (109, 109, -1, -1)):
        panel(img, (ex - 8, ey - 8, ex + 8, ey + 8), face=DARK, hi=MID, lo=EDGE)
        d.rectangle([ex - 4, ey - 4, ex + 4, ey + 4], fill=EDGE)
        d.rectangle([ex - 2, ey - 2, ex + 2, ey + 2], fill=A_MID)
        d.point([ex - 1, ey - 1], fill=A_WHITE)
        # stepped beam toward the centre
        for i in range(1, 9):
            bx = ex + sx * i * 3
            by = ey + sy * i * 3
            col = A_HOT if i % 3 else A_DEEP
            d.rectangle([bx - 1, by - 1, bx + 1, by + 1], fill=col)
    # focus
    d.rectangle([73, 73, 86, 86], fill=EDGE)
    d.rectangle([75, 75, 84, 84], fill=A_DEEP)
    d.rectangle([77, 77, 82, 82], fill=A_MID)
    d.rectangle([78, 78, 81, 81], fill=A_WHITE)
    d.line([70, 80, 89, 80], fill=A_HOT)
    d.line([80, 70, 80, 89], fill=A_HOT)
    return img


# ---------------------------------------------------------------------------
# Core Link - 7x7, Bayugo crystal application
# ---------------------------------------------------------------------------


def cl_platform():
    """7x7 Distributor-styled platform for the core module to sit on."""
    img = Image.new("RGBA", (CL, CL), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    # full-bleed footprint, like the vanilla core and distributor sprites:
    # the silhouette is cut back with shaded corner bevels instead of alpha.
    d.rectangle([0, 0, CL - 1, CL - 1], fill=EDGE)
    octo(img, 112, 112, 109, DARK, cut=46)
    pts = octagon(112, 112, 109, DARK, 46)
    for a, b in ((0, 1), (1, 2), (7, 0)):
        d.line([pts[a], pts[b]], fill=MID, width=2)
    for a, b in ((3, 4), (4, 5), (5, 6)):
        d.line([pts[a], pts[b]], fill=EDGE, width=2)
    # corner plates (Distributor sockets read as heavy corner clamps)
    for x0, y0, x1, y1 in ((6, 6, 30, 30), (CL - 31, 6, CL - 7, 30),
                           (6, CL - 31, 30, CL - 7), (CL - 31, CL - 31, CL - 7, CL - 7)):
        d.rectangle([x0, y0, x1, y1], fill=EDGE)
        d.rectangle([x0 + 1, y0 + 1, x1 - 1, y1 - 1], fill=MID)
        d.rectangle([x0 + 3, y0 + 3, x1 - 3, y1 - 3], fill=DARK)
        d.line([x0 + 3, y0 + 3, x1 - 3, y0 + 3], fill=EDGE)
        d.line([x0 + 3, y0 + 3, x0 + 3, y1 - 3], fill=EDGE)
        d.line([x0 + 1, y0 + 1, x1 - 1, y0 + 1], fill=LIGHT)
        bolt(img, (x0 + x1) // 2, (y0 + y1) // 2, 3, face=MID)
    # side clamp blocks
    for x0, y0, x1, y1 in ((96, 4, 128, 15), (96, CL - 16, 128, CL - 5),
                           (4, 96, 15, 128), (CL - 16, 96, CL - 5, 128)):
        d.rectangle([x0, y0, x1, y1], fill=EDGE)
        d.rectangle([x0 + 2, y0 + 2, x1 - 2, y1 - 2], fill=DARK)
        d.line([x0 + 2, y0 + 2, x1 - 2, y0 + 2], fill=MID)
        d.line([x0 + 2, y0 + 2, x0 + 2, y1 - 2], fill=MID)
    return img


def cl_crystal_window(img, cx, cy, vertical=True):
    """Small Bayugo sight-glass set into the outer platform."""
    d = ImageDraw.Draw(img)
    w, h = 6, 11
    if vertical:
        d.rectangle([cx - w - 3, cy - h - 3, cx + w + 3, cy + h + 3], fill=EDGE)
        d.rectangle([cx - w - 1, cy - h - 1, cx + w + 1, cy + h + 1], fill=DARK)
        d.line([cx - w, cy - h, cx + w, cy - h], fill=MID)
        shard(img, cx, cy + h, w - 1, 2 * h - 2)
    else:
        d.rectangle([cx - h - 3, cy - w - 3, cx + h + 3, cy + w + 3], fill=EDGE)
        d.rectangle([cx - h - 1, cy - w - 1, cx + h + 1, cy + w + 1], fill=DARK)
        d.line([cx - h, cy - w, cx - h, cy + w], fill=MID)
        shard(img, cx, cy + w, w - 1, 2 * h - 2)


def cl_base(with_windows=True):
    img = cl_platform()
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([29, 29, 194, 194], radius=15, fill=EDGE)
    d.rounded_rectangle([30, 31, 195, 195], radius=15, fill=EDGE)
    module = restyle(load_vanilla("core-nucleus"), NUCLEUS, [DARK, MID, LIGHT])
    img.alpha_composite(module, (32, 32))
    if with_windows:
        for cx, cy in ((112, 15), (209, 112), (112, 209), (15, 112)):
            cl_crystal_window(img, cx, cy, vertical=(cx == 112))
    return img


def cl_deck(img, deck_r=58, vault_r=44):
    """Flat deck + recessed vault, sitting inside the vanilla nucleus rings."""
    d = ImageDraw.Draw(img)
    octo(img, 112, 112, deck_r + 4, EDGE)
    octo(img, 112, 112, deck_r, DARK)
    pts = octagon(112, 112, deck_r, DARK)
    for a, b in ((0, 1), (1, 2), (7, 0)):
        d.line([pts[a], pts[b]], fill=MID, width=2)
    # vault recess
    octo(img, 112, 112, vault_r, EDGE)
    octo(img, 112, 112, vault_r - 3, DARK)
    octo(img, 112, 112, vault_r - 6, EDGE)
    octo(img, 112, 112, vault_r - 10, DARK)
    pts = octagon(112, 112, vault_r - 3, MID)
    for a, b in ((0, 1), (1, 2), (7, 0)):
        d.line([pts[a], pts[b]], fill=MID)
    # deck clamps at the diagonals
    for ang in (45, 135, 225, 315):
        a = math.radians(ang)
        bx = int(112 + (deck_r + 1) * math.cos(a))
        by = int(112 + (deck_r + 1) * math.sin(a))
        bolt(img, bx, by, 3, face=MID)


def cl_dais(img, w=40):
    d = ImageDraw.Draw(img)
    d.rectangle([112 - w, 132, 112 + w, 146], fill=EDGE)
    d.rectangle([112 - w + 2, 133, 112 + w - 2, 145], fill=DARK)
    d.line([112 - w + 2, 133, 112 + w - 2, 133], fill=MID)
    d.rectangle([112 - 12, 144, 112 + 12, 150], fill=EDGE)
    d.rectangle([112 - 10, 145, 112 + 10, 149], fill=C_DEEP)
    d.line([112 - 10, 145, 112 + 10, 145], fill=C_DARK)


def cl_trinity():
    """A - Trinity Cluster: three shards on an octagonal dais."""
    img = cl_base()
    cl_deck(img)
    cl_dais(img)
    shard(img, 90, 136, 7, 34, lean=-2)
    gold_shard(img, 134, 136, 7, 36, lean=2)
    shard(img, 112, 144, 9, 56)
    # corner inlays on the vault floor
    for dx, dy in ((-34, -34), (34, -34), (-34, 34), (34, 34)):
        shard(img, 112 + dx, 112 + dy + 7, 4, 13)
    return img


def cl_body_vents(img):
    """Raised service housings and structural gussets for a deeper Core Link chassis."""
    d = ImageDraw.Draw(img)

    def raised_panel(box, radius=4, face=DARK):
        x0, y0, x1, y1 = box
        d.rounded_rectangle((x0 + 1, y0 + 4, x1 + 1, y1 + 4),
                            radius=radius, fill=EDGE)
        d.rounded_rectangle(box, radius=radius, fill=EDGE)
        d.rounded_rectangle((x0 + 2, y0 + 2, x1 - 2, y1 - 2),
                            radius=max(1, radius - 1), fill=face)
        d.line((x0 + radius, y0 + 2, x1 - radius, y0 + 2), fill=LIGHT, width=2)
        d.line((x0 + 2, y0 + radius, x0 + 2, y1 - radius), fill=LIGHT, width=2)
        d.line((x0 + radius, y1 - 2, x1 - radius, y1 - 2), fill=EDGE, width=3)
        d.line((x1 - 2, y0 + radius, x1 - 2, y1 - radius), fill=EDGE, width=3)
        d.line((x0 + radius + 2, y0 + 4, x1 - radius - 2, y0 + 4),
               fill=MID, width=1)

    def grille(box, vertical=False, count=10):
        x0, y0, x1, y1 = box
        d.rounded_rectangle(box, radius=1, fill=EDGE, outline=EDGE, width=2)
        if vertical:
            step = max(3, (y1 - y0) // count)
            for yy in range(y0 + 3, y1 - 2, step):
                d.line((x0 + 3, yy, x1 - 3, yy), fill=EDGE, width=2)
                d.line((x0 + 3, yy - 1, x1 - 3, yy - 1), fill=MID, width=1)
        else:
            step = max(3, (x1 - x0) // count)
            for xx in range(x0 + 3, x1 - 2, step):
                d.line((xx, y0 + 3, xx, y1 - 3), fill=EDGE, width=2)
                d.line((xx - 1, y0 + 3, xx - 1, y1 - 3), fill=MID, width=1)
        d.line((x0 + 3, y0 + 3, x1 - 3, y0 + 3), fill=DARK, width=1)

    # Raised cooling / service housings with visible lower sidewalls.
    raised_panel((64, 31, 160, 55), face=MID)
    raised_panel((64, 169, 160, 193), face=DARK)
    raised_panel((31, 64, 55, 160), face=MID)
    raised_panel((169, 64, 193, 160), face=DARK)
    grille((77, 38, 147, 49), vertical=False)
    grille((77, 175, 147, 186), vertical=False)
    grille((38, 77, 49, 147), vertical=True)
    grille((175, 77, 186, 147), vertical=True)

    # Crystal-powered status lamps set into the ends of each housing.
    for cx, cy in ((69, 43), (155, 43), (69, 181), (155, 181),
                   (43, 69), (43, 155), (181, 69), (181, 155)):
        d.rectangle((cx - 3, cy - 3, cx + 3, cy + 3), fill=EDGE)
        d.rectangle((cx - 1, cy - 1, cx + 1, cy + 1), fill=C_DEEP)
        d.point((cx - 1, cy - 1), fill=C_MID)

    # Four thick diagonal load-bearing gussets; cast shadows make them read
    # as raised members rather than flat surface markings.
    gussets = [
        [(34, 45), (45, 34), (83, 72), (72, 83)],
        [(178, 34), (189, 45), (151, 83), (140, 72)],
        [(34, 179), (45, 190), (83, 152), (72, 141)],
        [(178, 190), (189, 179), (151, 141), (140, 152)],
    ]
    for pts in gussets:
        d.polygon([(x + 1, y + 5) for x, y in pts], fill=EDGE)
        d.polygon(pts, fill=EDGE)
        inner = [(round(0.78 * x + 0.22 * 112),
                  round(0.78 * y + 0.22 * 112)) for x, y in pts]
        d.polygon(inner, fill=MID)
        d.line([pts[0], pts[1]], fill=LIGHT, width=2)
        d.line([pts[0], pts[3]], fill=DARK, width=1)
        ax, ay = pts[0]
        d.rectangle((ax - 2, ay - 2, ax + 2, ay + 2), fill=EDGE)
        d.point((ax - 1, ay - 1), fill=LIGHT)

    # Thick lower / right chassis skirt to establish the building's body depth.
    d.polygon([(28, 188), (196, 188), (188, 202), (36, 202)], fill=EDGE)
    d.line((37, 197, 187, 197), fill=DARK, width=3)
    d.line((43, 191, 181, 191), fill=MID, width=2)
    d.polygon([(188, 28), (202, 36), (202, 188), (188, 196)], fill=EDGE)
    d.line((197, 42, 197, 183), fill=DARK, width=3)
    d.line((191, 45, 191, 179), fill=MID, width=2)

    # Gold fasteners anchor the new armor to the underlying platform.
    for cx, cy in ((59, 59), (165, 59), (59, 165), (165, 165),
                   (112, 28), (112, 196), (28, 112), (196, 112)):
        d.rectangle((cx - 3, cy - 3, cx + 3, cy + 3), fill=EDGE)
        d.rectangle((cx - 1, cy - 1, cx + 1, cy + 1), fill=A_MID)
        d.point((cx - 1, cy - 1), fill=LIGHT)


def cl_prism():
    """B - Prism Heart: faceted gem in a reinforced vault with detailed service apron."""
    img = cl_base()
    cl_deck(img)
    cl_body_vents(img)
    d = ImageDraw.Draw(img)
    for rr, col in ((36, EDGE), (33, DARK), (30, EDGE), (27, DARK)):
        d.ellipse([112 - rr, 112 - rr, 112 + rr, 112 + rr], fill=col)
    d.arc([112 - 33, 112 - 33, 112 + 33, 112 + 33], 180, 270, fill=MID, width=2)
    # teal outer gem
    pts = [(112, 76), (130, 108), (122, 138), (112, 146), (102, 138), (94, 108)]
    d.polygon(pts, fill=C_MID)
    d.polygon([(112, 76), (94, 108), (102, 138), (112, 146)], fill=C_HI)
    d.polygon([(112, 76), (112, 146), (122, 138), (130, 108)], fill=C_DARK)
    d.line(pts + [pts[0]], fill=C_DEEP)
    d.line([(112, 76), (112, 146)], fill=C_DEEP)
    d.line([(94, 108), (130, 108)], fill=C_DEEP)
    # gold inner facet
    d.polygon([(112, 92), (124, 110), (112, 132), (100, 110)], fill=A_MID)
    d.polygon([(112, 92), (100, 110), (112, 132)], fill=A_HOT)
    d.line([(112, 92), (124, 110), (112, 132), (100, 110), (112, 92)], fill=A_DEEP)
    d.line([(112, 92), (112, 132)], fill=A_DEEP)
    # socket studs
    for ang in range(0, 360, 45):
        a = math.radians(ang)
        sx = int(112 + 40 * math.cos(a))
        sy = int(112 + 40 * math.sin(a))
        bolt(img, sx, sy, 2, face=MID)
    return img


def cl_ring():
    """C - Crystal Ring: alternating shards orbiting a bright core."""
    img = cl_base()
    cl_deck(img)
    d = ImageDraw.Draw(img)
    d.ellipse([112 - 29, 112 - 29, 112 + 29, 112 + 29], fill=EDGE)
    d.ellipse([112 - 26, 112 - 26, 112 + 26, 112 + 26], fill=DARK)
    d.arc([112 - 26, 112 - 26, 112 + 26, 112 + 26], 180, 270, fill=MID, width=2)
    d.ellipse([112 - 12, 112 - 12, 112 + 12, 112 + 12], fill=C_DEEP)
    d.ellipse([112 - 8, 112 - 8, 112 + 8, 112 + 8], fill=C_DARK)
    d.ellipse([112 - 4, 112 - 4, 112 + 4, 112 + 4], fill=C_HI)
    for i, ang in enumerate(range(0, 360, 60)):
        a = math.radians(ang)
        sx = int(112 + 37 * math.cos(a))
        sy = int(112 + 37 * math.sin(a))
        if i % 3 == 1:
            gold_shard(img, sx, sy + 9, 5, 24)
        else:
            shard(img, sx, sy + 9, 5, 24)
    return img


def cl_nexus():
    """D - Nexus Cross: four crystal arms around a central lens."""
    img = cl_base()
    cl_deck(img)
    d = ImageDraw.Draw(img)
    d.rectangle([104, 74, 121, 153], fill=EDGE)
    d.rectangle([74, 104, 153, 121], fill=EDGE)
    d.rectangle([106, 76, 119, 151], fill=DARK)
    d.rectangle([76, 106, 151, 119], fill=DARK)
    d.line([106, 76, 119, 76], fill=MID)
    d.line([76, 106, 76, 119], fill=MID)
    shard(img, 112, 88, 7, 22)
    gold_shard(img, 112, 150, 7, 22)
    shard(img, 88, 128, 7, 22)
    shard(img, 136, 128, 7, 22)
    d.ellipse([112 - 18, 112 - 18, 112 + 18, 112 + 18], fill=EDGE)
    d.ellipse([112 - 15, 112 - 15, 112 + 15, 112 + 15], fill=C_DEEP)
    d.ellipse([112 - 10, 112 - 10, 112 + 10, 112 + 10], fill=C_DARK)
    d.ellipse([112 - 4, 112 - 4, 112 + 4, 112 + 4], fill=C_HI)
    return img


def cl_vault_door():
    """E - Vault Door: armoured hatch with a crystal key and corner windows."""
    img = cl_base(with_windows=False)
    cl_deck(img, vault_r=51)
    d = ImageDraw.Draw(img)
    panel(img, (85, 85, 140, 140), radius=6, face=DARK, hi=MID, lo=EDGE)
    d.rectangle([94, 94, 131, 131], fill=EDGE)
    d.rectangle([97, 97, 128, 128], fill=DARK)
    d.line([97, 97, 128, 97], fill=MID, width=2)
    d.line([97, 97, 97, 128], fill=MID, width=2)
    for cx, cy in ((98, 98), (127, 98), (98, 127), (127, 127)):
        d.rectangle([cx - 5, cy - 5, cx + 5, cy + 5], fill=EDGE)
        d.rectangle([cx - 3, cy - 3, cx + 3, cy + 3], fill=C_DEEP)
        d.rectangle([cx - 2, cy - 2, cx + 2, cy + 2], fill=C_MID)
        d.point([cx - 2, cy - 2], fill=C_HI)
    shard(img, 112, 127, 9, 36)
    gold_shard(img, 100, 129, 5, 18, lean=-1)
    shard(img, 124, 129, 5, 18, lean=1)
    for ang in (45, 135, 225, 315):
        a = math.radians(ang)
        bx = int(112 + 31 * math.cos(a))
        by = int(112 + 31 * math.sin(a))
        bolt(img, bx, by, 2, face=MID)
    return img


# ---------------------------------------------------------------------------
# contact sheets / audit
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
    ("A", "Beam Press", bb_beam_press),
    ("B", "Twin Bore", bb_twin_bore),
    ("C", "Cyclotron", bb_cyclotron),
    ("D", "Anvil Press", bb_press),
    ("E", "Crossfire", bb_crossfire),
]

CL_DESIGNS = [
    ("A", "Trinity Cluster", cl_trinity),
    ("B", "Prism Heart", cl_prism),
    ("C", "Crystal Ring", cl_ring),
    ("D", "Nexus Cross", cl_nexus),
    ("E", "Vault Door", cl_vault_door),
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


ASCII_MAP = {
    EDGE: " ", DARK: ".", MID: ":", LIGHT: "#",
    C_DEEP: "c", C_DARK: "C", C_MID: "m", C_HI: "H",
    A_DEEP: "a", A_MID: "A", A_HOT: "g", A_WHITE: "W",
}


def dump_ascii(name, img, step=2):
    px = img.load()
    print(f"--- {name} ascii (1 char = {step}px) ---")
    for y in range(0, img.height, step):
        line = ""
        for x in range(0, img.width, step):
            r, g, b, a = px[x, y]
            line += "`" if a == 0 else ASCII_MAP.get((r, g, b), "?")
        print(line)
    print()


def main():
    os.makedirs(DOCS, exist_ok=True)
    os.makedirs(SPRITES, exist_ok=True)
    ok = True

    built = {}
    for letter, label, factory in BB_DESIGNS:
        img = factory()
        ok &= audit(f"bb-{letter}", img)
        img.save(os.path.join(DOCS, f"bb-collider-{letter.lower()}.png"))
        built[("bb-collider", letter)] = img

    for letter, label, factory in CL_DESIGNS:
        img = factory()
        ok &= audit(f"cl-{letter}", img)
        img.save(os.path.join(DOCS, f"core-link-{letter.lower()}.png"))
        built[("core-link", letter)] = img

    for name, letter in CHOSEN.items():
        img = built[(name, letter)]
        img.save(os.path.join(SPRITES, name + ".png"))
        print(f"installed sprites/{name}.png <- design {letter}")

    bb_items = [(l, n, built[("bb-collider", l)]) for l, n, _ in BB_DESIGNS]
    cl_items = [(l, n, built[("core-link", l)]) for l, n, _ in CL_DESIGNS]

    contact_sheet(
        "B.B Collider - vanilla-derived candidates",
        "5x5  /  Core: Nucleus shell in Distributor grey  /  industrial accelerator housing, no crystal",
        bb_items,
        os.path.join(DOCS, "bb-collider-designs.png"),
        scale=2,
        gap=20,
    )
    contact_sheet(
        "Core Link - vanilla-derived candidates",
        "7x7  /  Distributor platform + Nexus core module  /  Bayugo crystal vault",
        cl_items,
        os.path.join(DOCS, "core-link-designs.png"),
        scale=1,
        gap=20,
    )

    if "--ascii" in sys.argv:
        for letter in ("A", "B", "C", "D", "E"):
            dump_ascii(f"bb-{letter}", built[("bb-collider", letter)])
        for letter in ("A", "B", "C", "D", "E"):
            dump_ascii(f"cl-{letter}", built[("core-link", letter)])

    print("palette clean" if ok else "PALETTE / COVERAGE PROBLEM")


if __name__ == "__main__":
    main()
