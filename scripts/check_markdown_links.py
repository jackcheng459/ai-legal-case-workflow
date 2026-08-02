#!/usr/bin/env python3
"""Validate local Markdown links and GitHub-style heading anchors."""

from __future__ import annotations

import re
import sys
import unicodedata
from pathlib import Path
from urllib.parse import unquote, urlsplit


HEADING_RE = re.compile(r"^(#{1,6})\s+(.+?)\s*#*\s*$")
MARKDOWN_LINK_RE = re.compile(r"!?\[[^\]]*\]\(([^)]+)\)")
HTML_LINK_RE = re.compile(r"\b(?:href|src)=[\"']([^\"']+)[\"']", re.IGNORECASE)
HTML_TAG_RE = re.compile(r"<[^>]+>")
INLINE_LINK_RE = re.compile(r"!?\[([^\]]*)\]\([^)]+\)")


def strip_fenced_blocks(lines: list[str]) -> list[tuple[int, str]]:
    visible: list[tuple[int, str]] = []
    fence: str | None = None
    for number, line in enumerate(lines, 1):
        stripped = line.lstrip()
        marker = "```" if stripped.startswith("```") else "~~~" if stripped.startswith("~~~") else None
        if marker:
            fence = None if fence == marker else marker if fence is None else fence
            continue
        if fence is None:
            visible.append((number, line))
    return visible


def github_slug(title: str) -> str:
    title = HTML_TAG_RE.sub("", title)
    title = INLINE_LINK_RE.sub(r"\1", title)
    title = title.replace("`", "").replace("*", "")
    title = unicodedata.normalize("NFKC", title).strip().lower()
    chars: list[str] = []
    for char in title:
        category = unicodedata.category(char)
        if char.isspace():
            chars.append("-")
        elif char in "-_":
            chars.append(char)
        elif category[0] in {"L", "N"}:
            chars.append(char)
    return "".join(chars)


def anchors_for(path: Path) -> set[str]:
    counts: dict[str, int] = {}
    anchors: set[str] = set()
    lines = path.read_text(encoding="utf-8").splitlines()
    for _, line in strip_fenced_blocks(lines):
        match = HEADING_RE.match(line)
        if not match:
            continue
        base = github_slug(match.group(2))
        if not base:
            continue
        count = counts.get(base, 0)
        anchor = base if count == 0 else f"{base}-{count}"
        counts[base] = count + 1
        anchors.add(anchor)
    return anchors


def normalize_target(raw: str) -> str:
    target = raw.strip()
    if target.startswith("<") and ">" in target:
        return target[1 : target.index(">")]
    return target.split(maxsplit=1)[0]


def resolve_path(root: Path, source: Path, path_text: str) -> Path:
    decoded = unquote(path_text)
    if decoded.startswith("/"):
        return root / decoded.lstrip("/")
    return source.parent / decoded


def main() -> int:
    root = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
    markdown_files = sorted(path for path in root.rglob("*.md") if ".git" not in path.parts)
    anchor_cache = {path.resolve(): anchors_for(path) for path in markdown_files}
    errors: list[str] = []

    for source in markdown_files:
        lines = source.read_text(encoding="utf-8").splitlines()
        for line_number, line in strip_fenced_blocks(lines):
            targets = MARKDOWN_LINK_RE.findall(line) + HTML_LINK_RE.findall(line)
            for raw_target in targets:
                target = normalize_target(raw_target)
                parsed = urlsplit(target)
                if parsed.scheme or target.startswith("//"):
                    continue
                target_path = source.resolve() if not parsed.path else resolve_path(root, source, parsed.path).resolve()
                display = source.relative_to(root)
                if not target_path.exists():
                    errors.append(f"{display}:{line_number}: missing relative target: {target}")
                    continue
                if parsed.fragment and target_path.suffix.lower() == ".md":
                    fragment = unquote(parsed.fragment)
                    anchors = anchor_cache.get(target_path)
                    if anchors is None:
                        anchors = anchors_for(target_path)
                        anchor_cache[target_path] = anchors
                    if fragment not in anchors:
                        errors.append(f"{display}:{line_number}: missing anchor #{fragment} in {target_path.relative_to(root)}")

    if errors:
        print("Markdown link validation failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    print(f"PASS: {len(markdown_files)} Markdown files, relative targets and heading anchors")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
