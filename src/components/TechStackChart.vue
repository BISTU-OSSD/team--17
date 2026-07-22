<template>
  <div class="stack-card">
    <h3>技术栈标签</h3>
    <div class="tags">
      <span class="tag">Vue3</span>
      <span class="tag">ECharts</span>
      <span class="tag">JavaScript</span>
    </div>
  </div>
</template>

<style scoped>
.stack-card{
  border:1px solid #eee;
  padding:16px;
  border-radius:8px;
  margin-bottom:15px;
}
.tags{
  display:flex;
  gap:10px;
  margin-top:10px;
}
.tag{
  background:#409eff;
  color:white;
  padding:4px 10px;
  border-radius:4px;
}
</style>