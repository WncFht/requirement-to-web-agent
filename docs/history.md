# History（2026-11-08 归档）

以下是 README.md、BASELINE_REPORT.md、DIFF_SUMMARY.md 收敛前的历史记录，原样保留作为诊断证据链。当前状态与用法见 README.md。

---

## 原 BASELINE_REPORT.md（截至 2026-11-08）

# 最新：实时日志验证

2026-11-08：定位到 Loading global config 是 minisweagent/__init__.py 导入时的提示，不足以认定卡在配置读取。新增 Adapter 阶段事件能区分依赖导入、初始化、输入编码、模型等待与 Bash 执行。

本轮仅运行本地测试服务与回归测试，不调用付费 API、不重复完整 Baseline。日志以单行 JSON 立即 flush 到 stdout，异常输出完整原因链但不展开冗长调用栈。不输出 Key、完整环境、输入图片、需求、模型响应或 Bash 正文。模型重试每次都有独立 start/error 事件。

tests/test_progress.py 通过子进程管道读取模型 start 日志后才允许本地 HTTP 服务返回，验证即时刷新；另主动断开连接验证两次失败和底层 RemoteProtocolError 可见。

正式平台页面展示仍需重新上传后确认，本轮不声称平台运行或业务测试成功。

---

# 最新：平台 MCP 依赖缺失修复

2026-11-08：用户平台日志中的本次错误是 ModuleNotFoundError: No module named 'mcp'，不是 API 断连。输入为 3 张图片、7,250 bytes YAML，不是先前 Keep。

原 requirements 仅固定 mini-swe-agent；本地原 LiteLLM 1.105.1，平台自动解析为 1.108.3。全新 Python 3.11 虚拟环境安装平台同版本后，使用本地 HTTP 测试服务复现同样错误：litellm/main.py completion 在存在 tools 时导入 MCP handler，最终 catalog.py 导入 mcp.types.CacheableResult 失败，尚未到达测试 HTTP 服务。

修复 requirements.txt：显式声明 litellm[mcp]==1.108.3，安装该版本要求的 MCP extra。保留原生 Agent、Bash 和图片输入，没有使用私有跳过参数绕过导入。

验证环境：mini-swe-agent 2.4.6、litellm 1.108.3、mcp 2.3.0、openai 3.46.0。修复后 scripts/check_model_transport.py 成功走真实 LiteLLM 请求序列化、本地 HTTP、原生 Bash 工具响应解析；pip check 无冲突；13 passed in 0.15s。这些是离线依赖/传输验证，不是付费模型或业务 Baseline，也不是正式 Linux 平台复测。

复现命令：
```
python3 -m venv /tmp/arc-check
/tmp/arc-check/bin/python -m pip install -r requirements.txt pytest
/tmp/arc-check/bin/python scripts/check_model_transport.py
/tmp/arc-check/bin/python -m pip check
/tmp/arc-check/bin/python -m pytest -q
python3 scripts/package_agent.py
```

新增 pytest.ini 限定 tests/，避免递归采集 runs/ 中解压 ZIP 的同名测试文件。证据在 runs/dependency-verification/。已重新打包，未重新上传正式平台；历史远端断连问题和真实 Keep N/A / 33 状态不因本次验证改变。

---

# 最新：平台入口修复（2026-11-08）

用户提供的线上 stderr 已确认：`Output directory must be empty for a clean baseline: /workspace/template`。平台入口退出码 1 的直接原因是适配器错误拒绝平台已有的输出目录，与模型连接失败是两个独立问题。此前交付没有验证这种 Runner 目录状态，这是验证缺口。

参考 version2 `infrastructure/shared/project/initialize.py`：公共入口改为只补齐缺失模板文件，保留已有源码及平台日志；干净目录约束只保留在本地 baseline 脚本。MODEL 环境变量作为 ARC_MODEL 之后的兼容别名。

公开 Runner 说明：https://github.com/code-philia/hackathon-local-simulation
该说明指出正式平台默认执行 frontend install/build、backend install/start，不保证执行 deploy.sh。原模板 backend start 直接加载尚未生成的 dist/server.js，故添加 prestart 自动构建。

## 本轮实际验证

