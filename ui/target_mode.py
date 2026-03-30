import streamlit as st
import asyncio
import pandas as pd

from orchestrator import Orchestrator
from ui.components import status_row, control_buttons
from utils.logger import Logger
from utils.helpers import DataHelper, ChartHelper

async def handle_generate(user_input):
    Logger.add_log(f"🚀 开始生成靶场: {user_input[:50]}...", "info")
    st.session_state.orchestrator = Orchestrator()

    try:
        result = await st.session_state.orchestrator.create_range(user_input)
        if result.get('status') == 'completed':
            vm_info = st.session_state.orchestrator.env_agent.get_vm_info()
            config = st.session_state.orchestrator.session_data['config']['targets']

            st.session_state.targets_info = []
            for i, t in enumerate(config):
                if i < len(vm_info):
                    st.session_state.targets_info.append({
                        'name': t['name'],
                        'type': t['type'],
                        'ip': vm_info[i]['ip'],
                        'vulnerabilities': t['vulnerabilities']
                    })
            Logger.add_log("✅ 靶场部署成功", "success")
        else:
            Logger.add_log("❌ 部署失败", "error")
    except Exception as e:
        Logger.add_log(f"❌ 错误: {e}", "error")

async def handle_attack():
    Logger.add_log("⚔️ 开始执行攻击...", "attack")
    try:
        if not st.session_state.orchestrator or not st.session_state.orchestrator.attack_agent:
            Logger.add_log("❌ 请先生成靶场", "error")
            return

        res = await st.session_state.orchestrator.attack_agent.execute_attacks(
            st.session_state.targets_info, None
        )
        st.session_state.attack_results = res
        Logger.add_log("✅ 攻击完成", "success")
    except Exception as e:
        Logger.add_log(f"❌ 攻击失败: {e}", "error")

async def handle_defense():
    Logger.add_log("🛡️ 开始防御分析...", "defense")
    try:
        if not st.session_state.orchestrator or not st.session_state.orchestrator.defense_agent:
            Logger.add_log("❌ 请先生成靶场", "error")
            return

        res = await st.session_state.orchestrator.defense_agent.monitor_and_respond(
            st.session_state.attack_results, st.session_state.targets_info
        )
        st.session_state.defense_results = res
        Logger.add_log("✅ 防御检测完成", "success")
    except Exception as e:
        Logger.add_log(f"❌ 防御失败: {e}", "error")

def render_target_mode():
    st.subheader("🎯 靶场生成模式")
    user_input, generate_btn, attack_btn, defense_btn = control_buttons(st.session_state.user_input)

    st.markdown("---")
    status_row()
    st.markdown("---")

    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📋 实时日志", "⚔️ 攻击结果", "🛡️ 防御结果", "📊 统计图表", "🌐 网络拓扑"
    ])

    with tab1:
        log_placeholder = st.empty()
        if st.session_state.messages:
            log_placeholder.markdown(Logger.get_log_html(st.session_state.messages), unsafe_allow_html=True)
        if st.button("🧹 清空日志"):
            st.session_state.messages = []
            st.rerun()

    with tab2:
        if st.session_state.attack_results:
            stats = DataHelper.process_attack_results(st.session_state.attack_results)
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("总攻击次数", stats['total'])
            c2.metric("成功率", f"{stats['success_rate']:.1f}%")
            c3.metric("攻击类型", stats['attack_types'])
            c4.metric("目标", stats['targets'])

            df = pd.DataFrame([{
                '阶段': a.get('phase', ''),
                '攻击类型': a.get('vulnerability', ''),
                '目标': a.get('target', ''),
                '结果': '✅ 成功' if a.get('success') else '❌ 失败'
            } for a in st.session_state.attack_results])
            st.dataframe(df, use_container_width=True)
        else:
            st.info("请先生成靶场并启动攻击")

    with tab3:
        if st.session_state.defense_results:
            detections = st.session_state.defense_results.get('detections', [])
            st.metric("检测到攻击", len(detections))
            df = pd.DataFrame([{
                '攻击类型': d.get('attack_type', ''),
                '置信度': f"{d.get('confidence', 0):.0%}"
            } for d in detections])
            st.dataframe(df, use_container_width=True)
        else:
            st.info("请先执行攻击")

    with tab4:
        if st.session_state.attack_results:
            fig = ChartHelper.create_attack_chart(st.session_state.attack_results)
            if fig:
                st.plotly_chart(fig, use_container_width=True)

    with tab5:
        if st.session_state.targets_info:
            for t in st.session_state.targets_info:
                st.markdown(f"**{t['name']}** | IP: {t['ip']} | 漏洞: {', '.join(t['vulnerabilities'])}")

    if generate_btn and user_input:
        st.session_state.messages = []
        asyncio.run(handle_generate(user_input))
        st.rerun()

    if attack_btn and st.session_state.orchestrator:
        asyncio.run(handle_attack())
        st.rerun()

    if defense_btn and st.session_state.orchestrator and st.session_state.attack_results:
        asyncio.run(handle_defense())
        st.rerun()