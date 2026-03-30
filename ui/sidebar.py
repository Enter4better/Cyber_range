# ui/sidebar.py
import streamlit as st
from config import PRESET_SCENARIOS, VULN_TYPES

def render_sidebar():
    """渲染侧边栏"""
    with st.sidebar:
        st.header("模式选择")
        mode = st.radio(
            "选择操作模式",
            ["🎯 靶场生成", "🔍 URL漏洞检测"],
            key="mode"
        )
        st.divider()
        
        if mode == "🎯 靶场生成":
            render_preset_scenarios()
            render_vuln_stats()
        
        return mode

def render_preset_scenarios():
    """渲染预设场景"""
    st.header("📋 预设场景")
    for name, desc in PRESET_SCENARIOS.items():
        if st.button(name, use_container_width=True):
            st.session_state.user_input = desc
            st.rerun()
    st.divider()

def render_vuln_stats():
    """渲染漏洞统计"""
    st.header("📊 支持的漏洞类型")
    for vuln, severity in VULN_TYPES.items():
        color = {
            "critical": "Critical🔴:",
            "high": "High🟠:",
            "medium": "Medium🟡:"
        }.get(severity, "⚪")
        st.write(f"{color} {vuln}")