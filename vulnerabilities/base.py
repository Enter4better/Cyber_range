from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
import random
import time

class BaseVulnerability(ABC):
    """漏洞基类 - 所有漏洞类型继承此类"""
    
    def __init__(self, name: str, description: str, severity: str, cve_id: Optional[str] = None):
        self.name = name
        self.description = description
        self.severity = severity  # low, medium, high, critical
        self.cve_id = cve_id
        
    @abstractmethod
    def deploy(self, vm, vm_name: str, session_dir: str) -> bool:
        """在虚拟机上部署漏洞环境"""
        pass
    
    @abstractmethod
    def exploit(self, target_info: Dict[str, Any]) -> Dict[str, Any]:
        """利用漏洞进行攻击"""
        pass
    
    @abstractmethod
    def detect(self, logs: str) -> Dict[str, Any]:
        """检测漏洞利用痕迹"""
        pass
    
    def get_indicators(self) -> List[str]:
        """获取漏洞利用的特征指标"""
        return []
    
    def get_mitigation(self) -> List[str]:
        """获取漏洞修复建议"""
        return []
    
    def get_info(self) -> Dict[str, Any]:
        """获取漏洞信息"""
        return {
            'name': self.name,
            'description': self.description,
            'severity': self.severity,
            'cve_id': self.cve_id
        }

class VulnerabilityFactory:
    """漏洞工厂 - 管理所有漏洞类型"""
    
    _vulnerabilities = {}
    
    @classmethod
    def register(cls, name: str, vuln_class):
        """注册漏洞类"""
        cls._vulnerabilities[name.lower()] = vuln_class
        
    @classmethod
    def create(cls, name: str, **kwargs) -> Optional[BaseVulnerability]:
        """创建漏洞实例"""
        vuln_class = cls._vulnerabilities.get(name.lower())
        if vuln_class:
            return vuln_class(**kwargs)
        return None
    
    @classmethod
    def get_all_types(cls) -> List[str]:
        """获取所有已注册的漏洞类型"""
        return list(cls._vulnerabilities.keys())
    
    @classmethod
    def get_by_severity(cls, severity: str) -> List[str]:
        """按严重程度获取漏洞类型"""
        result = []
        for name, vuln_class in cls._vulnerabilities.items():
            if hasattr(vuln_class, 'severity'):
                if vuln_class.severity == severity:
                    result.append(name)
        return result