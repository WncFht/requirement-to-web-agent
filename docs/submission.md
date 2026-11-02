# 按版本打包、上传与本地运行

在独立源码仓库 `source/` 操作。`make` 默认只显示帮助；打包和静态校验不调用模型。真实生成与网站评测仍处于停止状态，下面的生成命令作为接口参考，须重新获得明确授权后执行。

## 选择源码与引擎

一个版本由 Git 提交与引擎共同确定。日常只维护 `main`；历史版本由固定标签保留，打包时读取 Git 对象，不必切换分支或另建 worktree。

| 选择               | REF                                 | ENGINE   | 适用范围与证据限制                                                                     |
| ------------------ | ----------------------------------- | -------- | -------------------------------------------------------------------------------------- |
| 当前集成版旧流水线 | `HEAD`                              | `legacy` | 默认选择；包含后续恢复、计时与工程修复，当前提交通过离线检查，未重新进行付费全流程验证 |
| 当前集成版单循环   | `HEAD`                              | `coding` | 包含单循环候选与后续整理；本地模拟检查不证明真实任务成功率或视觉质量                   |
| 封存单循环候选     | `coding-agent-candidate-2026-11-02` | `coding` | `65220fd`；最新封存候选，同期对照中断，不能称为已证明最优版本                          |
| 教师契约旧版       | `teacher-contracts-2026-11-01`      | `legacy` | `590dd8c`；教师原需求与契约检查点，后续工程修复不包含在该提交内                        |
| 早期验证旧版       | `optimized-verified-2026-11-01`     | `legacy` | `e910eed`；保留当时验证和输入条件，不能把历史结果移植为当前平台成绩                    |

`make versions` 列出这些引用的提交 SHA 与支持引擎。教师原始 `teacher-baseline` 的入口只解析参数，没有接通生成，不属于可直接提交运行的成品。较早 `bd700aa` 单循环运行存在参考图片缺失，保留历史证据，不列为推荐交付。实验条件与负结果见[结果摘要](results.md)。

## 生成上传包

先提交想打包的源码。打包只读取 `REF` 指向的已提交文件，未提交改动不会进入 ZIP：

```sh
make versions
make package-check ENGINE=legacy
make package-check ENGINE=coding
make package-check REF=coding-agent-candidate-2026-11-02 ENGINE=coding
make package-check REF=teacher-contracts-2026-11-01 ENGINE=legacy
make package-check REF=optimized-verified-2026-11-01 ENGINE=legacy
```

默认产物为 `dist/agent-<引擎>-<12位SHA>-v2.zip` 和同名 `.json` 清单；`dist/` 不入库。可用 `ZIP=../work/my-agent.zip` 指定位置。相同内容可重复执行；目标已存在且内容不同时拒绝覆盖，换新文件名即可。清单记录完整提交 SHA、引擎、ZIP 哈希及逐文件哈希，分享或上传前保留它。

包内源码、模板与排除规则见[打包范围](packaging.md)。旧标签保持当时布局，当前源码不再保留旧入口或行为的兼容分支。

`package-check` 校验清单、原源码哈希、入口布局和所有 Python 文件语法。它不安装依赖、不执行生成，也不证明完整平台运行通过。单循环包另有本地模拟服务集成，运行方式见[操作指南](development.md#诊断与独立验收)。

## 在 ARC-Bench 选择并上传

按课程 `project_zh.pdf` 的流程，由队长进入竞赛，选择 Python，上传上一步选定的一个 ZIP。提交名建议写为 `legacy-590dd8c` 或 `coding-65220fd`，填写该接口支持的 Base URL 与 API Key，网站不需要填写模型名；清单 JSON 留在本地用于核对，不作为第二份智能体上传。

网站把填写值注入 `OPENAI_BASE_URL` 与 `OPENAI_API_KEY`；主模型和视觉模型均应使用它们。选择包时核对文件名、清单中的完整 SHA 与引擎，不以“最新文件”代替明确版本选择。

上传后还需单独启动任务，运行会调用模型。恢复授权后先用单任务 Smoke Competition（部分页面名为 First Competition）检查流程，再选择正式的 ARC-Bench: Web Application。正式综合榜要求同一份提交完成全部六个任务；排行榜默认选最新提交，也可在竞赛提交栏手动选择希望上榜的版本。这里没有上传或启动任何网站任务；最终要求与截止时间以课程公告为准。

## 本地生成与启动网站

准备根 README 的 Python 依赖，并把 Node 22 加入 PATH。`make run` 从本地 `.env` 读取模型配置，环境变量优先；不会把 `.env` 打进 ZIP。它生成并运行所选提交的同一份上传包，而非当前未提交文件：

```sh
# 接口参考；真实模型生成目前禁止执行。
export PATH="$HOME/.local/share/mise/installs/node/22.23.2/bin:$PATH"
make run REF=HEAD ENGINE=legacy INPUT=input OUT=../work/manual-legacy-001
make run REF=coding-agent-candidate-2026-11-02 ENGINE=coding INPUT=input OUT=../work/manual-coding-001

# 对已有生成结果启动网站；默认 http://localhost:3000。
make serve OUT=../work/manual-legacy-001 PORT=3000
```

`make run` 每次要求全新的、位于源码与输入目录之外的 `OUT`，拒绝覆盖。相邻的 `<OUT>.run.json` 记录提交、引擎与 ZIP 哈希，失败产物也保留；临时解压的源码在退出时删除。生成完成后 `make serve` 通过应用自己的 `deploy.sh` 安装依赖、初始化数据库、构建并启动服务；`PORT` 控制应用端口，多实例使用不同端口。停止前台服务使用 Ctrl+C。

希望运行未提交代码或使用 legacy 可信续跑时，改用[操作指南](development.md#运行与配置)中的源码入口；不要把该运行混称为某个已提交 ZIP 的结果。Windows 无 make 时，使用 `scripts/package_agent.py`、`scripts/run_submission.py` 的同名参数；启动 `deploy.sh` 需要 Bash 环境。
