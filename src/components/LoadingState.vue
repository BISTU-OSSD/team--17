<template>
  <div class="loading">
    <div class="spinner"></div>
    <p>正在分析中，LLM 需要一些时间...</p>
  </div>
</template>

<style scoped>
.loading {
  text-align: center;
  padding: 80px 0;
}
.spinner {
  width: 40px;
  height: 40px;
  border: 3px solid #eee;
  border-top-color: #409eff;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
  margin: 0 auto 16px;
}
@keyframes spin { to { transform: rotate(360deg); } }
p { color: #888; font-size: 14px; }
</style>
