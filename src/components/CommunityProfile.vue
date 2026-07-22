<template>
  <div>
    <h3>社区活跃度</h3>
    <ul class="stat-list">
      <li>
        <span class="label">总贡献者</span>
        <span class="value">{{ contributors.total_contributors }}</span>
      </li>
      <li>
        <span class="label">近30天活跃</span>
        <span class="value">{{ contributors.active_30d_contributors }}</span>
      </li>
      <li>
        <span class="label">Bus Factor</span>
        <span class="value">{{ contributors.bus_factor }}</span>
      </li>
      <li>
        <span class="label">近30天提交</span>
        <span class="value">{{ commits.commits_last_30_days }}</span>
      </li>
      <li>
        <span class="label">每周平均提交</span>
        <span class="value">{{ commits.commit_frequency_per_week }}</span>
      </li>
      <li>
        <span class="label">Issue 关闭率</span>
        <span class="value">{{ (issues.close_rate * 100).toFixed(1) }}%</span>
      </li>
    </ul>
  </div>
</template>

<script setup>
defineProps({
  contributors: { type: Object, default: () => ({}) },
  commits: { type: Object, default: () => ({}) },
  issues: { type: Object, default: () => ({}) },
})
</script>

<style scoped>
h3 { margin: 0 0 12px; font-size: 16px; }
.stat-list {
  list-style: none;
  padding: 0;
  margin: 0;
}
.stat-list li {
  display: flex;
  justify-content: space-between;
  padding: 6px 0;
  border-bottom: 1px solid #f5f5f5;
  font-size: 14px;
}
.label { color: #888; }
.value { color: #333; font-weight: 500; }
</style>
