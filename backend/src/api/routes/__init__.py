"""
API Routes package.

Export all routers for inclusion in main app.
"""

from .phantom import router as phantom_router
from .quick_scan import router as quick_scan_router
from .opportunities import router as opportunities_router
from .triggers import router as triggers_router
from .jobs import router as jobs_router

__all__ = [
    "phantom_router",
    "quick_scan_router",
    "opportunities_router",
    "triggers_router",
    "jobs_router",
]
