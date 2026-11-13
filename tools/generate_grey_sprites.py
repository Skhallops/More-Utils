"""
Sprite generator for Bayugo Crystals content.
Grey-themed industrial sprites, ~60% vanilla-like silhouette, 40% custom grey detailing.
Palette: steel greys with blue-grey accents.
"""

import os
from PIL import Image, ImageDraw

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SPRITES = os.path.join(ROOT, "sprites")

# Grey theme palette
GREY = {
    "L": (190, 195, 200),      # light steel
    "M": (150, 155, 160),      # mid steel
    "D": (100, 105, 110),      # dark steel
    "O": (120, 140, 160),      # blue-grey accent
    "G": (160, 180, 200),      # pale blue-grey
    "A": (200, 210, 220),      # amber/grey shade
    "outline": (55, 60, 68),   # dark outline
    "glint": (230, 235, 240),  # bright glint
    "shade": (140, 150, 160),  # mid shade
    "core": (240, 245, 250),   # core white-grey
}

def rect(draw, x0, y0, x1, y1, fill):
    draw.rectangle([x0, y0, x1, y1], fill=fill)

def crystal_shape(draw, cx, cy, h, pal, tip_color=None):
    """Draw a vertical crystal shard."""
    tip = tip_color or pal["O"]
    w = h // 3
    # shard body
    rect(draw, cx - w // 2, cy - h, cx + w // 2, cy, pal["M"])
    rect(draw, cx - w // 3, cy - h, cx + w // 3, cy - h // 2, pal["L"])
    # tip
    rect(draw, cx - 1, cy - h, cx + 1, cy - h + 3, tip)
    # facets
    rect(draw, cx - w // 2, cy - h // 2, cx - w // 4, cy, pal["D"])
    rect(draw, cx + w // 4, cy - h // 2, cx + w // 2, cy, pal["L"])

def block_base(draw, size, pal, center_dot=True):
    """Draw a vanilla-like block base: dark platform with lighter rim."""
    m = size // 2
    # base plate
    rect(draw, 2, size - 6, size - 3, size - 3, pal["D"])
    rect(draw, 3, size - 5, size - 4, size - 4, pal["M"])
    # central pillar
    rect(draw, m - 2, size - 10, m + 2, size - 3, pal["O"])
    if center_dot:
        rect(draw, m - 1, size - 9, m + 1, size - 7, pal["glint"])

def collider_ring(draw, size, pal):
    """Draw a collider accelerator ring around the center."""
    m = size // 2
    r = size // 3
    # outer ring
    for i in range(3):
        rect(draw, m - r + i, m - r + i, m + r - i, m + r - i, pal["outline"])
    rect(draw, m - r + 3, m - r + 3, m + r - 4, m + r - 4, pal["M"])
    # inner ring
    r2 = size // 6
    rect(draw, m - r2, m - r2, m + r2, m + r2, pal["O"])
    rect(draw, m - r2 + 1, m - r2 + 1, m + r2 - 1, m + r2 - 1, pal["G"])

def vault_structure(draw, size, pal):
    """Draw a vault with storage tanks/silos."""
    m = size // 2
    # outer walls
    rect(draw, 4, 4, size - 5, size - 5, pal["D"])
    rect(draw, 6, 6, size - 7, size - 7, pal["M"])
    # central silo cluster
    silo_w = size // 5
    for i in range(3):
        x = m - silo_w + i * (silo_w // 2)
        rect(draw, x, 10, x + silo_w, size - 10, pal["O"])
        rect(draw, x + 1, 11, x + silo_w - 1, size - 11, pal["G"])

def save_sprite(img, name):
    path = os.path.join(SPRITES, name + ".png")
    img.save(path)
    print(f"wrote {path} ({img.width}x{img.height})")

def main():
    os.makedirs(SPRITES, exist_ok=True)

    # ---- Item: Bayugo Crystal (32x32) ----
    img = Image.new("RGBA", (32, 32), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    crystal_shape(d, 16, 22, 14, GREY, tip_color=GREY["O"])
    rect(d, 15, 20, 17, 24, GREY["outline"])
    save_sprite(img, "bayugo-crystal")

    # ---- B.B Collider (5x5 = 160x160) ----
    size = 160
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    block_base(d, size, GREY)
    collider_ring(d, size, GREY)
    # accelerator spines
    m = size // 2
    for dx, dy in ((-40, 0), (40, 0), (0, -40), (0, 40)):
        rect(d, m + dx - 2, m + dy - 14, m + dx + 2, m + dy + 14, GREY["D"])
        rect(d, m + dx - 1, m + dy - 12, m + dx + 1, m + dy + 12, GREY["O"])
    save_sprite(img, "b-b-collider")

    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    block_base(d, size, GREY, center_dot=False)
    m = size // 2
    # base power conduits
    rect(d, m - 30, 4, m + 30, 12, GREY["M"])
    rect(d, m - 30, size - 16, m + 30, size - 8, GREY["M"])
    rect(d, 4, m - 30, 12, m + 30, GREY["M"])
    rect(d, size - 16, m - 30, size - 8, m + 30, GREY["M"])
    rect(d, m - 2, m - 2, m + 2, m + 2, GREY["O"])
    rect(d, m - 1, m - 1, m + 1, m + 1, GREY["glint"])
    save_sprite(img, "b-b-collider-base")

    # ---- Core Vault (7x7 = 224x224) ----
    size = 224
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    block_base(d, size, GREY)
    vault_structure(d, size, GREY)
    m = size // 2
    rect(d, m - 3, m - 3, m + 3, m + 3, GREY["O"])
    rect(d, m - 1, m - 1, m + 1, m + 1, GREY["core"])
    save_sprite(img, "core-vault")

    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    block_base(d, size, GREY, center_dot=False)
    m = size // 2
    # base heavy plating
    rect(d, m - 40, 4, m + 40, 14, GREY["M"])
    rect(d, m - 40, size - 18, m + 40, size - 8, GREY["M"])
    rect(d, 4, m - 40, 14, m + 40, GREY["M"])
    rect(d, size - 18, m - 40, size - 8, m + 40, GREY["M"])
    rect(d, m - 4, m - 4, m + 4, m + 4, GREY["O"])
    rect(d, m - 2, m - 2, m + 2, m + 2, GREY["core"])
    save_sprite(img, "core-vault-base")


if __name__ == "__main__":
    main()
