<template>
  <div class="home">
    <h1>给开源仓库做体检</h1>
    <p class="subtitle">输入 GitHub 仓库路径，获取 AI 智能分析报告</p>
    <div class="search-box">
      <input
        v-model="repoName"
        placeholder="输入仓库路径，例如 facebook/react"
        @keyup.enter="analyze"
      />
      <button @click="analyze" :disabled="!repoName.trim()">开始分析</button>
    </div>
    <p v-if="error" class="error">{{ error }}</p>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
const router = useRouter()
const repoName = ref('')
const error = ref('')

const analyze = () => {
  error.value = ''
  let val = repoName.value.trim()
  if (!val) {
    error.value = '请输入仓库路径'
    return
  }

  // 支持多种输入格式
  // https://github.com/owner/repo
  // github.com/owner/repo
  // owner/repo
  let match = val.match(/github\.com\/([^/]+)\/([^/]+)/)
  if (match) {
    router.push(`/report/${match[1]}/${match[2]}`)
    return
  }

  // owner/repo 格式
  const arr = val.split('/')
  if (arr.length === 2 && arr[0] && arr[1]) {
    router.push(`/report/${arr[0]}/${arr[1]}`)
    return
  }

  error.value = '格式错误，请输入 owner/repo 或完整 GitHub URL'
}
</script>

<style scoped>
.home {
  max-width: 600px;
  margin: 120px auto 0;
  text-align: center;
}
h1 {
  font-size: 40px;
  margin-bottom: 12px;
}
.subtitle {
  color: #888;
  font-size: 16px;
  margin-bottom: 40px;
}
.search-box {
  display: flex;
  gap: 12px;
  justify-content: center;
}
.search-box input {
  flex: 1;
  padding: 12px 16px;
  font-size: 16px;
  border: 1px solid #ddd;
  border-radius: 8px;
  outline: none;
}
.search-box input:focus {
  border-color: #409eff;
}
.search-box button {
  padding: 12px 28px;
  font-size: 16px;
  background: #409eff;
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
}
.search-box button:disabled {
  background: #ccc;
  cursor: not-allowed;
}
.search-box button:hover:not(:disabled) {
  background: #337ecc;
}
.error {
  color: #f56c6c;
  margin-top: 16px;
}
</style>
