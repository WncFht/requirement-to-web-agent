# docs/README.md — 按读者问题导航

- 「单循环候选实际通过了什么，成本与旧版如何比较？」→ [单循环编码智能体对照验证](experiments/2026-11-02-单循环编码智能体对照验证.md)
- 「怎样运行单循环候选、查看失败、打包和回退？」→ [操作指南](development.md#单循环候选的运行与审计)
- 「怎样复用旧能力、控制版本和推进验收？」→ [简洁编码智能体实施计划](2026-11-02-简洁编码智能体实施计划.md)（核心已实现，付费实验已停止）
- 「新候选怎样先做零付费验证，再与旧流程比较？」→ [编码智能体候选验证计划](experiments/2026-11-02-编码智能体候选验证计划.md)（已停止，原协议保留）
- 历史审查背景 → [单循环实施前的审查材料](history/2026-11-02-全流程与优化独立审查上下文.md)
- 「这套编译器整体怎么工作、每步吃进吐出什么？」→ [architecture.md](architecture.md)
- 「整体应该优先优化哪里、有哪些恢复和校验缺口？」→ [整体优化审阅](2026-11-01-整体优化审阅.md)
- 「怎么跑、断了怎么续、怎么量 token 和各阶段耗时？」→ [development.md](development.md)
- 「baseline 是多少、优化改了什么、效果如何？」→ [experiments/2026-11-01-baseline-optimization.md](experiments/2026-11-01-baseline-optimization.md)
- 「固定次数复测、串行速度消融和缓存 V2 的最终结果？」→ [串行消融与缓存验证](experiments/2026-11-02-串行消融与缓存验证.md)
- 「为什么这样设计而不是那样？」→ `.agents/notes/`（决策记录，按主题归档）
- 教师源码差异 → `git diff teacher-baseline main`；历史逐阶段用法见[教师教程](history/teacher-tutorial.md)

维护规则入口：根 [AGENTS.md](../AGENTS.md)、[docs/AGENTS.md](AGENTS.md)；
维护技能与参考见 `.agents/skills/` 与 `.agents/references/`。

- 开发里程碑与版本 → [history.md](history.md)
- GitHub 共享、分支、worktree、格式与清理 → [maintenance.md](maintenance.md)

- 报告与分享材料 → 课程侧 `../report/`、`../slides/` 与 `../README.md`；构建见 [维护指南](maintenance.md)

- 老师原版的固定验收 → [acceptance/README.md](../acceptance/README.md)
