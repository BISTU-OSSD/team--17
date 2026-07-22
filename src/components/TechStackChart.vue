<template>
  <div>
    <h3>技术栈分布</h3>
    <div class="tags">
      <span v-for="lang in topLanguages" :key="lang.language" class="tag">
        {{ lang.language }} {{ lang.percentage }}%
      </span>
    </div>
    <div v-if="!languages.length" class="empty">暂无语言数据</div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  languages: { type: Array, default: () => [] }
})

const topLanguages = computed(() => props.languages.slice(0, 6))
</script>

<style scoped>
h3 { margin: 0 0 12px; font-size: 16px; }
.tags { display: flex; flex-wrap: wrap; gap: 8px; }
.tag {
  background: #ecf5ff;
  color: #409eff;
  padding: 4px 12px;
  border-radius: 4px;
  font-size: 13px;
}
.empty { color: #aaa; font-size: 14px; }
</style>
