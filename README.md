# Lab 6 需求编译智能体

把 `requirements.yaml` 与参考图转换成 React、Express、SQLite Web 应用，产物包含 `package.json`、`deploy.sh`、`frontend/` 与 `backend/`。

源码同时保留两个引擎：`legacy` 执行 00–12 阶段流水线，当前仍为默认；`coding` 使用一个循环读取、搜索、修改前后端并运行固定检查。候选实现已完成，但同期对照中断，视觉还原仍有缺口，尚未证明稳定成本优势。[架构参考](docs/architecture.md)解释两个引擎的边界，[实验报告](docs/experiments/2026-11-02-单循环编码智能体对照验证.md)保留成功、失败和未知用量。

真实模型 API 调用已按用户要求停止。未经重新明确授权，不运行生成、重试或付费评测；下面的安装与离线检查不调用模型。

## 安装与离线检查

使用 Python 3.12、Node 22.23.2、npm 和 uv。先安装 Python 及文档维护依赖：

```sh
uv sync
uv pip install --python .venv/bin/python -r requirements-dev.txt
npm ci --ignore-scripts --no-audit --no-fund
pre-commit install
.venv/bin/python scripts/run_checks.py --config scripts/checks.json --mode ci
npm run format:check
npm run lint:md
```

`npm ci` 与 Python 安装需要依赖下载；检查不读取模型 Key。默认单测跳过真实浏览器重集成；其依赖、Node ABI 与执行方式见[操作指南](docs/development.md#单循环候选的运行与审计)。Windows 可直接运行 `python scripts/run_checks.py --config scripts/checks.json --mode ci`，自动 Git hook 的 POSIX 入口需自行适配。

## 代码与文档

| 路径                                 | 职责                                                |
| ------------------------------------ | --------------------------------------------------- |
| `main.py`                            | 平台参数与引擎选择；生成命令需另外获得授权          |
| `00_*.py`–`12_*.py`、`run_all.py`    | 保留的 legacy 教学流水线                            |
| `coding_agent/`                      | 单循环候选、工具、检查与运行记录                    |
| `infrastructure/`                    | 两个引擎使用的模板、阶段实现和基础工具              |
| `input/`、`examples/`、`acceptance/` | 教师输入、扩展示例和固定验收；保持原字节            |
| `tests/`、`scripts/tests/`           | 编译器与维护工具的离线回归                          |
| `docs/`                              | 架构、操作、实验结果及协作说明                      |
| `.agents/`                           | 从 agent-maintenance 采纳的维护规则、技能和决策记录 |

教师原始教程保存在[历史教程](docs/history/teacher-tutorial.md)，其生成命令不是当前执行授权。所有权规则见 [AGENTS.md](AGENTS.md)，更多入口见[文档导航](docs/README.md)。

## 共享与提交

GitHub 共享这个独立源码仓库。`main` 同时包含两个引擎，默认保持 legacy；成员使用短期 `feat/*`、`fix/*` 分支提交改动，不维护长期平行的源码副本。版本、worktree、首次发布和不应上传的本地材料见[维护指南](docs/maintenance.md#仓库共享与分支)。

ARC-Bench 上传的是智能体 ZIP，不是 Git bundle 或生成的网站。已封存候选为 `65220fd`，源码与打包方式见[操作指南](docs/development.md#单循环候选的运行与审计)；格式整理后的新提交不冒充原受测版本。平台评测会调用模型，目前禁止执行。
