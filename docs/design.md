# ARC-Bench 适配设计与运行档案

本文件是适配层的设计依据、机制清单、运行账本与决策记录。操作手册见 [README](../README.md)。

## 1. 定位与设计原则

适配层 = **未改动的 mini-swe-agent 2.4.6** 引擎 + 三类自持内容：

1. **任务域装配**：requirements.yaml 逐字 + 参考图（自动瘦身）+ 禁区与提交标记
2. **运输层政策**：思考回放、输出 spill、日志剥离、重试预算
3. **可观测性**：stdout 事件流 + calls.jsonl + payloads.jsonl + trajectory + run_summary

三条原则（每次路由错误后的修正都收敛于此）：

- **上游已有的原文沿用**；适配面只承载上游没有的任务域与平台契约
- **知识缺口用 prompt（一行事实+对策），样板重复用脚本，持续跟踪用工件**——三类问题三种工具，不混用
- **一次 A/B 一个变量**；分数跨套件版本不可比时显式标注

## 2. 架构分层与上游沿用清单

| 层 | 文件 | 职责 |
|---|---|---|
| CLI | `main.py` | Runner 入口约定、平台变量映射、dry-run |
| 任务域 | `arc_adapter.py` | 输入装配、图片瘦身、骨架常量、run_summary |
| 运输层 | `progress.py` | 事件流、calls.jsonl、payloads.jsonl delta、spill、reasoning 策略 |
| 引擎 | 上游 `DefaultAgent/LitellmModel/LocalEnvironment` | 循环、线性历史、bash 执行、重试——**零改动** |

上游沿用清单（逐字，来源 `minisweagent 2.4.6` 包内配置）：system、instance 骨架、输出截断（10K→head/tail 5K+教学文本）、format error、`drop_params`/`parallel_tool_calls`、step_limit 250、shell 环境（`PAGER=cat` 等）。**不可沿用的**：`BASH_TOOL` schema（上游硬编码）→ 工具描述类教学迁移到任务指令与模板脚本。

## 3. Prompt 架构

初始输入 ~6.5K tokens（指令 ~430 + 任务数据），运行中增长至 ~100K：

| 段 | 来源 | 内容 |
|---|---|---|
| System | 上游原文 | 1 句角色定义 |
| Instance 骨架 | 上游 + 4 处 ARC 改编（Overview/Boundaries/Workflow/Submission） | 每轮响应契约、禁区、验证管线（build+test:backend→逐场景对照→门槛）、提交协议 |
| Task 数据 | 本仓库 | 4 行任务指令 + 3 行 runner 事实 + YAML 逐字（50KB，含全部场景契约）+ 缩图 |

**实测行为证据**：t7→t9，workflow 步 4 的三处具体化（build/test:backend 具体化、逐场景对照、需求裁决规则）使通过数 24→33；环境三行使审计日志读取 2→0、pkill 自杀 1→0、浏览器发现 5 步→1 步。

## 4. 运输层政策（问题 → 机制 → 依据）

