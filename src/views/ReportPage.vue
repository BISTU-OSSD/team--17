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

    <!-- 最终结果 -->
    <template v-if="report && analysis">
      <h1>{{ report.repo.full_name }}</h1>
      <p class="desc">{{ report.repo.description || '暂无描述' }}</p>

      <div class="score-badge">
        <span class="score">{{ analysis.total_score }}</span>
        <span class="label">/ 10</span>
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
        <h3>总结建议</h3>
        <p>{{ analysis.summary }}</p>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()
const owner = route.params.owner
const repo = route.params.repo

const steps = ref([])
const errorMsg = ref('')
const report = ref(null)
const analysis = ref(null)

onMounted(async () => {
  const apiBaseUrl = import.meta.env.VITE_API_BASE_URL || ''

  steps.value.push({ step: 'loading', message: '正在分析仓库...', status: 'active' })

  try {
    const response = await fetch(`${apiBaseUrl}/api/analyze/${owner}/${repo}`)
    const data = await response.json()

    if (!response.ok) {
      throw new Error(data.detail || '分析失败')
    }

    report.value = {
      repo: {
        full_name: data.repo_url?.replace('https://github.com/', '') || `${owner}/${repo}`,
        description: data.summary || '',
        stargazers_count: 0,
        forks_count: 0
      }
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
})
</script>

<style scoped>
.report-page {
  max-width: 900px;
  margin: 0 auto;
  padding: 30px 20px;
}
.back-link {
  display: inline-block;
  margin-bottom: 20px;
  color: #409eff;
  text-decoration: none;
  font-size: 14px;
}
.back-link:hover { text-decoration: underline; }

.steps {
  margin-bottom: 24px;
  padding: 16px;
  background: #f9fafb;
  border-radius: 8px;
}
.step {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 4px 0;
  font-size: 14px;
  color: #888;
  transition: color 0.3s;
}
.step.active { color: #409eff; font-weight: 500; }
.step.done { color: #67c23a; }
.step.error { color: #f56c6c; }
.step-icon { width: 16px; text-align: center; }

h1 { font-size: 28px; margin: 0 0 8px; }
.desc { color: #888; margin-bottom: 20px; }
.score-badge {
  display: inline-flex;
  align-items: baseline;
  gap: 4px;
  background: #f0f9ff;
  padding: 8px 20px;
  border-radius: 20px;
  margin-bottom: 24px;
}
.score-badge .score { font-size: 32px; font-weight: bold; color: #409eff; }
.score-badge .label { font-size: 14px; color: #888; }
.card {
  border: 1px solid #eee;
  border-radius: 8px;
  padding: 20px;
  margin-bottom: 16px;
}
.card h3 { margin: 0 0 16px; font-size: 18px; }
.score-item {
  padding: 12px 0;
  border-bottom: 1px solid #f0f0f0;
}
.score-item:last-child { border-bottom: none; }
.score-label { font-weight: 500; margin-right: 8px; }
.score-value { color: #409eff; font-weight: bold; }
.score-detail { color: #666; font-size: 14px; margin: 4px 0 0; }
.error-box {
  background: #fef0f0;
  color: #f56c6c;
  padding: 12px 16px;
  border-radius: 8px;
  margin-bottom: 16px;
}
</style>
