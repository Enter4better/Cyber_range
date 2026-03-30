import random
from typing import Dict, List, Any
from .base import BaseVulnerability, VulnerabilityFactory

class SQLInjectionVulnerability(BaseVulnerability):
    """SQL注入漏洞"""
    
    def __init__(self):
        super().__init__(
            name="SQL注入",
            description="Web应用未正确过滤用户输入，导致可执行任意SQL语句",
            severity="high",
            cve_id="CVE-2021-1234"
        )
        
    def deploy(self, vm, vm_name: str, session_dir: str) -> bool:
        """部署SQL注入漏洞环境"""
        try:
            # 创建易受SQL注入的PHP页面
            php_code = """<?php
// 数据库配置
$host = 'localhost';
$username = 'root';
$password = 'root';
$database = 'testdb';

// 创建连接
$conn = new mysqli($host, $username, $password, $database);
if ($conn->connect_error) {
    die("连接失败: " . $conn->connect_error);
}

// 创建测试表
$conn->query("CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50),
    password VARCHAR(50),
    email VARCHAR(100)
)");

// 插入测试数据
$conn->query("INSERT IGNORE INTO users (username, password, email) VALUES 
    ('admin', 'Admin@123', 'admin@example.com'),
    ('user1', 'password123', 'user1@example.com'),
    ('test', 'test123', 'test@example.com')");

// 存在SQL注入漏洞的查询
if (isset($_GET['id'])) {
    $id = $_GET['id'];  // 未过滤，存在SQL注入
    $sql = "SELECT * FROM users WHERE id = $id";
    $result = $conn->query($sql);
    
    echo "<h2>查询结果：</h2>";
    if ($result && $result->num_rows > 0) {
        while($row = $result->fetch_assoc()) {
            echo "ID: " . $row['id'] . "<br>";
            echo "用户名: " . $row['username'] . "<br>";
            echo "密码: " . $row['password'] . "<br>";
            echo "邮箱: " . $row['email'] . "<br><br>";
        }
    } else {
        echo "未找到用户";
    }
}

// 存在SQL注入的登录功能
if (isset($_POST['username']) && isset($_POST['password'])) {
    $username = $_POST['username'];  // 未过滤
    $password = $_POST['password'];  // 未过滤
    
    $sql = "SELECT * FROM users WHERE username = '$username' AND password = '$password'";
    $result = $conn->query($sql);
    
    if ($result && $result->num_rows > 0) {
        echo "登录成功！";
        session_start();
        $_SESSION['user'] = $username;
    } else {
        echo "登录失败";
    }
}
?>

<html>
<body>
    <h1>SQL注入测试页面</h1>
    
    <h2>用户查询（通过ID）</h2>
    <form method="GET">
        ID: <input type="text" name="id">
        <input type="submit" value="查询">
    </form>
    
    <h2>登录</h2>
    <form method="POST">
        用户名: <input type="text" name="username"><br>
        密码: <input type="password" name="password"><br>
        <input type="submit" value="登录">
    </form>
</body>
</html>"""
            
            # 通过SSH写入文件
            vm.execute_ssh_command(
                session_dir,
                vm_name,
                f"sudo bash -c 'cat > /var/www/html/sqli.php << \"EOF\"\n{php_code}\nEOF'"
            )
            
            # 设置权限
            vm.execute_ssh_command(
                session_dir,
                vm_name,
                "sudo chmod 644 /var/www/html/sqli.php"
            )
            
            return True
        except Exception as e:
            print(f"部署SQL注入漏洞失败: {e}")
            return False
    
    def exploit(self, target_info: Dict[str, Any]) -> Dict[str, Any]:
        """执行SQL注入攻击"""
        ip = target_info.get('ip', 'unknown')
        
        # SQL注入payloads
        payloads = [
            "' OR '1'='1",
            "' UNION SELECT 1,2,3,4--",
            "admin' --",
            "' UNION SELECT username, password FROM users--",
            "1'; DROP TABLE users--",
            "' OR 1=1 LIMIT 1--",
            "' UNION SELECT @@version,2,3,4--"
        ]
        
        selected_payload = random.choice(payloads)
        
        # 随机决定成功概率
        success = random.random() > 0.3
        
        result = {
            'vulnerability': self.name,
            'target': ip,
            'payload': selected_payload,
            'success': success,
            'details': {}
        }
        
        if success:
            result['details'] = {
                'extracted_data': [
                    {'username': 'admin', 'password': 'Admin@123'},
                    {'username': 'user1', 'password': 'password123'}
                ],
                'database_version': 'MySQL 5.7.35',
                'current_user': 'root@localhost'
            }
        
        return result
    
    def detect(self, logs: str) -> Dict[str, Any]:
        """检测SQL注入攻击"""
        indicators = [
            "' or '1'='1",
            "' union select",
            "' and 1=1",
            "';--",
            "or '1'='1",
            "or 1=1",
            "admin' --",
            "waitfor delay",
            "sleep(",
            "benchmark("
        ]
        
        detected = False
        matched_indicators = []
        
        logs_lower = logs.lower()
        for indicator in indicators:
            if indicator.lower() in logs_lower:
                detected = True
                matched_indicators.append(indicator)
        
        confidence = len(matched_indicators) * 0.2 if detected else 0
        confidence = min(confidence, 1.0)
        
        return {
            'detected': detected,
            'confidence': confidence,
            'indicators': matched_indicators,
            'attack_type': self.name
        }
    
    def get_indicators(self) -> List[str]:
        return [
            "' OR '1'='1",
            "UNION SELECT",
            "DROP TABLE",
            "waitfor delay",
            "sleep(5)"
        ]
    
    def get_mitigation(self) -> List[str]:
        return [
            "使用参数化查询",
            "使用ORM框架",
            "输入验证和过滤",
            "最小权限原则",
            "使用WAF"
        ]

# 注册漏洞
VulnerabilityFactory.register('sqli', SQLInjectionVulnerability)
VulnerabilityFactory.register('sql_injection', SQLInjectionVulnerability)