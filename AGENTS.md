# AGENTS.md

需求到 Web 应用的智能体仓库，默认 upstream 教师路线，coding 为独立候选。

## 工作边界

- 用户禁止真实模型 API 调用。未经新的明确授权，不运行真实生成、重试或平台评测；仅做本地整理、静态检查及离线测试。
- `upstream/` 对应 `upstream.json` 固定的教师源码。尽量照搬；必要修正必须同时登记原/新哈希、原因和 `upstream.patch`，不得隐式批量格式化或改写提示词。检查会核对完整文件集。
- coding 的循环、冻结测试、预算与验收独立维护；`coding_agent/support/` 是从旧版本保留的检查/模板依赖，不与教师实现混装。
- 保留两条路线各自的 typecheck、后端、UI、E2E 与构建检查。失败不得改冻结断言转绿，平台适配层不得将上游失败报告当作成功。
- 根 `input/`、`acceptance/` 与 coding 模板保持原字节。上游模板来自固定快照，更新时按来源一起核对。不同版本、输入和引擎不能共用运行目录。
- 模型配置来自环境或 gitignored 的 `.env`，环境变量优先；凭据不得进入源码、文档、日志或 ZIP。
- 平台预置输出使用隔离生成、备份和交付；已有编译记录仍拒绝覆盖。当前 upstream/coding 都不承诺旧 legacy 的可信续跑。

## 开发与交付

长期维护 main，按需创建短期分支和 worktree，完成后移除。提交前执行：

```sh
make check
```

上游原测试在独立解释器中执行，清除真实模型凭据并阻断外网。模型模拟和浏览器重集成按开发指南显式启用。上游快照、教师材料、固定验收与模板排除自动格式化；其余 Python 用 Ruff，文档工具版本来自 package.json 与锁文件。

架构、开发、打包分别见 `docs/architecture.md`、`docs/development.md`、`docs/packaging.md`。长期理由归 `.agents/notes/`，沿用 agent-maintenance 规则。旧版 legacy 只通过固定标签恢复，不在当前代码中添加别名或重建旧驱动。
