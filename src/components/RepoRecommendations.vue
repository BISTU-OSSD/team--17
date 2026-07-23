<template>
  <div class="recommendations">
    <div class="summary-content">
      <p class="summary">{{ summary || '暂无总结' }}</p>
    </div>
  </div>
</template>

<script setup>
defineProps({
  summary: { type: String, default: '' }
})
</script>

<style scoped>
.recommendations {
  position: relative;
}

.summary-content {
  position: relative;
  padding: 20px;
  background: linear-gradient(135deg, var(--accent-bg) 0%, rgba(167, 139, 250, 0.05) 100%);
  border-radius: 12px;
  border-left: 4px solid var(--accent);
}

.summary {
  font-size: 15px;
  line-height: 1.8;
  color: var(--text);
  margin: 0;
}
</style>
