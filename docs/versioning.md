# 版本与运行溯源

## 版本管理

`mini-swe` 是适配器的主开发分支。tag 固定实验版本，例如 `mini6`、`mini8`、`mini9`；发布后保持 tag 指向不变。`mini6-max` 这样的实验变体应有自己的提交和 tag，不能移动 `mini6` 来表示参数变化。模型环境变量仍可能覆盖包内默认值，实际配置以运行记录为准。

不为每个 tag 长期保留一个分支。继续开发某个旧基线时，从 tag 创建维护分支，例如 `maint/mini6`。可复用功能先在主开发分支实现为独立提交，再通过 `git cherry-pick` 回移到需要的维护分支。回移后的发布使用新 tag，例如 `mini6-provenance.1`；它和原来的 `mini6` 是两个实验版本。没有维护任务的旧版可以直接用 detached worktree 检查和打包。

```bash
git worktree add ../adapter-mini6 -b maint/mini6 mini6
# 在该 worktree 内执行；替换占位符为经过验证的功能提交。
git cherry-pick <provenance-feature-commit>
python -m pytest -q
git tag mini6-provenance.1
python scripts/package_agent.py
```

开发包允许包含未提交修改，会明确记录 `dirty=true`。用于成绩对比的正式包应在提交完成、创建 tag 后打包，并确认 `dirty=false`。结果存入 `results/<tag>/<smoke|lite|practice>/<bench>/<时间戳>__<原包名>/`；变体之间同时比较 commit、源码指纹和实际运行参数。

## 包内版本证据

`python scripts/package_agent.py` 在 ZIP 根目录生成 `build_info.json`，包含：

| 字段 | 含义 |
|---|---|
| `commit`、`tags`、`branch` | 打包时 Git HEAD、精确指向 HEAD 的 tag，以及分支名；detached checkout 的分支为 null |
| `dirty` | 打包白名单范围内是否有未提交修改或未跟踪文件；无 Git 证据时为 null |
| `source_sha256` | 文件路径与每个文件内容 SHA-256 组成的排序清单的指纹 |
| `files` | ZIP 所含源码、模板、测试和文档的逐文件 SHA-256；不包含版本清单自身 |
| `built_at` | UTC 打包时间 |

源码快照同时用于 ZIP 和指纹计算。`.env`、依赖目录、构建目录及 `results/` 不进入提交包；它们也不影响源码指纹。`README.md` 和测试属于打包范围，因此修改它们也会改变指纹。该记录用于版本追溯，不是对外部篡改的数字签名。

## 运行产物与识别顺序

CLI 在模板准备完成后、模型运行前写入 `.arc_adapter/build_info.json`，并输出 `event=build_info` 的单行 JSON。dry-run 也记录版本；模型调用中途失败时该文件仍保留。正常返回后，`run_summary.json` 含版本摘要。

运行时优先读取包内冻结的身份信息，并重新计算源码指纹。`matches_build=true` 表示实际文件与打包清单一致；为 false 时列出 `changed_files`，另记 `runtime_source_sha256`。直接从仓库运行时读取当前 checkout；既无版本清单也无本目录 `.git` 时记为 unversioned，不继承父目录其他项目的 Git 身份。

`.arc_adapter/build_info.json` 的 `run_configuration` 记录模型名、step/time 预算和 effort 环境变量覆盖值。`reasoning_effort_override=null` 表示未设置环境变量，空字符串表示显式省略参数；最终送给模型的配置仍以 trajectory 中的 `model_kwargs` 和 `model_init_start` 事件为准。

整理结果时，先读取 `.arc_adapter/build_info.json`，缺失时查 `run_summary.json` 和 stdout 中的版本事件。只有 `dirty=false` 且运行文件与构建清单一致时，才能按该 commit 的已提交源码归类；dirty 包同时保留 commit 基线和源码指纹。旧 run 没有这些字段时，仅记录会话标注或配置推断，不补造精确 commit。
