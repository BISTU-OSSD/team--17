<template>
  <div class="report-page">
    <router-link to="/" class="back-link">← 返回</router-link>

    <LoadingState v-if="loading" />

    <ErrorState v-else-if="errorMsg" :message="errorMsg" />

    <template v-else-if="report && analysis">
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
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import RepoBasicInfo from '../components/RepoBasicInfo.vue'
import TechStackChart from '../components/TechStackChart.vue'
import RadarChart from '../components/RadarChart.vue'
import CommunityProfile from '../components/CommunityProfile.vue'
import RepoRecommendations from '../components/RepoRecommendations.vue'
import LoadingState from '../components/LoadingState.vue'
import ErrorState from '../components/ErrorState.vue'

const route = useRoute()
const owner = route.params.owner
const repo = route.params.repo

const loading = ref(true)
const errorMsg = ref('')
const report = ref(null)
const analysis = ref(null)

onMounted(async () => {
  try {
    const res = await fetch(`/api/analyze/${owner}/${repo}`)
    const data = await res.json()

    if (!res.ok) {
      errorMsg.value = data.detail || data.error || '请求失败'
      return
    }

    report.value = data.report
    analysis.value = data.analysis
  } catch (e) {
    errorMsg.value = '网络错误，请检查后端是否启动'
  } finally {
    loading.value = false
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
.back-link:hover {
  text-decoration: underline;
}
h1 {
  font-size: 28px;
  margin: 0 0 8px;
}
.desc {
  color: #888;
  margin-bottom: 20px;
}
.score-badge {
  display: inline-flex;
  align-items: baseline;
  gap: 4px;
  background: #f0f9ff;
  padding: 8px 20px;
  border-radius: 20px;
  margin-bottom: 24px;
}
.score-badge .score {
  font-size: 32px;
  font-weight: bold;
  color: #409eff;
}
.score-badge .label {
  font-size: 14px;
  color: #888;
}
.grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
  margin-bottom: 16px;
}
.card {
  border: 1px solid #eee;
  border-radius: 8px;
  padding: 20px;
  margin-bottom: 16px;
}
@media (max-width: 640px) {
  .grid {
    grid-template-columns: 1fr;
  }
}
</style>
