<template>
  <div ref="chartDom" style="width: 100%; height: 420px;"></div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import * as echarts from 'echarts'

const chartDom = ref(null)

onMounted(() => {
  const chart = echarts.init(chartDom.value)
  const option = {
    tooltip: {
      trigger: 'item'
    },
    radar: {
      radius: '70%',
      indicator: [
        { name: '学习力', max: 100 },
        { name: '执行力', max: 100 },
        { name: '沟通力', max: 100 },
        { name: '自律能力', max: 100 },
        { name: '思考能力', max: 100 }
      ],
      shape: 'polygon'
    },
    series: [
      {
        name: '个人能力',
        type: 'radar',
        areaStyle: { opacity: 0.3 },
        lineStyle: { width: 2 },
        data: [{ value: [76, 82, 68, 90, 72] }]
      }
    ]
  }
  chart.setOption(option)
})
</script>