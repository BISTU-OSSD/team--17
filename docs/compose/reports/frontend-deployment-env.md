---
feature: frontend-deployment-env
status: delivered
specs: []
plans:
  - ../plans/2026-07-23-frontend-deployment-env.md
branch: main
commits: 78b0af3..673a962
---

# 前端部署环境变量配置 — Final Report

## What Was Built

修改了前端代码，使用环境变量 `VITE_API_BASE_URL` 配置后端 API 地址，替代原先硬编码的 `/api` 路径。这使得前端可以部署到 Vercel 等平台，通过环境变量灵活配置后端地址。

## Architecture

- **修改文件**: `src/views/ReportPage.vue:77`
- **新增文件**: `.env.example`（环境变量模板）
- **环境变量**: `VITE_API_BASE_URL`（前缀 `VITE_` 确保客户端可访问）

### Design Decisions

- 使用 `import.meta.env.VITE_API_BASE_URL` 而非硬编码，支持多环境部署
- 保留 Vite dev proxy 配置，开发时无需设置环境变量即可工作

## Usage

**本地开发**:
```bash
# 无需设置环境变量，Vite proxy 自动代理到 8001
npm run dev
```

**生产部署**:
```bash
# 在 Vercel 控制台设置环境变量
VITE_API_BASE_URL=https://your-backend-domain.com
```

## Verification

- `npm run dev` 启动成功，本地测试 SSE 连接正常
- `npm run build` 构建成功，`dist/` 目录正常生成
- 构建产物包含所有必要文件（HTML、CSS、JS）

## Journey Log

- [lesson] Vite 环境变量前缀必须是 `VITE_` 才能在客户端访问
- [lesson] ECharts chunk 较大（~1.1MB），构建时会有警告，但不影响功能

## Source Materials

| File | Role | Notes |
|------|------|-------|
| `../plans/2026-07-23-frontend-deployment-env.md` | Implementation plan | Complete |
