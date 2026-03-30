# ui/scan_mode.py
import streamlit as st
from simple_scanner import SimpleScanner
from config import TEST_URLS
from typing import Optional

def render_scan_mode():
    """渲染URL扫描模式"""
    st.subheader("🔍 URL漏洞检测")
    st.markdown("输入要检测的网址，系统将自动进行安全扫描")
    
    target_url = st.text_input(
        "目标网址",
        placeholder="https://example.com",
        help="请输入完整的URL，包含http://或https://"
    )
    
    col1, col2 = st.columns([1, 1])
    with col1:
        scan_btn = st.button("🔍 开始扫描", type="primary", use_container_width=True)
    with col2:
        if st.button("🔄 清空", use_container_width=True):
            st.rerun()
    
    if scan_btn and target_url:
        if not target_url.startswith(('http://', 'https://')):
            st.error("❌ 请输入完整的URL（以http://或https://开头）")
        else:
            with st.spinner(f"正在扫描 {target_url}..."):
                scanner = SimpleScanner()
                result = scanner.scan_url(target_url)
                
                if result['success']:
                    st.success("✅ 扫描完成！")
                    
                    # 基础信息
                    with st.expander("📊 基础信息", expanded=True):
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("状态码", result['info'].get('status_code', 'N/A'))
                        with col2:
                            server = result['info'].get('server', 'N/A')
                            st.metric("服务器", server[:30] + "..." if len(server) > 30 else server)
                        with col3:
                            st.metric("响应时间", f"{result['info'].get('response_time', 0):.2f}s")
                    
                    st.info(f"**扫描摘要**: {result.get('summary', '')}")
                    
                    # 漏洞列表
                    vulns = result.get('vulnerabilities', [])
                    if vulns:
                        st.warning(f"发现 {len(vulns)} 个潜在问题")
                        
                        high_vulns = [v for v in vulns if v.get('severity') == 'high']
                        medium_vulns = [v for v in vulns if v.get('severity') == 'medium']
                        low_vulns = [v for v in vulns if v.get('severity') == 'low']
                        
                        if high_vulns:
                            st.error("🔴 高危漏洞")
                            for v in high_vulns:
                                st.write(f"  • {v['name']}")
                        
                        if medium_vulns:
                            st.warning("🟡 中危漏洞")
                            for v in medium_vulns:
                                st.write(f"  • {v['name']}")
                        
                        if low_vulns:
                            st.info("🔵 低危漏洞")
                            for v in low_vulns:
                                st.write(f"  • {v['name']}")
                        
                        with st.expander("📋 查看详细漏洞信息"):
                            for i, v in enumerate(vulns, 1):
                                st.markdown(f"**{i}. {v['name']}**")
                                st.json(v)
                    else:
                        st.success("✅ 未发现明显漏洞")
                else:
                    st.error(f"❌ 扫描失败: {result.get('error', '未知错误')}")
    
    # 测试示例
    with st.expander("📋 测试示例"):
        for url in TEST_URLS:
            st.write(f"- `{url}`")
    
    # 使用说明
    with st.expander("ℹ️ 使用说明"):
        st.markdown("""
        **扫描器功能：**
        - 检查安全头配置
        - 检测服务器信息泄露
        - 检查表单CSRF保护
        - 检测URL参数风险
        - 检查HTTPS使用情况
        - 检测敏感路径泄露
        """)