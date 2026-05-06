"""Allow ``python -m wisp`` to invoke the CLI."""

from .cli import main

raise SystemExit(main())
