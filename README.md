# mini-SWE-agent → ARC-Bench adapter

基于仓内 [mini-swe-agent v2.4.6](vendor/mini-swe-agent/README.md)，使用唯一的 bash 工具实现 ARC-Bench 应用。adapter 读取原始 YAML 与参考图片、准备 React/Vite + Express + SQLite 项目，并保存版本、请求和轨迹；模型调用与工具协议沿用该版本，引擎源码随仓库和 ZIP 分发。

- ARC-Bench: https://github.com/code-philia/arc-bench；Runner 入口：`python main.py <requirements目录> --output-dir <应用目录>`。
- 当前开发分支：`experiment/mini6-bash`，起点 `4dcaa54`。原生 read/write/edit 工具实验保留在另一个分支。
- 上游来源、许可证与修改范围：[UPSTREAM.json](vendor/mini-swe-agent/UPSTREAM.json)、[LICENSE.md](vendor/mini-swe-agent/LICENSE.md)。

## 执行与验证

`main.py → arc_adapter.py → 仓内 DefaultAgent/LitellmModel → LocalEnvironment → Bash`。入口显式选择 `vendor/mini-swe-agent/src`，避免环境里另一个已安装版本覆盖本仓修改；requirements 安装同一份本地源码。模型参数、重试策略和 step/time 配置沿用 bash 基线，默认 reasoning effort 为 `low`。

命令通过 `bash --noprofile --norc -o pipefail -c` 直接执行，每次从应用根目录开始，stdin 断开。stdout/stderr 写入应用目录 `.agent/commands/`，等待直接 shell 退出后返回有限输出，完整日志路径进入 observation。后台进程继承输出句柄不会使正常命令一直等待 EOF。超时或异常中断会终止该命令的进程组，并有界等待直接子进程；正常返回保留显式启动的后台服务，不提供服务归属登记或最终自动清理。后台服务必须独立 session、重定向日志、记录启动组并检查 HTTP readiness；主动脱离命令组的进程不在命令超时清理范围内。

`pipefail` 保留管道失败；`false; echo done` 仍返回最后命令的状态。构建、后端和浏览器检查各自用独立调用执行 `scripts/run_check.py`，检查脚本本身必须将断言失败转换为非零退出。

构建和后端命令使用 `python3 scripts/run_check.py --check build -- npm run build`、`--check backend -- npm run test:backend`。浏览器验收使用 `--case SCN-ID -- node tests/check.cjs`，分组时重复 `--case`；测试通过 `scripts/scenario.cjs` 的 `await scenario(id, assertions, setup)` 逐条记录开始和结果，可选的准备回调失败记为 `blocked`，断言失败记为 `failed`。缺失或非法事件会使检查失败，命令成功不能代替场景执行证据。`.agent/checks.jsonl` 保留命令和场景结果，`.agent/coverage.json` 按最新执行生成覆盖状态，重新运行会先撤销该场景旧的通过状态；尚未声明的需求场景仍须在需求映射里保留为 `not_run`。迁移旧测试时，将构建等命令的 `--case` 改为 `--check`，浏览器断言放入辅助函数，保留原始入口、操作和结果约束。

prompt 保留完整需求、真实入口、精确语义、拒绝分支、状态转换、账户隔离与持久化验证；增加固定项目目录、优先复用 Playwright、批量读写和带唯一匹配检查的局部修改指导。局部检查随实现推进，最终源码执行完整回归。测试错误须依据 REQ 修正，保留等价断言；完成标记仍为独立 bash 命令。源码引入和离线回归不代表已在真实 bench 验证提分或降本。

历史诊断见 [docs/history.md](docs/history.md)。版本溯源见 [docs/versioning.md](docs/versioning.md)。

## 安装

```bash
unzip mini_swe_arcbench_adapter.zip -d mini_swe_arcbench_adapter
cd mini_swe_arcbench_adapter
python3 -m venv .venv && source .venv/bin/activate
python -m pip install -r requirements.txt
mini --help   # 安装的 CLI 使用仓内源码
```

Python 3.11+（3.13 实测），Node.js 22.12+，Windows 用 WSL2。端点须支持 tool calling + 图片输入（LiteLLM `openai/<model>` provider）。

## 运行

