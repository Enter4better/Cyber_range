from flask import Flask, render_template, jsonify, request
import asyncio

from orchestrator import Orchestrator

app = Flask(__name__)

orc = Orchestrator()
log_list = []
round_num = 0

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/generate', methods=['POST'])
def generate():
    prompt = request.json.get('prompt', 'web靶场')
    asyncio.run(orc.create_range(prompt))
    return jsonify({'status': 'ok'})

@app.route('/api/attack', methods=['POST'])
def attack():
    global round_num
    round_num += 1
    log = f"第{round_num}轮 | 攻击：SQL注入、XSS、文件上传、RCE"
    log_list.append(log)
    return jsonify({'log': log})

@app.route('/api/defense', methods=['POST'])
def defense():
    log = f"第{round_num}轮 | 防御：参数化查询、CSP、文件检测、命令拦截"
    log_list.append(log)
    return jsonify({'log': log})

@app.route('/api/logs')
def logs():
    return jsonify(log_list)

if __name__ == '__main__':
    app.run(debug=True)