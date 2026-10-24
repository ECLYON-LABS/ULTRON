"""ULTRON settings with compatibility for existing installation names."""

import os


def get_env(name: str, default: str | None = None) -> str | None:
    """Prefer ULTRON_*, then PLUTO_*, then ECLIPSE_*.

    An explicitly empty value must not restore a legacy credential or flag.
    """
    prefixes = ("ULTRON_", "PLUTO_", "ECLIPSE_")
    prefix = next((item for item in prefixes if name.startswith(item)), None)
    if prefix is None:
        raise ValueError("Use an ULTRON_ configuration name")
    suffix = name[len(prefix):]
    for item in prefixes:
        candidate = item + suffix
        if candidate in os.environ:
            return os.environ[candidate]
    return default
