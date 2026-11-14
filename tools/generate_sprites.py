"""
Sprite generator for the More-Utils mod.

The two new drivers are built directly from Mindustry's vanilla mass driver
sprite (tools/vanilla/mass-driver.png, GPLv3), so their silhouette, pixel
density and shading language match the base game exactly. Each variant then
gets a full palette remap plus hand-placed tier detailing:

  * Thorium Mass Driver  - warm mauve steel, rose + thorium-pink accents,
                           muzzle accelerator collar, glowing charge rails,
                           pink emitter core and rear prong tip.
  * Surge Mass Driver    - blue steel, cyan + surge-yellow accents,
                           three accelerator collars, cyan energy spine,
                           cyan emitter core and prong tips.

New blocks should follow the same pipeline: derive the sprite from the matching
vanilla asset, remap the palette, then add hand-placed tier detailing. This keeps
every addition visually consistent with the base game.

Usage:  py -3 tools/generate_sprites.py
"""

import math
import os

from PIL import Image, ImageDraw, ImageFilter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VANILLA = os.path.join(ROOT, "tools", "vanilla")
SPRITES = os.path.join(ROOT, "sprites")
DOCS = os.path.join(ROOT, "docs")

# ----------------------------------------------------------------------------
# vanilla source palette (exact RGB values used by the vanilla sprite)
# L=light, M=mid, D=dark, O=orange accent, G=gold accent, A=amber shade
# ----------------------------------------------------------------------------

VANILLA_KEYS = [
    ("L", (176, 186, 192)),
    ("M", (152, 154, 164)),
    ("D", (110, 112, 128)),
    ("O", (212, 129, 107)),
    ("G", (255, 211, 127)),
    ("A", (234, 182, 120)),
]

THORIUM = {
    "L": (198, 184, 194),
    "M": (164, 148, 160),
    "D": (108, 90, 104),
    "O": (176, 74, 120),
    "G": (249, 163, 199),
    "A": (255, 201, 223),
    "outline": (46, 31, 41),
    "glint": (255, 217, 234),
    "shade": (184, 94, 138),
    "core": (255, 240, 247),
}

SURGE = {
    "L": (186, 202, 219),
    "M": (150, 169, 189),
    "D": (92, 112, 134),
    "O": (47, 143, 180),
    "G": (243, 233, 121),
    "A": (191, 238, 251),
    "outline": (24, 38, 53),
    "glint": (253, 247, 192),
    "shade": (179, 159, 63),
    "core": (223, 246, 255),
    "arc": (128, 214, 255),
    "arc_dark": (46, 122, 158),
    "arc_hi": (232, 251, 255),
}

# sprite pixel sizes: 32 px per block tile
THORIUM_SIZE = 96   # 3x3
SURGE_SIZE = 160    # 5x5
# surge detail coordinates were designed at this resolution and are scaled from it
SURGE_DESIGN = 128


# ----------------------------------------------------------------------------
# helpers
# ----------------------------------------------------------------------------

def load_vanilla(name):
    return Image.open(os.path.join(VANILLA, name + ".png")).convert("RGBA")


def remap(img, pal, size=None, alpha_cut=110):
    """Re-color a vanilla sprite onto a variant palette.

    Every pixel is snapped to its nearest vanilla palette entry and then to the
    variant's color for that entry, keeping the hard-edged pixel-art look.
    Optionally resamples first (used for the larger surge sprites).
    """
    if size is not None and img.width != size:
        img = img.resize((size, size), Image.LANCZOS)

    out = Image.new("RGBA", img.size, (0, 0, 0, 0))
    src = img.load()
    dst = out.load()
    keys = [(name, col) for name, col in VANILLA_KEYS]

    for y in range(img.height):
        for x in range(img.width):
            r, g, b, a = src[x, y]
            if a < alpha_cut:
                continue
            name = min(
                keys,
                key=lambda kv: (kv[1][0] - r) ** 2 + (kv[1][1] - g) ** 2 + (kv[1][2] - b) ** 2,
            )[0]
            dst[x, y] = pal[name] + (255,)
    return out


def band(img, x0, x1, y0, h, pal, accent_key="G", seams=8, bolts=True):
    """Horizontal armor collar / accelerator ring with flat pixel shading."""
    d = ImageDraw.Draw(img)
    base = pal[accent_key]
    light = pal["glint"]
    dark = pal["shade"]

    # row stack: outline, light, bright body, dark shade, outline
    rows = [pal["outline"], light] + [base] * max(1, h - 4) + [dark, pal["outline"]]
    rows = rows[:h]
    for i, col in enumerate(rows):
        d.line([x0, y0 + i, x1, y0 + i], fill=col)

    # rib seams through the bright rows
    if seams:
        for x in range(x0 + seams, x1 - 2, seams):
            d.line([x, y0 + 2, x, y0 + h - 3], fill=dark)
    # rivets
    if bolts:
        for x in (x0 + 3, x1 - 4):
            d.rectangle([x, y0 + 3, x + 1, y0 + 4], fill=dark)
            d.point([x, y0 + 3], fill=light)


