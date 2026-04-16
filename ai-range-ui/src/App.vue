<template>
  <div class="app-root" id="app-root">
    <!-- Three.js 动态粒子背景 -->
    <canvas id="bg-canvas"></canvas>

    <!-- 后端离线提示 -->
    <div v-if="!backendOnline" class="backend-offline glass-card fixed top-4 left-1/2 -translate-x-1/2 z-50 flex items-center gap-3 px-5 py-3 rounded-2xl">
      <div class="offline-dot"></div>
      <span class="text-sm font-medium">后端服务未启动，请先运行：<code class="text-cyan-300">cd backend && python app.py</code></span>
      <el-button size="small" type="primary" @click="checkBackend">重试</el-button>
    </div>

    <!-- 主内容层 -->
    <div class="content-layer">

      <!-- 顶部导航栏 - 玻璃质感 -->
      <header class="glass-nav">
        <div class="nav-brand">
          <div class="brand-icon">
            <svg width="28" height="28" viewBox="0 0 24 24" fill="none">
              <path d="M12 2L2 7l10 5 10-5-10-5z" fill="#22d3ee" opacity="0.8"/>
              <path d="M2 17l10 5 10-5M2 12l10 5 10-5" stroke="#22d3ee" stroke-width="2" stroke-linecap="round"/>
            </svg>
          </div>
          <span class="brand-text">AI 攻防靶场</span>
        </div>

        <!-- 玻璃质感导航 tabs -->
        <div class="glass-tabs">
          <button
            v-for="(tab, idx) in tabs"
            :key="idx"
            :class="['glass-tab', activeTab === idx ? 'active' : '']"
            @click="activeTab = idx"
          >
            <span class="tab-icon">{{ tab.icon }}</span>
            {{ tab.name }}
          </button>
        </div>

        <el-button type="primary" size="small" class="glass-btn" @click="fullScreen">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M8 3H5a2 2 0 00-2 2v3m18 0V5a2 2 0 00-2-2h-3m0 18h3a2 2 0 002-2v-3M3 16v3a2 2 0 002 2h3"/></svg>
          全屏
        </el-button>
      </header>

      <!-- 主面板 -->
      <main class="main-content">

        <!-- 控制台 -->
        <div v-show="activeTab === 0" class="tab-panel">

          <!-- 靶场生成区 -->
          <div class="glass-card prompt-card">
            <div class="prompt-header">
              <span class="prompt-label">🎯 靶场生成</span>
              <span class="prompt-hint">输入漏洞靶场描述，AI 自动构建攻防场景</span>
            </div>
            <el-input
              v-model="prompt"
              type="textarea"
              :rows="2"
              placeholder="输入靶场描述，例如：创建包含SQL注入、XSS的Web靶场"
              class="glass-input"
            />
            <div class="prompt-actions">
              <el-button type="success" size="large" class="action-btn attack-btn" @click="generateRange">
                <span>🚀</span> 生成靶场
              </el-button>
            </div>
          </div>

          <!-- 靶场信息三卡片 -->
          <div v-if="rangeData.name" class="info-grid">
            <div class="glass-card info-card">
              <div class="card-header">
                <span class="card-icon">📡</span>
                <span class="card-title">靶场概览</span>
              </div>
              <div class="info-list">
                <div class="info-row"><span class="info-key">名称</span><span class="info-val">{{ rangeData.name }}</span></div>
                <div class="info-row"><span class="info-key">IP</span><span class="info-val mono">{{ rangeData.ip }}</span></div>
                <div class="info-row"><span class="info-key">端口</span><span class="info-val mono">{{ rangeData.port }}</span></div>
                <div class="info-row"><span class="info-key">时间</span><span class="info-val">{{ rangeData.createTime }}</span></div>
              </div>
            </div>

            <div class="glass-card info-card">
              <div class="card-header">
                <span class="card-icon">💣</span>
                <span class="card-title">漏洞详情</span>
              </div>
              <div class="vuln-tags">
                <span v-for="(vuln, idx) in rangeData.vulns" :key="idx" :class="['vuln-tag', getVulnClass(vuln.type)]">
                  <span class="vuln-dot"></span>
                  {{ vuln.type }}
                  <span class="vuln-level">{{ vuln.desc }}</span>
                </span>
              </div>
            </div>

            <div class="glass-card info-card">
              <div class="card-header">
                <span class="card-icon">📊</span>
                <span class="card-title">状态监控</span>
              </div>
              <div class="monitor-list">
                <div class="monitor-row">
                  <span class="monitor-label">CPU 使用率</span>
                  <el-progress :percentage="rangeData.cpu" :color="cpuColor" :stroke-width="5" class="mini-progress" />
                </div>
                <div class="monitor-row">
                  <span class="monitor-label">内存使用率</span>
                  <el-progress :percentage="rangeData.mem" color="#34d399" :stroke-width="5" class="mini-progress" />
                </div>
                <div class="monitor-row">
                  <span class="monitor-label">网络流量</span>
                  <el-progress :percentage="rangeData.net" color="#60a5fa" :stroke-width="5" class="mini-progress" />
                </div>
              </div>
            </div>
          </div>

          <!-- 统计卡片 + 攻防进度条 -->
          <div class="stats-row">
            <div class="glass-card stat-card">
              <div class="stat-icon red">⚔️</div>
              <div class="stat-body">
                <div class="stat-label">攻防轮次</div>
                <div class="stat-value">{{ round }}</div>
              </div>
            </div>
            <div class="glass-card stat-card">
              <div class="stat-icon orange">💥</div>
              <div class="stat-body">
                <div class="stat-label">攻击次数</div>
                <div class="stat-value red">{{ attackCount }}</div>
              </div>
            </div>
            <div class="glass-card stat-card">
              <div class="stat-icon blue">🛡️</div>
              <div class="stat-body">
                <div class="stat-label">防御次数</div>
                <div class="stat-value blue">{{ defenseCount }}</div>
              </div>
            </div>
            <div class="glass-card stat-card">
              <div class="stat-icon purple">🔒</div>
              <div class="stat-body">
                <div class="stat-label">威胁等级</div>
                <div class="stat-value purple">高</div>
              </div>
            </div>
          </div>

          <!-- 全局进度条 -->
          <div v-if="progress > 0" class="glass-card progress-card">
            <div class="progress-header">
              <span>⚔️ 攻防进行中</span>
              <span>{{ progress }}%</span>
            </div>
            <div class="progress-track">
              <div class="progress-fill" :style="{ width: progress + '%' }"></div>
            </div>
          </div>

          <!-- 操作按钮组 - 攻防PK动态边框 -->
          <div class="glass-card pk-card">
            <div class="pk-inner">
              <!-- 攻击区 -->
              <div class="pk-side attack-side">
                <div class="pk-border attack-border"></div>
                <div class="pk-content">
                  <div class="pk-title red">红方 · 攻击</div>
                  <el-button type="danger" size="large" class="action-btn" @click="launchAttack">执行攻击</el-button>
                </div>
              </div>

              <!-- VS -->
              <div class="pk-vs">
                <div class="vs-ring">
                  <span>VS</span>
                </div>
              </div>

              <!-- 防御区 -->
              <div class="pk-side defense-side">
                <div class="pk-border defense-border"></div>
                <div class="pk-content">
                  <div class="pk-title blue">蓝方 · 防御</div>
                  <el-button type="primary" size="large" class="action-btn" @click="launchDefense">启动防御</el-button>
                </div>
              </div>
            </div>
            <!-- 中心自动按钮 -->
            <div class="auto-run-row">
              <el-button type="warning" size="large" class="action-btn auto-btn" @click="autoRun">
                <span>⚡</span> 自动攻防
              </el-button>
            </div>
          </div>

          <!-- 日志面板 -->
          <div class="glass-card log-card">
            <div class="log-header">
              <span>📜 攻防日志</span>
              <span class="log-count">{{ logs.length }} 条</span>
            </div>
            <div class="log-body" ref="logBodyRef">
              <div v-for="(log, idx) in logs" :key="idx" class="log-line">
                <span class="log-num">[{{ idx + 1 }}]</span>
                <span :class="getLogClass(log)">{{ log }}</span>
              </div>
              <div v-if="!logs.length" class="log-empty">暂无日志，等待攻防开始...</div>
            </div>
          </div>

          <!-- 网络拓扑图 -->
          <div class="glass-card topo-card">
            <div class="log-header">
              <span>🕸️ 网络拓扑</span>
              <el-button size="small" type="info" plain @click="initTopology">刷新</el-button>
            </div>
            <div id="topology" class="topology-container"></div>
          </div>
        </div>

        <!-- 其他 tab 面板 -->
        <div v-show="activeTab === 1" class="tab-panel">
          <div class="glass-card placeholder-card">
            <div class="placeholder-icon">🎯</div>
            <h3>靶场管理</h3>
            <p>虚拟靶场列表、场景管理功能开发中...</p>
          </div>
        </div>
        <div v-show="activeTab === 2" class="tab-panel">
          <div class="glass-card placeholder-card">
            <div class="placeholder-icon">📊</div>
            <h3>攻防日志</h3>
            <p>详细攻防记录分析功能开发中...</p>
          </div>
        </div>
        <div v-show="activeTab === 3" class="tab-panel">
          <div class="glass-card placeholder-card">
            <div class="placeholder-icon">🕸️</div>
            <h3>网络拓扑</h3>
            <p>可视化拓扑管理功能开发中...</p>
          </div>
        </div>
      </main>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, nextTick, computed } from 'vue'
