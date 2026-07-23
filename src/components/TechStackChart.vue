<template>
  <div>
    <div class="languages">
      <div
        v-for="(lang, index) in topLanguages"
        :key="lang.language"
        class="lang-item"
        :style="{ animationDelay: `${0.1 * index}s` }"
      >
        <div class="lang-info">
          <span class="lang-name">{{ lang.language }}</span>
          <span class="lang-percent">{{ lang.percentage }}%</span>
        </div>
        <div class="lang-bar">
          <div
            class="lang-progress"
            :style="{ width: animate ? lang.percentage + '%' : '0%' }"
          ></div>
        </div>
      </div>
    </div>
    <div v-if="!languages.length" class="empty">暂无语言数据</div>
  </div>
</template>

<script setup>
import { computed, ref, onMounted } from 'vue'

const props = defineProps({
  languages: { type: Array, default: () => [] }
})

const animate = ref(false)

onMounted(() => {
  setTimeout(() => {
    animate.value = true
  }, 500)
})

const topLanguages = computed(() => props.languages.slice(0, 6))
</script>

<style scoped>
.languages {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.lang-item {
  display: flex;
  flex-direction: column;
  gap: 6px;
  animation: fadeInUp 0.5s ease backwards;
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.lang-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.lang-name {
  font-weight: 500;
  color: var(--text-h);
  font-size: 14px;
}

.lang-percent {
  color: var(--accent);
  font-weight: 600;
  font-size: 13px;
  font-family: var(--mono);
}

.lang-bar {
  height: 8px;
  background: var(--border);
  border-radius: 4px;
  overflow: hidden;
}

.lang-progress {
  height: 100%;
  background: var(--accent-gradient);
  border-radius: 4px;
  transition: width 1s cubic-bezier(0.4, 0, 0.2, 1);
}

.empty {
  color: var(--text);
  opacity: 0.5;
  font-size: 14px;
  text-align: center;
  padding: 20px 0;
}
</style>
