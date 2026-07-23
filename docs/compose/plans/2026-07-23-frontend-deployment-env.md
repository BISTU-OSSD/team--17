# 前端部署环境变量配置实施计划

> [!NOTE]
> This document may not reflect the current implementation.
> See the final report for up-to-date state:
> [Final Report](../reports/frontend-deployment-env.md)

> **For agentic workers:** REQUIRED SUB-SKILL: Use compose:subagent (recommended) or compose:execute to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 修改前端代码，使用环境变量配置后端 API 地址，确保部署到 Vercel 时能正常工作

**Architecture:** 修改 ReportPage.vue 中硬编码的 API 路径，改用 `import.meta.env.VITE_API_BASE_URL` 环境变量

**Tech Stack:** Vue 3, Vite, EventSource (SSE)

## Global Constraints

- 开发环境使用 Vite dev proxy（端口 5000 → 8001）
- 生产环境使用环境变量 `VITE_API_BASE_URL`
- 环境变量前缀必须是 `VITE_` 才能在客户端访问

---

### Task 1: 修改 ReportPage.vue 使用环境变量

**Covers:** 前端 API 地址配置

**Files:**
- Modify: `src/views/ReportPage.vue:77`

**Interfaces:**
- Consumes: `import.meta.env.VITE_API_BASE_URL`
- Produces: 动态 API 地址

- [ ] **Step 1: 修改 ReportPage.vue**

```javascript
// 第77行，修改为：
evtSource = new EventSource(`${import.meta.env.VITE_API_BASE_URL}/api/analyze/${owner}/${repo}`)
```

- [ ] **Step 2: 测试本地开发**

运行: `npm run dev`
访问: http://localhost:5000
测试: 输入仓库路径，验证 SSE 连接正常

- [ ] **Step 3: Commit**

```bash
git add src/views/ReportPage.vue
git commit -m "feat: use VITE_API_BASE_URL for API endpoint"
```

---

### Task 2: 创建环境变量模板

**Covers:** 环境变量配置文档

**Files:**
- Create: `.env.example`

**Interfaces:**
- 无

- [ ] **Step 1: 创建 .env.example**

```bash
# 后端 API 地址（部署时在 Vercel 控制台配置）
VITE_API_BASE_URL=http://localhost:8001
```

- [ ] **Step 2: Commit**

```bash
git add .env.example
git commit -m "docs: add .env.example for API base URL"
```

---

### Task 3: 测试构建

**Covers:** 构建验证

**Files:**
- 无

**Interfaces:**
- 无

- [ ] **Step 1: 运行构建**

```bash
npm run build
```

- [ ] **Step 2: 验证构建产物**

检查 `dist/` 目录是否正常生成

- [ ] **Step 3: 测试生产模式**

```bash
npm run preview
```

访问: http://localhost:4173
验证: 前端能正常加载

---

## 执行方式

这是一个简单的 3 步任务，建议使用 **Inline** 方式执行。
