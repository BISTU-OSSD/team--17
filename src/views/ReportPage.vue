<template>
  <div class="report-page">
    <router-link to="/" class="back-link">← 返回</router-link>

    <!-- 步骤进度 -->
    <div v-if="steps.length" class="steps">
      <div v-for="(s, i) in steps" :key="i" class="step" :class="s.status">
        <span class="step-icon">{{ s.status === 'done' ? '✓' : s.status === 'error' ? '✗' : '●' }}</span>
        <span>{{ s.message }}</span>
      </div>
    </div>

    <!-- 错误 -->
    <div v-if="errorMsg" class="error-box">{{ errorMsg }}</div>

    <!-- LLM 思考过程 -->
    <div v-if="isThinking && thinkingContent" class="thinking-box">
      <div class="thinking-header">
        <span class="thinking-icon">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="12" cy="12" r="10"/>
            <path d="M12 6v6l4 2"/>
          </svg>
        </span>
        <span class="thinking-title">AI 思考中...</span>
      </div>
      <div class="thinking-content">{{ thinkingContent }}</div>
    </div>

    <!-- 最终结果 -->
    <template v-if="report && analysis">
      <h1>{{ report.repo.full_name }}</h1>
      <p class="desc">{{ report.repo.description || '暂无描述' }}</p>

      <div class="score-badge">
        <span class="score">{{ analysis.total_score }}</span>
        <span class="label">/ 10</span>
      </div>

      <div class="grid">
        <div class="card">
          <RadarChart :scores="analysis.scores" />
        </div>
        <div class="card">
          <TechStackChart :languages="report.languages" />
        </div>
      </div>

      <div class="card">
        <h3>评分详情</h3>
        <div v-for="(item, key) in analysis.scores" :key="key" class="score-item">
          <span class="score-label">{{ key }}</span>
          <span class="score-value">{{ item.score }}/10</span>
          <p class="score-detail">{{ item.detail }}</p>
        </div>
      </div>

      <div class="card">
        <CommunityProfile
          :contributors="report.contributors"
          :commits="report.commits"
          :issues="report.issues"
        />
      </div>

      <div class="card">
        <h3>项目总结</h3>
        <p>{{ analysis.summary }}</p>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useRoute } from 'vue-router'
import RadarChart from '../components/RadarChart.vue'
import TechStackChart from '../components/TechStackChart.vue'
import CommunityProfile from '../components/CommunityProfile.vue'

const route = useRoute()
const owner = route.params.owner
const repo = route.params.repo

const steps = ref([])
const errorMsg = ref('')
const report = ref(null)
const analysis = ref(null)
const thinkingContent = ref('')
const isThinking = ref(false)

let eventSource = null
let abortController = null

const NGROK_HEADERS = { 'ngrok-skip-browser-warning': 'true' }

onMounted(async () => {
  const apiBaseUrl = import.meta.env.VITE_API_BASE_URL || ''
  const isNgrok = apiBaseUrl.includes('ngrok')

  steps.value.push({ step: 'loading', message: '正在分析仓库...', status: 'active' })

  try {
    // 使用流式端点（fetch 替代 EventSource，支持自定义 header）
    abortController = new AbortController()

    const resp = await fetch(`${apiBaseUrl}/api/stream/${owner}/${repo}`, {
      headers: isNgrok ? NGROK_HEADERS : {},
      signal: abortController.signal,
    })

    if (!resp.ok) throw new Error(`HTTP ${resp.status}`)

    const reader = resp.body.getReader()
    const decoder = new TextDecoder()
    let buffer = ''

    while (true) {
      const { done, value } = await reader.read()
      if (done) break

      buffer += decoder.decode(value, { stream: true })
      const lines = buffer.split('\n')
      buffer = lines.pop() || ''

      for (const line of lines) {
        if (!line.startsWith('data: ')) continue
        const data = JSON.parse(line.slice(6))

        switch (data.type) {
          case 'start':
            steps.value = [{ step: 'start', message: data.message, status: 'active' }]
            break

          case 'step':
            const existingStep = steps.value.find(s => s.step === 'loading')
            if (existingStep) {
              existingStep.message = data.message
            } else {
              steps.value.push({ step: 'loading', message: data.message, status: 'active' })
            }
            break

          case 'thinking':
            isThinking.value = true
            thinkingContent.value += data.content
            break

          case 'answer':
            isThinking.value = false
            break

          case 'done': {
            const result = data.result
            report.value = {
              repo: {
                full_name: result.repo_url?.replace('https://github.com/', '') || `${owner}/${repo}`,
                description: result.description || result.summary || '',
                stargazers_count: result.star_count || 0,
                forks_count: result.fork_count || 0
              },
              languages: result.languages || [],
              contributors: result.contributors || {},
              commits: result.commits || {},
              issues: result.issues || {}
            }
            analysis.value = {
              total_score: result.total_score,
              scores: result.scores,
              summary: result.summary
            }
            steps.value = [{ step: 'done', message: '分析完成', status: 'done' }]
            return
          }

          case 'error':
            throw new Error(data.message)
        }
      }
    }
  } catch (error) {
    if (error.name === 'AbortError') return
    console.error('Stream error:', error)
    fallbackToNormalApi()
  }
})

