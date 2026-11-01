# Agent Note: 流水线断点续跑与传输退避重试

Status: implemented

## 实际选择

- `run_all.py` / `main.py` 新增 `--resume`：按哨兵产物跳过已完成阶段
  （00:package.json；01:requirements+visual_analysis；02:db_schema；03:db_obligations；
  05:backend/src/db/tables 内至少一个 .sql；06/07/10/11:对应 .arc json；08/12:对应 json
  且 status GREEN）。09 永远重入——其内部按需求 checkpoint 跳过已完成设计。
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

- 哨兵是文件存在性（05 特判 tables 目录须含 .sql——脚手架自带空目录，初版哨兵曾误判）；
  哨兵通过 ≠ 内容正确，语义正确性仍由各阶段自身的 gate 与后续阶段兜底。
- 验证：2026-11-01 运行实际中断续跑三次完成全流程；Stage 05 单独重跑后 06/07 按哨兵跳过；
  502 由重试吸收（日志可见 retrying 记录）。50/50 上游测试通过。
