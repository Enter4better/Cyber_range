# app.py
import streamlit as st
import sys
import os

# 添加项目路径到系统路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 导入UI组件
from ui.styles import load_css
from ui.sidebar import render_sidebar
from ui.target_mode import render_target_mode
from ui.scan_mode import render_scan_mode
from config import APP_TITLE, APP_ICON

# 从config导入页面配置
st.set_page_config(
    page_title=APP_TITLE,
    page_icon=APP_ICON,
    layout="wide"
)

# 加载CSS
load_css()

# 初始化session state，全局状态管理（存储靶场配置、插件、运行状态）
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'orchestrator' not in st.session_state:
    st.session_state.orchestrator = None
if 'scenario_config' not in st.session_state:
    st.session_state.scenario_config = None
if 'user_input' not in st.session_state:
    st.session_state.user_input = ""
if 'attack_results' not in st.session_state:
    st.session_state.attack_results = None
if 'defense_results' not in st.session_state:
    st.session_state.defense_results = None
if 'targets_info' not in st.session_state:
    st.session_state.targets_info = []
if 'run_generate' not in st.session_state:
    st.session_state.run_generate = False
if 'run_attack' not in st.session_state:
    st.session_state.run_attack = False
if 'run_defense' not in st.session_state:
    st.session_state.run_defense = False

# 标题
st.title(f"{APP_ICON} {APP_TITLE}")
st.markdown("---")

# 渲染侧边栏并获取当前模式
mode = render_sidebar()

# 根据模式渲染不同界面
if mode == "🎯 靶场生成":
    render_target_mode()
else:
    render_scan_mode()

# 底部信息
st.markdown("---")
st.caption(f"{APP_ICON} {APP_TITLE} - 毕业设计项目")
st.caption("支持漏洞类型: SQL注入, XSS, 弱密码, RCE, LFI, 文件上传")