# AGENTS.md

本仓库把需求与参考图编译为 React/Express/SQLite 网站，包含默认 legacy 和候选 coding 两种引擎。

## 工作边界

- 用户已禁止真实模型 API 调用。未经新的明确授权，不运行生成、重试或平台评测；仅做本地整理、静态检查和离线测试。
- 保留 typecheck、后端契约、UI 存在性、Playwright E2E 与生产构建门禁。不得修改冻结测试或放松断言使生成物转绿。
- 教师原件 `input/`、固定验收 `acceptance/` 与应用模板保持字节身份；示例与运行结果分别记录。修改生成语义须更新决策和有意义的回归。
- 模型凭据只存 gitignored 的 `.env` 或环境变量，不进入代码、日志、文档或上传包。环境变量优先于本地配置。
- 每次运行使用独立工作区。平台首次传入的预置输出目录由统一入口隔离生成、成功后备份交付；已有编译记录仍禁止覆盖。不同源码、输入、引擎不能共用 checkpoint；失败证据保留。
- 当前代码不保留 `ARC_LEGACY_*` 旧行为开关和旧哨兵恢复。需要旧行为时使用固定 Git 标签；历史版本兼容仅限打包工具读取其原始布局。

## 开发与交付

团队维护唯一 main，功能分支与临时 worktree 按需创建，合入后删除。源码提交前执行：

```sh
make check
```

Python 使用 Ruff，文档与配置工具版本由 `package.json` 和锁文件确定。提交 hook 格式化暂存快照，CI 使用相同检查。真实浏览器集成需按[开发指南](docs/development.md)单独启用。

文档归属见 [docs/AGENTS.md](docs/AGENTS.md)，架构见 [docs/architecture.md](docs/architecture.md)，打包契约见 [docs/packaging.md](docs/packaging.md)。长期理由归 `.agents/notes/`，遵循已引入的 agent-maintenance 技能；旧实验与计划通过 Git 标签查阅，不在当前入口并行维护。
