"""Wisp command-line entry point.

By default, `wisp` starts the local server and opens a browser tab. Use
`wisp --version` for the version, and `wisp --no-browser` for headless dev runs.
"""

from __future__ import annotations

import argparse

from . import __version__
from .launcher import LaunchOptions, serve


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="wisp",
        description="AI job-search decision-support assistant.",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"wisp {__version__}",
    )
    parser.add_argument(
        "--host",
        default="127.0.0.1",
        help="Host interface to bind (default: 127.0.0.1).",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=0,
        help="Port to bind. 0 = auto-pick a free port (default).",
    )
    parser.add_argument(
        "--no-browser",
        action="store_true",
        help="Do not open a browser tab automatically.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    serve(
        LaunchOptions(
            host=args.host,
            port=args.port,
            open_browser=not args.no_browser,
        )
    )
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
