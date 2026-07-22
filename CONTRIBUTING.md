# 贡献指南（Contributing）

感谢你对 DevSkillMapper 项目的关注！

为了保证项目开发规范，请按照以下流程参与开发。

---

## 开发流程

### ① 创建 Issue

任何新功能、Bug 修复或优化建议，请先创建 Issue。

例如：

- 新增仓库影响力分析
- 修复活跃度计算错误
- 优化页面布局

---

### ② 创建开发分支

不要直接修改 main 分支。

建议分支命名：

```
feature/功能名称
bugfix/问题名称
docs/文档名称
```

例如：

```
feature/repository-analysis

bugfix/activity-score

docs/readme-update
```

---

### ③ 提交代码

提交信息建议使用统一格式。

例如：

```
feat: 新增仓库分析功能

fix: 修复影响力评分错误

docs: 更新 README

ci: 配置 GitHub Actions
```

---

### ④ 创建 Pull Request

提交 Pull Request 时，请说明：

- 修改内容
- 修改原因
- 是否已经完成测试
- 是否关联 Issue

例如：

```
Close #5
```

---

### ⑤ Code Review

所有 Pull Request 必须经过至少一名成员 Review 后才能合并。

Review 内容包括：

- 功能是否正确
- 是否影响其他模块
- 是否符合代码规范
- 是否通过测试

---

## 编码规范

### Python

遵循 PEP8 编码规范。

### JavaScript

遵循 ESLint 推荐规范。

---

感谢你的贡献！