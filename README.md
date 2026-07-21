# team--17
# DevSkillMapper

## 项目简介

DevSkillMapper 是一个基于 GitHub API 的开源仓库分析平台。

用户输入 GitHub 仓库地址后，系统能够自动分析仓库的多项指标，并以可视化方式展示分析结果，帮助开发者快速了解项目质量与活跃程度。

---

## 功能介绍

目前支持以下功能：

- 📊 仓库影响力分析（Stars、Forks 等）
- 🔥 仓库活跃度分析（Commit、Issue、Release 等）
- 💻 技术栈统计（编程语言占比）
- 👥 社区参与度分析（Contributors、Issues）
- 📈 数据可视化展示

---

## 技术架构

### 前端

- Vue3
- Vite
- ECharts

### 后端

- Python
- FastAPI

### 数据来源

- GitHub REST API

---

## 项目结构

```
DevSkillMapper

├── backend        后端服务
├── frontend       前端页面
├── tests          测试代码
├── docs           项目文档
└── .github        GitHub 配置
```

---

## 本地运行

### 后端

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

### 前端

```bash
cd frontend
npm install
npm run dev
```

---

## 项目成员

- 成员1：项目管理、后端开发
- 成员2：GitHub API 数据获取
- 成员3：仓库分析算法
- 成员4：前端页面开发
- 丁程家祺：工程化、测试、CI、部署

---

## 开源协议

本项目采用 MIT License 开源。