#!/usr/bin/env python3
"""
_repo_generator.py — RoloTech Kodi repository builder

Run from the repo root.

Typical usage:

  # First time: stamp your GitHub username into the repo addon URLs,
  # then build everything.
  python _repo_generator.py --github-user mark-rolotech

  # Ongoing: just rebuild metadata after dropping a new addon zip in.
  python _repo_generator.py

  # Pack a fresh source folder into a versioned zip:
  python _repo_generator.py --pack repository.rolotech
  python _repo_generator.py --pack plugin.video.mpsupersearch

What it does:
  1. (Optional) Replaces YOUR_GITHUB_USER in repository.rolotech/addon.xml.
  2. (Optional) Zips a given addon source folder as <id>-<version>.zip,
     placed inside that addon's directory.
  3. Walks every <addon_id>/ subdirectory, reads its addon.xml, and
     writes a combined addons.xml at the repo root.
  4. Writes addons.xml.md5 next to it.

Repo layout this script expects:

  repo_root/
    _repo_generator.py
    addons.xml             <-- generated
    addons.xml.md5         <-- generated
    repository.rolotech/
      addon.xml
      icon.png
      repository.rolotech-1.0.0.zip
    plugin.video.mpsupersearch/
      addon.xml
      plugin.video.mpsupersearch-1.0.6.zip

Notes:
  - Hidden directories and the script itself are skipped.
  - addons.xml is the concatenation of every addon.xml wrapped in <addons>.
  - Run this AFTER updating an addon's addon.xml + dropping its new zip in.
"""

import argparse
import hashlib
import os
import re
import sys
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path

REPO_ADDON_ID = "repository.rolotech"
PLACEHOLDER = "YOUR_GITHUB_USER"


def repo_root() -> Path:
    return Path(__file__).resolve().parent


def stamp_github_user(username: str) -> None:
    """Replace YOUR_GITHUB_USER in the repo addon's addon.xml."""
    addon_xml = repo_root() / REPO_ADDON_ID / "addon.xml"
    if not addon_xml.exists():
        print(f"[skip stamp] {addon_xml} not found", file=sys.stderr)
        return
    text = addon_xml.read_text(encoding="utf-8")
    if PLACEHOLDER not in text:
        # Already stamped or someone replaced it manually; sanity-check anyway.
        if username and f"github.io" in text and username not in text:
            print(
                "[warn] addon.xml already stamped with a different username; "
                "leaving alone. Edit by hand if you really need to change it.",
                file=sys.stderr,
            )
        else:
            print("[stamp] no placeholder found, nothing to do.")
        return
    new_text = text.replace(PLACEHOLDER, username)
    addon_xml.write_text(new_text, encoding="utf-8")
    print(f"[stamp] wrote GitHub user '{username}' into {addon_xml.relative_to(repo_root())}")


def pack_addon(addon_dir_name: str) -> None:
    """Zip an addon source folder as <id>-<version>.zip inside the same folder."""
    src = repo_root() / addon_dir_name
    addon_xml = src / "addon.xml"
    if not addon_xml.exists():
        print(f"[pack] {addon_xml} not found, aborting", file=sys.stderr)
        sys.exit(1)
    root = ET.parse(addon_xml).getroot()
    addon_id = root.get("id")
    version = root.get("version")
    if not addon_id or not version:
        print(f"[pack] addon.xml missing id/version", file=sys.stderr)
        sys.exit(1)
    out_zip = src / f"{addon_id}-{version}.zip"
    if out_zip.exists():
        out_zip.unlink()

    # Skip these when zipping
    skip_names = {".git", ".github", "__pycache__", ".DS_Store"}
    skip_suffixes = {".pyc", ".pyo"}
    skip_zip_pattern = re.compile(rf"^{re.escape(addon_id)}-.*\.zip$")

    with zipfile.ZipFile(out_zip, "w", zipfile.ZIP_DEFLATED) as zf:
        for path in sorted(src.rglob("*")):
            if any(part in skip_names for part in path.relative_to(src).parts):
                continue
            if path.is_dir():
                continue
            if path.suffix in skip_suffixes:
                continue
            # Don't include the zip we're writing or any prior version zips
            if skip_zip_pattern.match(path.name):
                continue
            arcname = Path(addon_id) / path.relative_to(src)
            zf.write(path, arcname.as_posix())

    size_kb = out_zip.stat().st_size / 1024
    print(f"[pack] {out_zip.relative_to(repo_root())}  ({size_kb:.1f} KB)")


