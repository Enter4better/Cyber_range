from pydantic import BaseModel
from typing import List
import json
import re

class TargetConfig(BaseModel):
    name: str
    type: str
    vulnerabilities: List[str]

class ScenarioConfig(BaseModel):
    name: str
    targets: List[TargetConfig]

class LLMCoordinator:
    async def parse_scenario(self, user_input: str) -> ScenarioConfig:
        vuln_map = {
            "sql injection": "sqli",
            "sqli": "sqli",
            "xss": "xss",
            "文件上传": "upload",
            "upload": "upload",
            "rce": "rce",
            "命令执行": "rce",
            "smb": "smb",
            "域渗透": "domain",
            "dvwa": "dvwa"
        }

        detected = []
        for keyword, vuln_name in vuln_map.items():
            if keyword in user_input.lower():
                detected.append(vuln_name)

        if not detected:
            detected = ["sqli", "xss"]

        return ScenarioConfig(
            name="dynamic_range",
            targets=[
                TargetConfig(
                    name="web1",
                    type="server",
                    vulnerabilities=detected
                )
            ]
        )