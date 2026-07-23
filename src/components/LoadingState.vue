<template>
  <div class="loading">
    <div class="spinner-container">
      <div class="spinner-outer"></div>
      <div class="spinner-inner"></div>
      <div class="spinner-core"></div>
    </div>
    <p class="loading-text">正在分析中</p>
    <p class="loading-hint">LLM 需要一些时间来处理...</p>
    <div class="loading-dots">
      <span></span>
      <span></span>
      <span></span>
    </div>
  </div>
</template>

<style scoped>
.loading {
  text-align: center;
  padding: 100px 20px;
  animation: fadeIn 0.5s ease;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: scale(0.95);
  }
  to {
    opacity: 1;
    transform: scale(1);
  }
}

.spinner-container {
  position: relative;
  width: 80px;
  height: 80px;
  margin: 0 auto 32px;
}

.spinner-outer {
  position: absolute;
  inset: 0;
  border: 3px solid transparent;
  border-top-color: var(--accent);
  border-radius: 50%;
  animation: spin 1.2s linear infinite;
}

.spinner-inner {
  position: absolute;
  inset: 10px;
  border: 3px solid transparent;
  border-top-color: var(--accent-light);
  border-radius: 50%;
  animation: spin 1.8s linear infinite reverse;
}

.spinner-core {
  position: absolute;
  inset: 20px;
  background: var(--accent-gradient);
  border-radius: 50%;
  animation: pulse 1.5s ease-in-out infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

@keyframes pulse {
  0%, 100% {
    transform: scale(1);
    opacity: 1;
    box-shadow: 0 0 20px rgba(124, 58, 237, 0.5);
  }
  50% {
    transform: scale(0.8);
    opacity: 0.7;
    box-shadow: 0 0 30px rgba(124, 58, 237, 0.8);
  }
}

.loading-text {
  font-size: 20px;
  font-weight: 600;
  color: var(--text-h);
  margin: 0 0 8px;
  animation: fadeInUp 0.6s ease 0.2s backwards;
}

.loading-hint {
  font-size: 14px;
  color: var(--text);
  opacity: 0.7;
  margin: 0 0 24px;
  animation: fadeInUp 0.6s ease 0.3s backwards;
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

.loading-dots {
  display: flex;
  justify-content: center;
  gap: 8px;
  animation: fadeIn 0.6s ease 0.4s backwards;
}

.loading-dots span {
  width: 8px;
  height: 8px;
  background: var(--accent);
  border-radius: 50%;
  animation: bounce 1.4s ease-in-out infinite;
}

.loading-dots span:nth-child(1) {
  animation-delay: 0s;
}

.loading-dots span:nth-child(2) {
  animation-delay: 0.2s;
}

.loading-dots span:nth-child(3) {
  animation-delay: 0.4s;
}

@keyframes bounce {
  0%, 80%, 100% {
    transform: translateY(0);
    opacity: 0.5;
  }
  40% {
    transform: translateY(-12px);
    opacity: 1;
  }
}
</style>
