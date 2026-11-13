# Mass Driver Tiers

A small Mindustry mod that adds two late-game upgrades to the vanilla mass driver:
a **Thorium Mass Driver** and a **Surge Mass Driver**, plus Bayugo Crystals, the
B.B Collider factory, and the Core Vault storage building. The mass-driver art is
preserved in this release; the other three sprites have been refreshed.

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
| Craft time | 900 ticks (15 seconds) |

## The B.B Collider

A massive 5×5 particle collider that synthesizes Bayugo Crystals. Late-game only,
high power draw, expensive to build.

| Property | Value |
| --- | --- |
| Size | 5×5 |
| Health | 2500 |
| Category | Production |
| Craft time | 900 ticks (15 seconds) |
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
inventory. Place it directly adjacent to a core to merge its inventory with the core and
increase the shared per-item capacity by 20,000. Away from a core, it functions as
independent high-capacity storage. Extremely expensive, late-game strategic
building.

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

The Core Vault uses Mindustry's built-in `StorageBlock` core-merging behavior
(`coreMerge: true`). It shares the core's item inventory only when placed directly
adjacent to that core; a distant vault remains a separate storage building.
Its 20,000 item capacity is added to the connected core's shared capacity.


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
mod `1.2.00.1` ↔ GitHub tag/release `v1.2.00.1`. For example: a new feature bumps
the second number (`1.2.00.0`), a balance pass bumps the third (`1.2.01.0`), and a
bugfix bumps the last (`1.2.01.1`).

## How the sprites are made

The Thorium and Surge mass-driver sprites are based on the vanilla Mass Driver
assets in `tools/vanilla/` (GPLv3). Their existing checked-in PNGs are preserved
in this release, and the default generator command will not overwrite them.

The B.B Collider, Core Vault and Bayugo Crystal have refreshed, original pixel-art
sprites. Their concept sheet lives in `tools/source-art/`; the generator crops the
three isolated designs, scales them to Mindustry's native resolution, limits the
palette without dithering, and saves transparent 32-bit RGBA PNGs.

Install the small image dependency, regenerate the refreshed sprites, then run
static validation:

```sh
py -3 -m pip install -r requirements.txt
py -3 tools/generate_grey_sprites.py
py -3 tools/validate_mod.py
```

This writes:

- `sprites/b-b-collider.png` (160×160, 5×5 block)
- `sprites/core-vault.png` (224×224, 7×7 block)
- `sprites/bayugo-crystal.png` (32×32, item)
- `docs/preview.png` (sprite comparison sheet; mass-driver art is read only)

The mass-driver generator is deliberately opt-in. Use this command only when you
intentionally want to regenerate the two mass-driver sprite pairs:

```sh
py -3 tools/generate_sprites.py --regenerate-mass-drivers
```

Mindustry uses the content filename as the sprite name. Standard blocks use one
full-size sprite (`<name>.png`); Mass Drivers additionally load a static base
region (`<name>-base.png`) underneath their rotating turret region. The old
`-base` images for the B.B Collider and Core Vault were not used by their standard
block classes, so those redundant images have been removed.

> **Asset credit / license:** the vanilla mass-driver sprite is part of
> [Mindustry](https://github.com/Anuken/Mindustry) by Anuken and contributors. The
> Thorium and Surge tier sprites are derivative works of that asset. This mod is
> distributed under the **GPLv3**; the refreshed Collider, Vault and Crystal artwork
> is original artwork.

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

## Validation

Run `py -3 tools/validate_mod.py` to check JSON syntax, item fields, content
references, per-craft item capacity, recipe liquid totals, sprite dimensions and
32-bit RGBA formats. These are static checks; launch the mod in Mindustry before
publishing.

## Notes

- Balance is tuned as an endgame tier above the vanilla driver; edit the JSON files
  in `content/blocks/` to change stats or costs.
- `"name"` and `"description"` are set inline in each block JSON, so display names
  and descriptions are added to the bundle at load time without a separate
  `bundles/` file.
