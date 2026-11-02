# 操作指南：运行、续跑与度量

## 前提

- Python 3.12 venv 位于 `source/.venv`（含编译器依赖）
- Node 22（mise：`~/.local/share/mise/installs/node/22.23.2/bin`）。**构建产物必须用
  Node 22 运行**——系统 Node 24 的 ABI 与已编译的 better-sqlite3 不符（ERR_DLOPEN_FAILED）
- 模型 key 在 `.env`（gitignored）：`OPENAI_API_KEY` / `OPENAI_BASE_URL` / `MODEL`
- npm 镜像与 Playwright 下载 host 参见 `../tools/run-stage.sh`

## 全流程运行

```sh
.venv/bin/python main.py input -o ../work/<目录> [--resume]
# run_all 结束后自动：npm run db:init && npm run build，并生成 deploy.sh
```

- 单阶段：`.venv/bin/python -u 08_implement_backend_tdd.py --input input --output ../work/<目录>`
- 断点续跑：`--resume` 只跳过具有可信完成记录的连续成功阶段，条件与迁移见下节。

## 可信断点续跑与旧目录迁移

首次生成使用新的输出目录；普通失败或 Ctrl+C 后，用完全相同的输入、编译器和配置加 `--resume` 继续。编译器在 `.arc/pipeline_state.json` 原子发布状态：子进程成功退出且阶段完成条件通过，才把阶段加入 completed。部分 checkpoint 保留在工作区，不作为完成证明。Stage 02 必须覆盖全部叶子需求；Stage 05 必须具有 schema 中全部表的 SQL 和初始化代码；08/10/12 必须 GREEN，空设计仅在对应集合确实为空时接受 NO_APIS/NO_UI。

状态保存输入目录文件、编号脚本/infrastructure/依赖声明的内容指纹，以及模型、端点、输出上限、源码中直接读取的 ARC 开关和 Python 版本的配置指纹。`.env` 中配置与环境覆盖一起参与计算，API key 不参与，状态不保存配置原值。编译器 IR、应用源码、生成测试和构建配置使用整体工作区哈希：后续合法阶段会修改先前页面，不能拿先前页面的旧哈希误判为外部修改。日志、依赖、数据库、构建输出和固定验收证据不作为编译完成证明。

输入、源码、配置或受保护工作区文件变化会使整条流水线的复用资格失效，程序保留旧目录并提示换新输出目录。第一版采用保守的整体失效，尚不支持按 DAG 最小范围自动重建；不会自动删除、搬移旧产物，或让新阶段读取旧条件下的 UI checkpoint。文档、提交号或 API key 单独变化不会导致失效。不要手工修改 pipeline_state.json 来接纳旧目录。

旧版本生成的目录没有完成记录，默认拒绝自动接纳。需要继续旧实验时，先保留原实验身份和证据，再显式使用 `ARC_LEGACY_PIPELINE_RESUME=1` 回退旧哨兵行为；该模式保留旧误判风险，不生成可信记录。新实验优先使用新目录。直接运行单阶段脚本仍可用于诊断，但不会生成流水线完成记录；改动已记录目录的文件后，下一次可信续跑会拒绝复用。

同一目录的流水线写入由 `.arc/pipeline.lock` 排他保护。正常失败/中断会先停止所属子进程，再封存当前局部工作并释放锁；SIGKILL、断电或状态写入中断可能留下锁及 active 状态。仅在确认原写入进程已经退出后移除遗留锁；active 尚未封存时仍需新目录，不自动相信其局部文件。独立验收和构建需等流水线退出，不支持与生成同时修改同一目录。依赖环境仍须按前述 Node 22 要求准备；指纹不替代运行环境和验收检查。

## 环境变量

