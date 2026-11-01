# 编译器优化实验（2026-11-01）

> 本报告自 2026-11-01 起归属本仓库 docs/experiments/；同日从 JI 课程仓库迁入。
> 输入说明：编译对象是 `input/requirements.yaml`（198 行 / 9.3KB / 8 场景 / 9 步，含会话恢复与
> 未知会话两个场景）。注意不要与 plusplus 另一变体 `example/smoke`（131 行 / 7 场景 / 21 步 /
> 59 处 role=）混淆——两份是同一 smoke 的不同方言，本报告所有数字对应前者。
> baseline 原始产物在 JI 仓库 `notes/4810/lab6/artifacts/teammate-baseline/`（gitignored，jsonl 保留 gz）。

在队友 Windows baseline（`artifacts/teammate-baseline/`，34/34 全绿、约 82 分钟（含失败尝试）、2,141,102 token）的基础上，
对本仓库 `source/` 的需求编译器做了一轮「度量 → 根因 → 优化 → 复测」。全部修改记录于
课程侧 `upstream.patch`，实验报告与 slides 见 课程侧 `report/main.pdf` 与 课程侧 `slides/main.pdf`。

## 根因（来自 331 条调用事件的逐条分析）

- Stage 12 的 21 次调用每次重发 207–222K 字符提示词，其中
  `files`（整个前端工作区）110K、`task`（全需求 contracts/apis）81K、`feedback`（含 ANSI）10K；
- `target_event_ids` 每次只实现 1 个事件，却携带全部需求的契约与 API 定义；
- 文件随实现进度变化导致 DeepSeek 前缀缓存命中率剧烈波动（60K↔20K token）。

## 五项修改（按各项列出的开关回退）

| #   | 修改                                                                                                                                                                      | 文件                                                            |
| --- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------- |
| A   | Stage 12 非末次创建调用上下文瘦身：files 收窄到 3 个接线文件 + 相关页面源码，contracts/apis 收窄到目标事件；终验调用与测试生成保留完整上下文（`ARC_FULL_CONTEXT=1` 回退） | `infrastructure/stages/frontend/interactions/implementation.py` |
| B   | agent 反馈去噪：剥 ANSI、截断超长字符串                                                                                                                                   | `infrastructure/shared/agent/loop.py`（`compact_feedback`）     |
| C   | 瞬态传输错误退避重试（连接/超时/5xx/限流，10/30/90s，`ARC_MODEL_TRANSPORT_RETRIES`）                                                                                      | `infrastructure/shared/models/text.py`                          |
| D   | Stage 09 每接受一个叶子需求即 checkpoint（`ui_design_progress.json`）；重跑跳过已完成需求；3 次提案耗尽改为记账后继续，最后统一报错（`ARC_UI_DESIGN_FRESH=1` 强制全新）   | `infrastructure/stages/frontend/ui/synthesis.py`                |
| E   | `run_all.py --resume`（main.py 透传）：按哨兵产物跳过已完成阶段，08/12 额外要求 status GREEN                                                                              | `run_all.py`、`main.py`                                         |

上游 50/50 单元测试通过。开发中发现并修正一处 resume 哨兵误判：
`backend/src/db/tables` 在脚手架中即存在（空目录），改判为「目录内至少一个 .sql」。

## 结果（同输入、同模型 deepseek-flash；baseline 为跨机器参考）

| 指标                           |            baseline |                        优化后 |                                     变化 |
| ------------------------------ | ------------------: | ----------------------------: | ---------------------------------------: |
| 总 token                       |           2,141,102 |                       928,299 |                               **−56.6%** |
| 输入 / 输出                    | 1,576,030 / 565,072 |              859,534 / 68,765 |                          −45.5% / −87.8% |
| Stage 12 token                 |           1,468,588 |                       590,804 |                                   −59.8% |
| Stage 12 每次调用平均输入（含测试生成）       |              59,139 |                        27,596 |                                   −53.3% |
| 各阶段最后成功尝试的 wall 总和 |           4,481.8 s |                       489.8 s | −89.1%（跨机器，排除失败重试与最终构建） |
| 正确性                         |               34/34 | 后端 14/14、UI 9/9、E2E 11/11 |                                     全绿 |

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
- 队友 baseline 原始产物：`artifacts/teammate-baseline/`（原始 32MB jsonl 不入库，保留 gz 压缩版）

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
| -------------- | -------: | -------: | ----------------: |
| 全流程         |    51.6% |    36.3% |             36.5% |
| Stage 12       |    59.2% |    44.2% |             35.9% |

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

