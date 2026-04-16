from flask import Flask, jsonify, request
from flask_cors import CORS
import time

app = Flask(__name__)
CORS(app)

logs = []

@app.route("/api/health", methods=["GET"])
def api_health():
    """心跳检测 - 前端轮询此接口判断后端是否在线"""
    return jsonify({"status": "online", "time": time.strftime("%Y-%m-%d %H:%M:%S")})

@app.route("/api/generate", methods=["POST"])
def api_generate():
    prompt = request.json.get("prompt", "")
    
    # 🔥 修复：根据输入内容动态判断漏洞，不再写死
    vulns = []
    if "SQL注入" in prompt:
        vulns.append({"type": "SQL注入", "desc": "高危"})
    if "XSS" in prompt:
        vulns.append({"type": "XSS", "desc": "中危"})
    if "文件上传" in prompt:
        vulns.append({"type": "文件上传", "desc": "高危"})
    if "RCE" in prompt or "远程命令执行" in prompt:
        vulns.append({"type": "RCE", "desc": "极高危"})
    
    # 如果没匹配到具体漏洞，显示默认列表
    if not vulns:
        vulns = [
            {"type": "SQL注入", "desc": "高危"},
            {"type": "XSS", "desc": "中危"},
            {"type": "文件上传", "desc": "高危"},
            {"type": "RCE", "desc": "极高危"}
        ]

    logs.append(f"[生成] 靶场创建成功：{prompt}")
    
    return jsonify({
        "status": "ok",
        "range": {
            "name": "Web漏洞靶场",
            "ip": "172.20.0.2",
            "port": 8080,
            "status": "运行中",
            "createTime": time.strftime("%Y-%m-%d %H:%M:%S"),
            "cpu": 42,
            "mem": 65,
            "net": 73,
            "vulns": vulns  # ✅ 使用动态生成的漏洞列表
        }
    })

@app.route("/api/attack", methods=["POST"])
def api_attack():
    logs.append("[攻击] 正在进行漏洞利用...")
    return jsonify({"result": "ok"})

@app.route("/api/defense", methods=["POST"])
def api_defense():
    logs.append("[防御] 已拦截攻击流量")
    return jsonify({"result": "ok"})

@app.route("/api/logs", methods=["GET"])
def api_logs():
    return jsonify({"logs": logs})

if __name__ == "__main__":
    app.run(debug=True, port=5000)