def rail(img, x, y0, y1, pal, on=3, off=4, width=1, color=None, edge=None):
    """Dashed glowing conduit line (vertical)."""
    d = ImageDraw.Draw(img)
    col = color or pal["G"]
    dk = edge or pal["shade"]
    y = y0
    while y <= y1:
        yy = min(y + on - 1, y1)
        d.rectangle([x - 1, y, x - 1, yy], fill=dk)
        d.rectangle([x, y, x + width - 1, yy], fill=col)
        d.rectangle([x + width, y, x + width, yy], fill=dk)
        y += on + off


def core(img, x0, y0, x1, y1, pal, inset=2):
    """Bright emitter core with a dark rim."""
    d = ImageDraw.Draw(img)
    d.rectangle([x0 - 1, y0 - 1, x1 + 1, y1 + 1], fill=pal["outline"])
    d.rectangle([x0, y0, x1, y1], fill=pal["G"])
    d.rectangle([x0 + inset, y0 + 1, x1 - inset, max(y0 + 1, y1 - 1)], fill=pal["core"])


# ----------------------------------------------------------------------------
# variants
# ----------------------------------------------------------------------------

def thorium_turret(size=THORIUM_SIZE):
    img = remap(load_vanilla("mass-driver"), THORIUM, size=size)
    # charge rails running down both sides of the barrel
    rail(img, 40, 18, 31, THORIUM, on=3, off=4, width=1)
    rail(img, 56, 18, 31, THORIUM, on=3, off=4, width=1)
    # accelerator collar just below the muzzle
    band(img, 35, 60, 10, 7, THORIUM, "G", seams=7)
    # emitter core between the twin muzzle rails
    core(img, 44, 6, 51, 9, THORIUM)
    # rear prong tip
    core(img, 45, 88, 50, 91, THORIUM, inset=1)
    return img


def thorium_base(size=THORIUM_SIZE):
    img = remap(load_vanilla("mass-driver-base"), THORIUM, size=size)
    d = ImageDraw.Draw(img)
    for (x0, y0, x1, y1) in ((46, 2, 49, 5), (46, 90, 49, 93)):
        d.rectangle([x0 - 1, y0 - 1, x1 + 1, y1 + 1], fill=THORIUM["outline"])
        d.rectangle([x0, y0, x1, y1], fill=THORIUM["G"])
        d.rectangle([x0 + 1, y0 + 1, x1 - 1, y1 - 1], fill=THORIUM["core"])
    return img


def surge_turret(size=SURGE_SIZE):
    k = size / SURGE_DESIGN

    def s(v):
        return int(v * k + 0.5)

    img = remap(load_vanilla("mass-driver"), SURGE, size=size)
    # cyan energy spine down the barrel centre (collars are drawn over it)
    rail(img, s(62), s(22), s(112), SURGE, on=max(1, s(4)), off=max(1, s(5)),
         width=max(1, s(2)), color=SURGE["arc"], edge=SURGE["arc_dark"])
    # three accelerator collars, slightly wider than the barrel
    band(img, s(47), s(80), s(11), max(4, s(8)), SURGE, "G", seams=max(2, s(9)))
    band(img, s(48), s(79), s(30), max(4, s(8)), SURGE, "G", seams=max(2, s(9)))
    band(img, s(52), s(76), s(94), max(4, s(8)), SURGE, "G", seams=max(2, s(9)))
    # emitter core between the twin muzzle rails
    core(img, s(59), s(6), s(68), s(9), SURGE, inset=max(1, s(2)))
    # rear prong tip
    core(img, s(59), s(117), s(68), s(121), SURGE, inset=max(1, s(1)))
    return img


def surge_base(size=SURGE_SIZE):
    k = size / SURGE_DESIGN

    def s(v):
        return int(v * k + 0.5)

    img = remap(load_vanilla("mass-driver-base"), SURGE, size=size)
    d = ImageDraw.Draw(img)
    ticks = ((61, 3, 66, 6), (61, 121, 66, 124), (3, 61, 6, 66), (121, 61, 124, 66))
    for (x0, y0, x1, y1) in ticks:
        x0, y0, x1, y1 = s(x0), s(y0), s(x1), s(y1)
        d.rectangle([x0, y0, x1, y1], fill=SURGE["outline"])
        d.rectangle([x0 + 1, y0 + 1, x1 - 1, y1 - 1], fill=SURGE["G"])
        d.point([x0 + 1, y0 + 1], fill=SURGE["core"])
    return img


