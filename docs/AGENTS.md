# docs/AGENTS.md — 文档所有权地图

| 载体               | 位置                                                              | 更新时机                                                        |
| ------------------ | ----------------------------------------------------------------- | --------------------------------------------------------------- |
| 用途与最短使用路径 | 根 `README.md`（当前入口）+ `AGENTS.md`（代理规则）               | 入口或前提变化时                                                |
| 架构参考           | `docs/architecture.md`                                            | 阶段、工件链或模块职责变化时                                    |
| 操作指南           | `docs/development.md`                                             | 运行方式、环境变量、排错路径变化时                              |
| 实验报告           | `docs/experiments/*.md`                                           | 同条件新证据出现时更新所属报告                                  |
| Agent Notes        | `.agents/notes/{proposed,implemented,rejected,archived}/{class}/` | 长期取舍产生或反转时（maintain-decision-notes）                 |
| 开发历史           | `docs/history.md`                                                 | 已实施里程碑或验证结论变化时                                    |
| 维护与共享指南     | `docs/maintenance.md`                                             | 检查、分支、worktree 与共享约定变化时                           |
| 上游 diff          | `upstream.patch`                                                  | 相对 teacher-baseline 的内容变化合入后重新生成                  |
| 运行产物           | `../work/<目录>/`（gitignored）                                   | 每次 run；`.arc/*.json` 工件链与 `model_calls.jsonl` 是分析原料 |

规则：

- 一次性运行日志与终端面板不属于本目录；其结论摘录进实验报告并注明运行目录。
- 课程侧记录（10-29 打包上传、验收流程）保留在 JI 课程仓库 `notes/4810/lab6/`，此处不维护副本。
- baseline 原始产物（队友 Windows 运行）位于 JI 仓库 `notes/4810/lab6/artifacts/teammate-baseline/`
  （原始 jsonl 不入库，保留 gz）；实验报告以路径引用之。
- 篇幅预算见 `scripts/doc-policy.json`；超限先拆归属，不做摘要压缩。
