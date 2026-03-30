# simple_scanner.py
import requests
import re
from typing import Dict, List
import ssl
import urllib3

# 禁用 SSL 警告（仅用于测试）
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class SimpleScanner:
    """纯Python实现的简单扫描器 - 无需任何外部命令"""
    
    def scan_url(self, url: str) -> Dict:
        """扫描URL"""
        results = {
            'success': True,
            'url': url,
            'vulnerabilities': [],
            'info': {},
            'summary': ''
        }
        
        try:
            # 发送请求
            response = requests.get(
                url,
                timeout=10,
                headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'},
                verify=False,  # 忽略 SSL 证书验证
                allow_redirects=True
            )
            
            # 基础信息
            results['info']['status_code'] = response.status_code
            results['info']['server'] = response.headers.get('Server', 'Unknown')
            results['info']['content_type'] = response.headers.get('Content-Type', 'Unknown')
            results['info']['response_time'] = response.elapsed.total_seconds()
            
            # 1. 检查安全头
            self._check_security_headers(response, results)
            
            # 2. 检查信息泄露
            self._check_information_disclosure(response, results)
            
            # 3. 检查表单
            self._check_forms(response, results)
            
            # 4. 检查 URL 参数
            self._check_url_parameters(url, results)
            
            # 5. 检查 HTTPS
            self._check_https(url, results)
            
            # 6. 检查敏感路径泄露
            self._check_sensitive_paths(response, results)
            
            # 7. 检查常见漏洞特征
            self._check_vulnerability_patterns(response, results)
            
            # 生成摘要
            results['summary'] = self._generate_summary(results)
            
        except requests.exceptions.ConnectionError:
            results['success'] = False
            results['error'] = '无法连接到目标网站，请检查网址是否正确'
        except requests.exceptions.Timeout:
            results['success'] = False
            results['error'] = '连接超时，网站响应太慢'
        except Exception as e:
            results['success'] = False
            results['error'] = str(e)
        
        return results
    
    def _check_security_headers(self, response, results):
        """检查安全头"""
        security_headers = {
            'X-Frame-Options': '点击劫持保护',
            'X-XSS-Protection': 'XSS保护',
            'Content-Security-Policy': '内容安全策略',
            'Strict-Transport-Security': 'HSTS',
            'X-Content-Type-Options': 'MIME类型保护',
            'Referrer-Policy': '来源策略'
        }
        
        for header, desc in security_headers.items():
            if header not in response.headers:
                results['vulnerabilities'].append({
                    'name': f'缺少 {desc} 头',
                    'severity': 'medium',
                    'type': 'missing_security_header'
                })
    
    def _check_information_disclosure(self, response, results):
        """检查信息泄露"""
        # 服务器版本
        if 'Server' in response.headers:
            server = response.headers['Server']
            results['vulnerabilities'].append({
                'name': f'服务器信息泄露: {server}',
                'severity': 'low',
                'type': 'server_disclosure'
            })
        
        # X-Powered-By 头
        if 'X-Powered-By' in response.headers:
            powered = response.headers['X-Powered-By']
            results['vulnerabilities'].append({
                'name': f'技术栈信息泄露: {powered}',
                'severity': 'low',
                'type': 'tech_disclosure'
            })
        
        # 版本号泄露
        version_patterns = [
            r'wordpress[_-]version[=:"]?([\d.]+)',
            r'php[_-]version[=:"]?([\d.]+)',
            r'jquery[_-]version[=:"]?([\d.]+)',
            r'bootstrap[_-]version[=:"]?([\d.]+)',
            r'laravel[_-]version[=:"]?([\d.]+)'
        ]
        
        for pattern in version_patterns:
            if re.search(pattern, response.text, re.IGNORECASE):
                results['vulnerabilities'].append({
                    'name': '源码中可能泄露了版本信息',
                    'severity': 'low',
                    'type': 'version_disclosure'
                })
                break
    
    def _check_forms(self, response, results):
        """检查表单"""
        if '<form' in response.text.lower():
            form_count = len(re.findall(r'<form', response.text, re.IGNORECASE))
            
            # 检查是否有 CSRF 保护
            has_csrf = 'csrf' in response.text.lower() or 'token' in response.text.lower()
            if not has_csrf:
                results['vulnerabilities'].append({
                    'name': f'发现 {form_count} 个表单，但未检测到 CSRF 保护',
                    'severity': 'medium',
                    'type': 'csrf_missing'
                })
            
            # 检查输入字段
            input_fields = re.findall(r'<input[^>]*>', response.text, re.IGNORECASE)
            if input_fields:
                # 检查敏感字段
                sensitive_fields = ['password', 'credit', 'card', 'ssn', 'idcard']
                for field in input_fields:
                    field_lower = field.lower()
                    for sensitive in sensitive_fields:
                        if sensitive in field_lower and 'type="password"' not in field_lower:
                            results['vulnerabilities'].append({
                                'name': f'敏感字段未使用密码输入类型: {sensitive}',
                                'severity': 'medium',
                                'type': 'sensitive_field_exposed'
                            })
                            break
    
    def _check_url_parameters(self, url, results):
        """检查 URL 参数"""
        if '?' in url and '=' in url:
            # 简单检测可能的 SQL 注入点
            results['vulnerabilities'].append({
                'name': 'URL 包含查询参数，可能存在 SQL 注入风险',
                'severity': 'high',
                'type': 'potential_sql_injection'
            })
            
            # 检测可能的 XSS 点
            if any(x in url for x in ['<script', 'alert(', 'javascript:']):
                results['vulnerabilities'].append({
                    'name': 'URL 参数中检测到可能的 XSS 攻击特征',
                    'severity': 'high',
                    'type': 'potential_xss'
                })
    
    def _check_https(self, url, results):
        """检查 HTTPS"""
        if not url.startswith('https'):
            results['vulnerabilities'].append({
                'name': '网站未使用 HTTPS 加密',
                'severity': 'high',
                'type': 'no_https'
            })
    
    def _check_sensitive_paths(self, response, results):
        """检查敏感路径泄露"""
        sensitive_paths = [
            '/admin', '/login', '/wp-admin', '/phpmyadmin', 
            '/backup', '/config', '/.git', '/.env',
            '/api', '/swagger', '/docs', '/test'
        ]
        
        response_text = response.text.lower()
        for path in sensitive_paths:
            if path in response_text:
                results['vulnerabilities'].append({
                    'name': f'页面中可能泄露了敏感路径: {path}',
                    'severity': 'medium',
                    'type': 'path_disclosure'
                })
                break
    
    def _check_vulnerability_patterns(self, response, results):
        """检查漏洞特征"""
        patterns = {
            'sql_error': (r'(sql error|mysql_fetch|oracle error|postgresql error)', 'SQL 错误信息泄露', 'high'),
            'xss_reflected': (r'(<script>alert|onerror=|javascript:)', '可能存在反射型 XSS', 'high'),
            'path_traversal': (r'(\.\./|\.\.\\)', '路径遍历特征', 'high'),
            'php_error': (r'(warning|error|notice):.*(on line|in file)', 'PHP 错误信息泄露', 'medium'),
            'debug_mode': (r'(debug mode|development mode|stack trace)', '调试模式开启', 'medium'),
            'backup_file': (r'(\.bak|\.old|\.backup|\.swp|~$)', '备份文件特征', 'medium')
        }
        
        response_text = response.text.lower()
        for key, (pattern, name, severity) in patterns.items():
            if re.search(pattern, response_text, re.IGNORECASE):
                results['vulnerabilities'].append({
                    'name': name,
                    'severity': severity,
                    'type': key
                })
    
    def _generate_summary(self, results: Dict) -> str:
        """生成结果摘要"""
        vulns = results.get('vulnerabilities', [])
        if not vulns:
            return "✅ 未发现明显漏洞"
        
        severity_count = {'high': 0, 'medium': 0, 'low': 0}
        for v in vulns:
            severity_count[v.get('severity', 'low')] += 1
        
        return f"发现 {len(vulns)} 个潜在问题（高危:{severity_count['high']} 中危:{severity_count['medium']} 低危:{severity_count['low']}）"
    
    def quick_scan(self, url: str) -> str:
        """快速扫描返回文本结果"""
        result = self.scan_url(url)
        
        if not result['success']:
            return f"❌ 扫描失败: {result.get('error', '未知错误')}"
        
        output = []
        output.append("=" * 60)
        output.append(f"📌 URL: {url}")
        output.append(f"📊 状态码: {result['info'].get('status_code')}")
        output.append(f"🖥️ 服务器: {result['info'].get('server')}")
        output.append(f"⏱️ 响应时间: {result['info'].get('response_time', 0):.2f}秒")
        output.append("=" * 60)
        
        if result['vulnerabilities']:
            output.append("\n🔍 发现的问题:")
            for i, v in enumerate(result['vulnerabilities'], 1):
                severity = v.get('severity', 'low')
                if severity == 'high':
                    mark = '🔴'
                elif severity == 'medium':
                    mark = '🟡'
                else:
                    mark = '🔵'
                output.append(f"  {mark} [{severity.upper()}] {v['name']}")
        else:
            output.append("\n✅ 未发现明显漏洞")
        
        output.append(f"\n📋 {result['summary']}")
        
        return '\n'.join(output)