- 在含 `.arc/` 的输出目录复现旧入口失败；修改后完整 Keep dry-run 成功（48,386 bytes YAML、20 个图片部分）。
- 13 项 Python 回归测试通过（0.19s），含已有源码/日志保留、重复初始化、路径逃逸防护、MODEL 别名。
- pip check 无依赖冲突；Bash 语法检查通过。
- 新 staging 目录中按平台默认命令真实安装构建前端，后端 install 后直接 start（prestart 构建成功）。PORT=31874，首页和 /api/health HTTP 成功。
- 上述为 macOS 本地同命令兼容验证，不是正式 Linux Runner 复测，也不是 Keep 业务 Baseline。未重新上传平台。
- 本轮不重复消耗 API 跑已知断连的完整 Keep。此前本地真实生成失败仍未解决；33 项官方测试未运行，N/A / 33。

## 使用

上传重新生成的 dist/mini_swe_arcbench_adapter.zip。公共入口允许非空输出目录，保留现有文件；本地 baseline 仍需全新输出路径。旧输出目录中的 package.json 不会被覆盖，验证新模板请使用新目录或重新提交。

下面保留历史诊断记录，发生冲突时以本节为准。

---

# Keep 第一轮验证报告

日期：2026-11-08（Asia/Shanghai）。状态：BLOCKED_BEFORE_GENERATION。

## 真实结果

- 官方版本：code-philia/arc-bench，commit `e59696bbc68578c3b3da1ad47f9a0ac07e581184`，本地 benchmark/。
- Keep：22 个需求节点（官方统计）、20 张参考图片；源 YAML 48,386 字节，完整保留；16 个 spec 文件合计 33 个 test 声明。
- CLI dry-run 实际成功，20 个多模态图片部分，输出 runs/keep-dry/。这只是模板，不是生成网站。
- Python 测试：10 passed in 0.18s；Python 编译及 Bash 语法检查通过。
- 模板真实 npm install 成功（201 packages，18s），React/Vite 与 TypeScript 后端构建成功。
- 原始 deploy.sh 实际执行成功；PORT=31873，首页 HTTP 200、/api/health 返回 status=ok。
- 真实 Agent 入口预检失败：当前进程缺少 OPENAI_BASE_URL、OPENAI_API_KEY，项目没有 .env。没有读取或移用老师项目中的密钥。
- Playwright：未执行，分数 N/A / 33，不能记为 0/33；没有业务失败分类证据。
- LLM Calls：0；本轮 Input/Output Tokens：0/0（未请求）；实际 API Cost：不可获取（未发起请求）。完整生成/测试运行时间：N/A。

## 网络与 Connection error

普通沙箱内 git clone 报 Could not resolve host: github.com；获得工具网络权限后官方仓库克隆与 npm 安装成功。此证据只能说明沙箱网络差异，不能证明此前模型 Connection error 的根因。未向模型端点发请求，模型视觉能力、工具调用支持及完整上下文容量尚未验证。未修改 mini-SWE 核心、Prompt 或官方测试。

## 对比结论与限制

老师版本 main.py 同样接收 requirement_path 和 --output-dir，另外提供编译阶段参数；其 TextModel/VisualModel 使用 OpenAI SDK、dotenv，执行多阶段 JSON 协议。本适配器继续用原生 DefaultAgent + LitellmModel + LocalEnvironment、OpenAI provider 原生 bash tool calls；不复制老师的多阶段 JSON 协议。通用模板采用 React/Vite、Express、SQLite，后端读取 PORT，生产服务提供 frontend/dist。

核查了老师入口、模型传输与通用项目模板，以及本适配器入口、输入处理、运行脚本、mini 原生 Agent/模型/环境接口；未宣称全面审计老师所有业务阶段。平台私有上传接口与 ZIP 验收尚未验证。ZIP 根目录保留 main.py 和 requirements.txt，使用源码白名单打包。

## 下一轮建议（未实施）

先配置项目 .env 或平台环境变量，执行一次完整 baseline。若模型拒绝图片、工具或上下文，依据真实 HTTP 错误修复兼容性，不能删除图片或压缩需求规避。若网络失败，检查实际运行环境的 DNS、代理及证书。产生真实业务失败后，再按 UI 定位、交互行为、持久化与初始化数据分类；本轮不做功能优化。

# 2026-11-08 第二次：真实连接故障诊断（取代上述无凭据状态）

当前项目 .env 已存在，已使用其配置，未输出或打包密钥。

## 实测证据

