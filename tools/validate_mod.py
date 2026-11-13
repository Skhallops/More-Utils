"""Static validation for the JSON release of More Utils / Mass Driver Tiers.

Run from any working directory:
    python tools/validate_mod.py

This checks files and assets without launching Mindustry. A final in-game load
check is still recommended before publishing a release.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
CONTENT = ROOT / "content"
SPRITES = ROOT / "sprites"

VANILLA_ITEMS = {
    "copper", "lead", "graphite", "titanium", "silicon", "thorium",
    "plastanium", "surge-alloy", "phase-fabric", "blast-compound", "slag",
}
VANILLA_LIQUIDS = {"cryofluid"}
VANILLA_BLOCKS = {"mass-driver"}


class ValidationError(Exception):
    pass


def load_json(path: Path):
    try:
        with path.open("r", encoding="utf-8-sig") as handle:
            data = json.load(handle)
    except (OSError, json.JSONDecodeError) as exc:
        raise ValidationError(f"Invalid JSON in {path.relative_to(ROOT)}: {exc}") from exc
    if not isinstance(data, dict):
        raise ValidationError(f"Expected a JSON object in {path.relative_to(ROOT)}")
    return data


def check_image(path: Path, expected_size: tuple[int, int] | None = None) -> None:
    if not path.is_file():
        raise ValidationError(f"Missing sprite: {path.relative_to(ROOT)}")
    try:
        with Image.open(path) as image:
            image.verify()
        with Image.open(path) as image:
            if image.format != "PNG":
                raise ValidationError(f"{path.relative_to(ROOT)} is not a PNG")
            if image.mode != "RGBA":
                raise ValidationError(
                    f"{path.relative_to(ROOT)} must be 32-bit RGBA, got {image.mode}"
                )
            if expected_size and image.size != expected_size:
                raise ValidationError(
                    f"{path.relative_to(ROOT)} is {image.width}x{image.height}; "
                    f"expected {expected_size[0]}x{expected_size[1]}"
                )

    except ValidationError:
        raise
    except Exception as exc:
        raise ValidationError(f"Cannot read {path.relative_to(ROOT)}: {exc}") from exc


def main() -> int:
    errors: list[str] = []
    checked_json = 0
    checked_png = 0

    metadata = (ROOT / "mod.hjson").read_text(encoding="utf-8")
    for key in ("name", "displayName", "version", "minGameVersion"):
        if not re.search(rf"(?m)^\s*{key}\s*:", metadata):
            errors.append(f"mod.hjson is missing required metadata field: {key}")

    block_files = sorted((CONTENT / "blocks").glob("*.json"))
    item_files = sorted((CONTENT / "items").glob("*.json"))
    blocks: dict[str, dict] = {}
    items: dict[str, dict] = {}

    for path in sorted(CONTENT.rglob("*.json")):
        try:
            data = load_json(path)
            checked_json += 1
            if path.parent.name == "blocks":
                blocks[path.stem] = data
            elif path.parent.name == "items":
                items[path.stem] = data
        except ValidationError as exc:
            errors.append(str(exc))

    known_items = VANILLA_ITEMS | set(items)
    known_liquids = VANILLA_LIQUIDS
    known_blocks = VANILLA_BLOCKS | set(blocks)

    allowed_block_fields = {
        "MassDriver": {
            "type", "name", "description", "size", "health", "itemCapacity",
            "range", "reload", "rotateSpeed", "minDistribute", "translation",
            "knockback", "shake", "bulletSpeed", "bulletLifetime", "shootSoundVolume",
            "category", "consumes", "bullet", "shootEffect", "smokeEffect",
            "receiveEffect", "requirements", "research",
        },
        "GenericCrafter": {
            "type", "name", "description", "size", "health", "itemCapacity",
            "category", "craftTime", "craftEffect", "updateEffect", "consumes",
            "outputItem", "requirements", "research",
        },
        "StorageBlock": {
            "type", "name", "description", "size", "health", "itemCapacity",
            "category", "requirements", "research", "coreMerge",
        },
    }

    for stem, block in blocks.items():
        block_type = block.get("type")
        allowed_fields = allowed_block_fields.get(block_type)
        if allowed_fields is None:
            errors.append(f"{stem}: unsupported block type '{block_type}'")
        else:
            for field in block:
                if field not in allowed_fields:
                    errors.append(f"{stem}: unsupported {block_type} field '{field}'")
        size = block.get("size")
        if not isinstance(size, int) or size < 1:
            errors.append(f"content/blocks/{stem}.json has an invalid size")
            continue
        check_path = SPRITES / f"{stem}.png"
        try:
            check_image(check_path, (size * 32, size * 32))
            checked_png += 1
        except ValidationError as exc:
            errors.append(str(exc))

        # MassDriver specifically loads a second static-base sprite.
        if block.get("type") == "MassDriver":
            try:
                check_image(SPRITES / f"{stem}-base.png", (size * 32, size * 32))
                checked_png += 1
            except ValidationError as exc:
                errors.append(str(exc))

        research = block.get("research")
        if research and research not in known_blocks:
            errors.append(f"{stem}: research parent '{research}' does not exist in this mod or vanilla whitelist")

        consumes = block.get("consumes", {})
        for stack in consumes.get("items", []):
            item = stack.get("item")
            amount = stack.get("amount")
            if item not in known_items:
                errors.append(f"{stem}: unknown consumed item '{item}'")
            if not isinstance(amount, (int, float)) or amount <= 0:
                errors.append(f"{stem}: invalid consumed item amount for '{item}'")
        for stack in consumes.get("liquids", []):
            liquid = stack.get("liquid")
            amount = stack.get("amount")
            if liquid not in known_liquids:
                errors.append(f"{stem}: unknown consumed liquid '{liquid}'")
            if not isinstance(amount, (int, float)) or amount <= 0:
                errors.append(f"{stem}: invalid consumed liquid amount for '{liquid}'")

        output_item = block.get("outputItem")
        if output_item and output_item.get("item") not in known_items:
            errors.append(f"{stem}: unknown output item '{output_item.get('item')}'")

        requirements = block.get("requirements", [])
        for stack in requirements:
            if stack.get("item") not in known_items:
                errors.append(f"{stem}: unknown construction item '{stack.get('item')}'")

        if block.get("type") == "GenericCrafter":
            item_capacity = block.get("itemCapacity", 10)
            max_input = max(
                (stack.get("amount", 0) for stack in consumes.get("items", [])),
                default=0,
            )
            if item_capacity < max_input:
                errors.append(
                    f"{stem}: itemCapacity ({item_capacity}) is below the largest "
                    f"per-craft input stack ({max_input})"
                )

    allowed_item_fields = {
        "name", "description", "color", "explosiveness", "flammability",
        "radioactivity", "charge", "hardness", "cost", "healthScaling",
        "lowPriority", "frames", "transitionFrames", "frameTime", "buildable", "hidden",
    }
    for path in item_files:
        try:
            item_data = load_json(path)
            for field in item_data:
                if field not in allowed_item_fields and field != "research":
                    errors.append(
                        f"{path.relative_to(ROOT)} has unsupported Item field '{field}'"
                    )
            hardness = item_data.get("hardness", 0)
            if not isinstance(hardness, int):
                errors.append(f"{path.relative_to(ROOT)}: Item.hardness must be an integer")
        except ValidationError as exc:
            errors.append(str(exc))

    for stem in items:
        try:
            check_image(SPRITES / f"{stem}.png", (32, 32))
            checked_png += 1
        except ValidationError as exc:
            errors.append(str(exc))

    core_vault = blocks.get("core-vault", {})
    if core_vault.get("type") == "StorageBlock" and core_vault.get("coreMerge") is not True:
        errors.append("core-vault: coreMerge must be true for adjacent core inventory sharing")

    collider = blocks.get("b-b-collider", {})
    if collider:
        craft_time = collider.get("craftTime", 0)
        cryo_rate = next(
            (s.get("amount", 0) for s in collider.get("consumes", {}).get("liquids", [])
             if s.get("liquid") == "cryofluid"),
            0,
        )
        if craft_time <= 0 or cryo_rate <= 0:
            errors.append("b-b-collider: missing craftTime or cryofluid rate")
        else:
            batch = cryo_rate * craft_time
            if abs(batch - 100) > 0.02:
                errors.append(
                    f"b-b-collider: cryofluid consumption is {batch:.3f} per craft; expected 100"
                )

    try:
        check_image(ROOT / "icon.png", (128, 128))
        checked_png += 1
    except ValidationError as exc:
        errors.append(str(exc))

    # Check every shipped sprite, including the unchanged mass-driver assets.
    for path in sorted(SPRITES.glob("*.png")):
        try:
            check_image(path)
            checked_png += 1
        except ValidationError as exc:
            errors.append(str(exc))

    if errors:
        print("VALIDATION FAILED")
        for error in errors:
            print(f" - {error}")
        return 1

    print(
        f"Validation passed: {checked_json} JSON files parsed; "
        f"{checked_png} sprite PNG checks passed."
    )
    print("Static checks only; launch the mod in Mindustry before publishing.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
