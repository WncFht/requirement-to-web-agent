# 打包与提交

本页负责版本选择、ZIP 内容和网站上传。模型生成与平台评测仍停用；打包、语法与离线启动保护检查可执行。本地模型配置和生成接口见[开发指南](development.md#模型配置与运行)。

## 选择版本并打包

在源码仓库根目录执行：

```sh
make package-check REF=HEAD ENGINE=upstream
make package-check REF=HEAD ENGINE=coding
# 历史复核使用提交 SHA，不恢复旧标签或旧入口：
make package-check REF=a58ebed ENGINE=legacy
make package-check REF=65220fd ENGINE=coding
```

默认 upstream 固定教师 `13e78ef`；coding 是独立候选，不调用上游 Compiler。[架构](architecture.md)说明二者边界，[历史证据](results.md#历史证据)说明旧提交身份。**包只读取指定 Git 提交，未提交改动不进入包**；当前工作区调试与交付身份不能混用。

`make versions` 的实现仍引用已删除标签，目前不能完成列表，不作为版本选择入口；按上述 SHA 或 `git log --oneline` 选择。该限制不影响显式指定 REF 的打包路径。

产物为 `dist/agent-<引擎>-<SHA>-v3.zip` 和同名 JSON，`ZIP=work/my-agent.zip` 可指定新位置。相同内容可复用，目标内容不同时拒绝覆盖；保留清单供来源核验，网站只上传 ZIP。

## 包含和排除的内容

| 内容                                              | upstream 包                    | coding 包                     |
| ------------------------------------------------- | ------------------------------ | ----------------------------- |
| `main.py`、`_agent_main.py`                       | 固定引擎包装器、原平台入口     | 同左                          |
| `requirements.txt`、`runtime/`                    | 依赖声明、目录与进程适配       | 同左                          |
| `upstream.json`                                   | 教师来源记录                   | 同左                          |
| `upstream/main.py`、00–12 脚本、`infrastructure/` | 固定教师运行源码、模板和提示词 | 不包含                        |
| `coding_agent/`                                   | 不包含                         | 独立循环、检查与 support 模板 |

教师完整快照用于开发查阅；ZIP 排除其 input、tests、README、压力测试和配置示例。根 input/examples/acceptance、开发测试、文档、技能、`.env`、Key、`.git`、依赖、生成应用、数据库、日志和 `work/` 均不入包。

原平台入口字节保存在 `_agent_main.py`。包装器只固定引擎并补默认 MODEL，不覆盖平台注入的 OPENAI_BASE_URL、OPENAI_API_KEY。包外 JSON 记录完整提交及逐文件/ZIP 哈希。历史布局由打包器按提交识别，不自动继承当前平台修正，也不使当前入口支持 legacy。

## 上传前的验证边界

`make package-check` 只检查结构、源码哈希和 Python 语法。阻断模型的实际 ZIP 启动检查，以及 coding 假服务完整模拟，见[开发指南的诊断与验收](development.md#诊断与验收)。静态包检查不能证明生成成功或视觉达标。

平台可传入非空模板目录；完整成功后才备份并发布到目标根层。失败保留模板和工件，已有编译记录拒绝覆盖。两条路线各用自己的部署模板并读取 PORT，目录和进程边界见[架构](architecture.md#平台与评估边界)。

## 网站上传

按课程 `project_zh.pdf`，由队长进入竞赛，选择 Python，上传所选 ZIP；提交名写明引擎和 SHA，JSON 清单留在本地。填写支持该模型的 Base URL 和 API Key，网站不填写模型名；主模型与视觉模型使用平台注入的接口和 Key。

上传与启动是两步，启动才会生成并产生模型开销。只有重新明确授权后，才可用 Smoke Competition 检查并提交正式 Web Application；综合榜要求同一份提交完成全部六个任务。打包不等于网站成绩，最终要求与截止时间以课程公告为准。