1. 完整原始 YAML + 全部 20 张原始图片 + 原生 Bash tools 的低输出探针成功：图片合计 1,969,670 bytes，user message JSON 2,679,848 bytes；12.73 秒，21,327 input / 30 output tokens。
2. 一次完整 Keep Baseline 尝试：runs/keep-real-20261108。真实生成运行 159.67 秒；4 次调用成功，执行原生 Bash 检查项目；第 5 次逻辑调用尝试两次后失败。mini llm_calls=5（包含失败逻辑调用，不等于 HTTP 请求次数）。成功响应累计 92,656 input / 484 output tokens；失败请求是否计费、是否产生 tokens 无法获得。
3. 最底层异常是 httpx.RemoteProtocolError: Server disconnected without sending a response，随后映射为 OpenAI APIConnectionError 和 LiteLLM InternalServerError。不是收到明确 HTTP 500，也不是客户端 ReadTimeout。600 秒 timeout 未能解决该断连。
4. 使用失败时完整历史（包含全部原始图片、需求、工具结果）另做最多 32 output tokens 的探针：成功，9.50 秒，26,075 input / 2 output tokens。
5. 生成未完成，deploy.sh 和 33 个官方测试未在本次执行。得分 **N/A / 33**，不能声称成功或 0/33。actual API cost 不可获取。

低输出探针证明失败上下文仍可以被服务接受；长输出阶段出现断连，可能与网关/上游生成连接处理有关，但没有网关日志，不能确定触发机制，也不能宣称已修复服务端。未删除、缩小或转换任何图片，未裁剪需求。未重复完整任务。

额外说明：原有 missing-key 单元测试因本地新建 .env 意外进入真实请求，约 49 秒后主动终止；其无完整响应统计，额外用量未知。现已让测试明确设置空环境变量隔离 .env；最终 10 passed in 0.22s。以上 tokens 不能当作账户总账。

## 本轮变更与边界

arc_adapter.py 显式提供可配置 ARC_REQUEST_TIMEOUT（默认 600 秒）；关闭 LiteLLM 内层 num_retries，使用 mini 原生重试并默认最多两次（平台可覆盖）。增加脱敏 exception cause chain 写入未来 run_summary，避免只看到 Connection error。核心 Agent Loop、LitellmModel 和 LocalEnvironment 没有改写。超时与重试调整属于防止盲目重试的修正，**并未消除已复现断连**。

证据：runs/keep-real-20261108/.arc_adapter/{trajectory.json,run_summary.json}；runs/diagnostic/{baseline.log,failed-context-probe.log}。轨迹保留原始输入和响应，请按本地实验数据管理，不纳入上传包。

下一步需要端点维护方检查相应时段长输出请求的连接终止原因；或单独验证兼容流式返回并聚合工具调用的适配方式。该方式尚未实现/验证，本轮不以改写核心或丢弃输入规避问题。

---

## 原 DIFF_SUMMARY.md

# 最新：精简实时日志

- progress.py：flush=True 的单行 JSON、敏感环境值脱敏、完整异常原因链；model/env mixin 只包裹原生调用，不改变模型或 Bash 行为。
- arc_adapter.py：加入导入/初始化/输入准备/每次模型请求/Bash 执行/完成阶段事件。
- main.py：记录平台传入变量存在性，入口异常立即输出到 stdout；保留兼容 stderr 报错。
- tests/test_progress.py：本地 HTTP 成功与断连入口测试，验证请求返回前已收到 stdout 日志及异常链脱敏。
- scripts/package_agent.py：包含 progress.py。

未执行昂贵完整生成、未修改官方测试。

# 最新依赖修复

- requirements.txt：固定 litellm[mcp]==1.108.3，补齐 MCP 运行依赖，消除本地与平台模型库版本漂移。
- scripts/check_model_transport.py：真实 LiteLLM + 本地 HTTP 的无付费 API 冒烟验证，覆盖延迟导入和 Bash 工具解析。
- pytest.ini：仅采集 tests/，避免 runs/ 中解压包重复模块冲突。
- scripts/package_agent.py：上传包包含 pytest.ini。
- BASELINE_REPORT.md：记录修复前后隔离环境实测，13 项测试通过，未冒充正式平台或业务 Baseline。

# 最新平台兼容修复

- arc_adapter.py / prepare_output：参考 version2，只补齐缺失模板，保留平台 `.arc` 日志及已有应用；拒绝模板路径逃出输出目录。
- main.py：输出目录说明与实际行为一致；支持平台 MODEL 别名，优先级 CLI > ARC_MODEL > MODEL > 默认值。
- web_template/backend/package.json：新增 prestart build，适配平台直接 npm start 的部署流程。
- scripts/run_keep_baseline.sh：干净目录检查从公共入口移回本地 baseline 脚本。
- tests/test_adapter.py：覆盖非空平台目录、源码保留、重复初始化、符号链接逃逸、MODEL 别名。13 passed。
- 文档：明确线上入口错误已修复、本地模型断连尚未修复，不再将模板部署与真实 Baseline 混同。

