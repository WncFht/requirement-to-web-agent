# 编译器优化实验（2026-11-01）

> 本报告自 2026-11-01 起归属本仓库 docs/experiments/；同日从 JI 课程仓库迁入。
> 输入说明：编译对象是 `input/requirements.yaml`（198 行 / 9.3KB / 8 场景 / 9 步，含会话恢复与
> 未知会话两个场景）。注意不要与 plusplus 另一变体 `example/smoke`（131 行 / 7 场景 / 21 步 /
> 59 处 role=）混淆——两份是同一 smoke 的不同方言，本报告所有数字对应前者。
> baseline 原始产物在 JI 仓库 `notes/4810/lab6/baseline-teammate/`（gitignored，jsonl 保留 gz）。

在队友 Windows baseline（`baseline-teammate/`，34/34 全绿、82 分钟、2,141,102 token）的基础上，
对本仓库 `source/` 的需求编译器做了一轮「度量 → 根因 → 优化 → 复测」。全部修改记录于
课程侧 `upstream.patch`，实验报告与 slides 见 课程侧 `report/main.pdf` 与 课程侧 `slides/main.pdf`。

## 根因（来自 331 条调用事件的逐条分析）

- Stage 12 的 21 次调用每次重发 207–222K 字符提示词，其中
  `files`（整个前端工作区）110K、`task`（全需求 contracts/apis）81K、`feedback`（含 ANSI）10K；
- `target_event_ids` 每次只实现 1 个事件，却携带全部需求的契约与 API 定义；
- 文件随实现进度变化导致 DeepSeek 前缀缓存命中率剧烈波动（60K↔20K token）。

## 五项修改（按各项列出的开关回退）

| # | 修改 | 文件 |
| --- | --- | --- |
| A | Stage 12 非末次创建调用上下文瘦身：files 收窄到 3 个接线文件 + 相关页面源码，contracts/apis 收窄到目标事件；终验调用与测试生成保留完整上下文（`ARC_FULL_CONTEXT=1` 回退） | `infrastructure/stages/frontend/interactions/implementation.py` |
| B | agent 反馈去噪：剥 ANSI、截断超长字符串 | `infrastructure/shared/agent/loop.py`（`compact_feedback`） |
| C | 瞬态传输错误退避重试（连接/超时/5xx/限流，10/30/90s，`ARC_MODEL_TRANSPORT_RETRIES`） | `infrastructure/shared/models/text.py` |
| D | Stage 09 每接受一个叶子需求即 checkpoint（`ui_design_progress.json`）；重跑跳过已完成需求；3 次提案耗尽改为记账后继续，最后统一报错（`ARC_UI_DESIGN_FRESH=1` 强制全新） | `infrastructure/stages/frontend/ui/synthesis.py` |
| E | `run_all.py --resume`（main.py 透传）：按哨兵产物跳过已完成阶段，08/12 额外要求 status GREEN | `run_all.py`、`main.py` |

上游 50/50 单元测试通过。开发中发现并修正一处 resume 哨兵误判：
`backend/src/db/tables` 在脚手架中即存在（空目录），改判为「目录内至少一个 .sql」。

## 结果（同输入、同模型 deepseek-flash；baseline 为跨机器参考）

| 指标 | baseline | 优化后 | 变化 |
| --- | ---: | ---: | ---: |
| 总 token | 2,141,102 | 928,299 | **−56.6%** |
| 输入 / 输出 | 1,576,030 / 565,072 | 859,534 / 68,765 | −45.5% / −87.8% |
| Stage 12 token | 1,468,588 | 590,804 | −59.8% |
| 单次创建调用输入（均值） | 59,139 | 27,596 | −53.3% |
| 阶段累计耗时 | 4,940.2 s | 489.8 s | −90.1%（跨机器口径） |
| 正确性 | 34/34 | 后端 14/14、UI 9/9、E2E 11/11 | 全绿 |

输出目录 `work/opt-1101`（git 忽略），逐阶段聚合与 `model_calls.jsonl` 完整保留。
额外做了独立 API 冒烟（构建产物起服务器，绕开 Playwright）：
register 201 / session 200 / 重复注册 409 / login 201，全部符合契约义务。

## 运行事故与处置记录

- `--resume` 首版把空 `tables/` 目录误判为 Stage 05 完成，Stage 08 报
  「Missing implemented SQL for Account」——修正哨兵后由 05 续跑，未重做 01–04（OPT-E 首战生效）。
- Stage 08 期间 arc-bench 间歇 502，OPT-C 重试日志可见「retrying 1/1 in 10s」；
  将 `ARC_MODEL_TRANSPORT_RETRIES` 提到 4 后不再中断。
- `npm install` 因 nodejs.org/GitHub 下载被断连失败（better-sqlite3 原生编译）：
  复制 `work/demo/node_modules`（155MB，含已编译二进制）并以 mise node 22 重编译后解决。
  注意系统 node 是 v24（ABI 137），必须用 mise node 22（ABI 127）运行构建产物。

