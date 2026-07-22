<template>
  <div style="padding: 30px;">
    <div v-if="owner === 'test' && repo === 'demo'">
      <h3>项目基本信息</h3>
      <ul style="padding-left: 20px;">
        <li>项目名称：开源项目</li>
        <li>收藏数：2368</li>
        <li>复刻数：521</li>
      </ul>

      <h3 style="margin-top: 24px;">技术栈标签</h3>
      <div style="margin:8px 0;">
        <span style="background:#428bff;color:white;padding:5px 10px;border-radius:4px;margin-right:10px;">Vue3</span>
        <span style="background:#428bff;color:white;padding:5px 10px;border-radius:4px;margin-right:10px;">ECharts</span>
        <span style="background:#428bff;color:white;padding:5px 10px;border-radius:4px;">JavaScript</span>
      </div>

      <h3 style="margin-top: 24px;">社区活跃度介绍</h3>
      <p>社区交流频繁，维护频率稳定，适合新手学习使用</p >

      <h3 style="margin-top: 24px;">推荐评语</h3>
      <p>整体质量优秀，结构清晰，非常适合前端练习案例</p >

      <div ref="chartRef" style="width: 480px;height: 420px;margin-top:15px;"></div>
    </div>
    <div v-else>仓库不存在</div>
  </div>
</template>

<script setup>
import { useRoute } from 'vue-router'
import { ref, onMounted, nextTick } from 'vue'
import * as echarts from 'echarts'

const route = useRoute()
const owner = route.params.owner
const repo = route.params.repo
const chartRef = ref(null)

nextTick(() => {
  const myChart = echarts.init(chartRef.value)
  myChart.clear()
  const option = {
    radar: {
      shape: 'polygon',
      startAngle: 90,
      indicator: [
        { name: '学习力', max: 100 },
        { name: '自律性', max: 100 },
        { name: '执行力', max: 100 },
        { name: '创造力', max: 100 },
        { name: '思考能力', max: 100 }
      ],
      splitNumber: 4
    },
    series: [{
      type: 'radar',
      data: [88, 40, 82, 55, 70],
      symbol: 'circle',
      symbolSize: 6,
      lineStyle: {
        color: '#428bff',
        width: 2
      },
      areaStyle: {
        color: 'rgba(66, 139, 255, 0.25)'
      }
    }]
  }
  myChart.setOption(option, true)
})
</script>