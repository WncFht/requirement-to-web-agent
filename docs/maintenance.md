# 优化开发与维护

本指南管理编译器源码、实验、决策与提交。产品入口见 [development.md](development.md)，开发历史见 [history.md](history.md)。

## 接入来源与边界

维护规则来自 agent-maintenance；固定来源提交与脚本哈希保存在 `.agents/maintenance-source.json`。已采用三个维护技能、共享参考、模板、Notes 检查、文档检查、暂存快照检查与检查调度器。更新时对照记录的提交审阅差异，再同步项目适配；不直接覆盖项目配置。

源码使用独立 Git 仓库，外层 JI 忽略 `source/`。当前未配置远端，提交只保存在本机；GitHub Actions 配置须在源码仓库托管到 GitHub 后才会运行。外层仓库保存课程交付与源码导出，不能代替源码历史。模型凭据、虚拟环境和运行目录不入库。

## 本地准备与检查

在源码根目录执行：

```sh
uv pip install --python .venv/bin/python -r requirements-dev.txt
pre-commit install
.venv/bin/python scripts/run_checks.py --config scripts/checks.json --mode ci
```

提交 hook 检查暂存快照里的文档链接、技能与 Notes 格式及冻结记录；Python 改动执行编译器测试与 Ruff 格式检查。提交前先运行 `ruff format <修改的文件>`，再审阅并暂存。hook 不自动改写文件。全量维护工具行为测试由 `--mode ci` 执行；模型端到端实验单独运行，不在提交时自动消耗模型调用。

文档检查只接受仓库内可解析的本地链接。外层课程产物使用代码路径说明；原始运行证据在源码仓库外，通过实验报告记录路径与哈希。`scripts/doc-policy.json` 是篇幅预算来源，`scripts/checks.json` 是检查命令来源。检查通过不证明模型生成的应用满足需求，也不代表远端合并保护已经启用。

## 优化与实验

每次只推进一个可解释的修改，先保留成功基线和失败证据，再修改实现与对应测试。输入、源码提交、思考模式、依赖和运行目录影响比较口径；缓存实验同时报告全流程与目标阶段命中率，分母均为对应输入 token。模型生成的测试数会变化，测试全绿不能替代固定需求场景覆盖检查。

长期取舍写入 `.agents/notes/`，观测与限制写入所属实验报告；[history.md](history.md) 只保留可定位提交的开发里程碑。提案验收未完成时保留 proposed，不把局部测试结果写成全流程成功。

## 证据保留与清理

`../work/<run>/` 是实验目录。保留 `.arc` 工件、原始模型调用日志、失败测试、输入与代码身份后，才清理可重建的 `node_modules`、构建输出、浏览器临时产物与重复副本。压缩日志前逐字节校验解压结果；失败运行与负结果不得因清理消失。凭据目录不参与自动清理。

外层 `../upstream.patch` 使用以下命令从已提交源码导出，避免把运行产物与维护文件混入教师源码补丁：

```sh
git diff --binary teacher-baseline HEAD -- '*.py' pyproject.toml requirements.txt uv.lock > ../upstream.patch
```

更新外层课程记录时只暂存明确相关文件，不合并 JI 仓库里其他课程的未提交工作。

## 可恢复的课程归档

源码仓库未配置远端，外层 JI 只忽略工作副本，不应成为唯一备份缺口。源码工作区提交干净后运行：

```sh
.venv/bin/python scripts/export_source.py --output-dir ..
```

工具导出 `../artifacts/compiler-source.bundle`（完整已提交历史）、源码补丁和带提交号及 SHA-256 的 `compiler-export.json`。在不含 `source/` 的课程目录执行 `git clone artifacts/compiler-source.bundle source` 即可恢复；凭据、依赖和实验运行目录需单独准备。导出后对 bundle 做临时 clone，并核验提交号、文档和 `git fsck`，再提交外层归档。每次后续源码提交后重新导出，不能把旧 bundle 当成最新源码。

清理清单见 `docs/experiments/cleanup.json`；当前只删除经过解压哈希校验的队友 baseline 重复原始日志，压缩原件仍保留。失败实验、编译工件和课程报告未删除。