import axios from 'axios'
import * as G6 from '@antv/g6'

const activeTab = ref(0)
const prompt = ref("")
const round = ref(0)
const attackCount = ref(0)
const defenseCount = ref(0)
const logs = ref([])
const progress = ref(0)
const rangeData = ref({})
const backendOnline = ref(false)
const logBodyRef = ref(null)

let graph = null
let healthTimer = null

const tabs = [
  { name: "控制台", icon: "🖥️" },
  { name: "靶场管理", icon: "🎯" },
  { name: "攻防日志", icon: "📊" },
  { name: "网络拓扑", icon: "🕸️" },
]

// CPU 颜色动态
const cpuColor = computed(() => {
  const p = rangeData.value.cpu || 0
  if (p >= 80) return '#ef4444'
  if (p >= 50) return '#f59e0b'
  return '#22c55e'
})

// 检查后端在线状态
const checkBackend = async () => {
  try {
    await axios.get("http://127.0.0.1:5000/api/health", { timeout: 2000 })
    backendOnline.value = true
  } catch {
    backendOnline.value = false
  }
}

// 漏洞标签颜色
const getVulnClass = (type) => {
  const map = {
    "SQL注入": "vuln-red",
    "文件上传": "vuln-red",
    "RCE": "vuln-red",
    "XSS": "vuln-yellow",
  }
  return map[type] || "vuln-gray"
}

