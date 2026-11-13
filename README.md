# Mass Driver Tiers

A small Mindustry mod that adds two late-game upgrades to the vanilla mass driver:
a **Thorium Mass Driver** and a **Surge Mass Driver**, plus Bayugo Crystals, the
B.B Collider factory, and the Core Vault storage building.

![Preview](docs/preview.png)

## Blocks

| Block | Size | Health | Capacity | Range | Reload | Power | Research |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Mass Driver (vanilla) | 3×3 | 380 | 120 | 440 (55 tiles) | 200 | 1.75 | — |
| **Thorium Mass Driver** | 3×3 | 760 | 180 | 640 (80 tiles) | 150 | 3 | Mass Driver |
| **Surge Mass Driver** | 5×5 | 1850 | 520 | 1200 (150 tiles) | 110 | 10 | Thorium Mass Driver |

Both blocks are in the **Distribution** category and behave exactly like the vanilla
mass driver: they link to a matching driver, buffer items, and launch payloads when
powered. Range is measured in world units (8 units per tile).

### Firing effects

The launch and receive effects are configured per block in JSON, so each tier has
its own signature:

- **Thorium** — pink shockwave ring, rose spark streaks, a soft pink muzzle flash,
  and a lingering pink smoke puff. Launched shells leave a pink trail and glowing
  pink light.
- **Surge** — a wide cyan shockwave plus a delayed surge-yellow ring, cyan and
  yellow spark streaks, and a cyan smoke puff. Shells leave a yellow trail with a
  cyan glow.

Both tiers also use a stronger screen shake than vanilla (4 and 10 vs. 3) so the
larger drivers feel heavier when they fire.

## Bayugo Crystal

A volatile grey crystal synthesized in the B.B Collider from slag, cryofluid,
silicon, thorium and blast compound. Used in late-game core-linked storage.

| Property | Value |
| --- | --- |
| Color | Grey (`8a8a8a`) |
| Crafted at | The B.B Collider (5×5) |
| Ingredients | 120 slag, 80 silicon, 50 thorium, 40 blast-compound, 100 cryofluid |
| Craft time | 900 ticks |

## The B.B Collider

A massive 5×5 particle collider that synthesizes Bayugo Crystals. Late-game only,
high power draw, expensive to build.

| Property | Value |
| --- | --- |
| Size | 5×5 |
| Health | 2500 |
| Category | Production |
| Craft time | 900 ticks |
| Power | 20 |
| Research | Surge Mass Driver |

**Build cost:**

- 350 surge alloy
- 120 phase fabric
- 300 thorium
- 250 silicon
- 250 titanium
- 200 plastanium

**Craft recipe (per crystal):**

- 120 slag
- 80 silicon
- 50 thorium
- 40 blast-compound
- 100 cryofluid

## Core Vault

A colossal 7×7 storage vault engineered to interface directly with your core's
inventory. Place it anywhere and route belts straight into it - items flow to and
from core storage as if it were the core itself. Extremely expensive, late-game
strategic building.

| Property | Value |
| --- | --- |
| Size | 7×7 |
| Health | 9000 |
| Item capacity | 20000 |
| Category | Storage |
| Research | The B.B Collider |

**Build cost:**

- 250 Bayugo Crystals
- 600 surge alloy
- 250 phase fabric
- 500 thorium
- 400 plastanium
- 500 titanium

### Core inventory note

True shared-core-inventory behaviour requires custom game logic beyond pure JSON
content. This release ships the Core Vault as a high-capacity (20,000 item)
storage block you can place anywhere to decentralize your core's buffer. A Java
block class would be needed for literal core inventory sharing.


### Costs

**Thorium Mass Driver**

- 150 thorium
- 175 titanium
- 150 silicon
- 100 lead
- 300 copper

**Surge Mass Driver**

- 200 surge alloy
- 250 thorium
- 250 silicon
- 300 titanium
- 60 phase fabric
- 300 graphite