耗时口径已统一：旧 baseline 的 4,940.2s 含失败尝试，不能直接与优化后的最后成功阶段总和 489.8s 对比；按日志逐阶段取最后成功尝试，baseline 为 4,481.8s。新聚合脚本保留这一单位，并与模型调用累计时间分开。

## OPT-G 完整尝试与准入修复

`7ef3a5b` 在 `work/optg2-1101` 以同一输入和 deepseek-flash 运行：后端 14/14、UI 8/8 GREEN，REQ-1 E2E GREEN，REQ-2 在 18 轮修复后失败，未执行最终生产构建。总 token 为 1,884,192，全流程输入缓存命中率为 41.6%；另一次主动中断尝试消耗 60,543 token，单独计入 [optg-metrics.json](optg-metrics.json)。这些观测没有证明总 token、成功率或端到端耗时改善，反馈优化的全流程验收仍未满足。

冻结的注册测试包含以下设置：

```ts
await page.evaluate(() => {
    window.__ARC_UI_FIXTURE__ = {
        page: "registration",
        data: { "register.submitting": true },
    };
});
await page.reload();
```

窗口变量不会跨 reload 保留，且 E2E 生成指令本来就禁止 UI fixture 注入。这一断言失败被旧准入 gate 接受为行为 RED，导致后续应用修复耗尽轮数；同套件还存在 Cookie 的根 URL 观察断言失败，不能把它与 fixture 问题视为同一根因。

新增的 `validate_e2e_source` 在冻结前拒绝保留的 UI fixture 标识符，已经用原失败套件和回归测试验证拒绝。原冻结测试和失败工件没有改写。`ARC_LEGACY_E2E_SOURCE_CHECK=1` 恢复此前的 fixture 准入行为，原 loopback URL 检查仍生效。新规则尚未经过另一轮完整模型生成，因此不把此修复写成端到端 GREEN。

两次 OPT-G 尝试的安全运行元数据、原始审计日志、IR、源码及冻结测试已归档在课程侧 `artifacts/optimization-runs/`，清单为 `artifacts/optimization-runs.json`。归档逐文件解压哈希验证后才删除四套运行目录中的可重建依赖；IR、源码、冻结测试与原始日志由归档保留，重复工作副本已在逐文件校验后清理。恢复归档后需安装依赖，不能把缺少 node_modules 的目录当作可直接运行的应用。

## 报告与交接材料

课程侧 `report/main.pdf` 与 `slides/main.pdf` 已按完整改动清单、负结果与可比性限制更新，不再只是首轮结果快照。共享的 `change-effects.json` 维护工作项与效果分类；`scripts/prepare_materials.py` 从这些数据和既有调用聚合生成报告/Slides 的数字与图，避免手工重复数字。

原记录中的 log 路径是测量时的工作位置；当前队友文件在课程侧 `artifacts/teammate-baseline/`，模型日志与阶段日志均保留压缩原件。恢复原始优化快照使用 `artifacts/optimization-runs/` 的校验归档，不能把历史失败工件冒充新的完整运行。

源码差异可以相对 teacher-baseline 核验，但队友编译器提交号未知，不能证明所有较早工程修正都是队友没有的功能。Stage 12 的 59,139/27,596 是阶段输入除以 21 次返回的均值，包含测试生成，旧“单次创建调用”标签已纠正。

## 老师原版验收恢复

以上历史性能记录使用本地 pending 扩展输入。默认 input 现已按教师 ZIP 原始字节恢复，原件哈希在 input/source.json，扩展保留在 examples/registration-pending。两种输入不混算性能。原版独立验收执行未改动的老师四条测试及十条固定行为/数据库检查；契约 v2 只纠正失败会话读取后入口显示的过度约束，保留原要求的身份和无写入不变量，详情见 [验收说明](../../acceptance/README.md)。

| 原版运行 | SDK 总 token | 最终状态与定位 |
| --- | ---: | --- |
| teacher-original-1101 | 381,595 | Stage 08；对永远非空的 JSON 字符串取反，断言恒假 |
| teacher-original-1101-v2 | 424,915 | 后端 14 条通过，Stage 10 UI 失败；未完成应用被独立反例验收 0/14 拒绝 |
| teacher-original-1101-v3 | 251,506 | Stage 08；将未知凭据字面量与完整 JSON 响应判相等，断言恒假 |
| teacher-original-1101-v4 | 343,212 | 后端 13 条、UI 9 条通过；Stage 06 失败续跑后，Stage 11 交互提案耗尽三次 |
| teacher-original-1101-v5 | 369,551 | Stage 08；保密断言禁止 password_hash 键，却主动把含该键的对象传入同一断言 |