const getLogClass = (log) => {
  if (log.includes("攻击")) return "log-attack"
  if (log.includes("防御")) return "log-defense"
  return "log-gen"
}

const generateRange = async () => {
  try {
    const res = await axios.post("http://127.0.0.1:5000/api/generate", { prompt: prompt.value })
    rangeData.value = res.data.range
    await nextTick()
    updateTopology()
    fetchLogs()
  } catch (e) {
    backendOnline.value = false
  }
}

const launchAttack = async () => {
  round.value++
  attackCount.value++
  progress.value = 0
  const step = () => {
    progress.value = Math.min(progress.value + 8, 100)
    if (progress.value < 100) {
      setTimeout(step, 60)
    } else {
      axios.post("http://127.0.0.1:5000/api/attack").catch(() => { backendOnline.value = false })
      fetchLogs()
      setTimeout(() => progress.value = 0, 800)
    }
  }
  step()
}

const launchDefense = async () => {
  defenseCount.value++
  await axios.post("http://127.0.0.1:5000/api/defense").catch(() => { backendOnline.value = false })
  fetchLogs()
}

const autoRun = () => {
  launchAttack()
  setTimeout(launchDefense, 1500)
}

const fetchLogs = async () => {
  try {
    const res = await axios.get("http://127.0.0.1:5000/api/logs")
    logs.value = res.data.logs || []
    await nextTick()
    if (logBodyRef.value) logBodyRef.value.scrollTop = logBodyRef.value.scrollHeight
  } catch {
    backendOnline.value = false
  }
}

