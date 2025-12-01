"""
Router package initialization.

This module makes the routers directory a Python package.
"""

from ....material import rooms, autocomplete, websocket

__all__ = ["rooms", "autocomplete", "websocket"]