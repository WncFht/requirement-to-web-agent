# 开发与维护

默认 compiler 贴近固定教师源码，coding 独立维护。真实模型调用与网站评测仅按明确授权执行；当前第一轮的一次生成已获授权，其余命令是接口参考。安装步骤见[根 README](../README.md)，版本、包内容及上传见[交付指南](submission.md)。

## 修改范围

| 改动           | 所属位置与要求                                                                         |
| -------------- | -------------------------------------------------------------------------------------- |
| 教师路线       | 固定提交后更新 `compiler/`、`compiler.json`；必要修正登记 `compiler.patch`，保留原测试 |
| coding         | `coding_agent/`；support 为独立检查依赖，模板和冻结测试不得为修绿而改                  |
| 平台边界       | `main.py`、`runtime/`；保持隔离、失败拒绝和所属进程清理                                |
| 打包、独立验收 | `scripts/`；保留来源、固定断言和正负控制                                               |

不继续维护 legacy；按[历史证据](results.md#历史证据)恢复独立版本，不给当前入口增加别名或 `--resume`。当前工作区执行 `python main.py` 会包含未提交改动；`make run` 使用指定提交的上传包，二者身份不同。

## 离线检查与格式

Python 3.12、Node 22、npm、uv 为前提。在根 README 的安装步骤后运行：

```sh
make check
# 仅在需要修正维护源码/文档格式时运行：
make format
```

统一检查包含快照文件哈希、教师原测试、coding/平台/打包回归、Notes、Ruff、Prettier 和 Markdownlint。教师原测试使用独立解释器，清除真实模型配置并阻断外网；终端模拟使用 TERM=xterm。不得跳过原测试或将非 GREEN 报告记为成功。

教师快照、根输入、固定验收、示例和 coding 模板不参与格式化。git-format-staged 处理暂存内容，CI 使用相同入口；Markdownlint 修正改变文件后需重新暂存。维护技能与检查来源记录在 `.agents/maintenance-source.json`。

重浏览器模拟需已准备的 Node 22 依赖和 Chromium，不调用真实模型：

```sh
export PATH="$HOME/.local/share/mise/installs/node/22.23.2/bin:$PATH"
ARC_RUN_BROWSER_TESTS=1 ARC_TEST_DEPENDENCIES=/absolute/dependency-snapshot \
  .venv/bin/python -m unittest discover -s tests -p test_coding_checks.py -q
```

受测 Node 为 22.23.2，不混用其他 ABI 的 better-sqlite3。Windows 可直接运行 Python 检查入口；make、部署和部分命令需要 Bash。

## 模型配置与运行

两条路线读取 OPENAI_BASE_URL、OPENAI_API_KEY。`make run` 读取 gitignored 的根 `.env`，环境变量优先；ZIP 不携带 `.env`，包装入口缺省 MODEL=deepseek-flash。

| 配置                                      | 行为                                         |
| ----------------------------------------- | -------------------------------------------- |
| ARC_AGENT_ENGINE                          | 源码默认 compiler，ZIP 固定所选引擎          |
| MODEL_REASONING、VISUAL_REASONING         | compiler 默认 low，沿用教师配置              |
| MAX_OUTPUT_TOKENS                         | compiler 默认 320000，不表示提供方额度已验证 |
| ARC_AGENT_MAX_TURNS/TOKENS/SECONDS        | coding 默认 100 轮、2500000 token、1200 秒   |
| ARC_AGENT_OUTPUT_TOKENS/TRANSPORT_RETRIES | coding 默认 8192、1                          |

```sh
# 以下为接口示例，执行前确认当前授权范围。
make run ENGINE=compiler INPUT=input OUT=work/manual-compiler-001
make run ENGINE=coding INPUT=input OUT=work/manual-coding-001
make serve OUT=work/manual-compiler-001 PORT=3000
```

仅在明确授权范围内运行。当前默认引擎为 compiler（旧的 `ARC_AGENT_ENGINE=upstream` 改为 `compiler`）；历史提交打包仍按其布局使用 upstream。输出可放仓库 gitignored 的 work/，已有目录或身份清单拒绝覆盖。

```sh
.venv/bin/python scripts/run_submission.py --ref HEAD --engine compiler \
  --input input --output work/compiler-iterations/round-01 \
  --model-log --max-seconds 2400
```

需先将 Node 22 加入 PATH，并通过 `.env` 或环境提供模型配置；环境变量优先。审计包含请求正文与返回，保留在忽略目录，不进入提交。墙钟到期停止所属进程树并记录退出 124；token 仅按返回 usage 汇总，未返回调用的用量保持未知。没有自动追加完整生成。

要求新的 OUT，并在相邻 run.json 记录身份。平台预置模板由适配层隔离生成并备份发布；失败工件保留，已有编译输出不当作新模板。目录和进程语义见[架构](architecture.md#平台与评估边界)。

## 诊断与验收

compiler 先看 `.arc/compilation.json`、逐阶段报告及 compiler.log，`--model-log` 才保存详细模型输入输出；coding 先看 `.arc/agent/result.json`，再沿事件查调用、检查与附件。原生格式和测点不同，旧汇总工具不自动适配新格式；未返回 usage 和未闭合计时保持未知，不计零成本。

对已有登录应用执行固定验收，证据目录必须全新：

```sh
.venv/bin/python scripts/accept_agent.py work/my-run --evidence work/my-fixed --mode fixed
.venv/bin/python scripts/accept_agent.py work/my-run --evidence work/my-production --mode production
```

适配错误归评估错误，事后诊断不回填原成绩。完整验收标准与已知缺口见[结果摘要](results.md#当前验收标准)；视觉截图单独复核。

实际 ZIP 的预置目录保护检查在模型客户端创建前停止，不连接模型：

```sh
.venv/bin/python scripts/test_platform_startup.py dist/<当前版本>.zip --output work/new-startup-check
```

coding 假兼容服务可离线检查冻结测试、跨层修复、构建、交付后审计、PORT 和图片：

```sh
make package ENGINE=coding ZIP=work/new-coding-package.zip
.venv/bin/python scripts/test_agent_package.py work/new-coding-package.zip \
  --output work/new-package-check --dependencies /absolute/dependency-snapshot --initial-template
```

这些模拟不增加真实成功样本，也不证明视觉质量或 token 优势。

## 分支与本地材料

长期维护 main，功能分支与 worktree 按需短期使用，完成检查和审阅后移除。共享仓库为 `WncFht/requirement-to-web-agent`；源码历史和交付包用途不同，不把平台 ZIP 当源码备份。

```sh
git switch -c feat/my-change
# 确需并行开发时：
git worktree add -b feat/parallel-change work/parallel-change main
# 合入且工作区干净后：
git worktree remove work/parallel-change
git branch -d feat/parallel-change
```

新 run、审阅快照、diff、报告和绘图检查优先放仓库内 gitignored 的 `work/`，按版本、引擎和输入隔离，索引为 `work/README.md`；不进入 Git、源码导出或平台 ZIP。历史绝对路径保留在原始记录，兼容软链不视为新 run。

清理前保存协议、源码、冻结测试、调用、报告、截图、数据库和哈希；可删除可重建依赖，不改失败或未知用量。`scripts/archive_runs.py` 不替代数据库/图片备份。`scripts/export_source.py --output-dir <新目录>` 与 Git bundle 用于源码恢复，旧分享包不随 main 自动更新。凭据仅来自环境或 gitignored `.env`，不写入文档、日志、清单或 ZIP。