```bash
cp .env.example .env   # 填 OPENAI_BASE_URL / OPENAI_API_KEY；shell 环境变量优先于 .env
python main.py <requirements目录> --output-dir <应用目录> --dry-run   # 不花 API：校验输入、模板、多模态准备
python main.py <requirements目录> --output-dir <应用目录>             # 真实生成
PORT=3000 bash <应用目录>/deploy.sh                                    # 前台启动，期间保持运行
bash scripts/run_keep_baseline.sh <arc-bench克隆> <全新空输出目录>      # 生成→部署→官方 Playwright 测试 一键
```

模型优先级：`--model` > `ARC_MODEL` > `MODEL` > `deepseek-flash`。
环境变量：`ARC_REQUEST_TIMEOUT`（秒，默认 600）、`MSWEA_MODEL_RETRY_STOP_AFTER_ATTEMPT`（默认 100——网关错误通常不计费且失败即损失全部进度，最坏情形 ~6.6 小时重试直到平台/网关恢复）、`ARC_MAX_STEPS`（默认 250，沿用上游 swebench 配置）、`ARC_MAX_SECONDS`（3600）、`ARC_REASONING_EFFORT`（默认 `low`，传给端点的思考力度，设空省略该参数）、`ARC_TRANSPORT_REASONING`（`passthrough` 默认，按上游原样回传思考内容——DeepSeek 契约与重编码网关需要；`strip` 为显式剥离，仅在确认端点不需要且窗口/计费敏感时使用）、`ARC_LOG_IMAGES`（默认剥离审计产物中的图片 base64，`=1` 保留原图用于图片相关调试）。

Prompt 架构：system、format error、`drop_params`/`parallel_tool_calls` 和默认 step_limit 250 沿用上游 `config/benchmarks/swebench.yaml`，命令输出在引擎中限量，benchmark observation 同时保留日志路径；shell 环境（`PAGER=cat` 等）沿用 `config/default.yaml`。instance prompt 保留工具交互与完成标记契约，任务工作流由本仓库维护；YAML 和参考图通过任务文本注入。参考图附加前自动缩至 ≤1280px 并按更小的 JPEG/PNG 重编码（实测 19 张 13.2MB → 1.0MB，规避网关 413 请求体上限；原图在 `.arc_requirements/` 不变）。

## 日志（记在哪、有什么）

| 产物 | 内容 |
|---|---|
| stdout 单行 JSON（实时 flush） | 阶段事件：导入、初始化、任务准备、每次请求 `model_request_start/end`（耗时、finish_reason、**usage**）、bash 元数据、脱敏异常链 |
| `<output>/.arc_adapter/calls.jsonl` | 每次 HTTP 尝试一行：耗时、finish_reason、完整 usage，或失败异常链 |
| `<output>/.arc_adapter/payloads.jsonl` | append-only 增量日志（`prefix_len` + `append`），按序折叠可重建每次尝试发出的**字节级** payload（`scripts/reconstruct_payload.py`）；图片以 sha256 占位符剥离，可由 `.arc_requirements/` 原图确定性还原 |
| `<output>/.arc_adapter/trajectory.json` | 上游完整消息历史：每个 prompt（含 base64 图片）、每个响应 dump（含 reasoning 思考原文）、每条 bash 命令与有限输出；每步落盘，run 结束后图片同样剥离 |
| `<output>/.arc_adapter/run_summary.json` | status、llm_calls（逻辑调用）、model_http_attempts、token 聚合（成功尝试）、错误链 |

失败请求没有 usage（服务端未返回），token 聚合只覆盖成功尝试；`actual_api_cost_usd` 恒为 `null`（端点定价未知）。

## 上传

`python scripts/package_agent.py` → `dist/mini_swe_arcbench_adapter.zip`（源码白名单，无密钥/venv/node_modules）。以 Python agent 类型上传，表单 Base URL/Key 映射到 `OPENAI_BASE_URL`/`OPENAI_API_KEY`。

## 测试（不花 API）

```bash
python -m pip install pytest
python -m pytest -q   # 本地回环 HTTP mock：CLI 成功/断连、calls.jsonl、payload 快照、脱敏
```

## 安全

仓内 bash 工具会在输出目录执行模型生成的任意 shell 命令；请在隔离的可信工作区运行。
