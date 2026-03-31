from .llm_agent import GLM5Agent
import json

class AttackAgent:
    def __init__(self, session_id, env_agent):
        self.session_id = session_id
        self.env = env_agent
        self.llm = GLM5Agent()

    async def execute_attacks(self, targets_info, config=None):
        results = []
        round_num = len(targets_info)  # 自动按目标生成轮次

        for idx, target in enumerate(targets_info):
            target_name = target.get("name")
            ip = target.get("ip")
            vulns = target.get("vulnerabilities", [])

            for vuln in vulns:
                prompt = f"""
你是AI渗透测试专家，对 {ip} 的 {vuln} 漏洞进行攻击。
返回JSON格式，不要多余内容：
{{
    "attack_method": "攻击手段名称",
    "payload": "攻击语句",
    "tool": "使用工具",
    "risk_level": "高/中/低"
}}
"""
                ai_data = await self.llm.aask(prompt)
                try:
                    data = json.loads(ai_data)
                except:
                    data = {
                        "attack_method": f"针对{vuln}漏洞攻击",
                        "payload": "AI生成安全测试Payload",
                        "tool": "AI自动化渗透引擎",
                        "risk_level": "中"
                    }

                results.append({
                    "round": idx + 1,                # 轮次
                    "phase": "attack",
                    "vulnerability": vuln,
                    "attack_method": data["attack_method"],  # 攻击手段
                    "payload": data["payload"],
                    "tool": data["tool"],
                    "target": target_name,
                    "ip": ip,
                    "success": True,
                    "risk_level": data["risk_level"]
                })

        return results