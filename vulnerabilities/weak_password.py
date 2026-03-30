import random
from typing import Dict, List, Any
from .base import BaseVulnerability, VulnerabilityFactory

class WeakPasswordVulnerability(BaseVulnerability):
    """弱密码漏洞"""
    
    def __init__(self):
        super().__init__(
            name="弱密码",
            description="系统使用弱密码，容易被暴力破解",
            severity="critical"
        )
        
    def deploy(self, vm, vm_name: str, session_dir: str) -> bool:
        """部署弱密码环境"""
        try:
            # 检查操作系统类型
            info = vm.execute_ssh_command(session_dir, vm_name, "cat /etc/os-release")
            
            if 'ubuntu' in info.lower() or 'debian' in info.lower():
                # Ubuntu/Debian系统
                commands = [
                    "echo 'root:123456' | sudo chpasswd",
                    "echo 'ubuntu:ubuntu' | sudo chpasswd",
                    "sudo useradd -m -s /bin/bash testuser || true",
                    "echo 'testuser:password123' | sudo chpasswd",
                    
                    # 配置SSH允许密码登录
                    "sudo sed -i 's/PasswordAuthentication no/PasswordAuthentication yes/' /etc/ssh/sshd_config",
                    "sudo systemctl restart sshd",
                    
                    # 创建包含密码的文件
                    "echo 'db_password=admin123' > /tmp/config.txt",
                    "echo 'mysql root password: root' >> /tmp/notes.txt"
                ]
                
                for cmd in commands:
                    vm.execute_ssh_command(session_dir, vm_name, cmd)
                    
            elif 'centos' in info.lower() or 'red hat' in info.lower():
                # CentOS/RHEL系统
                commands = [
                    "echo 'root:123456' | chpasswd",
                    "useradd -m testuser",
                    "echo 'testuser:password123' | chpasswd",
                    "sed -i 's/PasswordAuthentication no/PasswordAuthentication yes/' /etc/ssh/sshd_config",
                    "systemctl restart sshd"
                ]
                
                for cmd in commands:
                    vm.execute_ssh_command(session_dir, vm_name, f"sudo {cmd}")
            
            return True
        except Exception:
            return False
    
    def exploit(self, target_info: Dict[str, Any]) -> Dict[str, Any]:
        """执行密码破解"""
        ip = target_info.get('ip', 'unknown')
        service = target_info.get('service', 'ssh')
        
        # 常见弱密码字典
        weak_passwords = [
            '123456', 'password', '12345678', 'qwerty',
            'admin', 'root', '12345', 'letmein',
            'monkey', 'dragon', '111111', 'abc123',
            'ubuntu', 'toor', 'passw0rd', 'admin123'
        ]
        
        # 常见用户名
        usernames = ['root', 'admin', 'ubuntu', 'testuser', 'administrator']
        
        selected_username = random.choice(usernames)
        selected_password = random.choice(weak_passwords)
        
        # 根据服务类型决定成功率
        if service == 'ssh':
            success_probability = 0.6
        elif service == 'mysql':
            success_probability = 0.7
        elif service == 'ftp':
            success_probability = 0.8
        else:
            success_probability = 0.5
            
        success = random.random() < success_probability
        
        result = {
            'vulnerability': self.name,
            'target': ip,
            'service': service,
            'username_tried': selected_username,
            'password_tried': selected_password,
            'success': success,
            'details': {}
        }
        
        if success:
            result['details'] = {
                'credentials': {
                    'username': selected_username,
                    'password': selected_password
                },
                'access_level': 'root' if selected_username == 'root' else 'user',
                'service_access': f"成功登录{service}服务"
            }
        
        return result
    
    def detect(self, logs: str) -> Dict[str, Any]:
        """检测暴力破解尝试"""
        indicators = [
            "failed password",
            "authentication failure",
            "invalid user",
            "brute force",
            "many authentication failures",
            "pam_unix",
            "sshd.*Failed password",
            "sudo.*authentication failure"
        ]
        
        detected = False
        matched_indicators = []
        
        logs_lower = logs.lower()
        for indicator in indicators:
            if indicator.lower() in logs_lower:
                detected = True
                matched_indicators.append(indicator)
        
        # 检查失败次数
        fail_count = logs_lower.count('failed password')
        confidence = 0.3 + (fail_count * 0.1) if detected else 0
        confidence = min(confidence, 1.0)
        
        return {
            'detected': detected,
            'confidence': confidence,
            'indicators': matched_indicators,
            'fail_count': fail_count,
            'attack_type': self.name
        }
    
    def get_indicators(self) -> List[str]:
        return ["failed password", "authentication failure", "invalid user"]
    
    def get_mitigation(self) -> List[str]:
        return [
            "使用强密码策略",
            "启用多因素认证",
            "限制登录尝试次数",
            "使用SSH密钥替代密码",
            "定期更换密码"
        ]

# 注册漏洞
VulnerabilityFactory.register('weak_password', WeakPasswordVulnerability)
VulnerabilityFactory.register('weakpass', WeakPasswordVulnerability)