## Installation

1. Download or build the mod folder/zip.
2. In Mindustry, open **Mods → Import Mod** and select the `.zip`, or drop the
   folder into your mods directory:
   - Windows: `%APPDATA%\Mindustry\mods\`
   - Linux: `~/.local/share/Mindustry/mods/`
   - macOS: `~/Library/Application Support/Mindustry/mods/`
3. Restart the game or reload mods.

Requires **Mindustry v8 (build 160 or newer)**. The mod is data-only (JSON), so it
works on desktop and mobile, in singleplayer and on servers (the server needs the
mod installed too).

## Versioning

Releases use the four-part scheme `1.x.xx.x`:

- `1` — project generation (fixed)
- `x` — major content update (new blocks/features)
- `xx` — minor update, zero-padded (`00`–`99`)
- `x` — hotfix/patch

The in-game version in `mod.hjson` and the GitHub release tag must always match:
mod `1.2.00.0` ↔ GitHub tag/release `v1.2.00.0`. For example: a new feature bumps
the second number (`1.2.00.0`), a balance pass bumps the third (`1.2.01.0`), and a
bugfix bumps the last (`1.2.01.1`).

## How the sprites are made

The turret sprites are derived from Mindustry's own `mass-driver.png` (kept in
`tools/vanilla/`), so the silhouette, pixel density and shading match the vanilla
driver exactly. The generator snaps every pixel to the vanilla 5-color palette and
remaps it onto a tier palette, then adds the tier detailing:

- **Thorium** — mauve steel with rose plating and thorium-pink accents; a muzzle
  accelerator collar, dashed charge rails, a pink emitter core and a glowing rear
  prong tip.
- **Surge** — blue steel with cyan plating and surge-yellow accents; three
  accelerator collars, a cyan energy spine, a cyan/yellow emitter core and cyan
  edge ticks on the base. The 5×5 art is upscaled from the vanilla bitmap and
  re-quantized so it stays crisp pixel art.

Future blocks should follow the same pipeline: derive from the matching vanilla
asset, remap the palette, then add hand-placed tier detailing. This keeps every
addition visually consistent with the base game.

All sprites and the mod icon are generated with [Pillow](https://python-pillow.org/),
so they can be re-rendered after tweaking the palettes or geometry:

```sh
py -3 tools/generate_sprites.py
py -3 tools/generate_grey_sprites.py
```

This writes:

- `sprites/thorium-mass-driver.png` / `-base.png` (96×96, 3×3)
- `sprites/surge-mass-driver.png` / `-base.png` (160×160, 5×5)
- `sprites/bayugo-crystal.png` (32×32, item)
- `sprites/b-b-collider.png` / `-base.png` (160×160, 5×5)
- `sprites/core-vault.png` / `-base.png` (224×224, 7×7)
- `icon.png` (128×128)
- `docs/preview.png` (README preview sheet)

Mindustry auto-prefixes mod sprite names with the mod's internal name
(`mass-driver-tiers`), so the file names map directly to the block names.
Each mass driver needs two regions: the rotating turret (`<name>.png`) and the
static base (`<name>-base.png`).

> **Asset credit / license:** the vanilla mass driver sprite is part of
> [Mindustry](https://github.com/Anuken/Mindustry) by Anuken and contributors, which
> is licensed under the **GPLv3**. The tier sprites here are derivative works of
> that asset and are distributed under the same license.

## Packaging a release

Only these are needed at runtime:

```text
mod.hjson
icon.png
content/
sprites/
```

`tools/` (sprite generator) and `docs/` (preview) can be left out of the release
archive.

## Notes

- Balance is tuned as an endgame tier above the vanilla driver; edit the JSON files
  in `content/blocks/` to change stats or costs.
- `"name"` and `"description"` are set inline in each block JSON, so display names
  and descriptions are added to the bundle at load time without a separate
  `bundles/` file.