| 政策 | 问题 | 机制 | 依据 |
|---|---|---|---|
| 思考回放 passthrough（默认） | reasoning_content 泄漏进历史（t4 实测 58K replay，占上下文 44%） | passthrough 逐字回传；`strip` 可选 | DeepSeek thinking 契约 + 重编码网关靠回传恢复签名（dsh 笔记）；[arXiv:2611.03852](https://arxiv.org/abs/2611.03852) 论证压缩须按模型评估 |
| 输出 spill（>4K 字符） | 工具输出无追读路径 + trajectory 膨胀 | 全量落 `spills/`，模型侧 head/tail 1.5K+1.5K+指针 | dsh stdoutMaxBytes+spill 模式的最小移植 |
| 图片瘦身（≤1280px，JPEG/PNG 择小） | 19 图 17.68MB → 网关 413（t6 全灭） | PIL 缩放重编码，原图不动 | 实测 13.2MB→1.0MB；编码器侧 tokens 与字节解耦 |
| 日志图片剥离（sha256 占位） | 审计产物膨胀（t4 trajectory 13.8MB 含 6 份图） | 落盘前替换，原图可确定性还原 | 字节级重建不受影响 |
| 重试 100 次 | t8 两次 502（精确 180s 网关超时墙）后损失 26 步 | setdefault 100 + 上游指数退避 | 网关错误通常不计费；失败即损失全部进度 |

## 5. 模板与脚本

模板 = **填洞式脚手架**（build/deploy 链完整；DB 初始化机器、API 注册表、test:backend 跑批器留洞）。三次 run 验证：agent 一致地按填洞设计扩展，零冲突。

| 脚本 | 吸收的损耗 | 实测 |
|---|---|---|
| `scripts/check.sh <cmd>` | 验证包装的退出码/日志（PIPESTATUS 类） | t9 烧 7 步；`$?` 直查 + 日志封装，机制上消灭 |
| `scripts/srv.sh start\|stop\|status\|restart\|logs` | 服务生命周期样板 + pkill 自杀/猎杀 | t4 ×5、t7 ×1；PID 文件直接起 node，无 npm 孤儿 |

dsh 对照（dsh 在工具层吸收同类问题的机制）：`bash -c` 钉死解释器 ≈ check.sh 的 bash shebang；jobs 系统 ≈ srv.sh 的 PID 文件约定；stdoutMaxBytes+spill ≈ spill 捕获政策。**未复刻**：schema 级 `run_in_background`（需改上游）、任务注册表（单服务场景不需要）。

## 6. 运行账本（同一网关，BookStack 除注明外）

| Run | 包要点 | 步数 | 上下文末值 | 官方测试 | 备注 |
|---|---|---|---|---|---|
| t3/t4 | v1 可观测性 + 手写 prompt | 88 | 133,881 | **5/5 = 100.0**（当时套件仅 5 tests） | reasoning 回放 58K（占 44%） |
| t5 | 上游骨架 + effort=low + delta 日志 | 50 | 83,424 | 5/5 = 100.0（Train Ticket 任务，3 需求） | reasoning 23K |
| t6 | 同 t5 | 0 | — | 未运行 | **413**：19 图首请求 17.68MB 超网关请求体上限 → 触发图片瘦身 |
| t7 | + workflow 步 4 + 环境三行 | 52 | 114,784 | 24/35 = 68.6（套件已扩至 35 tests） | 平台实收 ¥0.9581；失败：编辑器链 6 + Shelfs 2 + strict-mode 2 + 导航 1 |
| t8 | 同 t7 | 26（终止） | 91,197 | 本地 **28/35** | **502×2，精确 180s 网关上游超时墙**（上游退化 episode）；半成品即超 t7 |
| t9 | + retry 100 + spill + check/srv 脚本 | 45 | 99,231 | **33/35 = 94.3** | PIPESTATUS 陷阱 7 步（check.sh 待其验证）；失败仅 Shelfs 2 |

**套件版本注意**：BookStack 官方套件在 t4→t7 之间从 5 tests 扩至 35 tests——t4 的 100 与 t7/t8/t9 的分数不可直接比较；t7/t8/t9 为同口径（35 tests）可比序列：24 → 28(半成品) → 33。

## 7. 失败分类学与修复状态

| 类 | 实例 | 根因 | 修复 | 状态 |
|---|---|---|---|---|
| 请求体超限 | t6 首请求 17.68MB → 413 | 图片字节；网关请求体上限 | 图片瘦身 ≤1280px | **已修**（t8/t9 首请求 1.39MB 通过） |
| 网关上游超时 | t8 两次 502，精确 180s | 上游退化 episode + prefill 随上下文增长 | retry 100；spill 硬帽增长；strip 可再省 ~20% prefill | 部分缓解；根治需网关侧（request_id 已留痕） |
| shell-ism | t4 pkill 自杀 ×5；t9 PIPESTATUS 7 步 | bash-ism 在 sh 环境；样板重写 | 环境指令一行（pkill）→ 0 次；check.sh/srv.sh | **已修** |
| 契约细节漏检 | t7/t9 Shelfs ×2；t7 编辑器链 ×6 | 自测断言未从 YAML 转录；广度无清单 | workflow 步 4（编辑器链已回收）；清单工件在阶梯 | **部分回收**（33/35，余 2） |
| 上下文增长 | t4 末态 134K，回放占 44% | 线性历史 + reasoning 回放 | effort=low（58K→25K/30K）；strip 在阶梯 | **已缓解**（t9 99K @ 45 步） |

## 8. 成本模型（官方牌价，已核实 [定价页](https://api-docs.deepseek.com/zh-cn/quick_start/pricing)）

deepseek-flash = DeepSeek-V4.1-Flash-1017，**峰谷分时**（北京时间周一至五 9:00-12:00、14:00-18:00 为高峰，其余含周末节假日为空闲，空闲=半价）：

| 项 | 高峰 | 空闲 |
|---|---|---|
| 输入缓存命中 | ¥0.04/M | ¥0.02/M |
| 输入缓存未命中 | ¥2/M | ¥1/M |
| 输出 | ¥8/M | ¥4/M |

t7 实收 ¥0.9581 与**高峰卡逐位一致**（0.958084）；该 run 在周日晚（空闲时段），官方应收 ¥0.479——网关按高峰卡计费或 2× 加价，二者数据面不可分。

t9 官方牌价 **¥0.985**（命中 0.634 + 未命中 0.157 + 输出 0.194）。**按内容项目归因**（重发+新增+输出全口径）：文件写入 ¥0.475（36%，双重计费：参数按输出价一次 + 每剩余步重发）、思考 ¥0.324（24%）、任务文本 ¥0.188、工具输出 ¥0.177、助手文本 ¥0.172。图片全程 ≈ ¥0.01（命中单价极低）。

**杠杆排序（CNY）**：步数（边际递增，末段步 ¥0.028）> 思考（strip 官方价省 ~¥0.23，有静默退化风险）> 图片/重发（单价极低，省的是带宽与 413 余量）。**成本不是当前约束**（<¥1.4/run）。

## 9. 已知差距与升级阶梯

相对 dsh 的结构性差距（均需改上游，按纪律冻结）：schema 级 `run_in_background`/`job_*`（现为 srv.sh PID 约定等价）、工具描述可编辑（现为任务行指针）、任务注册表。

剩余 2 处失败的升级阶梯（Shelfs 对，2/2 次系统性失败）：

1. **prompt 尖锐化**：可数合规标准——"每场景一条从 YAML 逐字转录的断言，断言数 ≥ 场景数"
2. **运输层末段提醒**（`ARC_REMINDER_TOKENS`，已设计未实现）：recency + 持续在场
3. **清单工件**（self-check 文件）：外部状态 + 留痕

## 10. 决策记录

| 决策 | 依据 | 结果 |
|---|---|---|
| 思考回放 passthrough 为默认（strip 降为 opt-in） | dsh 笔记：重编码网关靠回传恢复签名，缺 reasoning 静默 diverge；DeepSeek 契约要求 tool-call 轮回传；实测 0 错误 | t9 33/35 验证 |
| 逐场景验证写入 workflow 步 4 | t7 失败根因 = 验证回路闭合在自建产物上 | t9 +9 tests |
| pkill/服务模式用一行事实+对策教学（非脚本强制） | 知识缺口类 prompt 最优；t9 模式逐字采用 | 5→1→0 |
| 图片瘦身为缩图+择小编码（非转 JPEG 一刀切） | UI 截图 PNG 常更小更清晰 | 13.2MB→1.0MB |
| 环境三行放 task 段（非 ENVIRONMENT.md） | 最小修改原则；ENVIRONMENT.md 形式被否决 | t9 三项全部落地 |
| spill 阈值 4K + 纯文本（非压缩） | 上游 10K 阈值下单层生效；agent 需直接 grep | 双重截断消除 |
| 日志不放任务数据；任务词汇不进 prompt/脚本 | 最小适配原则 | 全部 run 无任务词汇泄漏 |
