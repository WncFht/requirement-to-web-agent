# Agent Note: Stage 12 创建调用上下文瘦身

Status: implemented

## 实际选择

`interactions/implementation.py` 中，单事件创建调用（存在 `new_event` 且非该需求末次调用）
不再携带全量上下文：

- `files` 供给收窄为三个编译器接线文件（`ui-runtime.ts` / `ui-api.ts` / `ui-events.ts`）
  加上本需求相关页面的源文件；不再携带其他事件处理器、回归测试、backend/db 源码与
  package.json/tsconfig；
- `task.contracts` 与 `task.backend_apis` 收窄到目标事件引用的 API；
  `target_event_ids` 明确为当前一个事件；
- 每需求最后一次调用（终验，需跨文件修复能力）与 E2E 测试生成调用保留完整上下文；
- `ARC_FULL_CONTEXT=1` 整体回退到未瘦身行为。

## 理由

baseline（2,141,102 token，34/34 GREEN）中 Stage 12 的 21 次调用每次重发 207–222K 字符：
`files`（整个前端工作区，110K）+ `task`（全部需求的 contracts/apis，81K）。而每次调用只实现
一个事件，其语义必要性由需求的 `\ref[requirement]` 作用域声明限定——其他事件的行为已由
`task.events` 描述承载，源码并非必需。同时文件内容随实现进度变化，使 DeepSeek 前缀缓存
命中率在 20K–60K token 间剧烈波动：把易变内容后置、减少供给量本身就是缓存修复。

## 备选

- 批量合并创建调用以摊薄固定开销：被否——单目标调用 gate 定位无歧义，且与
  "creation gate 逐事件验收"的设计耦合；留作后续 A/B（同页面独立事件可 3–5 个一批）。
- 维持全量上下文仅靠缓存：被否——文件每轮变化使前缀失效，缓存救不了首轮。

## 代价与验证

- 跨文件修复依赖每需求末次的完整上下文调用兜底；若创建 gate 的类型检查错误落在
  未供给文件中，模型只能报告不能修复，极端情况下 18 轮耗尽中止阶段（可用 --resume 续跑）。
- 验证（2026-11-01 运行 work/opt-1101）：全流程 GREEN（后端 14/14、UI 9/9、E2E 11/11），
  Stage 12 输入 1,241,920 → 579,516 token（−53.3%，调用数不变），总 token −56.6%。
  Stage 12 每次调用输入均值（含测试生成） 59,139 → 27,596。
