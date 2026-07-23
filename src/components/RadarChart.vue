<template>
  <div ref="chartDom" class="radar-container"></div>
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
    tooltip: {
      trigger: 'item',
      backgroundColor: 'rgba(255, 255, 255, 0.95)',
      borderColor: '#eee',
      textStyle: { color: '#333' }
    },
    radar: {
      radius: '70%',
      indicator: DIMENSIONS.map(d => ({ name: d.name, max: 100 })),
      shape: 'polygon',
      splitNumber: 5,
      axisName: {
        fontSize: 12,
        color: '#666',
        fontWeight: 500
      },
      splitLine: {
        lineStyle: {
          color: 'rgba(124, 58, 237, 0.1)'
        }
      },
      splitArea: {
        areaStyle: {
          color: ['rgba(124, 58, 237, 0.02)', 'rgba(124, 58, 237, 0.05)']
        }
      },
      axisLine: {
        lineStyle: {
          color: 'rgba(124, 58, 237, 0.15)'
        }
      }
    },
    series: [{
      type: 'radar',
      data: [{
        value: values,
        areaStyle: {
          color: {
            type: 'linear',
            x: 0, y: 0, x2: 0, y2: 1,
            colorStops: [
              { offset: 0, color: 'rgba(124, 58, 237, 0.4)' },
              { offset: 1, color: 'rgba(167, 139, 250, 0.2)' }
            ]
          }
        },
        lineStyle: {
          width: 3,
          color: '#7c3aed'
        },
        itemStyle: {
          color: '#7c3aed',
          borderColor: '#fff',
          borderWidth: 2
        },
        symbol: 'circle',
        symbolSize: 8
      }],
      animationDuration: 1000,
      animationEasing: 'cubicOut'
    }],
  })
}

onMounted(renderChart)
watch(() => props.scores, renderChart, { deep: true })
</script>

<style scoped>
.radar-container {
  width: 100%;
  height: 320px;
  animation: fadeIn 0.8s ease;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: scale(0.95);
  }
  to {
    opacity: 1;
    transform: scale(1);
  }
}
</style>
