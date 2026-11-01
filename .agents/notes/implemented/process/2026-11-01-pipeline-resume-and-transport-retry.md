# Agent Note: 流水线断点续跑与传输退避重试

Status: implemented

## 实际选择

- 原哨兵恢复由[可信完成记录](../bug-fix/2026-11-01-pipeline-completion-provenance.md)部分取代，默认只复用输入/编译器/配置及工作区指纹一致的成功前缀。旧哨兵仅保留为 `ARC_LEGACY_PIPELINE_RESUME=1` 的兼容回退。传输重试与同条件 Stage 09 局部 checkpoint 继续适用。
- `shared/models/text.py` 的 `generate_json` 对 APIConnectionError / APITimeoutError /
  InternalServerError / RateLimitError 做 10/30/90s 退避重试，次数由
  `ARC_MODEL_TRANSPORT_RETRIES` 控制（默认 2 次额外重试）；非瞬态 4xx 立即抛出。
- Stage 09（`frontend/ui/synthesis.py`）逐叶子需求 checkpoint：每接受一个设计落盘
  `ui_design.json` + `ui_design_progress.json`；重跑跳过已完成需求；3 次提案耗尽
  改为记账后继续，最后统一报错。`ARC_UI_DESIGN_FRESH=1` 强制全新。

## 理由

baseline 运行中一次 APIConnectionError（Stage 05）和五次结构拒绝（Stage 09）分别导致
整阶段重跑，合计浪费约 466s 且 REQ-1/2 已完成的 UI 设计全部作废。一次网络抖动不应
把"部分完成的合法工作"一并丢弃。

## 备选

- 只提高 SDK max_retries：被否——同时间窗内的连续 502 需要更长退避；
- Stage 09 失败即中止保持简单：被否——代价是丢弃同阶段已完成设计。

## 代价与验证

- 旧哨兵检查文件存在性，无法区分局部与完整成功；当前默认机制及迁移代价归取代记录。Stage 09 局部进度不等于整个阶段完成，语义正确性仍需各阶段 gate 和独立验收。
- 验证：2026-11-01 运行实际中断续跑三次完成全流程；Stage 05 单独重跑后 06/07 按哨兵跳过；
  502 由重试吸收（日志可见 retrying 记录）。50/50 上游测试通过。