数字与安全元数据归 [teacher-original-validation.json](teacher-original-validation.json)，原始日志、设计、冻结测试和生成源码按逐文件哈希归档在课程侧 artifacts/optimization-runs；失败测试未改写。v4 的 UI IR 还把老师显式要求的 Gender radiogroup 设计为 select，说明内部 UI 全绿不能代替老师测试。v4 生成中发生契约审计修正，也不能视为验收源码始终不变的受控测量。

已实施修正包括：冻结前拒绝两类恒假后端断言；完整登录态可见性提示；只读外部测试供给及 radiogroup/select 冲突准入；radio 静态选项值与共享选择 checked 状态的正确存在性断言；API 叶子义务边界说明；交互重试明确基于已接受状态而非被拒提案增量。全部保留原阶段 gate，并分别提供环境回退开关。当前 73 项编译器测试、17 项维护测试通过；第五轮继续出现新的自相矛盾测试，说明两条静态准入不是通用可满足性证明。后续正确性基线从全新目录恢复模型默认思考模式（ARC_DISABLE_THINKING=0），仍使用固定 v2 验收；不能提前宣布稳定或性能收益。

五次失败的源码、冻结测试和原始审计在逐文件核验归档后删除了重复工作副本；浏览器诊断、阶段控制台与调用聚合另存 teacher-original-diagnostics.tar.gz，清理清单归课程侧 artifacts/optimization-runs/teacher-validation-cleanup.json。只清理这些已结束目录，正在运行的 reasoning 目录保留。

恢复思考的独立尝试在 Stage 08 首个生成调用等待 511.3 秒无返回后主动中断，已返回 usage 合计 97,129 token；未返回请求费用未知，不能计零。另加冻结前独立矛盾审阅，实测反例 2.7 秒拒绝、正例 1.4 秒放行；这是诊断覆盖，不是成功率证明。新的 reviewed 目录重新从头生成，默认快速模式加审阅，后续完整结果见下文。

## 原版稳定行为验收通过

reviewed 运行现已完成：后端 14/14、UI 9/9、生成 E2E 10/10，老师原测试 4/4 与固定 v2 检查 10/10 全部通过，无 skipped/flaky/errors，独立验收后生产构建通过。原版 input 和生成前固定 v2 断言哈希均一致。源码在 Stage 11 因 trigger 简写错误从 f19a655 续跑到 0d4739a，元数据明确记录，不能称为单一提交无人工干预从头成功。

90 次 SDK 返回共 1,271,206 token，其中输入 1,174,853、输出 96,353，reasoning 8,383；模型请求累计 416.4 秒，输入缓存命中 28.3%。这些数字包含首次失败的 Stage 11 和续跑，属于这一轨迹；与旧 pending 扩展输入、不同思考配置和队友未知源码不可直接作为优化因果比较。

这一版本达到原版自动化行为验收条件，可以作为稳定开发起点。视觉像素相似度没有人工签收；pending 扩展、重复种子成功率、降低 token 的受控对照均待后续工作。独立复核增加的成本必须计入后续对照，不能只计成功修复轮数。

## 单事件上下文对照：有局部收益，暂不默认启用

`ARC_EVENT_CONTEXT=1` 在非终验创建阶段只供给目标事件、完整契约、全部共享触发器、触发源元素、全部可用前端绑定和相关 API；终验保持全量，所有 gate 和固定 v2 验收保留。基于 teacher-stable 的隔离分支试验，默认仍为 0。整体审阅与下一步顺序见 [整体优化审阅](../2026-11-01-整体优化审阅.md)。

| 运行 | 范围 | 总 token | Stage 12 输入 | 外部固定验收 |
| --- | --- | ---: | ---: | --- |
| ab-stable-control-1101 | 稳定源码全新生成，开关 0 | 1,066,909 | 575,061 | 14/14，最终构建通过 |
| ab-event-context-1101 | 候选全新生成，开关 1 | 819,564 | 280,561 | 7/14；不能接受为优化完成 |
| ab-matched-event-context-1101 | 与对照同前置 IR/后端/UI 的 Stage 12 试验 | 229,744（仅 Stage 12） | 218,402 | 首跑 13/14；原样重跑 14/14，最终构建通过 |

