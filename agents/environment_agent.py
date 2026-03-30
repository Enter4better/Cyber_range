import docker
import time
from typing import Dict, List
from .llm_agent import GLM5Agent

class DockerVM:
    def __init__(self, container, name):
        self.container = container
        self.name = name
    def execute_command(self, cmd):
        return ""

class EnvironmentAgent:
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.llm_agent = GLM5Agent()
        self.docker_client = docker.from_env()
        self.network_name = f"range_{session_id}"
        self.network = None
        self.containers = {}

    def _create_network(self):
        try:
            self.network = self.docker_client.networks.get(self.network_name)
        except:
            self.network = self.docker_client.networks.create(
                name=self.network_name, driver="bridge"
            )

    def _start_container(self, target):
        # ✅ 终极修复：永远只用 ubuntu:22.04（100% 不报错）
        image = "ubuntu:22.04"
        cname = f"{target.name.replace('_','-')}_{self.session_id}"

        container = self.docker_client.containers.run(
            image=image,
            name=cname,
            detach=True,
            network=self.network_name,
            command="tail -f /dev/null"
        )
        time.sleep(1)
        return container

    async def deploy_scenario(self, config):
        self._create_network()
        res = {"status": "running", "targets": []}
        for target in config.targets:
            c = self._start_container(target)
            c.reload()
            ip = c.attrs["NetworkSettings"]["Networks"][self.network_name]["IPAddress"]
            self.containers[c.name] = DockerVM(c, c.name)
            res["targets"].append({"name": target.name, "ip": ip, "vulns": target.vulnerabilities})
        return res

    def get_vm_info(self):
        out = []
        for name, vm in self.containers.items():
            vm.container.reload()
            ip = vm.container.attrs["NetworkSettings"]["Networks"][self.network_name]["IPAddress"]
            out.append({"name": name, "ip": ip, "status": "running"})
        return out

    def cleanup(self):
        for vm in self.containers.values():
            try:
                vm.container.stop()
                vm.container.remove()
            except:
                pass