const fullScreen = () => {
  if (!document.fullscreenElement) {
    document.documentElement.requestFullscreen()
  } else {
    document.exitFullscreen()
  }
}

const initTopology = async () => {
  await nextTick()
  if (graph) { graph.destroy(); graph = null }
  const el = document.getElementById('topology')
  if (!el) return
  graph = new G6.Graph({
    container: 'topology',
    width: el.offsetWidth || 800,
    height: 280,
    modes: { default: ['drag-canvas', 'zoom-canvas'] },
    defaultNode: {
      size: 46,
      style: {
        fill: 'rgba(30,41,59,0.8)',
        stroke: '#22d3ee',
        lineWidth: 2,
        shadowBlur: 15,
        shadowColor: '#22d3ee44'
      },
      labelCfg: { style: { fill: '#e2e8f0', fontSize: 11 } }
    },
    defaultEdge: {
      type: 'polyline',
      style: {
        stroke: '#22d3ee',
        lineWidth: 2,
        endArrow: { path: G6.Arrow.triangle(6, 6, 0), fill: '#22d3ee' }
      }
    }
  })
  graph.render()
}

const updateTopology = () => {
  if (!graph) return
  const vulns = rangeData.value.vulns || []
  const data = {
    nodes: [
      { id: 'attacker', label: '🕵️ 攻击机' },
      { id: 'target', label: '🎯 靶机' },
      ...vulns.map(v => ({ id: v.type, label: v.type }))
    ],
    edges: [
      { source: 'attacker', target: 'target' },
      ...vulns.map(v => ({ source: 'target', target: v.type }))
    ]
  }
  graph.changeData(data)
}

// Three.js 粒子背景
let animId = null
const initBg = () => {
  const canvas = document.getElementById('bg-canvas')
  if (!canvas) return
  const ctx = canvas.getContext('2d')
  let W = canvas.width = window.innerWidth
  let H = canvas.height = window.innerHeight

  const particles = []
  const N = 90
  for (let i = 0; i < N; i++) {
    particles.push({
      x: Math.random() * W,
      y: Math.random() * H,
      r: Math.random() * 2 + 0.5,
      dx: (Math.random() - 0.5) * 0.5,
      dy: (Math.random() - 0.5) * 0.5,
      alpha: Math.random() * 0.6 + 0.2,
      color: ['#22d3ee', '#a78bfa', '#f472b6', '#34d399'][Math.floor(Math.random() * 4)]
    })
  }

  const resize = () => {
    W = canvas.width = window.innerWidth
    H = canvas.height = window.innerHeight
  }
  window.addEventListener('resize', resize)

  const draw = () => {
    ctx.clearRect(0, 0, W, H)

    // 背景渐变
    const grad = ctx.createRadialGradient(W * 0.5, H * 0.4, 0, W * 0.5, H * 0.4, W * 0.8)
    grad.addColorStop(0, 'rgba(15,23,42,0.85)')
    grad.addColorStop(1, 'rgba(3,7,18,0.95)')
    ctx.fillStyle = grad
    ctx.fillRect(0, 0, W, H)

    // 连接线
    for (let i = 0; i < particles.length; i++) {
      for (let j = i + 1; j < particles.length; j++) {
        const dx = particles[i].x - particles[j].x
        const dy = particles[i].y - particles[j].y
        const dist = Math.sqrt(dx * dx + dy * dy)
        if (dist < 140) {
          ctx.beginPath()
          ctx.moveTo(particles[i].x, particles[i].y)
          ctx.lineTo(particles[j].x, particles[j].y)
          ctx.globalAlpha = (1 - dist / 140) * 0.18
          ctx.strokeStyle = '#22d3ee'
          ctx.lineWidth = 0.5
          ctx.stroke()
          ctx.globalAlpha = 1
        }
      }
    }

    // 粒子
    particles.forEach(p => {
      p.x += p.dx
      p.y += p.dy
      if (p.x < 0 || p.x > W) p.dx *= -1
      if (p.y < 0 || p.y > H) p.dy *= -1

      ctx.beginPath()
      ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2)
      ctx.fillStyle = p.color
      ctx.globalAlpha = p.alpha
      ctx.shadowBlur = 8
      ctx.shadowColor = p.color
      ctx.fill()
      ctx.globalAlpha = 1
      ctx.shadowBlur = 0
    })

    animId = requestAnimationFrame(draw)
  }
  draw()
}

