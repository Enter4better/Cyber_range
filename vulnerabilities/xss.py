import random
from typing import Dict, List, Any
from .base import BaseVulnerability, VulnerabilityFactory

class XSSVulnerability(BaseVulnerability):
    """XSS跨站脚本漏洞"""
    
    def __init__(self):
        super().__init__(
            name="XSS",
            description="Web应用未正确过滤用户输入，导致可注入恶意脚本",
            severity="medium",
            cve_id="CVE-2021-2345"
        )
        
    def deploy(self, vm, vm_name: str, session_dir: str) -> bool:
        """部署XSS漏洞环境"""
        try:
            # 创建易受XSS攻击的留言板
            php_code = """<?php
// 留言板功能 - 存在XSS漏洞
session_start();

// 初始化留言文件
$message_file = '/tmp/messages.txt';

// 添加留言
if ($_SERVER['REQUEST_METHOD'] === 'POST' && isset($_POST['message'])) {
    $message = $_POST['message'];  // 未过滤，存在XSS
    $timestamp = date('Y-m-d H:i:s');
    $username = $_SESSION['username'] ?? '匿名';
    
    $entry = "[$timestamp] $username: $message\\n";
    file_put_contents($message_file, $entry, FILE_APPEND);
}

// 搜索功能 - 反射型XSS
if (isset($_GET['search'])) {
    $search = $_GET['search'];  // 未过滤，存在XSS
    echo "<div class='search-result'>您搜索的关键词: " . $search . "</div>";
}

// 读取留言
$messages = file_exists($message_file) ? file($message_file) : [];
?>

<html>
<head>
    <title>XSS测试留言板</title>
</head>
<body>
    <h1>留言板</h1>
    
    <h2>搜索</h2>
    <form method="GET">
        <input type="text" name="search" placeholder="搜索关键词...">
        <input type="submit" value="搜索">
    </form>
    
    <h2>留言</h2>
    <form method="POST">
        <textarea name="message" rows="4" cols="50" placeholder="输入留言..."></textarea><br>
        <input type="submit" value="提交留言">
    </form>
    
    <h2>所有留言</h2>
    <div class="messages">
        <?php foreach($messages as $msg): ?>
            <div class="message"><?php echo $msg; ?></div>
        <?php endforeach; ?>
    </div>
    
    <!-- 用户资料页面 - 存储型XSS -->
    <?php
    if (isset($_GET['profile'])) {
        $profile = $_GET['profile'];
        echo "<div class='profile'>用户资料: " . $profile . "</div>";
    }
    ?>
</body>
</html>"""
            
            vm.execute_ssh_command(
                session_dir,
                vm_name,
                f"sudo bash -c 'cat > /var/www/html/xss.php << \"EOF\"\n{php_code}\nEOF'"
            )
            
            return True
        except Exception:
            return False
    
    def exploit(self, target_info: Dict[str, Any]) -> Dict[str, Any]:
        """执行XSS攻击"""
        ip = target_info.get('ip', 'unknown')
        
        payloads = [
            "<script>alert('XSS')</script>",
            "<img src=x onerror=alert(1)>",
            "<svg onload=alert(document.cookie)>",
            "javascript:alert('XSS')",
            "<body onload=alert('XSS')>",
            "<input onfocus=alert(1) autofocus>",
            "<details open ontoggle=alert(1)>"
        ]
        
        selected_payload = random.choice(payloads)
        success = random.random() > 0.2
        
        result = {
            'vulnerability': self.name,
            'target': ip,
            'payload': selected_payload,
            'success': success,
            'details': {}
        }
        
        if success:
            injection_type = random.choice(['反射型', '存储型', 'DOM型'])
            result['details'] = {
                'injection_type': injection_type,
                'stolen_data': {
                    'cookies': 'session_id=abc123xyz',
                    'local_storage': 'token=user_token_456',
                    'session_info': '已获取管理员会话'
                } if random.random() > 0.5 else None
            }
        
        return result
    
    def detect(self, logs: str) -> Dict[str, Any]:
        """检测XSS攻击"""
        indicators = [
            "<script>",
            "<img src=x onerror=",
            "<svg onload=",
            "javascript:",
            "alert(",
            "prompt(",
            "confirm(",
            "document.cookie",
            "onerror=",
            "onload=",
            "onfocus="
        ]
        
        detected = False
        matched_indicators = []
        
        logs_lower = logs.lower()
        for indicator in indicators:
            if indicator.lower() in logs_lower:
                detected = True
                matched_indicators.append(indicator)
        
        confidence = len(matched_indicators) * 0.15 if detected else 0
        
        return {
            'detected': detected,
            'confidence': min(confidence, 1.0),
            'indicators': matched_indicators,
            'attack_type': self.name
        }
    
    def get_indicators(self) -> List[str]:
        return ["<script>", "onerror=", "javascript:", "alert("]
    
    def get_mitigation(self) -> List[str]:
        return [
            "输入验证和过滤",
            "输出编码",
            "使用Content-Security-Policy",
            "设置HttpOnly Cookie",
            "使用X-XSS-Protection头"
        ]

# 注册漏洞
VulnerabilityFactory.register('xss', XSSVulnerability)