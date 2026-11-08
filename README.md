# mini-SWE-agent → ARC-Bench adapter

围绕**未改动的 [mini-SWE-agent](https://github.com/SWE-agent/mini-swe-agent) v2.4.6**（PyPI 安装，不 vendor 源码）的 ARC-Bench 适配层。适配面收敛为三件事：任务域内容装配、运输层政策、可观测性；harness 契约逐字沿用上游配置。设计依据、运行档案与成本模型见 **[docs/design.md](docs/design.md)**。

- ARC-Bench: https://github.com/code-philia/arc-bench；Runner 约定：`python main.py <requirements目录> --output-dir <应用目录>`，ZIP 根含 `main.py` + `requirements.txt`

## 安装

```bash
unzip mini_swe_arcbench_adapter.zip -d mini_swe_arcbench_adapter
cd mini_swe_arcbench_adapter
python3 -m venv .venv && source .venv/bin/activate
python -m pip install -r requirements.txt
mini --help   # 上游 CLI 仍可用
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

| 环境变量 | 默认 | 说明 |
|---|---|---|
| `ARC_REQUEST_TIMEOUT` | 600 | 单请求超时（秒） |
| `MSWEA_MODEL_RETRY_STOP_AFTER_ATTEMPT` | 100 | 网关错误通常不计费且失败即损失全部进度；最坏 ~6.6h 重试直到平台/网关恢复 |
| `ARC_MAX_STEPS` / `ARC_MAX_SECONDS` | 250 / 3600 | 沿用上游 swebench 配置 |
| `ARC_REASONING_EFFORT` | `low` | 传给端点的思考力度，设空省略该参数 |
| `ARC_TRANSPORT_REASONING` | `passthrough` | `strip` 显式剥离思考回放（DeepSeek 契约与重编码网关需要回传，见 docs/design.md） |
| `ARC_LOG_IMAGES` | 0（剥离） | 审计产物中的图片 base64，`=1` 保留原图 |

## Prompt 与管线架构（摘要）

- **Harness 契约**：system、instance 骨架、输出截断、format error、`drop_params`/`parallel_tool_calls`、step_limit——逐字沿用上游 `config/benchmarks/swebench.yaml`；shell 环境沿用 `config/default.yaml`（`PAGER=cat` 等）
- **任务域**（本仓库唯一承载的 prompt 内容）：YAML 逐字、参考图（自动缩至 ≤1280px、JPEG/PNG 择小）、禁区与提交标记、runner 事实三行
- **验证管线**（workflow 步 4）：提交前逐场景对照运行中的应用，核对 exact roles/accessible names；自测脚本只是需求的代理，冲突时以需求为准
- **命令执行**：所有 agent 命令经 `bash -c` 包装（环境 shell 是 POSIX sh，PIPESTATUS 等 bash-isms 在解释器层根治）；**模板脚本** `scripts/srv.sh`（服务生命周期，PID 文件 + 探活）——进程类损耗由脚本吸收，prompt 只放指针

机制细节、依据与运行档案：[docs/design.md](docs/design.md)。

## 可观测性（三通道 + spill）

| 产物 | 内容 |
|---|---|
| stdout 单行 JSON（实时 flush） | 阶段事件：导入、初始化、任务准备、每次请求 `model_request_start/end`（耗时、finish_reason、usage）、bash 元数据（含 spilled）、脱敏异常链 |
| `.arc_adapter/calls.jsonl` | 每次 HTTP 尝试一行：耗时、finish_reason、完整 usage 或失败异常链 |
| `.arc_adapter/payloads.jsonl` | append-only 增量日志（`prefix_len`+`append`），按序折叠重建每次尝试的字节级 payload（`scripts/reconstruct_payload.py`）；图片以 sha256 占位符剥离 |
| `.arc_adapter/spills/` | 超过 4K 字符的工具输出全量落盘；模型侧只见 head/tail+追读指针 |
| `.arc_adapter/trajectory.json` | 上游完整消息历史（含 reasoning 原文）；每步落盘，run 结束后图片剥离 |
| `.arc_adapter/run_summary.json` | status、llm_calls、model_http_attempts、token 聚合、错误链 |

## 上传

`python scripts/package_agent.py` → `dist/mini_swe_arcbench_adapter.zip`（源码白名单，无密钥/venv/node_modules/.git）。以 Python agent 类型上传，表单 Base URL/Key 映射到 `OPENAI_BASE_URL`/`OPENAI_API_KEY`。

## 测试（不花 API）

```bash
python -m pip install pytest
python -m pytest -q   # 本地回环 HTTP mock：CLI 成功/断连、spill、脚本、脱敏、上游契约
```

## 安全

上游 bash 工具会在输出目录执行模型生成的任意 shell 命令；请在隔离的可信工作区运行。
