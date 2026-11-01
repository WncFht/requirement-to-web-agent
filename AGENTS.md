# AGENTS.md — CS4810J Lab 6 需求编译器（改良版）

把 `requirements.yaml`（需求 + 参考截图）编译为可运行 React/Express/SQLite 网站的规格编译器。
原始基线来自 Canvas Lab 6 zip（git tag `teacher-baseline`）；当前 HEAD 在其上叠加了
鲁棒性修正（2026-10-29）与性能优化（2026-11-01），全部改动见 `upstream.patch`。

## 硬性规则

1. **验收口径不可削弱**：任何修改不得删除或放松 gate —— typecheck、后端契约回归、
   UI 存在性测试、Playwright E2E、生产构建。性能优化只发生在上下文组装、调度与传输层。
2. **教师代码语义冻结**：00–12 号脚本的语义是 baseline 口径。语义性修改必须落一份
   Agent Note（`.agents/notes/`），并提供环境变量回退开关（如 `ARC_FULL_CONTEXT=1`）。
3. **凭据隔离**：模型 key 只存 `.env`（gitignored）；不得进入源码、日志、上传包或文档。
4. **输出目录隔离**：编译产物只写 `--output-dir` 指定目录；不同实验使用不同目录，禁止覆盖。

## 常用入口

```sh
.venv/bin/python -m unittest discover -s tests -q        # 编译器自带 50 项测试
.venv/bin/python main.py input -o ../work/<目录> --resume # 全流程（可断点续跑）
.venv/bin/python -u <NN 脚本> --input input --output ../work/<目录>  # 单阶段
```

运行前提与逐阶段行为见 `docs/development.md`；组件与数据流见 `docs/architecture.md`。

## 文档与决策

- 所有权地图：`docs/AGENTS.md`；读者导航：`docs/README.md`
- 实验报告：`docs/experiments/`；长期决策：`.agents/notes/`（遵循 maintain-decision-notes）
- 上游 diff：`upstream.patch`（相对 teacher-baseline，含 ruff 格式化；语义审阅加 `-w`）

维护规则与技能来自 agent-maintenance 工具包（引入于 2026-11-01）；规则本体见 `.agents/`。
