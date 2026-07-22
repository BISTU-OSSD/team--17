```markdown
# DevSkillMapper (GitHub 项目体检与分析平台)

[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688.svg?style=flat&logo=fastapi)](https://fastapi.tiangolo.com/)
[![Vue 3](https://img.shields.io/badge/Frontend-Vue%203-4FC08D.svg?style=flat&logo=vuedotjs)](https://vuejs.org/)
[![Deployed on Railway](https://img.shields.io/badge/Deploy-Railway-0B0D0E.svg?style=flat&logo=railway)](https://railway.app/)
[![Deployed on Vercel](https://img.shields.io/badge/Deploy-Vercel-000000.svg?style=flat&logo=vercel)](https://vercel.com/)
[![CI Pipeline](https://img.shields.io/badge/CI-GitHub%20Actions-2088FF.svg?style=flat&logo=githubactions)](https://github.com/features/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 📌 项目简介

**DevSkillMapper** 是一个基于 GitHub REST API 与大模型分析的开源仓库评估与体检平台。

用户只需输入任意 GitHub 仓库地址，系统即可多维度自动抓取仓库数据、计算健康度六维评分、生成技术栈饼图与雷达图，并通过 AI 智能体输出深度的项目分析报告与改进建议，帮助开发者与评估者快速掌握项目质量与社区活跃度。

---

## 🚀 在线演示与 API 文档 (Live Demo)

- 🌐 **前端公网演示地址**: [https://dev-skill-mapper.vercel.app](https://dev-skill-mapper.vercel.app) *(等待 Vercel 部署完成后更新)*
- ⚡ **后端 API 服务**: `https://team-17-backend-production-0c19.up.railway.app`
- 📖 **API 交互式文档 (Swagger UI)**: [https://team-17-backend-production-0c19.up.railway.app/docs](https://team-17-backend-production-0c19.up.railway.app/docs)

---

## 🔥 核心功能

- 📊 **健康度六维评分模型**：从活跃度、社区响应、文档质量、代码规模、稳定性及影响力进行综合评估。
- 🔥 **仓库动态与趋势分析**：深度分析 Commit 频率、Issue 解决周期及 Release 迭代情况。
- 💻 **技术栈与语言占比**：可视化展示项目核心语言分布与代码结构。
- 🤖 **AI 驱动的体检报告**：结合大语言模型（LLM）对项目质量、潜在风险与优化方向给出定制化建议。
- 💡 **相似项目推荐引擎**：基于语言、话题（Topics）与 Star 数精准推荐优质同类开源项目。

---

## 🛠️ 技术架构与工程化实践 (Architecture & DevOps)

### 系统架构


```

[ 用户端 Browser ]
│
▼ (HTTPS)
[ 前端应用 (Vercel / Vue3 + Vite + ECharts) ]
│
▼ (REST API)
[ 后端 API 服务 (Railway / FastAPI) ]
├──► [ GitHub REST API ] ── (拉取仓库元数据、Commit、Issue)
├──► [ 评分算法 Engine ] ── (计算六维健康度与推荐度)
└──► [ LLM 分析服务 ]   ── (生成 AI 项目体检建议)

```

### 工程化亮点 (DevOps & QA)
- **容器化部署 (Docker)**：后端统一打包为 Docker 镜像并部署于 Railway 云平台，实现了自动化的动态端口绑定与平滑重启。
- **持续集成 (CI Pipeline)**：基于 GitHub Actions 配置自动化工作流，在代码 PR/Push 时自动触发 `flake8` 校验与 `pytest` 单元测试。
- **规范化接口交付**：采用 OpenAPI / Swagger 标准自动生成云端交互式 API 调试文档。

---

## 📁 项目结构


```

DevSkillMapper/
├── .github/
│   └── workflows/          # GitHub Actions CI 工作流配置
│       └── ci.yml
├── backend/                # FastAPI 后端服务根目录
│   ├── app/
│   │   ├── api/            # API 路由接口定义 (/api/analyze, /api/health)
│   │   ├── core/           # 配置文件与环境变量加载
│   │   ├── services/       # GitHub API 数据获取、评分算法与大模型对接
│   │   └── models/         # Pydantic 数据模型与 Schema 定义
│   ├── Dockerfile          # 容器构建 Dockerfile
│   ├── requirements.txt    # Python 依赖清单
│   └── server.py           # 应用启动入口
├── frontend/               # Vue3 + Vite 前端工程
│   ├── src/
│   │   ├── components/     # 可视化图表组件 (ECharts 雷达图/饼图)
│   │   ├── views/          # 首页输入页与分析结果页
│   │   └── api/            # Axios 后端接口封装
│   └── package.json
├── tests/                  # pytest 后端单元测试目录
└── README.md

```

---

## 💻 本地开发指南

### 前置要求
- Python 3.10+
- Node.js 18+
- Git

### 1. 后端启动 (Backend)

```bash
# 进入后端目录
cd backend

# 安装依赖
pip install -r requirements.txt

# 本地启动开发服务器
uvicorn server:app --reload --host 0.0.0.0 --port 8000

```

启动成功后，浏览器打开 `http://localhost:8000/docs` 即可进行接口调试。

### 2. 前端启动 (Frontend)

```bash
# 进入前端目录
cd frontend

# 安装依赖
npm install

# 启动开发服务
npm run dev

```

---

## 👥 团队分工 (Team)

| 姓名 / 角色 | 负责模块与职责 |
| --- | --- |
| **成员 1** | **项目负责人 & 后端架构**：FastAPI 骨架搭建、接口路由设计、数据与算法链路串联、答辩主讲 |
| **成员 2** | **仓库数据获取**：GitHub REST API 封装、限流处理、缓存策略与原始数据提取 |
| **成员 3** | **评分算法 & 推荐引擎**：六维健康度模型设计、相似仓库推荐算法实现 |
| **成员 4** | **前端开发 & 可视化**：Vue3 页面构建、ECharts 各种雷达图/饼图开发、后端接口对接 |
| **丁程家祺** | **工程化 & 质量保障**：GitHub Actions CI 搭建、Railway/Vercel 自动化部署、pytest 测试编写、项目文档 |

---

## 📄 开源协议

本项目遵循 [MIT License](https://www.google.com/search?q=LICENSE) 开源协议。

```

```
