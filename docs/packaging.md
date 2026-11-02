# 打包范围

`make package REF=<提交或标签> ENGINE=upstream|coding` 读取指定提交，生成 `dist/agent-<引擎>-<SHA>-v3.zip` 和同名 JSON。未提交改动不进入包。

| 内容                                          | upstream 包                        | coding 包                       |
| --------------------------------------------- | ---------------------------------- | ------------------------------- |
| main.py、_agent_main.py                       | 固定引擎的包装器、原平台入口       | 同左                            |
| requirements.txt、runtime/                    | 依赖声明和平台目录/进程适配        | 同左                            |
| upstream.json                                 | 固定教师版本与来源记录             | 同左                            |
| upstream/main.py、00–12 脚本、infrastructure/ | 包含固定上游运行源码、模板和提示词 | 不包含                          |
| coding_agent/                                 | 不包含                             | 包含单循环、检查与 support 模板 |

上游全仓快照供开发查阅；ZIP 只取其运行部分，不包含上游 input、tests、README、压力测试和配置示例。root input/examples/acceptance、开发测试、文档、维护技能、.env、Key、.git、依赖、生成应用、数据库及日志均不入包。

原平台 main.py 字节保存在 _agent_main.py。包装器只固定引擎并补默认模型名，不覆盖平台注入的 OPENAI_BASE_URL、OPENAI_API_KEY。JSON 清单位于 ZIP 外，记录完整提交和逐文件哈希；网站只上传一个 ZIP。

平台输出可以预置模板，适配层隔离生成、完整成功后备份交付，原目录本身保留。上游部署脚本随模板复制；coding 继续使用其原有部署约定，两者都读取 PORT。

`make package-check` 只检查结构、源码哈希和 Python 语法。`scripts/test_platform_startup.py <ZIP> --output <新目录>` 在模型客户端创建前停止，验证实际 ZIP 的初始化与预置目录保护；完整生成要另行验证。

历史标签仍可用 `ENGINE=legacy` 或 `ENGINE=coding` 打包当时的实现，打包器识别旧目录布局；这些包不自动得到新 upstream 路线或当前平台修复。当前源码不接受 legacy 别名。