def _write_index_html(directory: Path, heading: str, skip_names: set) -> None:
    """Write a simple HTML directory listing Kodi (and browsers) can navigate."""
    rows = []
    for p in sorted(directory.iterdir()):
        if p.name in skip_names or p.name == "index.html":
            continue
        if p.name.startswith("."):
            continue
        if p.is_dir():
            # Only list addon dirs (those with addon.xml) at the root level
            if directory == repo_root() and not (p / "addon.xml").exists():
                continue
            rows.append(f'<a href="{p.name}/">{p.name}/</a>')
        else:
            rows.append(f'<a href="{p.name}">{p.name}</a>')

    body = "\n".join(f"        {r}<br>" for r in rows)
    html = f"""<!DOCTYPE html>
<html><head><title>{heading}</title>
<style>
body {{ font-family: ui-monospace, Menlo, Consolas, monospace;
        background: #f7f7f7; max-width: 760px; margin: 2em auto; padding: 1.5em;
        background-color: #fff; border: 1px solid #e1e4e8; border-radius: 6px; }}
h1 {{ font-size: 1.05em; border-bottom: 1px solid #e1e4e8; padding-bottom: .5em; }}
a {{ display: inline-block; padding: 4px 0; color: #0366d6; text-decoration: none; }}
a:hover {{ text-decoration: underline; }}
</style></head><body>
<h1>Index of {heading}</h1>
{body}
</body></html>
"""
    (directory / "index.html").write_text(html, encoding="utf-8")


def write_indexes() -> None:
    """Generate index.html files Kodi needs to browse over HTTP."""
    root = repo_root()
    _write_index_html(
        root,
        "/",
        skip_names={"_repo_generator.py", "README.md", ".gitignore", ".git"},
    )
    count = 1
    for entry in sorted(root.iterdir()):
        if not entry.is_dir() or entry.name.startswith((".", "_")):
            continue
        if not (entry / "addon.xml").exists():
            continue
        _write_index_html(entry, f"/{entry.name}/", skip_names=set())
        count += 1
    print(f"[index] wrote {count} index.html files (Kodi browsable)")


def build_addons_xml() -> Path:
    root = repo_root()
    out_lines = ['<?xml version="1.0" encoding="UTF-8" standalone="yes"?>', "<addons>"]
    found = []
    for entry in sorted(root.iterdir()):
        if not entry.is_dir():
            continue
        if entry.name.startswith(".") or entry.name.startswith("_"):
            continue
        addon_xml = entry / "addon.xml"
        if not addon_xml.exists():
            continue
        text = addon_xml.read_text(encoding="utf-8")
        # Strip XML prolog if present so we can embed cleanly.
        text = re.sub(r"^\s*<\?xml.*?\?>\s*", "", text, count=1, flags=re.DOTALL).rstrip()
        out_lines.append(text)
        try:
            tag_root = ET.fromstring(text)
            found.append((tag_root.get("id"), tag_root.get("version")))
        except ET.ParseError as e:
            print(f"[warn] could not parse {addon_xml}: {e}", file=sys.stderr)
    out_lines.append("</addons>")
    out = "\n".join(out_lines) + "\n"
    addons_xml = root / "addons.xml"
    addons_xml.write_text(out, encoding="utf-8")
    print(f"[build] {addons_xml.relative_to(root)}  ({len(found)} addons)")
    for aid, ver in found:
        print(f"        - {aid} {ver}")
    return addons_xml


def write_md5(addons_xml: Path) -> None:
    digest = hashlib.md5(addons_xml.read_bytes()).hexdigest()
    md5_path = addons_xml.with_suffix(".xml.md5")
    md5_path.write_text(digest + "\n", encoding="utf-8")
    print(f"[build] {md5_path.relative_to(repo_root())}  ({digest})")


def main() -> int:
    p = argparse.ArgumentParser(description="Build a Kodi repository.")
    p.add_argument("--github-user", help="Stamp this username into the repo addon URLs.")
    p.add_argument("--pack", metavar="DIR", help="Zip an addon source folder before building.")
    args = p.parse_args()

    if args.github_user:
        stamp_github_user(args.github_user)
    if args.pack:
        pack_addon(args.pack)

    addons_xml = build_addons_xml()
    write_md5(addons_xml)
    write_indexes()
    print("\nDone. Commit, push, and Kodi will see updates on next repo poll.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
