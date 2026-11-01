# Agent Note: 缓存友好的提示词键序

Status: proposed

## 问题

优化后运行（work/opt-1101）的全流程输入 token 缓存命中率为 36.3%（312K/859K），低于
baseline 的 51.6%；Stage 12 对应为 44.2%，不能混用两个分母。原因：`generate_json` 的 payload 键序为 `task → files → feedback`，
而 `task` 里 `target_event_ids`、目标事件 contracts、`backend_apis` 这些逐调用变化的内容
排在前面；`files.state()` 按路径字母序供给，新创建的事件文件会插入到已有文件中间。
DeepSeek 前缀缓存按序列化字符串前缀命中——易变内容居中使后续全部前缀失效。

## 拟议选择

不改任何语义，只调序列化键序，稳定者前置：

1. 顶层 payload：`files`（最稳定：接线文件 + 页面源码）→ `task`（半稳定）→ `feedback`（最易变）；
2. `task` 内部：`page_subtrees` / `triggers` / `events` / `requirement`（需求内稳定）→
   `implementation_paths` / `page_paths` → `backend_apis` / `contracts`（逐调用变化）→
   `target_event_ids` / `new_file`（最易变，task_state 末尾追加已满足）；
3. `FileWorkspace` 供给顺序：初始文件按路径排序在前，运行中新创建的文件追加在末尾
   （避免字母序插入破坏前缀）。

## 可观察的验收与风险

- 验收：同输入全流程重跑，Stage 12 的 `prompt_cache_hit_tokens` 占输入比例从 44.2%
  提升到 ≥50%；总 token 数不显著上升（键序不影响内容量）。
- 风险：无语义风险（JSON 键序对模型语义无影响）；唯一代价是与旧运行的
  model_calls.jsonl 不再字节可比——缓存命中率对比须同代码版本。

Status 保持 proposed 直到完成一次全流程重跑并核对缓存命中数据。

## 已有实现与验证缺口

`34fc0a8` 已实现上述调序。`work/optf-1101` 的完整尝试在 Stage 12 REQ-2 耗尽 18 轮修复；该阶段缓存命中率为 35.9%，原验收未满足，Status 保持 proposed。注册 Cookie 与数据库会话凭据不一致导致前端修复无法完成，单次失败不能隔离键序的因果效果。完整负结果与复现见 [实验报告](../../../../docs/experiments/2026-11-01-baseline-optimization.md)。
