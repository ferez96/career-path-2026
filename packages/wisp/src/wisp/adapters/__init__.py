"""Storage adapters for Wisp.

The :class:`VaultAdapter` Protocol is the storage interface the rest of
the package consumes. v1 ships :class:`SqliteVaultAdapter`; v1.1+ may
add a YAML-backed adapter that points at a CareerPath2026-style vault.
"""

from .base import VaultAdapter
from .sqlite_vault import SqliteVaultAdapter

__all__ = ["SqliteVaultAdapter", "VaultAdapter"]