| 变量                          | 默认               | 作用                                                             |
| ----------------------------- | ------------------ | ---------------------------------------------------------------- |
| `ARC_DISABLE_TIMING` | 0 | =1 停用新增 timings.jsonl，不影响 gate 或原模型审计 |
| `ARC_LEGACY_PIPELINE_RESUME` | 0 | =1 显式回退旧哨兵恢复；不接入可信记录，保留部分产物误判风险 |
| `ARC_EVENT_CONTEXT` | 1 | 非终验单事件上下文收窄；=0 回退基础瘦身，终验保持全量，FULL_CONTEXT=1 优先回退 |
| `ARC_CACHE_PREFIX` | 1 | 共享字段与文件稳定部分前置；=0 回退后期可开关排序，仍不等于教师原始代码 |
| `ARC_CACHE_PREFIX_V2` | 0 | =1 显式启用更强共享字段排序，须同时启用CACHE_PREFIX；两次完整候选均未通过，保持默认关闭 |
| `ARC_LEGACY_LABEL_LOCATORS` | 0 | =1 回退新增精确标签定位检查和提示；原 accessible-name/类型检查保留 |
| `ARC_LEGACY_READ_FAILURES` | 0 | =1 回退只读 mount 处理器故障探针和提示；原浏览器错误上报保留 |
| `ARC_LEGACY_E2E_COOKIE_NAMES` | 0 | =1 回退有效会话场景的字面量 Cookie 名称准入；测试仍可读取后端源码证据 |
| `ARC_LEGACY_E2E_SOURCE_CHECK` | 0                  | =1 回退新增的 E2E fixture 准入检查，既有 loopback URL 检查仍保留 |
| `ARC_LEGACY_REFERENCE_TESTS` | 0 | =1 不向前端设计/实现提供 input/tests 外部交互契约 |
| `ARC_LEGACY_RADIO_ASSERTIONS` | 0 | =1 回退 radio 存在性测试的选项值/checked 分离断言 |
| `ARC_LEGACY_API_SCOPE` | 0 | =1 回退 API 分解中叶子需求边界与 excess 修正提示 |
| `ARC_LEGACY_INTERACTION_RETRY` | 0 | =1 回退交互提案失败后“已接受状态”基准说明 |
| `ARC_LEGACY_UI_PREDICATES` | 0 | =1 回退完整可见性谓词提示；UI IR 与 gate 不变 |
| `ARC_LEGACY_TEST_SANITY` | 0 | =1 回退后端恒假 header 断言的冻结前准入检查 |
| `ARC_LEGACY_TEST_REVIEW` | 0 | =1 回退冻结前独立模型矛盾审阅；其他 gate 保留 |
| `ARC_FULL_FEEDBACK`           | 0                  | =1 恢复旧的字符串修复反馈与重复 output                           |
| `ARC_FULL_CONTEXT`            | 0                  | =1 恢复 Stage 12 未瘦身的创建调用上下文（A/B 对照）              |
| `ARC_UI_DESIGN_FRESH`         | 0                  | =1 强制 Stage 09 忽略 checkpoint 全新设计                        |
| `ARC_MODEL_TRANSPORT_RETRIES` | 2                  | 瞬态传输错误额外重试次数（退避 10/30/90s）                       |
| `ARC_REUSE_E2E_TESTS`         | 0                  | =1 复用既有 E2E 测试（重新校验，不重新生成）                     |
| `ARC_DISABLE_THINKING`        | 1（deepseek 自动） | 关闭 DeepSeek 思考模式                                           |

## 度量

- 逐阶段 token/耗时：聚合 `<输出目录>/model_calls.jsonl`（每条含 usage 与 elapsed_seconds）
- 历史阶段 wall time：`compiler.log` 中各 `[DONE] Completed in`，不含被中断未完成部分；新运行使用下述结构化计时。
- 正确性：`.arc/backend_tdd.json`、`.arc/ui_checks.json`、`.arc/frontend_e2e.json` 的 status 与 summary

### 流水线与检查耗时

新运行在输出目录追加 `timings.jsonl`，每个步骤有独立 span_id、trace_id、parent_id 和 start/end。耗时使用单调时钟，UTC 时间戳只用于定位。一次 main.py 启动测 entrypoint（包括 run_all、db:init、最终 build 与 deploy.sh 写出），run_all 独立记录 pipeline 与各阶段；单阶段脚本也通过 console_log 记录 stage_session。续跑使用新的 trace，不覆盖失败尝试，跳过阶段显式标为 skipped。强制终止只有 start 的记录按未知耗时保留。

按以下命令汇总，拒绝覆盖已有摘要：

```sh
.venv/bin/python scripts/summarize_timings.py ../work/<目录>/timings.jsonl --output ../work/<目录>/timing-summary.json
```

`entrypoint_seconds` 是一次入口调用的 wall time，`pipeline_seconds` 不含入口最后的数据库初始化与构建。阶段 seconds 包括子进程启动、实际工作及完成记录检查。categories 列出 SDK 模型请求、模型外层退避、typecheck、backend_tests、ui_tests、e2e_tests、dependency_install、browser_install、read_failure_probe、build/db_init 等累计耗时与成功/失败次数。SDK 请求含其内部重试与网络等待；外层显式 sleep 单列，原 model_calls.jsonl 的 call_id 与 model_request.name 对应。模型 SDK 计时只包围实际 SDK create，不包括请求预览、JSON 解析和完整日志写出。

