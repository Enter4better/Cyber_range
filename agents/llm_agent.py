import os
from dotenv import load_dotenv
from zhipuai import ZhipuAI

load_dotenv()

class GLM5Agent:
    def __init__(self):
        self.client = ZhipuAI(api_key=os.getenv("ZHIPU_API_KEY"))

    async def aask(self, prompt):
        resp = self.client.chat.completions.create(
            model="glm-4-flash", # ✅ 修复模型
            messages=[{"role":"user","content":prompt}]
        )
        return resp.choices[0].message.content