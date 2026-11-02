# Requirement to Web Agent

把 `requirements.yaml`、参考图和任务附带测试转换成 React、Express、SQLite 网站，输出 `package.json`、`deploy.sh`、`frontend/` 与 `backend/`。

提供两个引擎：默认 `legacy` 按数据库、后端、页面与交互分阶段生成；`coding` 在同一编码循环中修改整个前后端。两者都由程序执行测试和构建来判断完成。coding 仍为候选，尚未证明稳定成本优势或视觉还原质量，已有证据见[结果摘要](docs/results.md)。

真实模型 API 已按用户要求停用；未经重新明确授权，仅进行本地整理与离线验证。

## 准备环境

使用 Python 3.12、Node 22、npm 和 uv：

```sh
uv sync
uv pip install --python .venv/bin/python -r requirements-dev.txt
npm ci --ignore-scripts --no-audit --no-fund
pre-commit install
make check
```

依赖安装可能需要下载；`make check` 不调用模型。开发流程与浏览器集成见[开发指南](docs/development.md)。

## 生成提交包

```sh
make versions
make package-check ENGINE=legacy
make package-check ENGINE=coding
```

`dist/` 中生成含引擎、提交 SHA 的 ZIP 和同名哈希清单，只包含已提交源码。[打包范围](docs/packaging.md)说明具体内容，[提交指南](docs/submission.md)说明历史版本选择、网站上传和本地运行。

## 目录

| 路径                                 | 职责                                 |
| ------------------------------------ | ------------------------------------ |
| `main.py`、`Makefile`                | 平台入口与开发命令                   |
| `legacy/`、`run_all.py`              | 十三阶段引擎与调度                   |
| `coding_agent/`                      | 单循环引擎、工具、检查和记录         |
| `infrastructure/`                    | 阶段实现、模型客户端、模板和基础工具 |
| `input/`、`examples/`、`acceptance/` | 原始教师任务、扩展示例和固定验收     |
| `tests/`、`scripts/`                 | 离线回归、独立验收与维护工具         |
| `docs/`、`.agents/`                  | 当前文档与维护规则、长期决策         |

GitHub 仓库建议命名为 `requirement-to-web-agent`，使用队伍私有仓库。维护一个 `main`，改动通过短期 `feat/*`、`fix/*` 分支合入；历史版本由标签保留。共享约定见[维护指南](docs/maintenance.md)，文档入口见[docs/README.md](docs/README.md)。
