# 打包范围

`make package REF=<提交或标签> ENGINE=legacy|coding` 从指定 Git 提交读取已提交文件，生成 `dist/agent-<引擎>-<SHA>-v2.zip` 和同名 `.json` 哈希清单。未提交修改不会入包。

| 内容                    | legacy 包                               | coding 包 |
| ----------------------- | --------------------------------------- | --------- |
| `main.py`               | 固定引擎、补默认模型名的薄入口          | 同左      |
| `_agent_main.py`        | 该提交原始 `main.py`，字节保持不变      | 同左      |
| `requirements.txt`      | Python 依赖声明                         | 同左      |
| `infrastructure/`       | 共享工具、阶段实现、模板和提示词        | 同左      |
| `run_all.py`、`legacy/` | 包含；旧提交使用当时根目录的 00–12 脚本 | 不包含    |
| `coding_agent/`         | 不包含                                  | 包含      |

`infrastructure/` 整体保留共享依赖闭包，因此 coding 包也包含部分旧阶段工具。当前独立评估器位于 `scripts/`；历史提交可能在 `coding_agent/` 中保留其当时的评估模块。

不打包：`.env` 与 Key、`.git`、`.venv`、`node_modules`、生成网站、数据库、日志、输入示例、固定验收、测试、文档、维护技能及开发脚本。JSON 清单位于 ZIP 外，记录完整提交 SHA、引擎、ZIP 和逐文件哈希；网站只上传 ZIP。

平台从包根目录执行 `python main.py <需求目录> --output-dir <应用目录>`。连接地址和 Key 读取 `OPENAI_BASE_URL`、`OPENAI_API_KEY`，默认模型为 `deepseek-flash`；包装器不覆盖连接配置。`make package-check` 只验证结构、源码哈希与 Python 语法，完整生成仍需另行验证。

平台指定的输出目录可以预先包含模板。当前 `main.py` 在干净临时工作区生成，通过后把原目录内容移到独立备份，再交付到原输出目录根层；不会要求平台另选目录。失败保留原模板和独立失败工件，已有编译记录仍按续跑规则保护。该修复属于当前运行源码，重新打包旧标签不会自动得到它。

无真实 Key 的实际 ZIP 启动检查：

```sh
.venv/bin/python scripts/test_platform_startup.py dist/<当前版本>.zip --output ../work/new-startup-check
```

检查预置模板场景，并在模型客户端创建前强制阻断；通过仅证明初始化入口可用，不代表应用已完整生成。