# 本轮最小修改

| 文件 | 修改原因与影响 |
|---|---|
| main.py | 在解析参数前读取项目 .env，override=False；支持本地持久化，平台环境变量始终优先 |
| requirements.txt | 显式声明 python-dotenv，不依赖间接依赖 |
| .env.example / .gitignore | 提供无密钥配置样例，排除本地密钥和生成物 |
| scripts/run_keep_baseline.sh | 探测多个官方目录布局；配置检查统一交给入口；兼容可选 cjs 文件；官方 setup 失败必须停止，防止继续使用不完整环境 |
| scripts/package_agent.py | 源码白名单 ZIP，排除环境、缓存、网站输出及密钥 |
| tests/test_adapter.py | 新增本地配置不得覆盖平台变量的回归测试 |
| BASELINE_REPORT.md / README.md | 记录本轮真实验证、阻断及复现命令 |

arc_adapter.py、web_template 与 mini-SWE-agent 核心未修改；官方 benchmark 未修改。没有根据未经复现的 Connection error 猜测性修改模型协议。

## 第二次连接故障诊断变更

- arc_adapter.py：可配置 600 秒请求超时，禁用内层重试、mini 默认最多两次；保存脱敏异常因果链。实际断连未修复。
- .env.example：记录超时和 mini 重试配置。
- tests/test_adapter.py：隔离真实 .env，验证 timeout 和 num_retries 参数；10 项通过。
- BASELINE_REPORT.md：加入真实完整任务失败结果与两次短输出探针证据。

---

## 原 README.md 的历史章节（已被当前 README 取代）


`Loading global config ...` 来自 minisweagent/__init__.py 的导入提示，之后继续加载模型库、初始化 Agent、编码输入并调用模型；仅凭旧日志无法确认具体等待位置。

Adapter 现在向 stdout 输出立即刷新的单行 JSON：
- entry_start：平台注入变量是否存在（不输出值）。
- engine_import_start/end：模型库导入及耗时。
- environment_check：加载配置后 Key/Base 是否存在、选择的模型。
- model_init_start、task_prepare_start、agent_loop_start：初始化和输入准备。
- model_request_start/end/error：每次实际请求尝试，返回耗时或完整脱敏异常原因链。
- bash_start/end/submitted/error：执行编号、耗时和退出码，不输出命令或工具输出正文。
- agent_end / entry_error：完成或失败。

时间戳为 UTC，字段含时区。默认最多尝试两次，每次失败立即输出；未改原生 Agent Loop 或重试机制。网页不展开冗长 traceback；原生 trajectory 保存详细执行记录。若最后一行是 model_request_start，则正在模型调用内等待；若只有 engine_import_start，则尚未完成依赖导入。环境存在性检查不代表 API Key 已通过服务端认证。

验证：`python -m pytest -q`（需要本地 loopback 监听权限）。tests/test_progress.py 使用本地 HTTP 服务覆盖 CLI 成功/断连、管道 stdout 实时刷新及密钥脱敏，不消耗付费 API。

---

# 最新依赖修复（2026-11-08）

平台 `No module named mcp` 已在独立环境复现并修复。请重新安装 `python -m pip install -r requirements.txt`，上传新 ZIP；安装清单现固定 `litellm[mcp]==1.108.3`。

无外部 API 验证：`python scripts/check_model_transport.py`。该脚本只连接本地测试 HTTP 服务，不加载项目 .env，不生成应用，不代表真实 Baseline。详见 BASELINE_REPORT.md 最新章节。

---

# 当前平台兼容说明

2026-11-08 修复：公共入口允许平台预创建的非空输出目录，采用 version2 的“仅补齐缺失文件”方式；现有日志和源码保留。独立本地 baseline 脚本仍要求全新目录。

正式平台可能不运行 deploy.sh。当前模板 frontend 支持独立 npm install/build，backend 支持独立 npm install/start，prestart 自动构建 TypeScript。deploy.sh 仍保留用于本地启动。

模型参数优先级：--model > ARC_MODEL > MODEL > deepseek-flash。项目 .env 不覆盖平台注入变量。

**已验证入口及模板启动，尚未完成真实 Keep Baseline。** 详见 BASELINE_REPORT.md 顶部的最新记录。上传包须重新执行 `python scripts/package_agent.py` 生成，不要继续使用旧 ZIP。

