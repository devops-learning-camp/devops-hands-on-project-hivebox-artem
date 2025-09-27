#!/usr/bin/env python3
"""
Simple CLI app that prints the current application version and exits.
"""

APP_VERSION = "v0.0.1"


def print_version() -> None:
    """Print the current application version and exit."""
    print(APP_VERSION)


if __name__ == "__main__":
    # For this phase the requirement is just to print the version and exit.
    # Keeping it simple: no args parsing needed.
    print_version()
