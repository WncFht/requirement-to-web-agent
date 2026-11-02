# AGENTS.md — CS4810J Lab 6 需求编译器（改良版）

把 `requirements.yaml`（需求 + 参考截图）编译为可运行 React/Express/SQLite 网站的规格编译器。
原始基线来自 Canvas Lab 6 zip（git tag `teacher-baseline`）；当前 HEAD 在其上叠加了
鲁棒性修正（2026-10-29）与性能优化（2026-11-01），版本以本仓库 Git 历史为准；课程侧 `../upstream.patch` 是导出的源码补丁。

## 硬性规则

1. **验收口径不可削弱**：任何修改不得删除或放松 gate —— typecheck、后端契约回归、
   UI 存在性测试、Playwright E2E、生产构建。性能优化只发生在上下文组装、调度与传输层。
2. **教师代码语义冻结**：00–12 号脚本的语义是 baseline 口径。语义性修改必须落一份
   Agent Note（`.agents/notes/`），并提供环境变量回退开关（如 `ARC_FULL_CONTEXT=1`）。
3. **凭据隔离**：模型 key 只存 `.env`（gitignored）；不得进入源码、日志、上传包或文档。
4. **输出目录隔离**：编译产物只写 `--output-dir` 指定目录；不同实验使用不同目录，禁止覆盖。
5. **模型 API 已停用**：用户于 2026-11-02 明确要求停止比较并禁止后续 API 调用，撤销此前付费实验授权。未经用户重新明确授权，不得调用真实模型 API、启动或续跑生成实验；仅可进行本地整理、静态检查和不调用模型的离线测试。

## 工作区与检查

团队在独立源码仓库的 main 集成两套引擎，默认 legacy；功能分支与 worktree 按需创建，完成后移除。外层 JI 仓库只保存课程材料。共享、清理与格式规则见 `docs/maintenance.md`，禁止未经授权启动文档中的模型生成命令。

```sh
.venv/bin/python scripts/run_checks.py --config scripts/checks.json --mode ci
npm run format:check
npm run lint:md
```

Python 用 Ruff，文档与配置用锁定的 Prettier/Markdownlint；提交时通过 git-format-staged 格式化暂存内容。教师输入、固定验收、应用模板、vendor 和冻结归档排除，保留字节身份。

## 文档与决策

- 所有权地图：`docs/AGENTS.md`；读者导航：`docs/README.md`
- 实验报告：`docs/experiments/`；长期决策：`.agents/notes/`（遵循 maintain-decision-notes）
- 上游 diff：`../upstream.patch`（相对 teacher-baseline 的源码导出；生成方式见维护指南）

维护规则与技能来自 agent-maintenance 工具包（引入于 2026-11-01）；规则本体见 `.agents/`。