---

# mini-SWE-agent → ARC-Bench adapter (baseline v1)

This archive is a **minimal ARC-Bench adapter around the real, unmodified [mini-SWE-agent](https://github.com/SWE-agent/mini-swe-agent) v2.4.6 library**. The original `mini` CLI is available when the Python requirements are installed; the additional `main.py` supports ARC-Bench's runner contract.

- **Official ARC-Bench project:** https://github.com/code-philia/arc-bench
- **ARC compiler interface reference:** https://github.com/code-philia/agentic-requirement-compiler
- **Course requirements:** `python main.py <requirement-directory> --output-dir <application-directory>`; ZIP contains `main.py` beside `requirements.txt`.

## What is implemented

1. Read `requirements.yaml` **verbatim** and parse it to validate the input. Preserve every requirement, scenario, and selector; do not flatten or truncate YAML.
2. Pass every PNG/JPEG/WebP/GIF in `reference/` to mini-SWE-agent as an `image_url` multimodal payload (alongside full YAML). Copy all original source assets to `<output>/.arc_requirements/` for shell access.
3. Copy the supplied ARC-style React + Vite / Express / SQLite application starter into `<output>` with `package.json`, `frontend/`, `backend/`, and **unchanged `deploy.sh`**. The model edits these files using upstream mini-SWE-agent's bash tool and agent loop. This is generic REQ-to-Web generation, not a task-specific implementation.
4. Route model calls through `OPENAI_BASE_URL` and `OPENAI_API_KEY` using LiteLLM's OpenAI-compatible provider. No fallback model endpoints or embedded keys. Default model name is `deepseek-flash` (override with `ARC_MODEL` / `--model`); the endpoint must support **tool calling and image input**.
5. Record local trajectory and available usage data under `<output>/.arc_adapter/`. Unknown API pricing remains `null`, **not $0**.

**Important:** The ZIP vendors the **web template**, but does **not** vendor the upstream mini-SWE-agent package. `pip install -r requirements.txt` installs the pinned v2.4.6 engine from PyPI. This keeps the change surface minimal. The template is sourced from the provided `参考代码.zip`, under `infrastructure/shared/project/templates/`.

## Dependencies

- Python 3.11+ recommended, pip, Bash
- Node.js **22.12+**, npm, `curl`
- Internet access for Python/npm dependencies, and for Chromium on first run
- A valid model proxy API supporting `openai/<your-model>` through LiteLLM, with image inputs and bash/function tool calls
- Sufficient API credits for generating a 22-requirement, 33-scenario application

### 1. Install

```bash
unzip mini_swe_arcbench_adapter.zip -d mini_swe_arcbench_adapter
cd mini_swe_arcbench_adapter
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
mini --help  # original mini-SWE-agent CLI remains intact
```

On Windows, use **WSL2 Ubuntu** (the platform deployment script is Bash and upstream LocalEnvironment uses shell commands).

### 2. Clone official ARC-Bench

```bash
git clone https://github.com/code-philia/arc-bench.git ../arc-bench
```

Expected fixture paths:

```text
../arc-bench/arc-bench/keep/requirements/requirements.yaml
../arc-bench/arc-bench/keep/requirements/reference/*.png
../arc-bench/arc-bench/keep/tests/*.spec.ts
../arc-bench/setup-playwright.sh
```

### 3. Check input and output without spending API tokens

```bash
python main.py ../arc-bench/arc-bench/keep/requirements \
  --output-dir ../output/keep-dry-run --dry-run
```

This checks the public entry, YAML, assets, full image attachment preparation, template copy and output layout. **It does not generate a website**. Use a different empty output directory for the real run.

### 4. Full one-shot baseline (generate → start → official Playwright tests)

Set model credentials **only in your local shell or the ARC-Bench submission form**; never place them in source code or the ZIP:

```bash
export OPENAI_BASE_URL='https://YOUR-OPENAI-COMPATIBLE-ENDPOINT/v1'
export OPENAI_API_KEY='YOUR_SECRET_KEY'
export ARC_MODEL='deepseek-flash'  # or the exact model name supported by your endpoint

bash scripts/run_keep_baseline.sh ../arc-bench ../output/keep-baseline
```

`run_keep_baseline.sh` creates an output application, runs upstream mini-SWE-agent, launches its original `deploy.sh`, waits for the application entry URL (`/`), **copies the untouched official `keep/tests/`** into a separate test directory, sources the official `setup-playwright.sh`, and runs `npm run test:e2e`. No tests are modified, skipped or rewritten. The official generated config uses Chromium, one worker, no retries, and per-test timeouts as documented by ARC-Bench.

Results:

```text
../output/keep-baseline/.arc_adapter/trajectory.json
../output/keep-baseline/.arc_adapter/run_summary.json
../output/keep-baseline/arc_app_startup.log
../output/keep-baseline/arc_playwright.log
../output/keep-baseline/arc_playwright_report/  (when available)
../output/keep-baseline/arc_playwright_artifacts_path.txt
```

**If functional tests fail**, the script exits nonzero but preserves their logs and HTML report; do not treat the exit code as an adapter failure without checking the logs. A generation failure will stop before startup/test stages.

### Manual platform-compatible entry / startup

```bash
python main.py ../arc-bench/arc-bench/keep/requirements --output-dir ../output/keep-run
PORT=3000 bash ../output/keep-run/deploy.sh
# In another terminal, run official tests against http://127.0.0.1:3000
```

`deploy.sh` performs `npm install`, builds both workspaces, initializes SQLite on server start, and serves frontend and backend on `PORT` (default 3000). It runs in the foreground; keep that process running during tests.

## Upload to arc-bench.com

Upload `mini_swe_arcbench_adapter.zip` as a **Python agent**. The ZIP root includes both `main.py` and `requirements.txt`, the complete `web_template/` and `arc_adapter.py`, without `.venv`, `node_modules`, `.env`, generated websites or secrets. In the submission form, enter your API Base URL and Key (mapped by the platform to `OPENAI_BASE_URL` and `OPENAI_API_KEY`). Select a competition and start its task separately. Platform `keep` and course Smoke Train Booking are different tasks; do not assume a local `keep` run is the Smoke Competition score.

## Safety / test scope

The upstream mini-SWE-agent bash tool executes arbitrary model-generated shell commands in the provided output working directory; run only in an isolated workspace/container that you trust. This first pass deliberately does not modify upstream agent control flow, prompts for performance, token accounting logic, logging verbosity, testing rules, or optimize application behavior. A completed dry-run verifies **compatibility wiring**, not task accuracy.

### Adapter-only tests (no LLM API)

```bash
python -m pip install pytest
python -m pytest -q tests/test_adapter.py
bash -n scripts/run_keep_baseline.sh
```

The mock-based boundary test only verifies integration wiring and does not count as a generated application or benchmark score.

## 2026-11-08 本轮复现

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt pytest
cp .env.example .env
# 在本地编辑 .env，填写 OPENAI_BASE_URL 和 OPENAI_API_KEY；不要提交密钥。
# 运行环境已注入同名变量时，它们优先于 .env。
python -m pytest -q
git clone https://github.com/code-philia/arc-bench.git benchmark
# 本轮版本：e59696bbc68578c3b3da1ad47f9a0ac07e581184
python main.py benchmark/arc-bench/keep/requirements --output-dir runs/new-keep
PORT=3000 bash runs/new-keep/deploy.sh
```

完整生成、启动、官方测试一键执行（使用另一个全新目录，避免重复生成）：

```bash
source .venv/bin/activate
bash scripts/run_keep_baseline.sh benchmark runs/full-keep
```

对已有生成网站单独执行官方测试，保持网站运行：

```bash
mkdir -p runs/official-tests
cp -R benchmark/arc-bench/keep/tests runs/official-tests/
cp benchmark/setup-playwright.sh benchmark/setup-playwright.cjs runs/official-tests/
cd runs/official-tests
source ./setup-playwright.sh http://127.0.0.1:3000
npm run test:e2e
```

打包：`python scripts/package_agent.py`。产物 `dist/mini_swe_arcbench_adapter.zip`，根目录包含入口和依赖文件。通过平台 UI 上传该 ZIP 并配置环境变量；平台私有上传命令/API 未提供，未执行上传。此前 README 的平台表单描述仅供参考，未在本轮核实。

### 请求诊断配置

`ARC_REQUEST_TIMEOUT=600` 显式设置单次模型请求超时；`MSWEA_MODEL_RETRY_STOP_AFTER_ATTEMPT=2` 控制 mini 原生重试总尝试数。LiteLLM 内层重试关闭，避免叠加。运行结果的 `llm_calls` 是逻辑调用次数，不能直接当作 HTTP 请求总数；失败请求没有 usage 时，实际消耗未知。最新真实失败见 BASELINE_REPORT.md 的第二次诊断记录。
