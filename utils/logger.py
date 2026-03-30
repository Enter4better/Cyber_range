# utils/logger.py
from datetime import datetime
import streamlit as st

class Logger:
    """日志处理类"""
    
    @staticmethod
    def add_log(message: str, level: str = "info"):
        """添加日志到session state"""
        if 'messages' not in st.session_state:
            st.session_state.messages = []
            
        st.session_state.messages.append({
            'timestamp': datetime.now().strftime('%H:%M:%S'),
            'level': level,
            'message': message
        })
    
    @staticmethod
    def get_log_html(messages, max_lines=50):
        """生成日志HTML"""
        log_html = "<div class='log-container'>"
        for msg in messages[-max_lines:]:
            timestamp = msg.get('timestamp', '')
            level = msg.get('level', 'info')
            content = msg.get('message', '')
            
            css_class = {
                'attack': 'attack-log',
                'defense': 'defense-log',
                'recon': 'recon-log',
                'alert': 'alert-log',
                'success': 'success-log',
                'error': 'attack-log'
            }.get(level, 'info-log')
            
            icon = {
                'attack': '⚔️',
                'defense': '🛡️',
                'recon': '📡',
                'alert': '⚠️',
                'success': '✅',
                'error': '❌'
            }.get(level, '')
            
            log_html += f"<div class='log-entry {css_class}'>[{timestamp}] {icon} {content}</div>"
        log_html += "</div>"
        return log_html