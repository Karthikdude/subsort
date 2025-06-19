"""
Scanning modules for SubSort
Each module performs specific reconnaissance tasks
"""

from .status import StatusModule
from .server import ServerModule
from .title import TitleModule
from .techstack import TechstackModule
from .vhost import VhostModule
from .responsetime import ResponsetimeModule
from .faviconhash import FaviconhashModule
from .robots import RobotsModule

# Module registry
MODULES = {
    'status': StatusModule,
    'server': ServerModule,
    'title': TitleModule,
    'techstack': TechstackModule,
    'vhost': VhostModule,
    'responsetime': ResponsetimeModule,
    'faviconhash': FaviconhashModule,
    'robots': RobotsModule,
    # Placeholder modules for advanced features - using StatusModule as base
    'js': StatusModule,
    'auth': StatusModule,
    'jsvuln': StatusModule,
    'loginpanels': StatusModule,
    'jwt': StatusModule,
    'cname': StatusModule,
    'iphistory': StatusModule,
    'httpmethods': StatusModule,
    'port': StatusModule,
    'ssl': StatusModule,
    'headers': StatusModule,
    'content': StatusModule,
    'cors': StatusModule,
    'cdn': StatusModule,
    'length': StatusModule,
    'geoip': StatusModule,
    'cms': StatusModule,
    'waf': StatusModule,
    'cloudassets': StatusModule,
    'dirscan': StatusModule,
    'wappalyzer': StatusModule,
    'vulnscan': StatusModule,
}

def get_module(module_name: str):
    """Get module class by name"""
    return MODULES.get(module_name.lower())

def list_modules():
    """List available modules"""
    return list(MODULES.keys())
