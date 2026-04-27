"""Local file context loader for chat requests."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


ALLOWED_ROOTS = ("data", "docs", "templates", "config")
MAX_FILES = 8
MAX_CHARS_PER_FILE = 12000
MAX_TOTAL_CHARS = 40000


@dataclass(slots=True)
class LoadedFileContext:
    """Represents one attached file loaded for prompt context."""

    path: str
    content: str
    truncated: bool
    chars_included: int


@dataclass(slots=True)
class SkippedFileContext:
    """Represents a file that was skipped and why."""

    path: str
    reason: str


@dataclass(slots=True)
class FileContextResult:
    """Aggregate result for loaded and skipped context files."""

    loaded: list[LoadedFileContext]
    skipped: list[SkippedFileContext]

    @property
    def included_chars(self) -> int:
        return sum(item.chars_included for item in self.loaded)


def parse_attached_paths(raw_value: str | None) -> list[str]:
    """Parse newline/comma separated paths into normalized list."""
    if not raw_value:
        return []
    tokens = raw_value.replace(",", "\n").splitlines()
    parsed: list[str] = []
    for token in tokens:
        value = token.strip()
        if value:
            parsed.append(value)
    # Keep order while removing duplicates.
    seen: set[str] = set()
    unique: list[str] = []
    for item in parsed:
        key = item.lower()
        if key not in seen:
            seen.add(key)
            unique.append(item)
    return unique


class LocalFileContextLoader:
    """Safely loads local files as prompt context blocks."""

    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root.resolve()
        self.allowed_roots = [self.repo_root / root for root in ALLOWED_ROOTS]

    def load_paths(self, paths: list[str] | None) -> FileContextResult:
        loaded: list[LoadedFileContext] = []
        skipped: list[SkippedFileContext] = []
        total_chars = 0

        if not paths:
            return FileContextResult(loaded=loaded, skipped=skipped)

        for raw_path in paths[:MAX_FILES]:
            if total_chars >= MAX_TOTAL_CHARS:
                skipped.append(
                    SkippedFileContext(path=raw_path, reason="total_context_limit_reached")
                )
                continue

            safe_path = self._resolve_safe_path(raw_path)
            if safe_path is None:
                skipped.append(SkippedFileContext(path=raw_path, reason="path_not_allowed"))
                continue

            if not safe_path.exists() or not safe_path.is_file():
                skipped.append(SkippedFileContext(path=raw_path, reason="file_not_found"))
                continue

            try:
                raw_text = safe_path.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                skipped.append(SkippedFileContext(path=raw_path, reason="non_utf8_or_binary"))
                continue

            remaining = MAX_TOTAL_CHARS - total_chars
            max_chars = min(MAX_CHARS_PER_FILE, remaining)
            truncated = len(raw_text) > max_chars
            content = raw_text[:max_chars]
            rel_path = safe_path.relative_to(self.repo_root).as_posix()
            loaded.append(
                LoadedFileContext(
                    path=rel_path,
                    content=content,
                    truncated=truncated,
                    chars_included=len(content),
                )
            )
            total_chars += len(content)

        if len(paths) > MAX_FILES:
            for extra_path in paths[MAX_FILES:]:
                skipped.append(
                    SkippedFileContext(path=extra_path, reason="max_files_limit_exceeded")
                )

        return FileContextResult(loaded=loaded, skipped=skipped)

    def _resolve_safe_path(self, raw_path: str) -> Path | None:
        candidate = Path(raw_path.strip())
        if not candidate or candidate.is_absolute():
            return None
        try:
            resolved = (self.repo_root / candidate).resolve()
        except OSError:
            return None
        if not resolved.is_relative_to(self.repo_root):
            return None
        if not any(resolved.is_relative_to(root.resolve()) for root in self.allowed_roots):
            return None
        return resolved


def build_file_context_message(result: FileContextResult) -> str | None:
    """Build one deterministic context message from loaded files."""
    if not result.loaded:
        return None

    blocks: list[str] = [
        "Use the following local files as factual context. "
        "If conflicts happen, prefer these files over assumptions."
    ]

    for item in result.loaded:
        truncation_note = "\n[TRUNCATED]" if item.truncated else ""
        blocks.append(
            "\n".join(
                [
                    f"--- file: {item.path} ---",
                    "```text",
                    f"{item.content}{truncation_note}",
                    "```",
                ]
            )
        )

    if result.skipped:
        skipped_lines = ", ".join(f"{item.path}({item.reason})" for item in result.skipped)
        blocks.append(f"Skipped files: {skipped_lines}")

    return "\n\n".join(blocks)

