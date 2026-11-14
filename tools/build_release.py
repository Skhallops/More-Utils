"""
Build the release zip for More Utils.

The published package must contain exactly the files the game loads:

  mod.hjson, icon.png, content/**, sprites/**, scripts/**

Development-only trees (docs/, tools/, .git/, OpenCode-Unlimited/) and the
generated zip itself are never included. This is deliberately an allow-list so
a stray folder can't leak into a release.

Usage:  py -3 tools/build_release.py [--version 1.x.xx.x]
"""

import argparse
import os
import sys
import zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ZIP_NAME = "More-Utils.zip"

ROOT_FILES = ("mod.hjson", "icon.png", "LICENSE")
INCLUDE_DIRS = ("content", "sprites", "scripts")

# Never ship these even if they appear inside an allowed directory.
SKIP_NAMES = {"__pycache__", ".DS_Store", "Thumbs.db"}


def collect():
    files = []
    for name in ROOT_FILES:
        path = os.path.join(ROOT, name)
        if os.path.isfile(path):
            files.append(path)

    for folder in INCLUDE_DIRS:
        base = os.path.join(ROOT, folder)
        if not os.path.isdir(base):
            continue
        for dirpath, dirnames, filenames in os.walk(base):
            dirnames[:] = sorted(d for d in dirnames if d not in SKIP_NAMES)
            for filename in sorted(filenames):
                if filename in SKIP_NAMES:
                    continue
                files.append(os.path.join(dirpath, filename))
    return files


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--version",
        default=None,
        help="Expected mod.hjson version. Build fails if it does not match.",
    )
    args = parser.parse_args()

    mod_path = os.path.join(ROOT, "mod.hjson")
    with open(mod_path, encoding="utf-8") as handle:
        mod_text = handle.read()

    if args.version:
        marker = 'version: "'
        index = mod_text.find(marker)
        if index < 0:
            sys.exit("mod.hjson has no version field")
        start = index + len(marker)
        end = mod_text.find('"', start)
        actual = mod_text[start:end]
        if actual != args.version:
            sys.exit(f"version mismatch: mod.hjson={actual} expected={args.version}")

    files = collect()
    if not files:
        sys.exit("nothing to package")

    out = os.path.join(ROOT, ZIP_NAME)
    if os.path.exists(out):
        os.remove(out)

    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as archive:
        for path in files:
            rel = os.path.relpath(path, ROOT).replace("\\", "/")
            archive.write(path, rel)

    print(f"wrote {ZIP_NAME} ({len(files)} files)")
    with zipfile.ZipFile(out) as archive:
        for info in archive.infolist():
            print(f"  {info.filename:44s} {info.file_size:7d}")

    required = ("mod.hjson", "icon.png", "scripts/main.js")
    present = {info.filename for info in zipfile.ZipFile(out).infolist()}
    missing = [r for r in required if r not in present]
    if missing:
        sys.exit(f"missing required entries: {', '.join(missing)}")
    if not any(name.startswith("sprites/") for name in present):
        sys.exit("no sprites packaged")
    if not any(name.startswith("content/") for name in present):
        sys.exit("no content packaged")


if __name__ == "__main__":
    main()
