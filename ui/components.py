# ui/components.py
import streamlit as st
from typing import Any, Optional
from utils.helpers import DataHelper

def metric_card(title: str, value: Any, caption: Optional[str] = None, card_type: str = "default"):
    """显示指标卡片"""
    card_class = {
        'attack': 'attack-card',
        'defense': 'defense-card',
        'default': 'metric-card'
    }.get(card_type, 'metric-card')
    
    st.markdown(f"<div class='{card_class}'>", unsafe_allow_html=True)
    st.metric(title, value)
    if caption:
        st.caption(caption)
    st.markdown("</div>", unsafe_allow_html=True)

def status_row():
    """显示系统状态行"""
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        env_status = "✅ 已就绪" if st.session_state.get('orchestrator') else "⏳ 未创建"
        session_id = st.session_state.orchestrator.session_id[:8] if st.session_state.get('orchestrator') else None
        metric_card("靶场状态", env_status, f"会话: {session_id}" if session_id else None)
    
    with col2:
        targets_info = st.session_state.get('targets_info', [])
        target_count = len(targets_info)
        ips = [t.get('ip', 'N/A') for t in targets_info[:2]] if targets_info else []
        metric_card("目标数量", target_count, f"IP: {', '.join(ips)}" if ips else None)
    
    with col3:
        attack_results = st.session_state.get('attack_results')
        if attack_results:
            stats = DataHelper.process_attack_results(attack_results)
            metric_card("攻击次数", stats['total'], 
                       f"成功: {stats['success_count']} | 失败: {stats['total'] - stats['success_count']}",
                       "attack")
        else:
            metric_card("攻击次数", 0, "等待攻击")
    
    with col4:
        defense_results = st.session_state.get('defense_results')
        if defense_results:
            stats = DataHelper.process_defense_results(defense_results)
            metric_card("检测次数", stats['total_detections'], 
                       f"响应: {stats['total_responses']}", "defense")
        else:
            metric_card("检测次数", 0, "等待防御")
    
    with col5:
        defense_results = st.session_state.get('defense_results')
        if defense_results:
            blocked = len(defense_results.get('blocked_ips', []))
            metric_card("封禁IP", blocked, "已自动封禁", "defense")
        else:
            metric_card("封禁IP", 0, "等待检测")

def control_buttons(user_input):
    """显示控制按钮"""
    col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
    
    with col1:
        st.subheader("📝 描述靶场")
        user_input = st.text_area(
            "请输入自然语言描述",
            value=user_input,
            height=100,
            label_visibility="collapsed",
            key="user_input_area",
            placeholder="例如：创建一个包含Web服务器和MySQL数据库的靶场，Web服务器要有SQL注入漏洞"
        )
    
    with col2:
        st.subheader("🏗️ 环境管理")
        generate_btn = st.button(
            "1. 生成靶场", 
            type="primary", 
            use_container_width=True,
            help="根据描述创建虚拟机环境"
        )
    
    with col3:
        st.subheader("⚔️ 攻击控制")
        attack_disabled = st.session_state.get('orchestrator') is None
        attack_btn = st.button(
            "2. 开始攻击", 
            type="secondary",
            use_container_width=True,
            disabled=attack_disabled,
            help="对靶场中的目标进行渗透攻击"
        )
    
    with col4:
        st.subheader("🛡️ 防御控制")
        defense_disabled = st.session_state.get('attack_results') is None
        defense_btn = st.button(
            "3. 启动防御", 
            type="secondary",
            use_container_width=True,
            disabled=defense_disabled,
            help="检测攻击并自动响应"
        )
    
    return user_input, generate_btn, attack_btn, defense_btn