"""
Scanning modules for SubSort
Each module performs specific reconnaissance tasks
"""

from .status import StatusModule
from .server import ServerModule
from .title import TitleModule

# Module registry
MODULES = {
    'status': StatusModule,
    'server': ServerModule,
    'title': TitleModule
}

def get_module(module_name: str):
    """Get module class by name"""
    return MODULES.get(module_name.lower())

def list_modules():
    """List available modules"""
    return list(MODULES.keys())
