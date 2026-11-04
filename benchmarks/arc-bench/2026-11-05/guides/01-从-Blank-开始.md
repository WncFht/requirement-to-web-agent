## 从 Blank 开始

在任务或竞赛页面选择 **Download Template → Blank Template**，选择与上传时一致的语言。解压后修改入口文件，再把目录中的内容打包为 ZIP。Blank 是运行脚手架，不是自动完成需求的智能体；你需要实现读取需求、生成或修改应用的逻辑。

## 下载包包含什么

以 Python 为例：

~~~text
main.py                         智能体入口
requirements.txt                智能体的 Python 依赖
README.md                       输入、输出与运行说明
.env.example                    本地环境变量示例，不包含真实密钥
arcbench-agent-runtime/         本地可视化 SDK（由 requirements.txt 引用）
examples/model_calling.py        从环境变量调用模型
examples/minimal_agent.py        可替换 main.py 的最小 Web 示例
examples/sdk_and_skill_usage.py  状态、追溯、Git 与 skills 示例
skills/                         可选的工作流指引
template/                      对应任务类型的应用脚手架
~~~

智能体代码与应用代码是两个部分：ZIP 根目录的 main.py 是生成应用的程序；template/ 是可供它修改的应用起点。演化任务可能带有 evolution-templates/manifest.json 和各任务的基线 ZIP；系统执行时会再次注入权威基线，不能假设所有任务都从空应用开始。

## 上传格式与必需文件

| 语言 | ZIP 根目录的必需文件 | 依赖安装与启动 |
| --- | --- | --- |
| Python | main.py、requirements.txt | 安装 requirements.txt 后运行 python3 main.py |
| JavaScript | index.js、package.json | npm install 后运行 node index.js |
| TypeScript | index.ts、package.json | npm install 后使用本地 node_modules/.bin/tsx；package.json 需包含 tsx |

建议直接压缩文件本身，让入口位于 ZIP 根目录。保留依赖引用的本地 SDK 目录，别只上传 main.py。无需上传 node_modules、.venv、缓存、.git 或真实 .env。智能体依赖放在根目录依赖文件；生成应用的依赖放在应用自己的 package.json 等文件中。

~~~bash
# 在解压后的模板目录执行
zip -r agent.zip . -x 'agent.zip' '.env' '.env.local' 'node_modules/*' '.venv/*' '.git/*' '__pycache__/*'
~~~

## 输入：目录与命令行参数

系统以应用目录 /workspace/template 为工作目录，使用绝对路径启动上传的入口。Python 命令大致如下：

~~~bash
python3 /workspace/submission/main.py /tmp/arcbench/requirements-source --output-dir /workspace/template
~~~

第一个位置参数是**需求目录**，不是 JSON 字符串，也不是单个 YAML 文件。读取其中的 requirements.yaml；目录还可能包含 requirements.md、prerequisites.md、assets/、reference/ 等材料，按任务实际内容处理。优先使用命令行参数；相对路径依照当前工作目录解析。

--output-dir 指定应用输出根目录。任务类型通过 ARCBENCH_TASK_TYPE 传入（web、cli、android）；Blank 也接受 --type 供本地运行使用。不要依赖系统一定传入 --type。

requirements.yaml 的新版结构示例如下；实际字段和图片以所选任务提供的文件为准：

~~~yaml
id: ROOT
name: Example Web application
description:
  text: A small application.
scenarios: []
children:
  - id: REQ-1
    name: Welcome page
    description:
      text: Show a page with the heading "Welcome".
      image:
        - id: IMG-HOME
          reference: reference/homepage.png
          page: home
    scenarios:
      - id: SCN-REQ-1-01
        name: Open the home page
        steps:
          - id: STEP-REQ-1-01-01
            Given: The visitor is signed out.
            When: Open the home page /.
            Then: Display the heading Welcome.
            references:
              - \ref[image](IMG-HOME)
    children: []
~~~

id 标识需求节点，children 构成需求树，description.text 描述需要实现的行为；实际任务还可能包含其他字段。读取整个需求文件，不要只处理这个示例中的固定节点。

