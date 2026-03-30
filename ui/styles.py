# ui/styles.py
import streamlit as st

def load_css():
    """加载自定义CSS样式"""
    st.markdown("""
    <style>
        .attack-log { color: #ff4b4b; font-weight: bold; }
        .defense-log { color: #4b9eff; font-weight: bold; }
        .success-log { color: #4bff4b; }
        .info-log { color: #ffffff; }
        .alert-log { color: #ffaa00; font-weight: bold; }
        .recon-log { color: #9b59b6; font-weight: bold; }
        .stTextArea textarea { font-family: monospace; }
        .log-container {
            height: 400px;
            overflow-y: auto;
            background-color: #1e1e1e;
            padding: 10px;
            border-radius: 5px;
            font-family: monospace;
            font-size: 12px;
        }
        .log-entry {
            margin: 2px 0;
            line-height: 1.4;
        }
        .stButton button {
            width: 100%;
        }
        .metric-card {
            background-color: #f0f2f6;
            padding: 15px;
            border-radius: 5px;
            text-align: center;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .attack-card {
            background-color: #ffebee;
            padding: 15px;
            border-radius: 5px;
            border-left: 4px solid #ff4b4b;
        }
        .defense-card {
            background-color: #e3f2fd;
            padding: 15px;
            border-radius: 5px;
            border-left: 4px solid #4b9eff;
        }
        .stat-box {
            background-color: white;
            padding: 10px;
            border-radius: 5px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }
    </style>
    """, unsafe_allow_html=True)