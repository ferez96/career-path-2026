#!/usr/bin/env python3
"""Resolve Obsidian wikilinks in vault hub notes under data/.

Usage (repo root):
  python scripts/vault_hub_wikilinks.py
  python scripts/vault_hub_wikilinks.py --json

Scores resolved/total per file. A link resolves if a matching .md exists under data/.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, asdict
from pathlib import Path


WIKILINK_RE = re.compile(r"(?<!!)\[\[([^\]]+)\]\]")


def repo_root() -> Path:
    return Path(__file__).resolve().parent.parent


def vault_root() -> Path:
    return repo_root() / "data"


def parse_wikilink_inner(inner: str) -> str:
    """Return link target path/note name (no alias, no #heading)."""
    part = inner.split("|", 1)[0].strip()
    part = part.split("#", 1)[0].strip()
    return part


def resolve_link(target: str, source_file: Path, root: Path) -> tuple[bool, str, Path | None]:
    """Return (ok, detail, resolved_path)."""
    if not target or target.startswith("http://") or target.startswith("https://"):
        return False, "empty_or_url", None

    # Path-style (vault-relative or relative to source)
    if target.startswith("/"):
        target = target.lstrip("/")

    has_slash = "/" in target or target.startswith("..")

    if has_slash:
        base = source_file.parent
        candidate = (base / target).resolve()
        try:
            candidate.relative_to(root.resolve())
        except ValueError:
            return False, "outside_vault", None
        if candidate.suffix.lower() != ".md":
            md = candidate.with_suffix(".md")
        else:
            md = candidate
        if md.is_file():
            return True, "relative", md
        return False, "not_found", None

    # Bare note name: search **/{target}.md under vault
    matches = list(root.rglob(f"{target}.md"))
    if len(matches) == 1:
        return True, "unique_name", matches[0]
    if len(matches) > 1:
        # Obsidian may disambiguate; count as resolved but note ambiguity
        rels = sorted(str(m.relative_to(root)) for m in matches)
        return True, f"ambiguous({len(matches)}):{rels[0]}…", matches[0]

    return False, "not_found", None


def hub_files(root: Path) -> list[Path]:
    files: list[Path] = []
    for name in ("Home.md",):
        p = root / name
        if p.is_file():
            files.append(p)

    atlas = root / "atlas"
    if atlas.is_dir():
        for p in sorted(atlas.glob("*.md")):
            files.append(p)

    co = root / "opportunities" / "Central Opportunities.md"
    if co.is_file():
        files.append(co)

    for p in sorted((root / "opportunities").glob("*Opportunity Index.md")):
        files.append(p)

    # De-duplicate preserving order
    seen: set[Path] = set()
    out: list[Path] = []
    for p in files:
        rp = p.resolve()
        if rp not in seen:
            seen.add(rp)
            out.append(p)
    return out


@dataclass
class FileReport:
    path: str
    total: int
    resolved: int
    unresolved: list[str]


def analyze_file(path: Path, root: Path) -> FileReport:
    text = path.read_text(encoding="utf-8", errors="replace")
    unresolved: list[str] = []
    resolved = 0
    for m in WIKILINK_RE.finditer(text):
        inner = m.group(1)
        target = parse_wikilink_inner(inner)
        ok, detail, _ = resolve_link(target, path, root)
        if ok:
            resolved += 1
        else:
            unresolved.append(f"[[{inner}]] -> {detail}")
    total = resolved + len(unresolved)
    return FileReport(
        path=str(path.relative_to(repo_root())),
        total=total,
        resolved=resolved,
        unresolved=unresolved,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="Print JSON only")
    args = parser.parse_args()

    root = vault_root()
    if not root.is_dir():
        print("data/ vault not found", file=sys.stderr)
        return 2

    reports = [analyze_file(p, root) for p in hub_files(root)]

    if args.json:
        print(json.dumps([asdict(r) for r in reports], indent=2))
        return 0

    grand_total = sum(r.total for r in reports)
    grand_res = sum(r.resolved for r in reports)
    pct = (100.0 * grand_res / grand_total) if grand_total else 0.0

    print("Vault hub wikilink resolution (data/)")
    print(f"Overall: {grand_res}/{grand_total} ({pct:.1f}%)")
    print()
    for r in reports:
        line_pct = (100.0 * r.resolved / r.total) if r.total else 100.0
        print(f"{r.path}: {r.resolved}/{r.total} ({line_pct:.1f}%)")
        for u in r.unresolved:
            print(f"  UNRESOLVED: {u}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