## 输出：可运行的应用文件

把最终应用写入 --output-dir，完成后以退出码 0 退出，异常时使用非零退出码。stdout / stderr 用于日志，没有必须输出的结果 JSON。仅打印模型回答不会产生可评测应用，也不要把结果放在 submission/ 或 output/template/ 下。

Web 任务保留模板中的 frontend/、backend/ 及其构建、启动约定：系统构建前端后启动后端，应用应监听 0.0.0.0:3000。若输出根目录有 deploy.sh，系统改为执行 bash deploy.sh；脚本应准备并启动应用，遵守注入的 HOST、PORT，保持服务运行。CLI 与 Android 请保留对应下载模板的构建、执行约定，不要套用 Web 启动脚本。

## 最小 Web 智能体示例

下载包中 examples/minimal_agent.py 给出了完整示例。将其复制为根目录 main.py 即可体验“读需求 → 写应用 → 退出 → 平台启动应用”。它使用标准库生成静态页面，不调用模型，也不实现全部业务需求；用途是理解运行契约。

~~~python
import argparse
import html
import os
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument("requirement_path")
parser.add_argument("--output-dir", required=True)
parser.add_argument("--type", default=os.getenv("ARCBENCH_TASK_TYPE", "web"))
args = parser.parse_args()

requirements = (Path(args.requirement_path) / "requirements.yaml").read_text(encoding="utf-8")
output = Path(args.output_dir)
output.mkdir(parents=True, exist_ok=True)
(output / "index.html").write_text(
    "<!doctype html><meta charset='utf-8'><h1>My first agent</h1><pre>"
    + html.escape(requirements) + "</pre>", encoding="utf-8",
)
(output / "deploy.sh").write_text(
    'set -eu\ncd "$(dirname "$0")"\nexec python3 -m http.server "${PORT:-3000}" --bind "${HOST:-0.0.0.0}"\n',
    encoding="utf-8",
)
print("Application files are ready", flush=True)
~~~

正式智能体可以将上述写文件逻辑替换为“读取需求 → 调用模型 → 修改文件 → 自行检查 → 退出”。SDK 可视化集成是可选的，不决定平台最终测试结果。

## 班级与队伍

从工作台首页进入“我的班级”，查看班级人数、队伍、可参加的 Track 和班级排行榜。班级名单按注册邮箱自动匹配，队伍与队长由课程名单分配，成员不能自行离队或变更组员。队长可以修改队伍名。

Smoke Competition 对所有登录用户开放，每人可独立上传、运行并选择上榜提交，按个人账号计分，不受班级或队长身份限制。其他班级竞赛仅队长可以上传智能体、启动运行、选择上榜提交；队员可查看共享提交和结果，并以队伍名上榜。班内榜由后端验证成员身份并筛选，不再依赖前端邮箱白名单。若尚未分配班级或队伍，请联系教师。

## Base URL、API Key 如何使用

提交时只需填写上游的 **Base URL 和 API Key**，不需要填写主模型或视觉模型名称。模型可在智能体代码中固定指定，也可根据任务选择多个模型，但都必须由同一个 Base URL 和 Key 支持。

| 提交栏 | 容器环境变量 | 启用内置计费代理后的实际值 |
| --- | --- | --- |
| Base URL | `OPENAI_BASE_URL` | 网站代理地址，例如 `https://arc-bench.com/api/model-proxy/v1` |
| API Key | `OPENAI_API_KEY` | 此次运行专用的临时 Key |

填写的上游地址和真实 Key 由后端保存；代理使用它们转发请求。**模型 API 必须通过容器注入的 `OPENAI_BASE_URL` 和 `OPENAI_API_KEY` 访问。只有经代理转发到提交时填写的 Base URL 的请求才能参与网站计费。** 不要写死其他地址或 Key，不要用本地 `.env` 覆盖注入值。模型名称可以写死在代码中，连接地址和凭证则必须读取环境变量。这里的约束是调用与计费约定，不代表容器会自动拦截任意外部网络请求。

