from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict
from enum import Enum

class OSType(str, Enum):
    # ========== Ubuntu ==========
    UBUNTU_18_04 = "ubuntu/bionic64"
    UBUNTU_20_04 = "ubuntu/focal64"
    UBUNTU_22_04 = "ubuntu/jammy64"
    UBUNTU_24_04 = "ubuntu/noble64"

    # ========== CentOS ==========
    CENTOS_7 = "centos/7"
    CENTOS_8 = "centos/8"

    # ========== Kali (攻击机) ==========
    KALI_LINUX = "kalilinux/rolling"

    # ========== Windows ==========
    WINDOWS_7 = "gusztavvargadr/windows-7"
    WINDOWS_10 = "gusztavvargadr/windows-10"
    WINDOWS_11 = "gusztavvargadr/windows-11"
    WINDOWS_SERVER_2019 = "gusztavvargadr/windows-server-2019-standard"
    WINDOWS_SERVER_2022 = "gusztavvargadr/windows-server-2022-standard"

    # 默认攻击机
    ATTACKER = "kalilinux/rolling"


class ServiceType(str, Enum):
    APACHE = "apache2"
    NGINX = "nginx"
    MYSQL = "mysql"
    POSTGRESQL = "postgresql"
    REDIS = "redis"
    SSH = "ssh"
    FTP = "ftp"

class DefenseTool(str, Enum):
    WAF = "waf"
    SNORT = "snort"
    SURICATA = "suricata"
    ELK = "elk"
    SPLUNK = "splunk"

class TargetNode(BaseModel):
    name: str
    type: str
    os: OSType = OSType.UBUNTU_20_04
    services: List[ServiceType] = []
    vulnerabilities: List[str] = []
    defense_tools: List[DefenseTool] = []
    ip: Optional[str] = None
    network: str = "dmz"
    cpu: int = 1
    memory: int = 1024
    safe_name: Optional[str] = None

    @validator('name')
    def validate_hostname(cls, v):
        v = v.replace('_', '-')
        if v.startswith('-'):
            v = 'vm' + v
        return v

class NetworkConfig(BaseModel):
    name: str
    subnet: str
    gateway: str
    dhcp: bool = True

class ScenarioConfig(BaseModel):
    name: str
    description: str
    networks: Dict[str, NetworkConfig] = {
        "dmz": NetworkConfig(name="dmz", subnet="192.168.1.0/24", gateway="192.168.1.1"),
        "internal": NetworkConfig(name="internal", subnet="10.0.0.0/24", gateway="10.0.0.1")
    }
    targets: List[TargetNode]
    attack_goals: List[str] = []
    tags: List[str] = []