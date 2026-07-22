<template>
  <div>
    <h3>AI 分析总结</h3>
    <p class="summary">{{ summary || '暂无总结' }}</p>
  </div>
</template>

<script setup>
defineProps({
  summary: { type: String, default: '' }
})
</script>

<style scoped>
h3 { margin: 0 0 12px; font-size: 16px; }
.summary {
  font-size: 14px;
  line-height: 1.7;
  color: #555;
}
</style>
