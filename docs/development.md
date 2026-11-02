# 开发指南

在源码仓库修改生成器，生成结果写到指定应用目录。`make run` 仍要求新目录；平台 `main.py` 首次收到预置模板时使用独立工作区生成，成功后在原输出根层交付，原模板移至日志给出的备份。当前真实模型 API 已停用，下面的生成命令仅作接口参考；离线检查可正常执行。

## 团队开发

从 main 创建短期 `feat/*` 或 `fix/*` 分支，修改所属模块并补充能暴露真实问题的回归，运行 `make check` 后合回。分支管理见[维护指南](maintenance.md)。

| 需要改变                        | 主要位置                                            | 验证重点                               |
| ------------------------------- | --------------------------------------------------- | -------------------------------------- |
| legacy 阶段设计、提示词与修复   | `legacy/`、`infrastructure/stages/`                 | IR、权限、准入与原门禁完整保留         |
| coding 工具、循环、预算与提示词 | `coding_agent/`                                     | 文件边界、冻结测试、失败终态和真实检查 |
| 共享模型连接、进程、模板        | `infrastructure/shared/`、`infrastructure/utils/`   | 两种引擎均不回归；凭据与模板身份正确   |
| 独立验收与上传包                | `scripts/evaluation.py`、`scripts/package_agent.py` | 固定断言不变，包中源码与指定提交一致   |

两种引擎都先生成测试、观察有效 RED，再实现到 GREEN。legacy 按阶段/事件重复这一步；coding 冻结全应用测试后在同一循环修改前后端。日常开发修改智能体源码，通过新提交交付；生成应用只作为验证证据，不回填成智能体版本。

## 环境与离线检查

Python 3.12、Node 22、npm 与 uv 为前提。根 README 的安装步骤完成后：

```sh
make check
make format
```

`make check` 执行 Python 单测、文档与 Notes 检查、Ruff、Prettier 和 Markdownlint。常规单测跳过重浏览器集成。若有已准备好的 Node 22 依赖快照及 Chromium，可显式执行本地模拟测试，不连接真实模型：

```sh
export PATH="$HOME/.local/share/mise/installs/node/22.23.2/bin:$PATH"
ARC_RUN_BROWSER_TESTS=1 ARC_TEST_DEPENDENCIES=/absolute/dependency-snapshot \
  .venv/bin/python -m unittest discover -s tests -p test_coding_checks.py -q
```

Node 22.23.2 是本机已验证版本。不要将 Node 24 与 Node 22 编译的 better-sqlite3 混用。Windows 可直接执行 `python scripts/run_checks.py --config scripts/checks.json --mode ci`；make、自动 Git hook 与 `deploy.sh` 的 Bash 部分需要相应环境。

## 运行与配置

需要固定提交的结果时，用[提交指南](submission.md)中的 `make run`，它执行对应上传包。直接运行当前工作区则包含未提交改动：

```sh
# 真实模型生成目前禁止执行；保留接口示例。
.venv/bin/python main.py input --output-dir ../work/new-legacy
ARC_AGENT_ENGINE=coding .venv/bin/python main.py input --output-dir ../work/new-coding
.venv/bin/python legacy/08_implement_backend_tdd.py --input input --output ../work/new-legacy
```

直接运行前须把模型配置放入环境；legacy 客户端也能读取本地 `.env`。`make run` 统一加载本地 `.env`，以已有环境变量为优先。平台包读取平台注入的 URL 和 Key，不携带 `.env`。

