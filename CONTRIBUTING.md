```markdown
# DevSkillMapper 团队协作与贡献指南

感谢你参与 **DevSkillMapper** 项目的开发！

为了保证代码质量、提高团队协作效率并维持统一的工程规范，请所有团队成员在开发时严格遵守以下流程。

---

## ⚙️ Git 分支规范

主分支 `main` 为生产分支，**严禁直接推送 (push) 代码到 `main` 分支**。

### 1. 分支命名约定

开发新功能或修复问题时，请从最新的 `main` 创建独立分支，命名格式如下：

- **新功能**：`feature/功能简述`（例如：`feature/radar-chart`、`feature/llm-analysis`）
- **Bug 修复**：`bugfix/问题简述`（例如：`bugfix/cors-error`、`bugfix/rate-limit`）
- **文档更新**：`docs/文档名称`（例如：`docs/readme-update`）
- **DevOps/CI**：`ci/配置简述`（例如：`ci/railway-deploy`）

---

## 🔄 规范开发流程

第一步：同步主干代码
在开始任何开发前，先拉取 `main` 的最新代码：
```bash
git checkout main
git pull origin main
第二步：创建并切换分支
Bash
git checkout -b feature/your-feature-name
第三步：提交规范 (Commit Message Standard)
Commit 提交信息要求简明扼要，建议遵循 Conventional Commits 格式：

Bash
<type>(<scope>): <subject>
常用 Type 类型：

feat: 新增功能 (Feature)

fix: 修复 Bug

docs: 仅修改文档 (README, CONTRIBUTING 等)

style: 代码格式调整（不影响逻辑的空格、分号等）

refactor: 重构代码（既不是新功能也不是 Bug 修复）

test: 新加或修改单元测试

ci: CI/CD 自动化构建配置修改（GitHub Actions, Docker 等）

示例：

Bash
git commit -m "feat(api): add /api/analyze endpoint for repo health score"
git commit -m "fix(deploy): resolve dynamic PORT binding issue on Railway"
git commit -m "docs: update API endpoints in README"
第四步：推送分支并发起 Pull Request (PR)
完成本地开发与测试后，将分支推送到远程仓库：

Bash
git push origin feature/your-feature-name
在 GitHub 仓库页面点击 Compare & pull request 提交 PR，并注意填写：

修改内容：清晰描述本次变更做了什么。

测试情况：说明本地/云端调试是否通过。

关联 Issue（如有）：使用 Close #Issue编号 自动关联合集。

🔍 Code Review 与合并机制
自动 CI 检查：提交 PR 后，GitHub Actions 会自动运行 Lint 规范检查与 pytest 单元测试，测试不通过无法合并。

人工 Review：PR 需由项目负责人（成员 1）或至少一名队员 Review 确认无误后，点击 Merge pull request 合并入 main。

清理分支：合并完成后，请及时删除已废弃的 Feature 分支。

📐 代码与测试规范
Python (后端)
代码风格：遵循 PEP8 编码规范，建议使用 flake8 进行本地代码检查。

类型提示：函数定义尽量添加 Typing 类型标注与 Docstring 释义。

单元测试：新增加的核心算法或接口需在 tests/ 目录下补充 pytest 用例，确保测试覆盖率。

Vue3 / JS (前端)
代码风格：遵循 ESLint 推荐规范。

组件拆分：视图页面与 ECharts 可视化图表组件尽量解耦，保持单文件组件（SFC）简洁可读。

🎉 再次感谢大家的配合与贡献！高效的工程规范是项目成功的第一步！
