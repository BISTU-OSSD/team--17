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
    <ErrorState v-if="errorMsg" :message="errorMsg" />

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
          <RepoBasicInfo :repo="report.repo" />
        </div>
        <div class="card">
          <TechStackChart :languages="report.languages.languages" />
        </div>
      </div>

      <div class="card">
        <RadarChart :scores="analysis.scores" />
      </div>

      <div class="grid">
        <div class="card">
          <CommunityProfile
            :contributors="report.contributors"
            :commits="report.commits"
            :issues="report.issues"
          />
        </div>
        <div class="card">
          <RepoRecommendations :summary="analysis.summary" />
        </div>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useRoute } from 'vue-router'
import RepoBasicInfo from '../components/RepoBasicInfo.vue'
import TechStackChart from '../components/TechStackChart.vue'
import RadarChart from '../components/RadarChart.vue'
import CommunityProfile from '../components/CommunityProfile.vue'
import RepoRecommendations from '../components/RepoRecommendations.vue'
import ErrorState from '../components/ErrorState.vue'

const route = useRoute()
const owner = route.params.owner
const repo = route.params.repo

const steps = ref([])
const errorMsg = ref('')
const report = ref(null)
const analysis = ref(null)

let evtSource = null

onMounted(() => {
  evtSource = new EventSource(`${import.meta.env.VITE_API_BASE_URL}/api/analyze/${owner}/${repo}`)

  evtSource.addEventListener('step', (e) => {
    const data = JSON.parse(e.data)
    const existing = steps.value.find(s => s.step === data.step)
    if (existing) {
      existing.message = data.message
      existing.status = data.step === 'done' ? 'done' : 'active'
    } else {
      steps.value.push({
        step: data.step,
        message: data.message,
        status: data.step === 'done' ? 'done' : 'active',
      })
    }
    // 标记之前的步骤为完成
    if (data.step !== 'validating') {
      const idx = steps.value.findIndex(s => s.step === data.step)
      for (let i = 0; i < idx; i++) {
        if (steps.value[i].status !== 'done' && steps.value[i].status !== 'error') {
          steps.value[i].status = 'done'
        }
      }
    }
  })

  evtSource.addEventListener('result', (e) => {
    const data = JSON.parse(e.data)
    report.value = data.report
    analysis.value = data.analysis
    evtSource.close()
  })

  evtSource.addEventListener('error', (e) => {
    if (e.data) {
      const data = JSON.parse(e.data)
      errorMsg.value = data.message
    } else {
      errorMsg.value = '连接中断，请重试'
    }
    evtSource.close()
  })

  evtSource.onerror = () => {
    if (!report.value && !errorMsg.value) {
      errorMsg.value = '连接失败，请检查后端是否启动'
    }
    evtSource.close()
  }
})

onUnmounted(() => {
  if (evtSource) evtSource.close()
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
.grid { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin-bottom: 16px; }
.card {
  border: 1px solid #eee;
  border-radius: 8px;
  padding: 20px;
  margin-bottom: 16px;
}
@media (max-width: 640px) { .grid { grid-template-columns: 1fr; } }
</style>
