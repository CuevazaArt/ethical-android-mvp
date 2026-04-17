"""
Unified kernel settings package.

Provides single source of truth for all KERNEL_* and CHAT_* configuration.
"""

from .kernel_settings import KernelSettings, kernel_settings

__all__ = ["KernelSettings", "kernel_settings"]
