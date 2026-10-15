"""Pluto settings with compatibility for existing installation names."""

import os


def get_env(name: str, default: str | None = None) -> str | None:
    """Prefer PLUTO_*; fall back only when the new name is not set.

    An explicitly empty value must not restore a legacy credential or flag.
    """
    if not name.startswith("PLUTO_"):
        raise ValueError("Use a PLUTO_ configuration name")
    if name in os.environ:
        return os.environ[name]
    legacy = "ECLIPSE_" + name[len("PLUTO_"):]
    return os.environ.get(legacy, default)
