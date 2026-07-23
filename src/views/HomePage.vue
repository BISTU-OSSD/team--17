<template>
  <div class="home">
    <div class="badge">AI 驱动的项目分析</div>
    <h1>给开源仓库做体检</h1>
    <p class="subtitle">输入 GitHub 仓库路径，获取 AI 智能分析报告</p>
    <div class="search-box">
      <div class="input-wrapper">
        <svg class="search-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <circle cx="11" cy="11" r="8"/>
          <path d="m21 21-4.35-4.35"/>
        </svg>
        <input
          v-model="repoName"
          placeholder="输入仓库路径，例如 facebook/react"
          @keyup.enter="analyze"
        />
      </div>
      <button @click="analyze" :disabled="!repoName.trim()">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M5 12h14M12 5l7 7-7 7"/>
        </svg>
        开始分析
      </button>
    </div>
    <p v-if="error" class="error">{{ error }}</p>
    <div class="examples">
      <span>试试：</span>
      <button @click="repoName = 'facebook/react'" class="example">facebook/react</button>
      <button @click="repoName = 'vuejs/vue'" class="example">vuejs/vue</button>
      <button @click="repoName = 'torvalds/linux'" class="example">torvalds/linux</button>
    </div>
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
  let match = val.match(/github\.com\/([^/]+)\/([^/]+)/)
  if (match) {
    router.push(`/report/${match[1]}/${match[2]}`)
    return
  }

  const arr = val.split('/')
  if (arr.length === 2 && arr[0] && arr[1]) {
    router.push(`/report/${arr[0]}/${arr[1]}`)
    return
  }

  error.value = '格式错误，请输入 owner/repo 或完整 GitHub URL'
}
</script>

<style scoped>
/* 页面进入动画 */
@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes fadeInDown {
  from {
    opacity: 0;
    transform: translateY(-20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes float {
  0%, 100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-8px);
  }
}

@keyframes pulse-glow {
  0%, 100% {
    box-shadow: 0 4px 12px rgba(124, 58, 237, 0.3);
  }
  50% {
    box-shadow: 0 6px 24px rgba(124, 58, 237, 0.5);
  }
}

.home {
  max-width: 640px;
  margin: 0 auto;
  padding: 80px 20px;
  text-align: center;
}

.badge {
  display: inline-block;
  padding: 8px 20px;
  font-size: 13px;
  font-weight: 500;
  color: var(--accent);
  background: var(--accent-bg);
  border: 1px solid var(--accent-border);
  border-radius: 100px;
  margin-bottom: 24px;
  animation: fadeInDown 0.6s ease;
  transition: all 0.3s ease;
}

.badge:hover {
  background: rgba(124, 58, 237, 0.15);
  transform: scale(1.05);
}

h1 {
  font-size: 56px;
  margin-bottom: 16px;
  line-height: 1.1;
  animation: fadeIn 0.8s ease 0.1s backwards;
  background: var(--accent-gradient);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.subtitle {
  color: var(--text);
  font-size: 18px;
  margin-bottom: 40px;
  line-height: 1.5;
  animation: fadeIn 0.8s ease 0.2s backwards;
}

.search-box {
  display: flex;
  gap: 12px;
  justify-content: center;
  animation: slideUp 0.8s ease 0.3s backwards;
}

.input-wrapper {
  position: relative;
  flex: 1;
}

.search-icon {
  position: absolute;
  left: 16px;
  top: 50%;
  transform: translateY(-50%);
  width: 20px;
  height: 20px;
  color: var(--text);
  opacity: 0.5;
  transition: opacity 0.3s ease;
}

.search-box input:focus ~ .search-icon {
  opacity: 1;
  color: var(--accent);
}

.search-box input {
  width: 100%;
  padding: 16px 16px 16px 48px;
  font-size: 16px;
  border: 2px solid var(--border);
  border-radius: 12px;
  outline: none;
  background: var(--card-bg);
  backdrop-filter: blur(8px);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  box-sizing: border-box;
}

.search-box input:focus {
  border-color: var(--accent);
  box-shadow: 0 0 0 4px var(--accent-bg), 0 8px 24px rgba(124, 58, 237, 0.15);
  transform: translateY(-2px);
}

.search-box input::placeholder {
  color: var(--text);
  opacity: 0.5;
}

.search-box button {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 16px 32px;
  font-size: 16px;
  font-weight: 500;
  background: var(--accent-gradient);
  color: white;
  border: none;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 4px 12px rgba(124, 58, 237, 0.3);
  animation: pulse-glow 2s ease-in-out infinite;
}

.search-box button svg {
  width: 18px;
  height: 18px;
  transition: transform 0.3s ease;
}

.search-box button:disabled {
  background: var(--border);
  box-shadow: none;
  cursor: not-allowed;
  animation: none;
}

.search-box button:hover:not(:disabled) {
  transform: translateY(-2px) scale(1.02);
  box-shadow: 0 8px 24px rgba(124, 58, 237, 0.4);
}

.search-box button:hover:not(:disabled) svg {
  transform: translateX(4px);
}

.search-box button:active:not(:disabled) {
  transform: translateY(0) scale(0.98);
}

.error {
  color: var(--danger);
  margin-top: 16px;
  font-size: 14px;
  animation: fadeIn 0.4s ease;
}

.examples {
  margin-top: 32px;
  font-size: 14px;
  color: var(--text);
  opacity: 0;
  animation: fadeIn 0.8s ease 0.5s forwards;
}

.examples span {
  margin-right: 12px;
  opacity: 0.7;
}

.example {
  background: none;
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 6px 14px;
  margin: 0 6px;
  font-size: 13px;
  font-family: var(--mono);
  color: var(--accent);
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.example:hover {
  background: var(--accent-bg);
  border-color: var(--accent-border);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(124, 58, 237, 0.15);
}

.example:active {
  transform: translateY(0);
}

@media (max-width: 640px) {
  .home {
    padding: 60px 16px;
  }

  h1 {
    font-size: 36px;
  }

  .search-box {
    flex-direction: column;
  }

  .search-box button {
    width: 100%;
    justify-content: center;
  }
}
</style>
