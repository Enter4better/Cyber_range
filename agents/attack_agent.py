from .llm_agent import GLM5Agent

class AttackAgent:
    def __init__(self, session_id, env_agent):
        self.session_id = session_id
        self.env = env_agent
        self.llm = GLM5Agent()

    async def execute_attacks(self, targets_info, config=None):
        results = []

        for target in targets_info:
            target_name = target.get("name")
            ip = target.get("ip")
            vulns = target.get("vulnerabilities", [])

            for vuln in vulns:
                prompt = f"""
你是专业渗透测试AI，针对目标 {ip} 的 {vuln} 漏洞。
输出真实可用于测试的攻击Payload，不要多余解释。
返回格式：{{"payload":"...", "step":"...", "risk":"高/中/低"}}
"""
                # 真正调用大模型生成攻击内容
                ai_result = await self.llm.aask(prompt)

                results.append({
                    "phase": "exploit",
                    "vulnerability": vuln,
                    "target": target_name,
                    "ip": ip,
                    "ai_generated_payload": ai_result,  # 大模型输出真实Payload
                    "success": True,
                    "status": "AI攻击决策已完成"
                })

        return results