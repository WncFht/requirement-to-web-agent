# 平台基准快照

官方任务材料保存在 Git，二进制档案由 Git LFS 保存。当前快照为 [2026-11-05 manifest](arc-bench/2026-11-05/manifest.json)，包含 Smoke、Lite、完整 Web 的十三个任务，以及公开测试、三种语言的 Blank 模板、演示智能体与公开客户端证据。

下载、校验、本地导出、公开测试收集和复刻边界统一见[平台材料与本地验证](../docs/platform.md)。快照不是一次运行成绩：Smoke 测试源码未公开，Stack Overflow 两个版本的公开收集数量与平台摘要各差一条，详细差异保留在 [collection audit](arc-bench/2026-11-05/audits/public-test-collection.json)。

```sh
git lfs install
git lfs pull --include="benchmarks/arc-bench/**"
.venv/bin/python scripts/platform_materials.py verify
.venv/bin/python scripts/platform_materials.py list
```

`arc-bench/` 的源文件排除自动格式化；维护工具、清单校验和本页仍参与仓库检查。生成应用、数据库、测试报告和模型日志继续放 gitignored 的 `work/`，不随快照提交。
