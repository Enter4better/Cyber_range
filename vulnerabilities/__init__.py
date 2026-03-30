from .base import VulnerabilityFactory
from . import sqli
from . import xss
from . import weak_password
from . import rce
from . import lfi
from . import file_upload

# 导出工厂类
__all__ = ['VulnerabilityFactory']