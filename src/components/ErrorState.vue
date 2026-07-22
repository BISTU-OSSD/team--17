<template>
  <div class="error-box">
    <p class="error-msg">{{ message || '读取数据失败，请刷新重试' }}</p>
  </div>
</template>

<script setup>
defineProps({
  message: { type: String, default: '' }
})
</script>

<style scoped>
.error-box {
  text-align: center;
  padding: 80px 0;
}
.error-msg {
  color: #f56c6c;
  font-size: 16px;
}
</style>
