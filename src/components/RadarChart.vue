<template>
  <div ref="chartDom" style="width: 100%; height: 380px;"></div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import * as echarts from 'echarts'

const props = defineProps({
  scores: { type: Object, default: () => ({}) }
})

const chartDom = ref(null)
let chart = null

const DIMENSIONS = [
  { key: 'code_quality', name: '代码质量' },
  { key: 'community_activity', name: '社区活跃度' },
  { key: 'update_frequency', name: '更新频率' },
  { key: 'documentation', name: '文档完善度' },
  { key: 'security', name: '安全状况' },
  { key: 'community_impact', name: '社区影响力' },
]

function renderChart() {
  if (!chartDom.value) return
  if (!chart) chart = echarts.init(chartDom.value)

  const values = DIMENSIONS.map(d => {
    const s = props.scores[d.key]
    return s ? s.score * 10 : 0
  })

  chart.setOption({
    tooltip: { trigger: 'item' },
    radar: {
      radius: '65%',
      indicator: DIMENSIONS.map(d => ({ name: d.name, max: 100 })),
      shape: 'polygon',
      splitNumber: 4,
      axisName: { fontSize: 12 },
    },
    series: [{
      type: 'radar',
      data: [{ value: values }],
      areaStyle: { opacity: 0.25 },
      lineStyle: { width: 2, color: '#409eff' },
      itemStyle: { color: '#409eff' },
    }],
  })
}

onMounted(renderChart)
watch(() => props.scores, renderChart, { deep: true })
</script>
