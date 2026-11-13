"""Build the non-mass-driver sprites for the More Utils / Mass Driver Tiers mod.

The source concept sheet is intentionally kept in tools/source-art. This script
crops its three isolated pieces, fits them to Mindustry's native pixel sizes,
reduces the palette without dithering, and writes 32-bit RGBA PNGs.

Runtime sprite sizes follow Mindustry's 32 px per tile rule:
  * B.B Collider: 5x5 -> 160x160
  * Core Vault:   7x7 -> 224x224
  * Bayugo Crystal: item icon -> 32x32

Mass-driver sprites are deliberately not touched by this script.
"""

from __future__ import annotations

import os
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
SPRITES = ROOT / "sprites"
DOCS = ROOT / "docs"
SOURCE = ROOT / "tools" / "source-art" / "non-mass-driver-sprite-concepts.png"

# Connected visual bounds in the source concept atlas (left to right).
# Each crop contains one isolated, transparent sprite.
ASSETS = (
    {
        "name": "b-b-collider",
        "box": (88, 100, 632, 622),
        "size": (160, 160),
        "margin": 4,
        "colors": 64,
    },
    {
        "name": "core-vault",
        "box": (768, 14, 1432, 696),
        "size": (224, 224),
        "margin": 5,
        "colors": 72,
    },
    {
        "name": "bayugo-crystal",
        "box": (1626, 128, 2044, 627),
        "size": (32, 32),
        "margin": 2,
        "colors": 48,
    },
)

# Palette quantization is followed by a small warm-accent correction.

def render_asset(sheet: Image.Image, definition: dict) -> Image.Image:
    """Crop, scale, palette-limit and center one sprite at its native dimensions."""
    crop = sheet.crop(definition["box"])
    width, height = definition["size"]
    margin = int(definition["margin"])
    available = (width - 2 * margin, height - 2 * margin)
    scale = min(available[0] / crop.width, available[1] / crop.height)
    scaled_size = (
        max(1, round(crop.width * scale)),
        max(1, round(crop.height * scale)),
    )

    # Resize with high-quality filtering, then quantize RGB without dithering.
    # Keep alpha separately so the transparent silhouette remains clean.
    scaled = crop.resize(scaled_size, Image.Resampling.LANCZOS).convert("RGBA")
    alpha = scaled.getchannel("A")
    rgb_image = scaled.convert("RGB")
    quantized = rgb_image.quantize(
        colors=int(definition["colors"]),
        method=Image.Quantize.MEDIANCUT,
        dither=Image.Dither.NONE,
    ).convert("RGB")

    # Pillow-only palette adjustment; avoid making NumPy a build dependency.
    corrected_pixels = []
    quantized_pixels = quantized.load()
    alpha_pixels = alpha.load()
    for y in range(scaled_size[1]):
        for x in range(scaled_size[0]):
            red, green, blue = quantized_pixels[x, y]
            opacity = alpha_pixels[x, y]
            # Discard near-invisible fringe pixels from the AI-rendered source image.
            if opacity < 8:
                corrected_pixels.append((0, 0, 0, 0))
                continue
            brightness = (red + green + blue) / 3.0
            if red > 115 and (red - green) > 14 and (green - blue) > 16:
                if brightness >= 190:
                    red, green, blue = (255, 202, 93)
                elif brightness >= 140:
                    red, green, blue = (242, 151, 51)
                else:
                    red, green, blue = (174, 91, 38)
            corrected_pixels.append((red, green, blue, opacity))

    colored = Image.new("RGBA", scaled_size, (0, 0, 0, 0))
    colored.putdata(corrected_pixels)
    out = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    x = (width - scaled_size[0]) // 2
    y = (height - scaled_size[1]) // 2
    out.alpha_composite(colored, (x, y))
    return out