代理按每次请求中的 `model`、返回的 `usage` 和网站统一定价累计用量与费用，不再限定提交时选定的模型。临时 Key 在运行结束后撤销。未启用代理时，注入值为解析后的直连地址和 Key，但这不属于内置代理的计费路径；评测额度使用平台为运行分配的凭证。

~~~python
import os
from openai import OpenAI

client = OpenAI(
    base_url=os.environ["OPENAI_BASE_URL"],
    api_key=os.environ["OPENAI_API_KEY"],
)
result = client.chat.completions.create(
    model="deepseek-v4-flash",  # 可固定在代码中，须由填写的接口和 Key 支持
    messages=[{"role": "user", "content": "请根据需求生成实现计划。"}],
)
print(result.choices[0].message.content)
~~~

示例使用 Chat Completions；只有上游支持时才使用 Responses、多模态或结构化输出。不要打印 Key 或把它写入应用文件。上游必须返回可识别的 usage，模型也需有匹配的定价，否则无法得到完整费用；缺少 usage 或匹配定价的请求会跳过费用统计，不会阻止其余请求累计。

## 环境变量与子进程

环境变量由平台在启动容器和智能体时注入，不需要智能体再读取网站表单或请求登录接口。

| 变量 | 含义 |
| --- | --- |
| OPENAI_BASE_URL、OPENAI_API_KEY | 模型连接地址与凭证；必须直接读取，勿覆盖 |
| MODEL、VISUAL_MODEL | 为兼容旧智能体保留的默认模型提示，可忽略，在代码中指定模型 |
| VISUAL_BASE_URL、VISUAL_API_KEY | 视觉调用的兼容别名，使用同一地址与凭证；模型由代码指定 |
| ARCBENCH_PROJECT_DIR、ARCBENCH_OUTPUT_DIR | 应用根目录，通常为 /workspace/template |
| ARCBENCH_SUBMISSION_DIR | 上传智能体目录，通常为 /workspace/submission |
| ARCBENCH_TASK_DIR、ARCBENCH_REQUIREMENT_DIR | 工作目录中的 requirements 相对目录；读取输入优先用位置参数 |
| ARCBENCH_TASK_TYPE | web、cli 或 android |
| ARCBENCH_ARC_DIR | 运行产物目录，通常为应用下的 .arc/ |
| ARCBENCH_RUNNER_EVENTS_PATH、ARCBENCH_TRACEABILITY_DIR | 可视化事件文件与追溯目录；SDK 自动使用 |

子进程默认继承环境变量。自行指定 env 时请保留原环境：

~~~python
import os
import subprocess

subprocess.run(["python3", "worker.py"], env={**os.environ, "MY_AGENT_MODE": "build"}, check=True)
~~~

.env.example 仅用于本地配置参考，Python 不会自动加载 .env 文件。可在终端 export 后执行示例；本地使用自己的上游凭证会直接调用上游，费用不会自动记到某次网站运行。

## 上传后的完整流程

1. 网站保存智能体包与模型配置；选择任务启动评测（竞赛的一个提交可运行多个任务）。
2. 系统排队、准备隔离工作目录，放入任务需求与应用起点；演化任务使用对应基线。
3. 系统安装智能体依赖，注入环境变量，以固定参数启动入口。
4. 智能体读取需求并修改输出目录；日志持续显示，可选 SDK 上报进度和 Git 提交。
5. 智能体退出后，系统启动或构建生成的应用，再执行平台测试；智能体标记“通过”不能替代平台测试。
6. 网站展示通过率、开销、测试报告和产物；竞赛分数由平台统一计分。

## 本地体验与重新打包

~~~bash
python3 -m pip install -r requirements.txt
# examples/requirements/ 包含一个本地输入示例
# 体验最小 Web 示例；正式提交时将此脚本复制为 main.py
python3 examples/minimal_agent.py ./examples/requirements --output-dir ./local-output
bash ./local-output/deploy.sh
~~~

原 Blank 的 main.py 会复制 template/ 脚手架，默认不调用模型。完善 run_agent 后再上传；演化任务或已有工作目录中请保留已有文件，只修改需要变更的部分，避免每次启动都覆盖用户或前序阶段的成果。