| 配置                                        | 行为                                                                    |
| ------------------------------------------- | ----------------------------------------------------------------------- |
| `OPENAI_BASE_URL`、`OPENAI_API_KEY`         | 必需的模型接口和凭据                                                    |
| `MODEL`                                     | 模型名；平台包与 coding 缺省为 `deepseek-flash`，legacy 直接运行需配置  |
| `ARC_AGENT_ENGINE`                          | 源码默认 legacy；上传包固定所选引擎                                     |
| `ARC_AGENT_MAX_TURNS/TOKENS/SECONDS`        | coding 默认 100 轮、2,500,000 token、1200 秒，共享安装、模型和检查预算  |
| `ARC_AGENT_OUTPUT_TOKENS/TRANSPORT_RETRIES` | coding 默认每次输出 8192、额外传输重试 1 次                             |
| `ARC_MODEL_TRANSPORT_RETRIES`               | legacy 瞬态传输额外重试次数，默认 2                                     |
| `ARC_DISABLE_THINKING`                      | legacy 默认 0；平台入口遇 DeepSeek 模型时缺省设为 1                     |
| `ARC_EVENT_CONTEXT`、`ARC_CACHE_PREFIX`     | legacy 单事件上下文与稳定排序，默认 1；支持显式消融，不代表稳定性能收益 |
| `ARC_FULL_CONTEXT`、`ARC_FULL_FEEDBACK`     | legacy 完整上下文/原始反馈诊断，默认 0                                  |
| `ARC_UI_DESIGN_FRESH`                       | legacy 忽略本阶段 UI checkpoint 重做，默认 0                            |

`ARC_LEGACY_*`、旧哨兵恢复和未晋升的 `ARC_CACHE_PREFIX_V2` 已移除；需要旧行为时运行固定标签中的源码。当前版本不可使用旧输出目录续跑。平台初始模板不是旧 checkpoint；入口适配不会放松这条规则。

## 可信续跑

legacy 在同一输入、源码、配置下普通失败或 Ctrl+C 后，可用原命令加 `--resume`。`.arc/pipeline_state.json` 仅在子进程成功退出并满足阶段完成条件后登记成功前缀；局部 checkpoint 不算成功证明。

状态核对输入、运行源码、依赖声明、关键配置和整体应用工作区哈希。后续阶段会合法修改页面，所以按整体工作区封存；日志、依赖、数据库与构建输出不作为完成证明。配置只保存指纹，不保存原值，API Key 轮换不影响身份。

输入、源码、配置或受保护文件改变、锁残留或强制终止造成未封存时，保留原目录并使用新目录。不要手工补写状态、删除下游 IR 或信任旧哨兵。coding 要求新输出，不支持断点续跑。

## 诊断与独立验收

legacy 查看阶段 `.arc/*.json`、`compiler.log` 和 `model_calls.jsonl`。coding 先看 `.arc/agent/result.json`，再按事件定位检查、请求与附件；`INTERNAL_GREEN` 仅代表内部通过。`INVALID_TEST`、无进展和预算耗尽都保留为失败，不能靠修改冻结测试修绿。

对已有的登录应用运行独立验收，每个证据路径必须全新：

```sh
.venv/bin/python scripts/accept_agent.py ../work/my-run --evidence ../work/my-fixed --mode fixed
.venv/bin/python scripts/accept_agent.py ../work/my-run --evidence ../work/my-production --mode production
```

验收使用隔离数据库，核对原应用与固定断言身份。映射/环境错误记为评估错误，诊断不回填原成绩；视觉截图仍需另行复核。Notes 示例另有固定正负控制，不代表已完成真实模型泛化。

单循环上传包可用本地假兼容服务验证解压入口、全检查、生产端口和静态图片；不会调用真实模型：

```sh
make package ENGINE=coding ZIP=../work/new-coding-package.zip
.venv/bin/python scripts/test_agent_package.py ../work/new-coding-package.zip \
  --output ../work/new-package-check --dependencies /absolute/dependency-snapshot --initial-template
```

该模拟场景预先填入平台模板，核对全检查、交付后审计、生产端口及图片。仅需要验证实际 ZIP 初始化时，用 `scripts/test_platform_startup.py <ZIP> --output <新证据目录>`；它禁止网络连接并在模型客户端创建前停止，legacy 要求 Stage 00 已通过。

legacy 的 `timings.jsonl` 用单调时钟记录父子 span，父子耗时有包含关系，不能相加；中断缺失 end 保持未知。`scripts/summarize_calls.py` 汇总已返回 SDK 用量，`scripts/summarize_timings.py` 汇总计时。它们不证明供应商账单、缓存路由或模型速度因果关系。