onMounted(async () => {
  initBg()
  await checkBackend()
  await fetchLogs()
  await nextTick()
  await initTopology()

  // 每 5s 检测一次后端状态
  healthTimer = setInterval(checkBackend, 5000)
})

onUnmounted(() => {
  if (animId) cancelAnimationFrame(animId)
  if (graph) graph.destroy()
  if (healthTimer) clearInterval(healthTimer)
})
</script>

<style scoped>
/* ===== 玻璃质感核心样式 ===== */
.app-root {
  position: relative;
  min-height: 100vh;
  overflow-x: hidden;
}

#bg-canvas {
  position: fixed;
  inset: 0;
  z-index: 0;
  pointer-events: none;
}

.content-layer {
  position: relative;
  z-index: 1;
  min-height: 100vh;
  padding-bottom: 60px;
}

/* 玻璃卡片 */
.glass-card {
  background: rgba(15, 23, 42, 0.45);
  backdrop-filter: blur(20px) saturate(1.8);
  -webkit-backdrop-filter: blur(20px) saturate(1.8);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 20px;
  box-shadow:
    0 8px 32px rgba(0, 0, 0, 0.35),
    inset 0 1px 0 rgba(255, 255, 255, 0.08);
}

/* 导航栏 */
.glass-nav {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 32px;
  height: 64px;
  background: rgba(10, 15, 35, 0.6);
  backdrop-filter: blur(24px);
  -webkit-backdrop-filter: blur(24px);
  border-bottom: 1px solid rgba(255, 255, 255, 0.06);
  position: sticky;
  top: 0;
  z-index: 100;
  box-shadow: 0 4px 24px rgba(0, 0, 0, 0.3);
}

.nav-brand {
  display: flex;
  align-items: center;
  gap: 10px;
}

.brand-icon {
  display: flex;
  align-items: center;
}

.brand-text {
  font-size: 18px;
  font-weight: 700;
  background: linear-gradient(135deg, #22d3ee, #a78bfa);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  letter-spacing: 0.5px;
}

/* 玻璃 tabs */
.glass-tabs {
  display: flex;
  gap: 4px;
  background: rgba(15, 23, 42, 0.5);
  padding: 4px;
  border-radius: 14px;
  border: 1px solid rgba(255, 255, 255, 0.06);
}

.glass-tab {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 7px 18px;
  border-radius: 10px;
  border: none;
  background: transparent;
  color: rgba(226, 232, 240, 0.55);
  font-size: 13.5px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.25s ease;
  white-space: nowrap;
}

.glass-tab:hover {
  background: rgba(34, 211, 238, 0.08);
  color: #22d3ee;
}

.glass-tab.active {
  background: rgba(34, 211, 238, 0.15);
  color: #22d3ee;
  box-shadow: 0 0 16px rgba(34, 211, 238, 0.15);
  font-weight: 600;
}

.tab-icon {
  font-size: 14px;
}

/* 玻璃按钮 */
.glass-btn {
  background: rgba(34, 211, 238, 0.12) !important;
  border: 1px solid rgba(34, 211, 238, 0.25) !important;
  color: #22d3ee !important;
  border-radius: 10px !important;
  backdrop-filter: blur(10px);
  transition: all 0.2s;
  font-size: 12px;
  display: flex;
  align-items: center;
  gap: 5px;
}

.glass-btn:hover {
  background: rgba(34, 211, 238, 0.22) !important;
  box-shadow: 0 0 16px rgba(34, 211, 238, 0.2);
}

/* 主内容 */
.main-content {
  max-width: 1280px;
  margin: 0 auto;
  padding: 32px 24px 0;
}

.tab-panel {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

/* 靶场生成 */
.prompt-card {
  padding: 24px;
}

.prompt-header {
  display: flex;
  align-items: baseline;
  gap: 12px;
  margin-bottom: 16px;
}

.prompt-label {
  font-size: 16px;
  font-weight: 700;
  color: #22d3ee;
}

.prompt-hint {
  font-size: 12px;
  color: rgba(148, 163, 184, 0.7);
}

.glass-input :deep(.el-textarea__inner) {
  background: rgba(15, 23, 42, 0.6) !important;
  border: 1px solid rgba(255, 255, 255, 0.1) !important;
  border-radius: 12px !important;
  color: #e2e8f0 !important;
  backdrop-filter: blur(12px);
  font-size: 14px;
  padding: 12px 14px;
  resize: none;
}

.glass-input :deep(.el-textarea__inner)::placeholder {
  color: rgba(148, 163, 184, 0.45) !important;
}

.prompt-actions {
  margin-top: 14px;
  display: flex;
  justify-content: center;
}

/* 信息卡片网格 */
.info-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
}

.info-card {
  padding: 20px 22px;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 14px;
  padding-bottom: 10px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.06);
}

