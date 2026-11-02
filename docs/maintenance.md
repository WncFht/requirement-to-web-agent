# 开发、共享与维护

本页管理源码仓库、分支、格式化与本地证据。运行接口见[操作指南](development.md)，设计见[架构参考](architecture.md)，实际观测见[实验报告](experiments/2026-11-02-单循环编码智能体对照验证.md)。

## 维护规则来源

agent-maintenance 提供文档、文字和决策记录三个技能，规则与固定上游版本位于 `.agents/maintenance-source.json`。它是维护方法与检查工具，不是智能体运行框架。当前项目拥有 hook、CI、格式配置和文档分工；更新上游规则时审阅差异，不覆盖项目适配。

当前架构和配置写入 `architecture.md`、`development.md`，研究证据归 `experiments/`，长期理由归 `.agents/notes/`。完成的实施细节不在多个入口重复维护。历史审查材料移到 `docs/history/`；仍然影响权限、会话或兼容性的决策继续保留。

## 仓库共享与分支

GitHub 上建立独立的 `lab6-requirement-agent` 仓库，上传本仓库完整 Git 历史。名称只是建议，目前没有创建远端或发布。外层 `JI-course` 保存课程笔记与交付记录，忽略本机 `source/`，不能代替这个源码仓库；agent-maintenance 的上游仓库也不是本项目的提交位置。课程任务材料与同学协作放在队伍私有仓库更合适。

| 身份                                | 维护方式                                                          |
| ----------------------------------- | ----------------------------------------------------------------- |
| `main`                              | 团队唯一集成分支，包含两个引擎，默认 legacy；常规离线检查必须通过 |
| `feat/*`、`fix/*`                   | 从 main 建短期分支，审阅后合回并删除；不另设长期 develop          |
| 历史提交与标签                      | 教师基线、已有验收检查点和受测源码保留，不因清理而移动旧标签      |
| `coding-agent-candidate-2026-11-02` | 指向 `65220fd` 的候选身份；不是稳定性或平台成绩认证               |
| `pre-sharing-2026-11-02`            | 整理前开发分支的备份，保护未发布历史                              |

本机常驻工作区为课程侧 `source/`，检出 main；需要同时开发时才新建一个工作区，例如：

```sh
git worktree add -b feat/my-change ../work/feature-my-change main
# 完成修改、离线检查与审阅后，在 main 工作区合入。
git merge --ff-only feat/my-change
git worktree remove ../work/feature-my-change
git branch -d feat/my-change
```

上例的合入命令在 main 工作区执行；分支已经分叉时通过 PR 或常规 merge 处理，不能用强制覆盖消除别人的提交。关闭的实验 checkout 已从工作目录移走，原提交、输入清单和备份均保留。需要复核时按原协议路径与 SHA 重建 detached worktree，复核结束后移除；原实验目录不覆盖。`work/maintenance-2026-11-02/` 的本地清单记录旧 checkout、备份和释放的依赖空间。

首次 GitHub 发布需用户另行授权。创建远端后，从本机 `source/` 设置地址并只推 main 与需要共享的标签，不执行 `git push --all`，避免发布已结束的临时分支。队友 clone 后按根 README 安装并运行离线检查，再用自己的功能分支改代码。当前禁止模型 API 的约定同样适用于后续代理，不因共享而撤销。

## 格式化与本地检查

Python 版本和依赖由 `pyproject.toml`、`requirements-dev.txt` 声明；文档格式工具版本唯一来源为 `package.json` 与 `package-lock.json`。Python 保留教师代码的 unittest 风格，仅检查语法、未定义名称等既有安全项，不批量引入新的业务 lint 规则。

```sh
uv pip install --python .venv/bin/python -r requirements-dev.txt
npm ci --ignore-scripts --no-audit --no-fund
pre-commit install
ruff format .
npm run format
npm run lint:md
.venv/bin/python scripts/run_checks.py --config scripts/checks.json --mode ci
npm run format:check
```

提交时先修 Markdown 结构，再由 git-format-staged 格式化暂存的 Python、Markdown、JSON 与 YAML；未暂存改动不被整文件覆盖。Markdown 结构修正若改变文件，重新暂存再提交。随后验证暂存快照中的文档、Notes、编译器测试和凭据模式。CI 使用同一锁定工具与检查入口，只有离线任务，不配置模型 Key。

教师输入、扩展示例、固定验收、应用模板、vendor 和冻结归档不进入自动格式化，避免改变输入、断言或模板哈希。文档工具还排除上游维护技能和历史教师教程，保留原始来源字节。`scripts/doc-policy.json` 只约束文档篇幅，不证明内容正确；超软预算先核对归属，不能自动删字。

## 证据保留与清理

本机实验均位于课程侧 `work/`，不上传 GitHub。保留协议、生成源码、冻结测试、模型日志、检查报告、截图、结果和封存哈希，再删除可重建的 `node_modules` 与 Python 缓存。保留一份已登记哈希的依赖快照；每次实验的副本不必长期占用磁盘。清理不改失败结果，也不把缺失 usage 当免费调用。

新候选原始应用清单含构建输出哈希，因此保留这些 dist 文件。删除依赖前对全部非依赖文件做前后哈希核对，清单写入本机维护目录。移除旧 worktree 前确认干净、创建提交引用和 Git bundle，保存输入清单；还原时依赖应由保留的快照重建。

源码 bundle 用于离线恢复，平台 ZIP 用于上传智能体，两者职责不同。`scripts/export_source.py --output-dir <新归档目录>` 只导出已提交历史，恢复后核对 SHA、干净工作区及 `git fsck --full`。旧课程 `artifacts/`、报告和 Slides 是历史交付物，不随本次源码整理伪装成最新实验结论。

## 分享边界

源码仓库包含运行源码、模板、提示词、固定测试、依赖声明、CI、维护规则和精选实验摘要。`.env`、真实 Key、依赖、数据库、原始模型请求响应、大型运行目录、ZIP 和 Git bundle 留在本机；需要共享的交付包通过受控附件提供。源码仓库没有部署、自动生成或后台实验服务，用户没有重新授权前禁止任何真实模型 API 请求。
