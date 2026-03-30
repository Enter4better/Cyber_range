# config.py
import os

# 应用配置
APP_TITLE = "AI驱动的靶场自动生成系统"
APP_ICON = "🎯"
APP_LAYOUT = "wide"

# 预设场景
PRESET_SCENARIOS = {
    "Web渗透测试": "创建一个Web渗透测试环境，包含一个存在SQL注入和XSS漏洞的Web服务器，以及一个MySQL数据库。部署WAF进行防护。",
    "内网横向移动": "创建一个域环境，包含域控制器、两台Windows客户端。域控存在SMB漏洞，目标是获取域控权限。",
    "漏洞演练平台": "创建一个包含多种漏洞的Web应用，包括SQL注入、XSS、文件上传和RCE漏洞，用于安全测试培训。",
    "红蓝对抗": "创建红蓝对抗环境，蓝队使用Kali攻击机，红队部署Snort和WAF进行防御。"
}

# 漏洞类型
VULN_TYPES = {
    "SQL注入": "high",
    "XSS": "medium", 
    "弱密码": "critical",
    "RCE": "critical",
    "LFI": "high",
    "文件上传": "high"
}

# 测试URL示例
TEST_URLS = [
    "http://testphp.vulnweb.com/",
    "https://juice-shop.herokuapp.com/",
    "http://demo.testfire.net/"
]