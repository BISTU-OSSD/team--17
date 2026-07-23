<template>
  <div class="community">
    <div class="stat-grid">
      <div class="stat-card">
        <div class="stat-icon contributors">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/>
            <circle cx="9" cy="7" r="4"/>
            <path d="M23 21v-2a4 4 0 0 0-3-3.87"/>
            <path d="M16 3.13a4 4 0 0 1 0 7.75"/>
          </svg>
        </div>
        <div class="stat-content">
          <span class="stat-value">{{ contributors.total_contributors }}</span>
          <span class="stat-label">总贡献者</span>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon commits">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="12" cy="12" r="4"/>
            <line x1="1.05" y1="12" x2="7" y2="12"/>
            <line x1="17.01" y1="12" x2="22.96" y2="12"/>
          </svg>
        </div>
        <div class="stat-content">
          <span class="stat-value">{{ commits.commits_last_30_days }}</span>
          <span class="stat-label">近30天提交</span>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon frequency">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/>
          </svg>
        </div>
        <div class="stat-content">
          <span class="stat-value">{{ commits.commit_frequency_per_week }}</span>
          <span class="stat-label">每周平均提交</span>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon issues">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="12" cy="12" r="10"/>
            <line x1="12" y1="8" x2="12" y2="12"/>
            <line x1="12" y1="16" x2="12.01" y2="16"/>
          </svg>
        </div>
        <div class="stat-content">
          <span class="stat-value">{{ (issues.close_rate * 100).toFixed(0) }}%</span>
          <span class="stat-label">Issue 关闭率</span>
        </div>
      </div>
    </div>
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
.stat-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
}

.stat-card {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 16px;
  background: var(--accent-bg);
  border-radius: 12px;
  transition: all 0.3s ease;
  animation: scaleIn 0.4s ease backwards;
}

.stat-card:nth-child(1) { animation-delay: 0.7s; }
.stat-card:nth-child(2) { animation-delay: 0.8s; }
.stat-card:nth-child(3) { animation-delay: 0.9s; }
.stat-card:nth-child(4) { animation-delay: 1.0s; }

@keyframes scaleIn {
  from {
    opacity: 0;
    transform: scale(0.9);
  }
  to {
    opacity: 1;
    transform: scale(1);
  }
}

.stat-card:hover {
  background: rgba(124, 58, 237, 0.12);
  transform: translateY(-4px) scale(1.02);
  box-shadow: 0 8px 24px rgba(124, 58, 237, 0.2);
}

.stat-icon {
  width: 44px;
  height: 44px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 12px;
  background: var(--accent-gradient);
  color: white;
}

.stat-icon svg {
  width: 22px;
  height: 22px;
}

.stat-content {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.stat-value {
  font-size: 24px;
  font-weight: 700;
  color: var(--text-h);
  font-family: var(--mono);
}

.stat-label {
  font-size: 13px;
  color: var(--text);
  opacity: 0.7;
}

@media (max-width: 480px) {
  .stat-grid {
    grid-template-columns: 1fr;
  }
}
</style>
