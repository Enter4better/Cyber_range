import random
from typing import Dict, List, Any
from .base import BaseVulnerability, VulnerabilityFactory

class LFIVulnerability(BaseVulnerability):
    """本地文件包含漏洞"""
    
    def __init__(self):
        super().__init__(
            name="本地文件包含",
            description="应用包含文件时未正确过滤用户输入，导致可读取任意文件",
            severity="high"
        )
        
    def deploy(self, vm, vm_name: str, session_dir: str) -> bool:
        """部署LFI漏洞环境"""
        try:
            # 创建易受LFI攻击的页面
            php_code = """<?php
// 本地文件包含漏洞
if (isset($_GET['page'])) {
    $page = $_GET['page'];  // 未过滤，存在LFI
    include($page . '.php');
}

// 另一种包含方式
if (isset($_GET['file'])) {
    $file = $_GET['file'];
    include($file);
}

// 创建一些敏感文件供读取
file_put_contents('/tmp/passwords.txt', "root:SuperSecretPassword123\\nadmin:Admin@2024\\nuser:password123");
file_put_contents('/var/www/html/config.php', "<?php\\n$db_host = 'localhost';\\n$db_user = 'root';\\n$db_pass = 'rootpassword';\\n$db_name = 'users';\\n?>");
?>

<html>
<body>
    <h1>LFI测试页面</h1>
    
    <h2>页面包含</h2>
    <form method="GET">
        页面: <input type="text" name="page" value="home">
        <input type="submit" value="包含">
    </form>
    
    <h2>文件读取</h2>
    <form method="GET">
        文件: <input type="text" name="file" value="/etc/passwd">
        <input type="submit" value="读取">
    </form>
    
    <?php
    // 正常页面内容
    if (isset($_GET['page']) && $_GET['page'] == 'home') {
        echo "<h3>欢迎来到首页</h3>";
    } elseif (isset($_GET['page']) && $_GET['page'] == 'about') {
        echo "<h3>关于我们</h3>";
    } elseif (isset($_GET['page']) && $_GET['page'] == 'contact') {
        echo "<h3>联系我们</h3>";
    }
    ?>
</body>
</html>"""
            
            vm.execute_ssh_command(
                session_dir,
                vm_name,
                f"sudo bash -c 'cat > /var/www/html/lfi.php << \"EOF\"\n{php_code}\nEOF'"
            )
            
            return True
        except Exception:
            return False
    
    def exploit(self, target_info: Dict[str, Any]) -> Dict[str, Any]:
        """执行LFI攻击"""
        ip = target_info.get('ip', 'unknown')
        
        files = [
            '../../../../etc/passwd',
            '../../../../etc/shadow',
            '../../../../var/www/html/config.php',
            'php://filter/convert.base64-encode/resource=index',
            '../../../../proc/self/environ',
            '../../../../var/log/apache2/access.log',
            '../../../../var/log/auth.log'
        ]
        
        selected_file = random.choice(files)
        success = random.random() > 0.3
        
        result = {
            'vulnerability': self.name,
            'target': ip,
            'file_attempted': selected_file,
            'success': success,
            'details': {}
        }
        
        if success:
            file_content = {
                '/etc/passwd': "root:x:0:0:root:/root:/bin/bash\ndaemon:x:1:1:daemon:/usr/sbin:/usr/sbin/nologin",
                '/etc/shadow': "root:$6$xyz$encrypted_hash:18937:0:99999:7:::",
                'config.php': "<?php $db_pass = 'rootpassword'; ?>"
            }
            
            result['details'] = {
                'file_read': selected_file,
                'file_content': file_content.get(selected_file, '敏感文件内容示例'),
                'contains_sensitive': 'password' in str(file_content).lower()
            }
        
        return result
    
    def detect(self, logs: str) -> Dict[str, Any]:
        """检测LFI攻击"""
        indicators = [
            "../../",
            "..\\",
            "/etc/passwd",
            "/etc/shadow",
            "php://filter",
            "file://",
            "expect://",
            "phar://",
            "zip://"
        ]
        
        detected = False
        matched_indicators = []
        
        logs_lower = logs.lower()
        for indicator in indicators:
            if indicator.lower() in logs_lower:
                detected = True
                matched_indicators.append(indicator)
        
        confidence = len(matched_indicators) * 0.25 if detected else 0
        confidence = min(confidence, 1.0)
        
        return {
            'detected': detected,
            'confidence': confidence,
            'indicators': matched_indicators,
            'attack_type': self.name
        }
    
    def get_indicators(self) -> List[str]:
        return ["../../", "/etc/passwd", "php://filter"]
    
    def get_mitigation(self) -> List[str]:
        return [
            "使用白名单限制可包含的文件",
            "禁用远程文件包含",
            "输入验证和过滤",
            "使用绝对路径",
            "设置open_basedir限制"
        ]

# 注册漏洞
VulnerabilityFactory.register('lfi', LFIVulnerability)
VulnerabilityFactory.register('file_inclusion', LFIVulnerability)