## 交付物

- 报告：课程侧 `report/main.pdf`（7 页，含背景、根因、五项优化、结果、复现指南）
- Slides：课程侧 `slides/main.pdf`（15 帧 Beamer）
- 队友 baseline 原始产物：`baseline-teammate/`（原始 32MB jsonl 不入库，保留 gz 压缩版）

## 格式化与版本化（2026-11-01 补充）

- `source/` 已建为独立 git 仓库（JI 仓库忽略该目录）：tag `teacher-baseline` = 原始 zip 原样导入，
  随后两笔提交分别为「10-29 修正 + 11-01 优化」与「ruff format」。每项优化的 diff 可
  `git diff teacher-baseline main -- <路径>` 随时取用。
- 全部 88 个 Python 文件经 `ruff format`（67 个文件重排，LF 规范化），无语义变化：
  py_compile 全过、上游 50/50 测试通过。
- `upstream.patch` 改为由 `git diff teacher-baseline main` 生成（740KB，含格式化噪音；
  语义审阅用 `git diff -w teacher-baseline main`）。
- 注意：运行构建产物必须使用 mise node 22（系统 node 24 的 ABI 与已编译 better-sqlite3 不符）。

## 可比性与 OPT-F 负结果

以上 56.6% 是组合改动的单次总 token 变化，不能全部归因于上下文瘦身。baseline 的 reasoning token 为 491,658，首轮优化为 11,151；思考模式、机器和模型生成轨迹均不同。模型请求累计秒数、各阶段 wall time 与包含安装及人工续跑的端到端时间是不同单位，不能互换。

逐阶段原始聚合见 [call-metrics.json](call-metrics.json)，用 `scripts/summarize_calls.py` 从 SDK `response` 事件生成，HTTP 镜像事件不重复计费。哈希对应记录中路径的原始文件；压缩或迁移后应重新核验。缺少 usage 的 SDK 响应会阻断统计，不静默当作零成本。该统计不估算供应商未返回 usage 的失败请求费用。

`34fc0a8` 的 OPT-F 完整尝试位于课程侧 `work/optf-1101`，Stage 12 REQ-2 在 18 轮修复后失败，未执行生产构建。总 token 2,089,717；Stage 12 为 1,610,093。前置后端 9/9、UI 9/9 GREEN 不代表注册与会话 API 的组合正确。

| 输入缓存命中率 | baseline | 首轮优化 | OPT-F（失败运行） |
| --- | ---: | ---: | ---: |
| 全流程 | 51.6% | 36.3% | 36.5% |
| Stage 12 | 59.2% | 44.2% | 35.9% |

原缓存提案把全流程 36.3% 写成 Stage 12，现已纠正。OPT-F 没有达到 Stage 12 至少 50% 的原验收要求；失败、重试次数和不同生成轨迹也使单轮数据无法隔离键序的因果效果，仍保留 proposed。

失败工件的最小组合复现：注册接口生成的 `sessionCookie` 与存入 `Session.credential` 的 `credential` 来自两次随机生成；携带返回 Cookie 查询会话得到 `authenticated: false`。复现脚本为 [optf-session-probe.mjs](optf-session-probe.mjs)，结果为 [optf-session-probe.json](optf-session-probe.json)。在原失败产物根目录，用 Node 22 执行：

```sh
node --import tsx ../../source/docs/experiments/optf-session-probe.mjs .
```

脚本使用内存数据库，不修改失败工件或持久化数据库。Stage 12 的可写范围只有前端，因而无法修正该后端错误；不应将这一失败直接归因于提示词键序。后续跨层修复须重新执行冻结的后端测试，并另做可回退设计。

## OPT-G：结构化修复反馈

保留 gate 的结构化报告，避免先转成 Python 字典字符串、再经过 JSON 转义；只有当 `output` 解码后与其他全部字段完全相等时才移除这份重复副本。断言、失败数量与位置仍传给模型，原始审计日志保持完整。`ARC_FULL_FEEDBACK=1` 恢复旧的模型反馈格式。

从 OPT-F 日志提取的 17 份可完整解析失败报告，序列化反馈从 48,006 字符降至 18,821 字符，减少 60.8%；见 [feedback-replay.json](feedback-replay.json)。这是历史反馈的字符重放测量，不是模型 token、端到端耗时或成功率的测量。全流程验证结果另按实际运行状态更新。

初始反馈另有独立缺陷：调用者传入的报告字典被循环按键展开，首轮仅收到 `typecheck/e2e/ui` 等字段名。已补齐完整字典传输与回归断言。首次 OPT-G 尝试在 Stage 08 被主动中断，保留在 `work/optg-1101`；修改后的完整验证使用新目录，不复用该次产物。