def checkerboard(size: tuple[int, int], cell: int = 8) -> Image.Image:
    image = Image.new("RGBA", size, (33, 38, 47, 255))
    draw = ImageDraw.Draw(image)
    for y in range(0, size[1], cell):
        for x in range(0, size[0], cell):
            if (x // cell + y // cell) % 2 == 0:
                draw.rectangle(
                    (x, y, min(x + cell - 1, size[0] - 1), min(y + cell - 1, size[1] - 1)),
                    fill=(43, 49, 59, 255),
                )
    return image


def load_font(size: int = 15):
    candidates = (
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/Library/Fonts/Arial Bold.ttf",
        "C:/Windows/Fonts/arialbd.ttf",
    )
    for candidate in candidates:
        if os.path.exists(candidate):
            try:
                return ImageFont.truetype(candidate, size)
            except OSError:
                pass
    return ImageFont.load_default()


def make_preview() -> Image.Image:
    """Create a README preview while compositing existing mass-driver art as-is."""
    entries: list[tuple[str, str, Image.Image]] = []

    # The two mass-driver pairs are loaded from disk and never regenerated here.
    for title, stem in (
        ("THORIUM MASS DRIVER", "thorium-mass-driver"),
        ("SURGE MASS DRIVER", "surge-mass-driver"),
    ):
        base = Image.open(SPRITES / f"{stem}-base.png").convert("RGBA")
        turret = Image.open(SPRITES / f"{stem}.png").convert("RGBA")
        if base.size != turret.size:
            raise ValueError(f"{stem} base/turret dimensions do not match")
        entries.append((title, f"{base.width} × {base.height}", Image.alpha_composite(base, turret)))

    for title, file, dims in (
        ("B.B COLLIDER", "b-b-collider.png", "5 × 5 tiles"),
        ("CORE VAULT", "core-vault.png", "7 × 7 tiles"),
        ("BAYUGO CRYSTAL", "bayugo-crystal.png", "item"),
    ):
        image = Image.open(SPRITES / file).convert("RGBA")
        entries.append((title, dims, image))

    cell_w, cell_h = 360, 330
    gap, pad = 24, 28
    rows, cols = 2, 3
    canvas = Image.new(
        "RGBA",
        (pad * 2 + cols * cell_w + (cols - 1) * gap,
         pad * 2 + rows * cell_h + (rows - 1) * gap),
        (20, 24, 31, 255),
    )
    draw = ImageDraw.Draw(canvas)
    title_font = load_font(15)
    info_font = load_font(12)

    for index, (title, subtitle, sprite) in enumerate(entries):
        col, row = index % cols, index // cols
        x = pad + col * (cell_w + gap)
        y = pad + row * (cell_h + gap)
        draw.rounded_rectangle((x, y, x + cell_w, y + cell_h), radius=12,
                               fill=(27, 33, 43, 255), outline=(57, 69, 86, 255), width=2)
        draw.text((x + 16, y + 13), title, font=title_font, fill=(223, 232, 244, 255))
        draw.text((x + 16, y + 35), subtitle, font=info_font, fill=(143, 164, 187, 255))

        art_area = (cell_w - 36, cell_h - 90)
        scale = min(art_area[0] / sprite.width, art_area[1] / sprite.height)
        preview_size = (max(1, round(sprite.width * scale)), max(1, round(sprite.height * scale)))
        sprite_preview = sprite.resize(preview_size, Image.Resampling.NEAREST)
        bg = checkerboard(preview_size, cell=12)
        bg.alpha_composite(sprite_preview)
        canvas.alpha_composite(bg, (x + (cell_w - preview_size[0]) // 2,
                                    y + 70 + (art_area[1] - preview_size[1]) // 2))
    return canvas.convert("RGB")


def main() -> None:
    if not SOURCE.is_file():
        raise FileNotFoundError(f"Missing source concept sheet: {SOURCE}")
    SPRITES.mkdir(parents=True, exist_ok=True)
    DOCS.mkdir(parents=True, exist_ok=True)
    sheet = Image.open(SOURCE).convert("RGBA")
    if sheet.size != (2172, 724):
        raise ValueError(
            f"Unexpected source sheet dimensions {sheet.size}; expected 2172x724. "
            "Update the crop bounds if you replace the source art."
        )

    for definition in ASSETS:
        sprite = render_asset(sheet, definition)
        destination = SPRITES / f"{definition['name']}.png"
        sprite.save(destination, format="PNG", optimize=True)
        print(f"wrote {destination.relative_to(ROOT)} ({sprite.width}x{sprite.height}, RGBA)")

    preview = make_preview()
    preview.save(DOCS / "preview.png", format="PNG", optimize=True)
    print("wrote docs/preview.png")
    print("Mass-driver sprites were read for the preview only; no mass-driver files were changed.")


if __name__ == "__main__":
    main()
