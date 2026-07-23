<template>
  <div class="info-grid">
    <div class="info-item">
      <span class="info-label">Star</span>
      <span class="info-value star">
        <svg viewBox="0 0 24 24" fill="currentColor">
          <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/>
        </svg>
        {{ repo.stars }}
      </span>
    </div>
    <div class="info-item">
      <span class="info-label">Fork</span>
      <span class="info-value fork">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <circle cx="12" cy="18" r="3"/>
          <circle cx="6" cy="6" r="3"/>
          <circle cx="18" cy="6" r="3"/>
          <path d="M18 9v1a2 2 0 0 1-2 2H8a2 2 0 0 1-2-2V9"/>
          <path d="M12 12v3"/>
        </svg>
        {{ repo.forks }}
      </span>
    </div>
    <div class="info-item">
      <span class="info-label">语言</span>
      <span class="info-value">{{ repo.language || '未知' }}</span>
    </div>
    <div class="info-item">
      <span class="info-label">许可证</span>
      <span class="info-value">{{ repo.license || '未知' }}</span>
    </div>
  </div>
</template>

<script setup>
defineProps({
  repo: { type: Object, required: true }
})
</script>

<style scoped>
.info-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
}

.info-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
  padding: 12px;
  background: var(--accent-bg);
  border-radius: 8px;
}

.info-label {
  font-size: 12px;
  color: var(--text);
  opacity: 0.7;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.info-value {
  font-size: 18px;
  font-weight: 600;
  color: var(--text-h);
  display: flex;
  align-items: center;
  gap: 6px;
}

.info-value.star {
  color: #f59e0b;
}

.info-value.star svg {
  width: 18px;
  height: 18px;
}

.info-value.fork {
  color: var(--accent);
}

.info-value.fork svg {
  width: 18px;
  height: 18px;
}

@media (max-width: 480px) {
  .info-grid {
    grid-template-columns: 1fr;
  }
}
</style>
