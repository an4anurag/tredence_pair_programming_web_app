"""
Router package initialization.

This module makes the routers directory a Python package.
"""

from app.routers import rooms, autocomplete, websocket

__all__ = ["rooms", "autocomplete", "websocket"]