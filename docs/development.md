# 开发指南

当前维护两条路线：默认 upstream 贴近固定教师源码，coding 独立开发。用户仍禁止真实模型 API 调用；下面的生成命令仅作接口参考，离线验证可执行。

## 修改范围

| 改动           | 所属位置与要求                                                                   |
| -------------- | -------------------------------------------------------------------------------- |
| 更新教师路线   | 先确定上游提交，更新 upstream/ 和 upstream.json；必要小修正记录在 upstream.patch |
| 改进 coding    | 修改 coding_agent/；support 是保留的检查依赖，模板和冻结测试不能为修绿而改       |
| 平台入口与目录 | main.py、runtime/；保持引擎隔离和失败终态                                        |
| 打包与独立验收 | scripts/；保留源码身份、原始断言及正负控制                                       |

不要继续向旧 legacy 添加补丁。旧调度、契约推断与 interactions 仍能在 `pre-upstream-migration-2026-11-02` 标签中查看。当前没有 legacy 别名或 --resume；需要复核旧实验时用固定标签的独立 checkout 和原协议。

## 安装与检查

Python 3.12、Node 22、npm 和 uv 为前提，安装步骤见根 README。执行：

```sh
make check
make format
```

检查包含上游完整文件哈希、上游原单测、coding/平台/打包回归、Notes、Ruff、Markdownlint 与 Prettier。上游文件和测试不经本地格式工具改写，原测试单独启动解释器，清除真实模型配置并阻断外网。交互终端测试使用 TERM=xterm，避免把模拟 TTY 当成 dumb 终端。

当前上游原测试已有相应回归支持 2 个兼容修正：失败退出码和 SDK 超时类型。不能通过跳过原测试或把非 GREEN 报告算成功来保留未记录的行为差异。

重浏览器模拟需要 Node 22、Chromium 和已准备的依赖快照，不调用真实模型：

```sh
export PATH="$HOME/.local/share/mise/installs/node/22.23.2/bin:$PATH"
ARC_RUN_BROWSER_TESTS=1 ARC_TEST_DEPENDENCIES=/absolute/dependency-snapshot \
  .venv/bin/python -m unittest discover -s tests -p test_coding_checks.py -q
```

原候选已验证的本机 Node 为 22.23.2；不要将其他 ABI 的 better-sqlite3 混用。Windows 可以直接执行 Python 检查入口，make 和部署 Bash 需要相应环境。

## 模型配置与运行

两条路线都读取环境中的 OPENAI_BASE_URL、OPENAI_API_KEY。make run 从 gitignored 的根 .env 读取配置，环境变量优先；ZIP 不携带 .env。包装入口缺省 MODEL=deepseek-flash。

| 配置                                      | 行为                                                          |
| ----------------------------------------- | ------------------------------------------------------------- |
| ARC_AGENT_ENGINE                          | 源码默认 upstream；ZIP 固定所选引擎                           |
| MODEL_REASONING、VISUAL_REASONING         | upstream 默认 low，沿用上游；不会套用旧 legacy 的关闭思考开关 |
| MAX_OUTPUT_TOKENS                         | upstream 默认 320000，按上游配置，不是本地已验证的提供方额度  |
| ARC_AGENT_MAX_TURNS/TOKENS/SECONDS        | coding 默认 100 轮、2500000 token、1200 秒                    |
| ARC_AGENT_OUTPUT_TOKENS/TRANSPORT_RETRIES | coding 默认 8192 和 1                                         |

```sh
# 接口参考；真实模型生成目前禁止执行。
make run ENGINE=upstream INPUT=input OUT=../work/manual-upstream-001
make run ENGINE=coding INPUT=input OUT=../work/manual-coding-001
make serve OUT=../work/manual-upstream-001 PORT=3000
```

直接 `python main.py input --output-dir <目录>` 使用当前工作区，包括未提交改动。make run 执行指定提交的同一份上传包，要求新目录。平台预置模板由薄层隔离生成并备份交付；日志中的临时目录保存失败诊断，已有编译状态不被当作新模板。

## 诊断与验收

upstream 首先看 `.arc/compilation.json`、各阶段报告与 compiler.log；--model-log 才保存详细模型输入输出。coding 先看 `.arc/agent/result.json`，再按事件查找原调用、检查和附件。原生日志及用量边界不同，不直接比较旧 summarizer 的数字。

对已有登录应用执行独立固定验收，每个证据路径必须全新：

```sh
.venv/bin/python scripts/accept_agent.py ../work/my-run --evidence ../work/my-fixed --mode fixed
.venv/bin/python scripts/accept_agent.py ../work/my-run --evidence ../work/my-production --mode production
```

字段/环境映射错误归评估错误，诊断不回填原成绩；视觉截图仍需独立复核。原生报告的成功不是教师任务全部通过的证明。

实际 ZIP 的预置目录启动检查会在模型客户端创建前强制停止，完全不连接模型：

```sh
.venv/bin/python scripts/test_platform_startup.py dist/<当前版本>.zip --output ../work/new-startup-check
```

coding 包另有本地假兼容服务全流程，检查测试冻结、跨层修复、构建、交付后审计、PORT 与图片：

```sh
make package ENGINE=coding ZIP=../work/new-coding-package.zip
.venv/bin/python scripts/test_agent_package.py ../work/new-coding-package.zip \
  --output ../work/new-package-check --dependencies /absolute/dependency-snapshot --initial-template
```

这些模拟不证明真实模型的成功率、视觉质量或 token 优势。历史用量/计时工具仍可复核对应格式的原日志，但不自动适配所有上游报告。