# ----------------------------------------------------------------------------
# icon + preview
# ----------------------------------------------------------------------------

def fit_sprite(tile, size, pal):
    """Downscale a composited sprite crisply onto the variant palette."""
    small = tile.resize((size, size), Image.LANCZOS)
    out = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    src = small.load()
    dst = out.load()
    keys = list(pal.items())
    for y in range(size):
        for x in range(size):
            r, g, b, a = src[x, y]
            if a < 90:
                continue
            col = min(
                (c for k, c in keys if len(c) == 3),
                key=lambda c: (c[0] - r) ** 2 + (c[1] - g) ** 2 + (c[2] - b) ** 2,
            )
            dst[x, y] = col + (255,)
    return out


def make_icon(size=128):
    plate = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(plate)
    d.rounded_rectangle([1, 1, size - 2, size - 2], radius=11, fill=(19, 23, 30, 255))
    d.rounded_rectangle([1, 1, size - 2, size - 2], radius=11, outline=(58, 68, 82, 255), width=2)
    d.rounded_rectangle([5, 5, size - 6, size - 6], radius=8, fill=(25, 30, 38, 255))
    # vertical sheen
    d.polygon([(5, 5), (size - 6, 5), (size - 6, 34), (5, 60)], fill=(30, 36, 46, 255))

    left = fit_sprite(Image.alpha_composite(thorium_base(), thorium_turret()), 50, THORIUM)
    right = fit_sprite(Image.alpha_composite(surge_base(), surge_turret()), 60, SURGE)
    plate.alpha_composite(left, (10, 40))
    plate.alpha_composite(right, (60, 30))

    d = ImageDraw.Draw(plate)
    d.rectangle([12, 105, 58, 109], fill=THORIUM["G"])
    d.rectangle([12, 105, 58, 106], fill=THORIUM["core"])
    d.rectangle([70, 105, 116, 109], fill=SURGE["G"])
    d.rectangle([70, 105, 116, 106], fill=SURGE["core"])
    d.rectangle([108, 105, 116, 109], fill=SURGE["O"])
    return plate


def make_preview(tiles, scale=2, pad=26, gap=26):
    tiles = [t.resize((t.width * scale, t.height * scale), Image.NEAREST) for t in tiles]

    w = pad * 2 + sum(t.width for t in tiles) + gap * (len(tiles) - 1)
    h = pad * 2 + max(t.height for t in tiles)
    out = Image.new("RGBA", (w, h), (24, 28, 36, 255))

    d = ImageDraw.Draw(out)
    cell = 16
    for y in range(0, h, cell):
        for x in range(0, w, cell):
            if (x // cell + y // cell) % 2 == 0:
                d.rectangle([x, y, x + cell - 1, y + cell - 1], fill=(28, 33, 42, 255))

    x = pad
    for t in tiles:
        out.alpha_composite(t, (x, pad + (h - pad * 2 - t.height) // 2))
        x += t.width + gap
    return out


# ----------------------------------------------------------------------------

def main():
    os.makedirs(SPRITES, exist_ok=True)
    os.makedirs(DOCS, exist_ok=True)

    jobs = [
        ("thorium-mass-driver", THORIUM_SIZE, THORIUM, thorium_turret, thorium_base),
        ("surge-mass-driver", SURGE_SIZE, SURGE, surge_turret, surge_base),
    ]

    for name, size, pal, turret, base in jobs:
        base(size).save(os.path.join(SPRITES, name + "-base.png"))
        turret(size).save(os.path.join(SPRITES, name + ".png"))
        print(f"wrote {name} ({size}x{size})")

    make_icon().save(os.path.join(ROOT, "icon.png"))
    print("wrote icon.png")

    # Banner preview: every block at the same 32px-per-tile scale so the
    # relative footprint of each building reads correctly.
    tiles = [
        Image.alpha_composite(base(size), turret(size))
        for _name, size, _pal, turret, base in jobs
    ]
    for extra in ("bb-collider", "core-link"):
        path = os.path.join(SPRITES, extra + ".png")
        if os.path.exists(path):
            with Image.open(path) as handle:
                tiles.append(handle.convert("RGBA"))
        else:
            print(f"skip preview tile {extra} (missing sprite)")

    make_preview(tiles).save(os.path.join(DOCS, "preview.png"))
    print("wrote docs/preview.png")


if __name__ == "__main__":
    main()