父级耗时包含子级，不能把 pipeline、阶段和各检查相加；分类累计时间也不能直接当 wall time 或 CPU 时间，并发执行时会重叠。非零返回含预期的 TDD RED，不能直接算作阶段失败次数。categories 未覆盖的部分包括提案校验、上下文组装、序列化、部分测试准备和计时记账。不从差值自动归因于缓存或网络。固定老师验收是 main.py 结束后的独立步骤，不计入该入口的 wall time。历史日志没有这些测点，不能补造旧阶段或 gate 的实测耗时。

计时只写类别、内部标识符、状态、错误类型和耗时，不复制命令参数、请求正文、凭据或异常消息。写日志失败会发出固定警告并保留原操作结果，此时测量不完整；开关 `ARC_DISABLE_TIMING=1` 可以停用新增计时，原模型 I/O 审计仍保留。该开关与内部 trace 标识不参与可信恢复的配置指纹；timings.jsonl 和固定命名 timing-summary.json 属于测量记录，不使已完成工作区失效。归档工具会保存并逐文件校验原始计时日志。

### 已记录的计时反例

`work/timing-baseline-1101` 在 Stage 12 重复修复错误的已冻结会话 fixture 后主动中断，入口 wall time 707.57s；模型 SDK 请求 424.12s，UI/E2E 检查累计 223.27s，typecheck 39.75s。93 次已返回调用共 1,791,464 token，输入缓存命中 35.7%。这是失败/中断轨迹，不能作为成功基线或性能改进。

该后端采用空名称 Cookie，实际 Chromium 注册后可恢复会话；生成测试却把凭据同时当名称和值。冻结前静态名称检查在没有识别到命名 producer 时跳过，未覆盖此形式。默认固定验收适配器也无法自动推断空名；显式按实测空名提供结构适配器后，固定 14 条检查和构建通过，但内部 E2E 保持 FAILED，故不晋升稳定标签。证据与边界归 [计时记录](experiments/timing-validation.json)，真实处理器与浏览器重放脚本为 `scripts/replay_empty_cookie.py`；重放使用隔离内存数据库，需要该运行的 npm 依赖、Node 22 和 Chromium，不修改应用或冻结测试。

## 启动生成的网站

```sh
cd <输出目录> && PORT=3309 npm start   # 或使用生成的 deploy.sh
```

注意：`.venv`、`node_modules` 迁移或重建后，需以 Node 22 执行
`npm rebuild better-sqlite3`（npm_config_nodedir 指向 mise Node 22 的安装目录）。

## 已知坑

- 生成测试禁止写死 localhost/127.0.0.1（运行器使用随机端口；Cookie 域不匹配会造成假失败）
- Quiz/提交类平台故障（502/断连）由 OPT-C 退避重试兜底；超过重试上限的阶段用 `--resume` 续跑
- 输出目录之间不复用 `.arc` 工件；对比实验必须使用全新输出目录

维护检查、版本与实验管理见 [maintenance.md](maintenance.md)。

## 老师原版稳定验收

默认 `input/` 已恢复教师 ZIP 原字节，哈希归 `input/source.json`；旧 pending 输入迁到 `examples/registration-pending/`，必须分开运行和记录。完整生成后额外运行 `scripts/accept_teacher.py`，命令及准入标准见 [固定验收](../acceptance/README.md)。现有阶段 GREEN 和独立验收/最终构建同时通过，才可记录为稳定运行。

`ARC_LEGACY_TEST_SANITY=1` 回退后端冻结前新增的恒假 header 断言检查；原有类型、RED/GREEN 和回归仍保留。该开关不影响固定的老师独立验收。

页面存在性测试额外检查精确标签定位到实际控件；带必填星号时仅 aria-hidden 不足，控件应保留精确 aria-label。Stage 12 在创建/修复和终验时对已实现的只读 GET mount 处理器注入 503 与传输失败，报告归 `.arc/frontend_read_failures.json`。这不是完整浏览器故障验收；NOT_EXERCISED 表示条件路径未到 API，仍需固定验收检查身份与持久化。

编译器单元检查包含纯 JavaScript 故障探针，需要 PATH 中有 Node；Node 22 仍是完整生成的已验证版本。
