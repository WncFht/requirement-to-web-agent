# Requirement to Web Agent

读取 `requirements.yaml`、参考图和附带测试，生成可运行的 React、Express、SQLite 网站。仓库保留两条独立路线：

| 引擎             | 实现                                                                               |
| ---------------- | ---------------------------------------------------------------------------------- |
| `upstream`，默认 | 基于教师仓库固定提交 `13e78ef`，沿用其十三阶段、契约、triggers、模型配置和部署模板 |
| `coding`         | 我们的单循环候选；先冻结测试，再由同一循环修改整个前后端                           |

`upstream/` 保存完整上游快照，141 个文件中，2 个运行源码文件有明确的小修正：失败退出码和 SDK 超时类型；另有 Git 属性调整，保护快照的原始换行字节。来源及逐文件哈希见 `upstream.json`，差异见 `upstream.patch`。`coding_agent/support/` 保留候选原有检查与模板依赖，避免上游升级改变候选行为。

真实模型 API 按用户要求停用；未经重新明确授权，仅进行本地整理与离线验证。两条路线的真实效果尚未完成同期比较，已有结果及限制见[结果摘要](docs/results.md)。

## 环境与离线检查

使用 Python 3.12、Node 22、npm 和 uv：

```sh
uv sync
uv pip install --python .venv/bin/python -r requirements-dev.txt
npm ci --ignore-scripts --no-audit --no-fund
pre-commit install
make check
```

`make check` 核对上游快照、执行上游原测试、coding 与平台回归、文档和格式检查，不调用真实模型。依赖安装可能需要下载。

## 打包

```sh
make versions
make package-check ENGINE=upstream
make package-check ENGINE=coding
```

产物为 `dist/agent-<引擎>-<提交SHA>-v3.zip` 和同名哈希清单，只包含指定提交中的运行源码。[打包范围](docs/packaging.md)说明具体内容，[提交指南](docs/submission.md)说明上传及本地运行。

## 目录

| 路径                                 | 职责                                                 |
| ------------------------------------ | ---------------------------------------------------- |
| `main.py`、`runtime/`                | 引擎选择、平台输出适配和所属进程治理                 |
| `upstream/`                          | 固定版本的教师源码、模板和原测试                     |
| `coding_agent/`                      | 独立循环、检查、工具和记录；support 是保留的检查依赖 |
| `input/`、`examples/`、`acceptance/` | 原教师任务、扩展示例和固定独立验收                   |
| `tests/`、`scripts/`                 | coding、适配层、打包、独立验收与维护检查             |
| `docs/`、`.agents/`                  | 当前文档、维护规则与决策理由                         |

共享仓库为 `WncFht/requirement-to-web-agent`。长期维护一个 main，用短期功能分支协作；原本地 legacy 及其实验保留在 `pre-upstream-migration-2026-11-02` 等历史标签中。更多说明见[文档导航](docs/README.md)。
