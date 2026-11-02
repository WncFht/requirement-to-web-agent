# 仓库维护

GitHub 建议使用队伍私有仓库 `requirement-to-web-agent`，上传本独立源码仓库的 Git 历史。课程材料和本地运行目录由外层课程仓库管理；源码已推送到该 GitHub 仓库，main 跟踪 origin/main。

## 分支与 worktree

只长期维护 `main`，它包含默认 upstream 与独立候选 coding。成员从 main 创建短期 `feat/*`、`fix/*`，检查和审阅后合入并删除，不另设长期 develop 或候选源码副本。

```sh
git switch -c feat/my-change
# 修改、离线验证、提交，再通过 PR 合回 main。
```

仅在确需同时开发时建立临时 worktree：

```sh
git worktree add -b feat/parallel-change ../work/parallel-change main
# 合入且工作区干净后：
git worktree remove ../work/parallel-change
git branch -d feat/parallel-change
```

上游来源和小修正由 upstream.json/upstream.patch 管理，更新时审阅差异并运行原测试。受测版本用固定标签标识，旧标签不移动。打包任意标签无需切换分支；当前代码不携带旧运行行为的回退开关。恢复历史环境时按提交和原协议新建 checkout，不拿旧 checkpoint 配新源码。

只推 main 与需要共享的标签，队友 clone 后依照根 README 安装并执行离线检查。共享不会撤销真实模型 API 停用约定。

## 检查与格式

`make check` 是统一离线入口；`make format` 应用 Ruff 与文档格式工具。版本来源为 `package.json`、锁文件和 Python 依赖声明。提交 hook 用 git-format-staged 格式化暂存内容并同步工作区，Markdownlint 修正若改变文件则重新暂存；CI 使用同一工具和检查入口。

上游快照、教师输入、扩展示例、固定验收与 coding 模板保持来源身份，不参与自动格式化。`.agents/` 保留从 agent-maintenance 引入的三个技能、参考和检查工具，当前项目负责 hook、CI 与适配配置；来源见 `.agents/maintenance-source.json`。

## 交付与本地产物

源码仓库保留运行代码、模板、提示词、固定测试、依赖声明、CI 和当前文档；历史计划与结束的实验工具通过固定标签查阅。上传 ZIP 与哈希清单位于 gitignored 的 `dist/`，范围见[打包说明](packaging.md)。

`.env`、真实 Key、依赖、数据库、原始模型请求响应与运行证据留在本机。清理运行目录前保存协议、源码、冻结测试、报告、截图及哈希；可以删除可重建依赖，但不改写失败结果或未知 usage。`scripts/archive_runs.py` 提供可核对的证据归档，不能代替完整数据库或原始图片备份。

源码恢复使用 Git 历史或 `scripts/export_source.py --output-dir <新归档目录>`。Git bundle 用于恢复源码，平台 ZIP 用于执行智能体；二者不互换。旧课程分享包与报告是固定版本，不因新 main 提交自动更新。
