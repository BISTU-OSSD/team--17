import { useEffect, useRef } from 'react'
import * as echarts from 'echarts'

const LABEL_MAP = {
  activity: '活跃度',
  community: '社区响应',
  documentation: '文档质量',
  scale: '代码规模',
  stability: '稳定性',
  impact: '影响力',
}

export default function RadarChart({ scores, grade }) {
  const chartRef = useRef(null)
  const instanceRef = useRef(null)

  useEffect(() => {
    if (!chartRef.current) return

    if (!instanceRef.current) {
      instanceRef.current = echarts.init(chartRef.current)
    }

    const indicators = Object.entries(LABEL_MAP).map(([key, label]) => ({
      name: label,
      max: 100,
    }))

    const values = Object.keys(LABEL_MAP).map((key) => scores[key] || 0)

    instanceRef.current.setOption({
      tooltip: {
        formatter: (params) => {
          const lines = params.value.map((v, i) =>
            `${indicators[i].name}: ${v}`
          ).join('<br/>')
          return `<strong>健康评分 (${grade})</strong><br/>${lines}`
        },
      },
      radar: {
        indicator: indicators,
        radius: '65%',
        splitArea: {
          areaStyle: {
            color: ['rgba(96, 165, 250, 0.02)', 'rgba(96, 165, 250, 0.04)'],
          },
        },
        axisLine: {
          lineStyle: {
            color: 'rgba(148, 163, 184, 0.3)',
          },
        },
        splitLine: {
          lineStyle: {
            color: 'rgba(148, 163, 184, 0.3)',
          },
        },
      },
      series: [
        {
          type: 'radar',
          data: [
            {
              value: values,
              name: grade,
              areaStyle: {
                color: 'rgba(96, 165, 250, 0.3)',
              },
              lineStyle: {
                color: '#60a5fa',
                width: 2,
              },
              itemStyle: {
                color: '#60a5fa',
              },
            },
          ],
        },
      ],
    })

    const handleResize = () => instanceRef.current?.resize()
    window.addEventListener('resize', handleResize)
    return () => window.removeEventListener('resize', handleResize)
  }, [scores, grade])

  return (
    <div className="card">
      <h2>六维健康评分</h2>
      <div ref={chartRef} className="chart-wrapper" />
    </div>
  )
}
