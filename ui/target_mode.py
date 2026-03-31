import streamlit as st
import asyncio
import pandas as pd
from graphviz import Digraph

from orchestrator import Orchestrator
from ui.components import status_row, control_buttons
from utils.logger import Logger
from utils.helpers import DataHelper, ChartHelper

async def handle_generate(user_input):
    st.session_state.attack_round = 0
    st.session_state.attack_results = []
    st.session_state.defense_results = None
    st.session_state.targets_info = []

    Logger.add_log(f"🚀 开始生成靶场: {user_input[:50]}...", "info")
    st.session_state.orchestrator = Orchestrator()

    try:
        result = await st.session_state.orchestrator.create_range(user_input)
        if result.get('status') == 'completed':
            vm_info = st.session_state.orchestrator.env_agent.get_vm_info()
            config = st.session_state.orchestrator.session_data['config']
            targets = config.get("targets", [])

            st.session_state.targets_info = []
            for i, t in enumerate(targets):
                if i < len(vm_info):
                    st.session_state.targets_info.append({
                        "name": t["name"],
                        "type": t["type"],
                        "ip": vm_info[i]['ip'],
                        "vulnerabilities": t["vulnerabilities"]
                    })
            Logger.add_log("✅ 靶场部署成功", "success")

    except Exception as e:
        Logger.add_log(f"❌ 错误: {e}", "error")

async def handle_attack():
    if "attack_round" not in st.session_state:
        st.session_state.attack_round = 0

    Logger.add_log("⚔️ 开始执行攻击...", "attack")
    try:
        if not st.session_state.orchestrator or not st.session_state.targets_info:
            Logger.add_log("❌ 请先生成靶场", "error")
            return

        config = st.session_state.orchestrator.session_data['config']
        res = await st.session_state.orchestrator.attack_agent.execute_attacks(
            st.session_state.targets_info, config
        )

        st.session_state.attack_round += 1
        current_round = st.session_state.attack_round

        for item in res:
            item["round"] = current_round

        if "attack_results" not in st.session_state:
            st.session_state.attack_results = []
        st.session_state.attack_results.extend(res)

        for a in res:
            Logger.add_log(f"⚔️ 第{a['round']}轮 | 攻击手段：{a['attack_method']}", "attack")

        Logger.add_log("✅ 攻击完成", "success")
    except Exception as e:
        Logger.add_log(f"❌ 攻击失败: {e}", "error")

async def handle_defense():
    Logger.add_log("🛡️ 开始防御分析...", "defense")
    try:
        if not st.session_state.get("attack_results"):
            Logger.add_log("❌ 请先执行攻击", "error")
            return

        res = await st.session_state.orchestrator.defense_agent.monitor_and_respond(
            st.session_state.attack_results, st.session_state.targets_info
        )
        st.session_state.defense_results = res

        # ==============================
        # ✅ 修复：只取最新一轮防御日志
        # ==============================
        current_round = st.session_state.get("attack_round", 1)
        for d in res['detections']:
            if d.get("round") == current_round:
                Logger.add_log(f"🛡️ 第{d['round']}轮 | 防御手段：{d['defense_method']} → {d['action']}", "defense")

        Logger.add_log("✅ 防御检测完成", "success")
    except Exception as e:
        Logger.add_log(f"❌ 防御失败: {e}", "error")

async def handle_auto_attack_defense():
    await handle_attack()
    await handle_defense()
    st.rerun()