async function fallbackToNormalApi() {
  const apiBaseUrl = import.meta.env.VITE_API_BASE_URL || ''
  const isNgrok = apiBaseUrl.includes('ngrok')

  try {
    steps.value = [{ step: 'loading', message: '正在分析仓库...', status: 'active' }]

    const response = await fetch(`${apiBaseUrl}/api/analyze/${owner}/${repo}`, {
      headers: isNgrok ? NGROK_HEADERS : {},
    })
    const data = await response.json()

    if (!response.ok) {
      throw new Error(data.detail || '分析失败')
    }

    report.value = {
      repo: {
        full_name: data.repo_url?.replace('https://github.com/', '') || `${owner}/${repo}`,
        description: data.description || data.summary || '',
        stargazers_count: data.star_count || 0,
        forks_count: data.fork_count || 0
      },
      languages: data.languages || [],
      contributors: data.contributors || {},
      commits: data.commits || {},
      issues: data.issues || {}
    }
    analysis.value = {
      total_score: data.total_score,
      scores: data.scores,
      summary: data.summary
    }

    steps.value = [{ step: 'done', message: '分析完成', status: 'done' }]
  } catch (error) {
    errorMsg.value = error.message || '连接失败，请检查后端是否启动'
    steps.value = [{ step: 'error', message: errorMsg.value, status: 'error' }]
  }
}

onUnmounted(() => {
  if (abortController) {
    abortController.abort()
  }
})
</script>

<style scoped>
.report-page {
  max-width: 960px;
  margin: 0 auto;
  padding: 40px 24px;
}

