<template>
  <div>
    <h3>项目基本信息</h3>
    <ul class="info-list">
      <li><span class="label">项目名称</span><span class="value">{{ repo.full_name }}</span></li>
      <li><span class="label">Star</span><span class="value">{{ repo.stars }}</span></li>
      <li><span class="label">Fork</span><span class="value">{{ repo.forks }}</span></li>
      <li><span class="label">主要语言</span><span class="value">{{ repo.language || '未知' }}</span></li>
      <li><span class="label">许可证</span><span class="value">{{ repo.license || '未知' }}</span></li>
      <li><span class="label">Open Issues</span><span class="value">{{ repo.open_issues_count }}</span></li>
    </ul>
  </div>
</template>

<script setup>
defineProps({
  repo: { type: Object, required: true }
})
</script>

<style scoped>
h3 { margin: 0 0 12px; font-size: 16px; }
.info-list {
  list-style: none;
  padding: 0;
  margin: 0;
}
.info-list li {
  display: flex;
  justify-content: space-between;
  padding: 6px 0;
  border-bottom: 1px solid #f5f5f5;
  font-size: 14px;
}
.label { color: #888; }
.value { color: #333; font-weight: 500; }
</style>
