import uuid
import asyncio
from datetime import datetime
from typing import Optional

from llm_coordinator import LLMCoordinator
from agents.environment_agent import EnvironmentAgent
from agents.attack_agent import AttackAgent
from agents.defense_agent import DefenseAgent

class Orchestrator:
    def __init__(self, websocket=None):
        self.session_id = str(uuid.uuid4())[:8]
        self.websocket = websocket
        self.llm = LLMCoordinator()
        
        self.env_agent = None
        self.attack_agent = None
        self.defense_agent = None

        self.session_data = {
            'session_id': self.session_id,
            'created_at': datetime.now().isoformat(),
            'status': 'initialized',
            'user_prompt': '',
            'config': None,
            'deployment': None,
            'attack_results': [],
            'defense_results': []
        }

    async def create_range(self, user_prompt: str) -> dict:
        await self._send_update("🚀 开始生成靶场...", "info")

        config = await self.llm.parse_scenario(user_prompt)
        self.session_data['user_prompt'] = user_prompt
        self.session_data['config'] = config.dict()

        self.env_agent = EnvironmentAgent(self.session_id)
        deployment_info = await self.env_agent.deploy_scenario(config)

        if deployment_info.get('status') != 'running':
            await self._send_update("❌ 容器部署失败", "error")
            return {'status': 'failed'}

        await self._send_update("✅ Docker 容器启动成功", "success")

        vm_info = self.env_agent.get_vm_info()
        for i, target in enumerate(config.targets):
            if i < len(vm_info):
                target.ip = vm_info[i]['ip']

        self.session_data['deployment'] = {
            'vms': vm_info,
            'targets': [t.dict() for t in config.targets]
        }

        self.attack_agent = AttackAgent(self.session_id, self.env_agent)
        self.defense_agent = DefenseAgent(self.session_id, self.env_agent)

        try:
            attack_results = await self.attack_agent.execute_attacks(
                [t.dict() for t in config.targets], config
            )
            self.session_data['attack_results'] = attack_results

            defense_results = await self.defense_agent.monitor_and_respond(
                attack_results, [t.dict() for t in config.targets]
            )
            self.session_data['defense_results'] = defense_results
        except Exception as e:
            print(f"攻防执行异常: {e}")

        self.session_data['status'] = 'completed'
        await self._send_update("🎯 攻防演练全部完成！", "success")
        return self.session_data

    async def _send_update(self, message: str, level: str = "info"):
        from utils.logger import Logger
        Logger.add_log(message, level)
        print(f"[{level}] {message}")

    def cleanup(self):
        if self.env_agent:
            self.env_agent.cleanup()