.card-icon {
  font-size: 16px;
}

.card-title {
  font-size: 13px;
  font-weight: 600;
  color: rgba(148, 163, 184, 0.85);
  letter-spacing: 0.5px;
  text-transform: uppercase;
}

.info-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.info-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 13px;
}

.info-key {
  color: rgba(148, 163, 184, 0.6);
}

.info-val {
  color: #e2e8f0;
  font-weight: 500;
}

.info-val.mono {
  font-family: 'Courier New', monospace;
  color: #22d3ee;
}

/* 漏洞标签 */
.vuln-tags {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.vuln-tag {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 7px 12px;
  border-radius: 10px;
  font-size: 13px;
  font-weight: 500;
  background: rgba(15, 23, 42, 0.5);
  border: 1px solid;
  transition: all 0.2s;
}

.vuln-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  flex-shrink: 0;
}

.vuln-red {
  color: #fca5a5;
  border-color: rgba(239, 68, 68, 0.3);
  background: rgba(239, 68, 68, 0.08);
}
.vuln-red .vuln-dot { background: #ef4444; box-shadow: 0 0 6px #ef4444; }

.vuln-yellow {
  color: #fde68a;
  border-color: rgba(245, 158, 11, 0.3);
  background: rgba(245, 158, 11, 0.08);
}
.vuln-yellow .vuln-dot { background: #f59e0b; box-shadow: 0 0 6px #f59e0b; }

.vuln-gray {
  color: #94a3b8;
  border-color: rgba(148, 163, 184, 0.2);
  background: rgba(148, 163, 184, 0.05);
}
.vuln-gray .vuln-dot { background: #64748b; }

.vuln-level {
  margin-left: auto;
  font-size: 11px;
  opacity: 0.7;
}

/* 监控 */
.monitor-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.monitor-row {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.monitor-label {
  font-size: 11px;
  color: rgba(148, 163, 184, 0.55);
  text-transform: uppercase;
  letter-spacing: 0.3px;
}

.mini-progress {
  width: 100%;
}

.mini-progress :deep(.el-progress-bar__outer) {
  background: rgba(15, 23, 42, 0.6) !important;
  border-radius: 4px !important;
}

/* 统计卡片 */
.stats-row {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
}

.stat-card {
  padding: 18px 20px;
  display: flex;
  align-items: center;
  gap: 14px;
  transition: transform 0.2s, box-shadow 0.2s;
}

.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.4), inset 0 1px 0 rgba(255, 255, 255, 0.1);
}

.stat-icon {
  font-size: 24px;
  width: 44px;
  height: 44px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 12px;
  flex-shrink: 0;
  background: rgba(15, 23, 42, 0.6);
}

.stat-body {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.stat-label {
  font-size: 11px;
  color: rgba(148, 163, 184, 0.6);
  text-transform: uppercase;
  letter-spacing: 0.4px;
}

.stat-value {
  font-size: 24px;
  font-weight: 700;
  color: #e2e8f0;
  line-height: 1.2;
}

.stat-value.red { color: #f87171; }
.stat-value.blue { color: #60a5fa; }
.stat-value.purple { color: #a78bfa; }

/* 进度条 */
.progress-card {
  padding: 16px 22px;
}

.progress-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 13px;
  color: #22d3ee;
  margin-bottom: 10px;
  font-weight: 500;
}

.progress-track {
  height: 8px;
  border-radius: 4px;
  background: rgba(15, 23, 42, 0.6);
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  border-radius: 4px;
  background: linear-gradient(90deg, #22d3ee, #a78bfa);
  box-shadow: 0 0 12px rgba(34, 211, 238, 0.5);
  transition: width 0.1s ease;
  position: relative;
  overflow: hidden;
}

.progress-fill::after {
  content: '';
  position: absolute;
  right: 0;
  top: 0;
  bottom: 0;
  width: 30%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.4));
  animation: shimmer 1s infinite;
}

@keyframes shimmer {
  0% { opacity: 0; transform: translateX(-100%); }
  50% { opacity: 1; }
  100% { opacity: 0; transform: translateX(0); }
}

/* ===== PK 攻防动态边框 ===== */
.pk-card {
  padding: 0;
  overflow: hidden;
}

.pk-inner {
  display: flex;
  align-items: center;
  padding: 28px 32px;
  position: relative;
}

.pk-side {
  flex: 1;
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
}

/* 攻击方动态边框 */
.attack-border {
  position: absolute;
  inset: 0;
  border-radius: 16px;
  padding: 2px;
  background: linear-gradient(90deg, #ef4444, transparent, transparent, #ef4444);
  background-size: 200% 100%;
  animation: borderScrollRed 2.5s linear infinite;
  -webkit-mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
  mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
  -webkit-mask-composite: xor;
  mask-composite: exclude;
}

@keyframes borderScrollRed {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}

/* 防御方动态边框 */
.defense-border {
  position: absolute;
  inset: 0;
  border-radius: 16px;
  padding: 2px;
  background: linear-gradient(90deg, #3b82f6, transparent, transparent, #3b82f6);
  background-size: 200% 100%;
  animation: borderScrollBlue 2.5s linear infinite reverse;
  -webkit-mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
  mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
  -webkit-mask-composite: xor;
  mask-composite: exclude;
}

@keyframes borderScrollBlue {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}

.pk-content {
  position: relative;
  z-index: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
  padding: 8px;
}

.pk-title {
  font-size: 14px;
  font-weight: 700;
  letter-spacing: 1px;
}

.pk-title.red { color: #f87171; text-shadow: 0 0 16px rgba(248, 113, 113, 0.4); }
.pk-title.blue { color: #60a5fa; text-shadow: 0 0 16px rgba(96, 165, 250, 0.4); }

/* VS 圆环 */
.pk-vs {
  width: 80px;
  flex-shrink: 0;
  display: flex;
  justify-content: center;
  align-items: center;
}

.vs-ring {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  border: 2px solid rgba(34, 211, 238, 0.4);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
  font-weight: 800;
  color: #22d3ee;
  background: rgba(15, 23, 42, 0.6);
  backdrop-filter: blur(10px);
  box-shadow: 0 0 24px rgba(34, 211, 238, 0.2), inset 0 0 16px rgba(34, 211, 238, 0.05);
  animation: vsPulse 2s ease-in-out infinite;
}

@keyframes vsPulse {
  0%, 100% { transform: scale(1); box-shadow: 0 0 24px rgba(34, 211, 238, 0.2); }
  50% { transform: scale(1.06); box-shadow: 0 0 36px rgba(34, 211, 238, 0.35); }
}

.auto-run-row {
  padding: 14px 32px 20px;
  border-top: 1px solid rgba(255, 255, 255, 0.05);
  display: flex;
  justify-content: center;
}

/* 按钮 */
.action-btn {
  border-radius: 14px !important;
  font-weight: 600 !important;
  letter-spacing: 0.3px;
  transition: all 0.25s !important;
  min-width: 140px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
}

.action-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.4);
}

.attack-btn {
  min-width: 200px;
}

/* 日志 */
.log-card {
  padding: 0;
  overflow: hidden;
}

.log-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.06);
  font-size: 13px;
  color: rgba(148, 163, 184, 0.8);
  font-weight: 500;
}

.log-count {
  font-size: 11px;
  color: rgba(148, 163, 184, 0.45);
  background: rgba(15, 23, 42, 0.5);
  padding: 2px 8px;
  border-radius: 8px;
}

.log-body {
  height: 240px;
  overflow-y: auto;
  padding: 14px 20px;
  font-family: 'Courier New', 'Fira Code', monospace;
  font-size: 12.5px;
  scrollbar-width: thin;
  scrollbar-color: rgba(34, 211, 238, 0.3) transparent;
}

.log-body::-webkit-scrollbar { width: 4px; }
.log-body::-webkit-scrollbar-track { background: transparent; }
.log-body::-webkit-scrollbar-thumb { background: rgba(34, 211, 238, 0.3); border-radius: 2px; }

.log-line {
  display: flex;
  gap: 8px;
  align-items: baseline;
  margin-bottom: 6px;
  line-height: 1.5;
}

.log-num {
  color: rgba(148, 163, 184, 0.35);
  flex-shrink: 0;
  font-size: 11px;
}

.log-attack { color: #f87171; }
.log-defense { color: #60a5fa; }
.log-gen { color: #4ade80; }

.log-empty {
  text-align: center;
  color: rgba(148, 163, 184, 0.3);
  padding: 60px 0;
  font-family: inherit;
}

/* 拓扑图 */
.topo-card {
  padding: 0;
  overflow: hidden;
}

.topo-card .log-header {
  border-radius: 20px 20px 0 0;
}

.topology-container {
  height: 300px;
  width: 100%;
}

/* placeholder */
.placeholder-card {
  padding: 60px 40px;
  text-align: center;
}

.placeholder-icon {
  font-size: 48px;
  margin-bottom: 16px;
}

.placeholder-card h3 {
  font-size: 20px;
  color: #e2e8f0;
  margin-bottom: 8px;
}

.placeholder-card p {
  color: rgba(148, 163, 184, 0.5);
  font-size: 14px;
}

/* 后端离线 */
.backend-offline {
  background: rgba(239, 68, 68, 0.15) !important;
  border: 1px solid rgba(239, 68, 68, 0.35) !important;
  backdrop-filter: blur(20px);
  animation: offlineIn 0.3s ease;
}

@keyframes offlineIn {
  from { opacity: 0; transform: translateX(-50%) translateY(-10px); }
  to { opacity: 1; transform: translateX(-50%) translateY(0); }
}

.offline-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #ef4444;
  animation: blink 1.2s ease-in-out infinite;
  flex-shrink: 0;
}

@keyframes blink {
  0%, 100% { opacity: 1; box-shadow: 0 0 8px #ef4444; }
  50% { opacity: 0.4; box-shadow: none; }
}

/* Element Plus 组件玻璃化覆盖 */
:deep(.el-button--success) {
  background: rgba(34, 197, 94, 0.15) !important;
  border-color: rgba(34, 197, 94, 0.4) !important;
  color: #4ade80 !important;
  box-shadow: 0 0 16px rgba(34, 197, 94, 0.1);
}

:deep(.el-button--danger) {
  background: rgba(239, 68, 68, 0.15) !important;
  border-color: rgba(239, 68, 68, 0.4) !important;
  color: #f87171 !important;
  box-shadow: 0 0 16px rgba(239, 68, 68, 0.1);
}

:deep(.el-button--primary) {
  background: rgba(59, 130, 246, 0.15) !important;
  border-color: rgba(59, 130, 246, 0.4) !important;
  color: #60a5fa !important;
  box-shadow: 0 0 16px rgba(59, 130, 246, 0.1);
}

:deep(.el-button--warning) {
  background: rgba(245, 158, 11, 0.15) !important;
  border-color: rgba(245, 158, 11, 0.4) !important;
  color: #fbbf24 !important;
  box-shadow: 0 0 16px rgba(245, 158, 11, 0.1);
}

:deep(.el-progress-bar__outer) {
  background: rgba(15, 23, 42, 0.6) !important;
  border-radius: 4px !important;
}

/* 响应式 */
@media (max-width: 1024px) {
  .info-grid { grid-template-columns: 1fr; }
  .stats-row { grid-template-columns: repeat(2, 1fr); }
  .glass-nav { padding: 0 16px; }
  .glass-tab { padding: 6px 12px; font-size: 12px; }
  .tab-icon { display: none; }
}

@media (max-width: 640px) {
  .stats-row { grid-template-columns: repeat(2, 1fr); }
  .pk-inner { flex-direction: column; gap: 24px; }
  .pk-side { width: 100%; }
}
</style>
