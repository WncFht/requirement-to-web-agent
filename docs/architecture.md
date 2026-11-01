# 架构参考：需求编译器（Lab 6 改良版）

本文回答「编译器整体怎么工作、每个阶段吃进吐出什么、哪些是模型哪些是确定性代码」。
运行方式见 [development.md](development.md)；逐阶段 token 度量见
[experiments/2026-11-01-baseline-optimization.md](experiments/2026-11-01-baseline-optimization.md)。

## 总体形态

规格编译器：`requirements.yaml` + 参考截图 → React/Express/SQLite 网站。
13 个阶段脚本（`00`–`12`，`run_all.py` 顺序执行）共享输出目录下的 `.arc/*.json` 工件链；
每个阶段的输出是下一阶段的输入，链路逐层可追溯。

## 阶段与工件链

| 阶段 | 工作 | 主要产物（`.arc/`） | 模型 |
| --- | --- | --- | --- |
| 00 | React/Express/SQLite npm workspaces 骨架 | project/report.json | 否 |
| 01 | 需求树解析 + 视觉分析参考截图 | requirements.json、visual_analysis.json | 是（视觉） |
| 02 | 数据库实体/字段/关系 | db_schema.json | 是 |
| 03–04 | 字段级读写义务推断 + 守恒校验 | db_obligations.json | 03 是 |
| 05 | 建表 SQL 与初始化代码 | backend/src/db/tables/*.sql | 是 |
| 06–07 | 后端 API 拆分 + P/Q 契约 | backend_apis.json、backend_contracts.json | 是 |
| 08 | 契约冻结为测试（RED）→ 实现（GREEN） | backend_tdd.json | 是 |
| 09 | 页面/元素/绑定/显示状态设计（增量 + RAG） | ui_design.json | 是 |
| 10 | 存在性测试 + 页面实现 | ui_checks.json | 是 |
| 11 | 触发器/事件/事件契约 | ui_interactions.json | 是 |
| 12 | 逐需求 E2E 冻结 → 逐事件实现 → 回归 | frontend_e2e.json | 是 |

## 关键机制

- **文件编辑协议**（`infrastructure/shared/agent/`）：模型返回
  `{"edits":[{path,content}]}` 整文件批编辑；`FileWorkspace` 校验路径合法性、
  原子写入失败回滚、每次请求重新供给文件内容。`run_file_agent` 是有界修复循环：
  生成 → gate → 失败反馈 → 重试。
- **义务守恒**：叶子需求与分配 API、交互调用的字段级 R/W 集合保持一致；
  04 号脚本检查义务记录和字段引用，06/11 比较分配集合。这不证明自然语言义务推断或业务实现本身正确。
- **契约冻结测试**：08/12 先把 P/Q 与场景冻结为可执行测试（RED），实现以
  通过冻结测试为完成定义——模型没有"我觉得做完了"的话语权。
- **确定性接线**：工件校验、运行时接线和测试执行由代码完成；数据库、API、页面与事件提案依赖模型。
- **失败语义**：单阶段失败由 `guarded` 转为警告继续（部分阶段）或中止流水线；
  `run_all.py --resume` 按可信成功前缀恢复；完成记录与局部 checkpoint 分离，08/10/12 检查成功状态。输入/编译器/配置指纹与整体工作区哈希不符时拒绝复用，要求新目录，尚无最小 DAG 增量重建。详见 [恢复规则](development.md#可信断点续跑与旧目录迁移)。

## 性能优化落点（详见实验报告）

| 优化 | 位置 | 触发/回退 |
| --- | --- | --- |
| Stage 12 创建调用上下文瘦身 | `interactions/implementation.py` | `ARC_FULL_CONTEXT=1` 回退 |
| 进一步单事件上下文试验 | `interactions/creation_context.py` | `ARC_EVENT_CONTEXT=1` 显式启用，默认 0；完整候选未通过外部验收 |
| agent 反馈去噪（ANSI/截断） | `shared/agent/loop.py` | 常开 |
| 瞬态传输退避重试 | `shared/models/text.py` | `ARC_MODEL_TRANSPORT_RETRIES` |
| Stage 09 逐需求设计 checkpoint | `frontend/ui/synthesis.py` | `ARC_UI_DESIGN_FRESH=1` 全新 |
| 流水线断点续跑 | `run_all.py`、`utils/pipeline_state.py`、`main.py` | `--resume`；`ARC_LEGACY_PIPELINE_RESUME=1` 回退 |

## 仓库布局

- `00`–`12_*.py`：阶段脚本（教师内容，语义冻结）
- `infrastructure/`：编译器库——`shared/agent`（编辑协议与循环）、`shared/models`
  （text/vision 客户端）、`stages/*`（各 pass）、`shared/rag`（页面检索）、`utils`、`project/templates`
- `input/`：按教师 ZIP 原字节冻结的需求、截图与原始 E2E；pending 扩展在 `examples/registration-pending/`
- `tests/`：编译器单元测试（含文件编辑、流程与反馈回归）
- `main.py`：平台入口（run_all → db:init → build → deploy.sh）

当前成本分布、恢复边界和优化顺序见 [整体优化审阅](2026-11-01-整体优化审阅.md)。JSON 形状/义务校验、行为测试与固定外部验收分别承担不同职责，不把任一 IR 检查称为完整业务证明。