全新候选总 token 下降 23.2%、Stage 12 输入下降 51.2%，但必须连同验收失败解释。候选模型调用 82 次，对照 73 次；模型请求累计 358.7 秒与 408.4 秒不是端到端耗时，运行并发、依赖预装不同，不宣称延迟加速。全流程未命中缓存输入从 564,994 仅降到 534,028（5.5%）；输出从 95,387 降至 78,560，不能把总 token 降幅当费用降幅。

全新候选内部后端 15、UI 9、生成 E2E 12 全绿，却因注册密码精确标签定位与 503 未处理异常而未通过外部验收。密码类型实际仍是 password；隔离浏览器反例确认 aria-hidden 必填星号仍影响 getByLabel 的精确文本定位，不能据 accessible-name 全绿宣称老师可操作。候选失败保持原样，不修改冻结断言转绿。

共享上游试验核验 requirements/visual/schema/obligations/API/contract/UI/interactions 八份 IR 哈希相同，固定 v2 断言不变；它不是从头完整生成证据。Stage 12 输入下降 62.0%，其中十个匹配非终验创建调用均值从 23,760.6 到 6,321.4（−73.4%）；末次全量修复仍约 48k token。测试生成轨迹和新 E2E 套件不同，不能把该阶段全部下降归到上下文。首跑唯一失败为 F04 networkidle 超时，轨迹含未完成第三方图片请求；未改代码或测试原样重跑 14/14。必须保留首次失败，不宣称稳定性提升。

历史同请求重放另显示 18 个创建负载字符下降 79.4%，不是新 token 测量。完整调用聚合、配对、协议、输入/验收身份、失败与 probe 归 [event-context-comparison.json](event-context-comparison.json)，可由 scripts/profile_compiler.py 重算。结论是局部上下文收益有证据，完整候选未通过，开关保持显式启用，原稳定标签不变。下一项先提前校验真实外部控件契约和会话失败路径，再重复同口径全流程。

## 精确标签与会话失败的提前检查

修复分支 fix/teacher-interaction-contracts 增加两道提前检查：Stage 10 精确标签必须定位到真实控件，Stage 12 的只读 GET mount 处理器接受隔离 503/传输失败探针；全局浏览器错误上报不变。历史失败页面仍通过原 accessible-name 检查，却被新增标签检查拒绝；历史处理器在两种故障中均被拒绝。DOM 正例只用于隔离验证，没有修改历史失败源码或冻结测试。

首轮 teacher-contracts-1101 的标签和故障检查通过，但冻结 E2E 把实际 session_id 写为 session，运行被主动中断而未将正确前端改成迎合错误测试。补充已通过后端的只读源码/Cookie producer 证据，并在冻结前对明确有效会话场景检查直接字面量 Cookie 名；原错误套件被新检查拒绝，归档保留。

teacher-contracts-1101-v2 从全新目录生成，无断点续跑、无人为修改生成源码：后端 13/13、UI 9/9、生成 E2E 10/10，老师原测试 4/4 加固定 v2 检查 10/10 全绿，无 skip/flaky，最终生产构建通过。只读加载处理器 503 和传输失败均实际执行 API 并通过，NOT_EXERCISED=0。老师 input 与固定断言的生成前后哈希一致。

包装脚本在运行期间被更新记录字段，Bash 后续读取偏移导致自动验收命令未启动；生成和构建已完成，之后用原独立验收脚本、同一输出目录单独启动，日志和元数据保留。这是操作问题，不隐藏为一次无故障包装脚本执行；当前脚本已通过语法和 shellcheck 检查。

本轮成功生成返回 usage 合计 1,118,249 token；这是正确性修复验证，另有首轮中断成本，不能称为相对旧实验的性能收益。完整指标、旧反例、Cookie 反例、原件哈希和验收结果见 [teacher-contract-validation.json](teacher-contract-validation.json)。84 项编译器测试、18 项维护测试通过。旧稳定标签保留，新版本标签为 teacher-contracts-2026-11-01；激进上下文试验仍默认关闭。

这些检查只覆盖已执行路径，不能证明所有输入均正确；动态 Cookie 设置、未执行分支与其他跨 API 组合仍由后续真实验收发现。接下来独立处理阶段完成/依赖失效标记，不在这一正确性运行中叠加性能改动。
