"""
API endpoints for Promptitron Unified System
"""

# Import from both main files for backward compatibility
try:
    from .main import app  # New modular version
except ImportError:
    from .main import app  # Fallback to original

__all__ = ["app"]