# 选择版本与提交

在独立源码仓库操作，make 默认只显示帮助。当前模型生成和网站评测仍禁止执行，打包与离线检查可正常进行。

## 当前两条路线

| 选择               | 参数                     | 实际行为                                                              |
| ------------------ | ------------------------ | --------------------------------------------------------------------- |
| 固定教师路线，默认 | REF=HEAD ENGINE=upstream | 上游 13e78ef，保留其阶段、triggers、配置和模板，只有 2 个登记的小修正 |
| 独立候选           | REF=HEAD ENGINE=coding   | 保留单循环及原检查/模板支持，不调用上游 Compiler                      |

日常只维护 main；历史检查点由标签保留，打包无需切换分支：

```sh
make versions
make package-check ENGINE=upstream
make package-check ENGINE=coding
# 复核旧版时显式选择历史提交和引擎：
make package-check REF=pre-upstream-migration-2026-11-02 ENGINE=legacy
make package-check REF=coding-agent-candidate-2026-11-02 ENGINE=coding
```

`teacher-contracts-2026-11-01`、`optimized-verified-2026-11-01` 属于旧教师派生路线，不能称为当前上游。`65220fd` 是受测 coding 候选身份；当前 namespace 整理不冒充其原提交。结果与限制见[结果摘要](results.md)。

产物位于 dist，文件名包含引擎和提交 SHA；可用 ZIP=../work/my-agent.zip 指定新位置。只打包已提交文件，相同内容可复用，目标内容不同则拒绝覆盖。内容与排除范围见[打包说明](packaging.md)，保留同名 JSON 以核对来源。

## 网站上传

按课程 project_zh.pdf，由队长进入竞赛，选择 Python，上传所选 ZIP。提交名写明 upstream/coding 和 SHA，填写支持该模型的 Base URL 与 API Key，网站不填写模型名。JSON 清单留在本地。

平台注入 OPENAI_BASE_URL、OPENAI_API_KEY；主模型与视觉模型都应使用该接口和 Key。上传与启动任务是两步，启动才会生成并产生模型开销。恢复授权后可先用 Smoke Competition 检查，再提交正式 Web Application；综合榜要求同一份提交完成全部六个任务。

本地只是准备交付包，不代替网站成绩。课程最终要求和截止时间以公告为准。

## 本地运行

环境准备见[开发指南](development.md)。固定版本生成与启动：

```sh
# 真实模型生成目前禁止执行，仅作接口参考。
make run ENGINE=upstream OUT=../work/manual-upstream-001
make run ENGINE=coding OUT=../work/manual-coding-001
make serve OUT=../work/manual-upstream-001 PORT=3000
```

make run 运行对应已提交 ZIP，读取本地 .env，以环境变量为优先；要求新的 OUT，并在相邻 run.json 中记录身份。失败目录保留，临时智能体源码退出后删除。平台预置目标由统一入口处理，生成工作区与目标目录分开。

当前两个引擎都不支持旧 --resume。需要运行历史 legacy 时，恢复该标签的独立 checkout；不要给新入口增加旧行为别名，或跨源码复用 checkpoint。Windows 无 make 可直接使用 scripts/package_agent.py 与 scripts/run_submission.py；部署需要 Bash。
