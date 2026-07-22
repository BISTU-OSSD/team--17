import { useEffect, useRef } from 'react'
import * as echarts from 'echarts'

const COLORS = [
  '#60a5fa', '#a78bfa', '#f472b6', '#fb923c',
  '#34d399', '#fbbf24', '#818cf8', '#f87171',
  '#2dd4bf', '#c084fc', '#38bdf8', '#e879f9',
]

export default function LanguagePie({ languages }) {
  const chartRef = useRef(null)
  const instanceRef = useRef(null)

  useEffect(() => {
    if (!chartRef.current || !languages || Object.keys(languages).length === 0) return

    if (!instanceRef.current) {
      instanceRef.current = echarts.init(chartRef.current)
    }

    const total = Object.values(languages).reduce((a, b) => a + b, 0)
    const data = Object.entries(languages)
      .map(([name, bytes], i) => ({
        name,
        value: +(bytes / total * 100).toFixed(1),
        itemStyle: { color: COLORS[i % COLORS.length] },
      }))
      .sort((a, b) => b.value - a.value)

    instanceRef.current.setOption({
      tooltip: {
        formatter: (params) =>
          `<strong>${params.name}</strong>: ${params.value}%`,
      },
      series: [
        {
          type: 'pie',
          radius: ['40%', '70%'],
          center: ['50%', '50%'],
          data,
          label: {
            color: '#94a3b8',
            formatter: '{b}: {d}%',
          },
          labelLine: {
            lineStyle: { color: 'rgba(148, 163, 184, 0.3)' },
          },
          emphasis: {
            itemStyle: {
              shadowBlur: 10,
              shadowOffsetX: 0,
              shadowColor: 'rgba(0, 0, 0, 0.5)',
            },
          },
        },
      ],
    })

    const handleResize = () => instanceRef.current?.resize()
    window.addEventListener('resize', handleResize)
    return () => window.removeEventListener('resize', handleResize)
  }, [languages])

  return (
    <div className="card">
      <h2>语言分布</h2>
      <div ref={chartRef} className="chart-wrapper" />
    </div>
  )
}