/* 页面进入动画 */
@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes fadeInDown {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes scaleIn {
  from {
    opacity: 0;
    transform: scale(0.9);
  }
  to {
    opacity: 1;
    transform: scale(1);
  }
}

@keyframes slideInLeft {
  from {
    opacity: 0;
    transform: translateX(-30px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

@keyframes pulse {
  0%, 100% {
    transform: scale(1);
    opacity: 1;
  }
  50% {
    transform: scale(1.05);
    opacity: 0.8;
  }
}

@keyframes shimmer {
  0% {
    background-position: -200% 0;
  }
  100% {
    background-position: 200% 0;
  }
}

.back-link {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  margin-bottom: 32px;
  color: var(--accent);
  text-decoration: none;
  font-size: 14px;
  font-weight: 500;
  padding: 8px 12px;
  border-radius: 8px;
  transition: all 0.2s ease;
  animation: fadeInDown 0.5s ease;
}

.back-link:hover {
  background: var(--accent-bg);
  transform: translateX(-4px);
}

.steps {
  margin-bottom: 32px;
  padding: 20px;
  background: var(--glass-bg);
  backdrop-filter: blur(8px);
  border: var(--glass-border);
  border-radius: 12px;
  box-shadow: var(--card-shadow);
  animation: fadeIn 0.6s ease;
}

.step {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 8px 0;
  font-size: 14px;
  color: var(--text);
  transition: all 0.3s ease;
  animation: slideInLeft 0.5s ease backwards;
}

.step:nth-child(1) { animation-delay: 0.1s; }
.step:nth-child(2) { animation-delay: 0.2s; }
.step:nth-child(3) { animation-delay: 0.3s; }

.step.active { color: var(--accent); font-weight: 500; }
.step.done { color: var(--success); }
.step.error { color: var(--danger); }

.step-icon {
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  background: var(--card-bg);
  font-size: 12px;
}

.step.active .step-icon { background: var(--accent-bg); }
.step.done .step-icon { background: rgba(16, 185, 129, 0.1); }
.step.error .step-icon { background: rgba(239, 68, 68, 0.1); }

h1 {
  font-size: 32px;
  margin: 0 0 12px;
  line-height: 1.2;
  animation: fadeIn 0.6s ease 0.1s backwards;
}

.desc {
  color: var(--text);
  margin-bottom: 24px;
  font-size: 16px;
  line-height: 1.6;
  animation: fadeIn 0.6s ease 0.2s backwards;
}

.score-badge {
  display: inline-flex;
  align-items: baseline;
  gap: 8px;
  background: var(--accent-gradient);
  padding: 12px 28px;
  border-radius: 100px;
  margin-bottom: 32px;
  box-shadow: 0 4px 16px rgba(124, 58, 237, 0.3);
  animation: scaleIn 0.5s ease 0.3s backwards;
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.score-badge:hover {
  transform: scale(1.05);
  box-shadow: 0 6px 24px rgba(124, 58, 237, 0.4);
}

.score-badge .score {
  font-size: 40px;
  font-weight: 700;
  color: white;
}

.score-badge .label {
  font-size: 16px;
  color: rgba(255, 255, 255, 0.8);
}

.grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
  margin-bottom: 20px;
}

.card {
  background: var(--glass-bg);
  backdrop-filter: blur(8px);
  border: var(--glass-border);
  border-radius: 16px;
  padding: 24px;
  margin-bottom: 20px;
  box-shadow: var(--card-shadow);
  transition: all 0.3s ease;
  animation: fadeInUp 0.6s ease backwards;
}

.card:nth-child(1) { animation-delay: 0.4s; }
.card:nth-child(2) { animation-delay: 0.5s; }

.card:hover {
  box-shadow: var(--card-shadow-hover);
  transform: translateY(-4px);
}

.card h3 {
  margin: 0 0 20px;
  font-size: 18px;
  font-weight: 600;
  color: var(--text-h);
  display: flex;
  align-items: center;
  gap: 8px;
}

.card h3::before {
  content: '';
  width: 4px;
  height: 20px;
  background: var(--accent-gradient);
  border-radius: 2px;
}

.score-item {
  padding: 16px 0;
  border-bottom: 1px solid var(--border);
  animation: fadeIn 0.4s ease backwards;
  transition: background 0.2s ease;
}

.score-item:hover {
  background: var(--accent-bg);
  margin: 0 -12px;
  padding: 16px 12px;
  border-radius: 8px;
}

.score-item:nth-child(1) { animation-delay: 0.6s; }
.score-item:nth-child(2) { animation-delay: 0.7s; }
.score-item:nth-child(3) { animation-delay: 0.8s; }
.score-item:nth-child(4) { animation-delay: 0.9s; }
.score-item:nth-child(5) { animation-delay: 1.0s; }
.score-item:nth-child(6) { animation-delay: 1.1s; }

.score-item:last-child {
  border-bottom: none;
  padding-bottom: 0;
}

.score-item:first-child {
  padding-top: 0;
}

.score-label {
  font-weight: 600;
  color: var(--text-h);
  display: block;
  margin-bottom: 4px;
}

.score-value {
  display: inline-block;
  padding: 2px 10px;
  background: var(--accent-bg);
  color: var(--accent);
  border-radius: 6px;
  font-weight: 600;
  font-size: 14px;
  margin-bottom: 8px;
}

.score-detail {
  color: var(--text);
  font-size: 14px;
  margin: 0;
  line-height: 1.5;
}

.error-box {
  background: rgba(239, 68, 68, 0.1);
  color: var(--danger);
  padding: 16px 20px;
  border-radius: 12px;
  margin-bottom: 20px;
  border: 1px solid rgba(239, 68, 68, 0.2);
}

/* LLM 思考过程样式 */
@keyframes pulse-glow {
  0%, 100% {
    box-shadow: 0 0 10px rgba(124, 58, 237, 0.3);
  }
  50% {
    box-shadow: 0 0 20px rgba(124, 58, 237, 0.6);
  }
}

@keyframes typewriter {
  from { width: 0; }
  to { width: 100%; }
}

.thinking-box {
  background: var(--glass-bg);
  backdrop-filter: blur(8px);
  border: var(--glass-border);
  border-radius: 12px;
  padding: 20px;
  margin-bottom: 24px;
  animation: fadeIn 0.5s ease, pulse-glow 2s ease-in-out infinite;
}

.thinking-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 1px solid var(--border);
}

.thinking-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  background: var(--accent-gradient);
  border-radius: 8px;
  color: white;
  animation: pulse 1.5s ease-in-out infinite;
}

.thinking-icon svg {
  width: 18px;
  height: 18px;
}

@keyframes pulse {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.1); }
}

.thinking-title {
  font-weight: 600;
  color: var(--accent);
  font-size: 14px;
}

.thinking-content {
  font-family: var(--mono);
  font-size: 13px;
  line-height: 1.7;
  color: var(--text);
  max-height: 300px;
  overflow-y: auto;
  padding: 12px;
  background: var(--code-bg);
  border-radius: 8px;
  white-space: pre-wrap;
  word-break: break-word;
}

.thinking-content::-webkit-scrollbar {
  width: 6px;
}

.thinking-content::-webkit-scrollbar-track {
  background: transparent;
}

.thinking-content::-webkit-scrollbar-thumb {
  background: var(--border);
  border-radius: 3px;
}

@media (max-width: 640px) {
  .report-page {
    padding: 24px 16px;
  }

  .grid {
    grid-template-columns: 1fr;
  }

  h1 {
    font-size: 24px;
  }
}
</style>
