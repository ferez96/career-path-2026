"""SQL migrations applied by :mod:`wisp.db.apply_migrations`.

Files are named ``NNN_description.sql`` and live next to this ``__init__``;
they're discovered via ``importlib.resources`` so the wheel works
post-install. Numbers are gap-tolerant but must be unique. The actual
schema lands in M2.2.
"""