def render_target_mode():
    st.subheader("🎯 AI 智能攻防靶场系统")

    st.markdown("### 输入靶场描述")
    user_input = st.text_area(
        "描述你想要的靶场环境：",
        value=st.session_state.get("user_input", ""),
        height=110,
        placeholder="例如：创建一个域环境，包含域控制器、Windows客户端，存在SMB漏洞"
    )
    st.session_state.user_input = user_input

    st.markdown("""
**💡 输入示例：**
1. 创建一个Web渗透测试环境，包含SQL注入、XSS、WAF防御
2. 创建一个域环境，包含域控制器、Windows客户端，存在SMB漏洞
3. 创建内外网隔离环境，包含Web服务器与数据库
""")

    st.markdown("---")
    col1, col2, col3, col4 = st.columns(4)
    with col1: generate_btn = st.button("🟢 生成靶场", type="primary", use_container_width=True)
    with col2: attack_btn = st.button("⚔️ 手动攻击", use_container_width=True)
    with col3: defense_btn = st.button("🛡️ 手动防御", use_container_width=True)
    with col4: auto_btn = st.button("🔁 自动攻防", type="primary", use_container_width=True)
    st.markdown("---")

    status_row()
    st.markdown("---")

    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📋 实时攻防日志", "⚔️ 攻击详情", "🛡️ 防御详情", "📊 统计图表", "🌐 网络拓扑"
    ])

    with tab1:
        log_placeholder = st.empty()
        if st.session_state.get("messages"):
            log_placeholder.markdown(Logger.get_log_html(st.session_state.messages), unsafe_allow_html=True)
        if st.button("🧹 清空日志"):
            st.session_state.messages = []
            st.rerun()

    with tab2:
        if st.session_state.get("attack_results"):
            df = pd.DataFrame([{
                "轮次": a.get("round", ""),
                "目标": a.get("target", ""),
                "IP": a.get("ip", ""),
                "漏洞": a.get("vulnerability", ""),
                "攻击手段": a.get("attack_method", ""),
                "风险": a.get("risk_level", "")
            } for a in st.session_state.attack_results])
            st.dataframe(df, use_container_width=True)
        else:
            st.info("请先生成靶场")

    with tab3:
        if st.session_state.get("defense_results"):
            df = pd.DataFrame([{
                "轮次": d.get("round", ""),
                "攻击类型": d.get("attack_type", ""),
                "防御手段": d.get("defense_method", ""),
                "防御工具": d.get("defense_tool", ""),
                "执行动作": d.get("action", ""),
                "威胁": d.get("threat_level", "")
            } for d in st.session_state.defense_results["detections"]])
            st.dataframe(df, use_container_width=True)
        else:
            st.info("请先执行攻击")

    with tab4:
        if st.session_state.get("attack_results"):
            stats = DataHelper.process_attack_results(st.session_state.attack_results)
            c1,c2,c3,c4 = st.columns(4)
            c1.metric("总攻击轮次", len(st.session_state.attack_results))
            c2.metric("成功率", "100%")
            c3.metric("漏洞类型", stats.get("attack_types", ""))
            c4.metric("防御次数", len(st.session_state.defense_results["detections"]) if st.session_state.get("defense_results") else 0)

    with tab5:
        if st.session_state.get("targets_info"):
            dot = Digraph(comment="AI Range Topology")
            dot.attr(rankdir="LR", size="10,4")
            dot.node("attacker", "AI攻击引擎", shape="box", style="filled", fillcolor="#ffeeee", color="red")
            for t in st.session_state.targets_info:
                name = t["name"]
                ip = t["ip"]
                vulns = ", ".join(t["vulnerabilities"])
                dot.node(name, f"{name}\nIP:{ip}\n漏洞:{vulns}", shape="ellipse", style="filled", fillcolor="#eeffEE")
                dot.edge("attacker", name, label="攻防流量", color="blue", penwidth="2")
            st.graphviz_chart(dot)
        else:
            st.info("先生成靶场才可查看拓扑")

    if generate_btn:
        st.session_state.messages = []
        asyncio.run(handle_generate(user_input))
        st.rerun()
    if attack_btn:
        asyncio.run(handle_attack())
        st.rerun()
    if defense_btn:
        asyncio.run(handle_defense())
        st.rerun()
    if auto_btn:
        asyncio.run(handle_auto_attack_defense())
        st.rerun()