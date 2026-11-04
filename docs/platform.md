# 平台材料与本地验证

本页用于在干净 clone 中取得固定的平台输入与公开测试、运行本地验证，并区分已经复刻的接口与未知的平台行为。受测应用和模型调用仍按[运行协议](runs.md)独立登记；下载或收集测试不构成应用通过。

## Git 中保存的材料

[2026-11-05 快照](../benchmarks/arc-bench/2026-11-05/manifest.json)包含官方 API 原始响应、任务 YAML、需求 Markdown、公开测试及 fixtures、原始需求 ZIP、Python/JavaScript/TypeScript Blank 起始包、公开 demo-agent 包和客户端静态资源。原始文件保持字节；清单记录来源 URL、大小、SHA-256 和已知缺口。登录 Cookie、用户资料、私有提交、模型凭据与运行日志不进入快照。

| 页面名称             | 实际 ID             | 任务 | 平台摘要用例数 | 本地公开用例收集                               |
| -------------------- | ------------------- | ---: | -------------: | ---------------------------------------------- |
| Smoke Competition    | `first-competition` |    1 |              5 | 官方不展示测试源码，接口404；只导出输入与3张图 |
| Lite Web Application | `arc-bench-lite`    |    6 |            182 | 181；Stack Overflow为27，摘要28                |
| 完整 Web Application | `arc-bench-web`     |    6 |            515 | 514；Stack Overflow为66，摘要67                |

十二个可见测试任务中十个数量一致，两个 Stack Overflow 差一条。使用 Node 22.23.2、Playwright 1.64.1 执行 `--list`，没有启动应用或执行业务测试；所有 API 返回的475个测试/辅助文件原样保留。差异不能靠新增断言、改摘要数字或减少预期修绿，原因仍需平台原评测器或额外官方材料确认。审计见[公开测试收集记录](../benchmarks/arc-bench/2026-11-05/audits/public-test-collection.json)。

三条赛道均不继承初始项目，`initial-projects-download` 返回409；Blank中仍有应用脚手架，两者含义不同。Lite/Web的ARC起始智能体接口返回404；公开demo-agent已另外下载，不声称它等价于缺失的ARC模板。`smoke` 是另一个不可用标识，不能用它的403判断 `first-competition`。

## 取得与校验

前提是 Git LFS、项目 Python 开发依赖。默认快照路径固定，`--snapshot <目录>` 可显式选择另一份同格式快照。

```sh
git lfs install
git lfs pull --include="benchmarks/arc-bench/**"
.venv/bin/python scripts/platform_materials.py verify
.venv/bin/python scripts/platform_materials.py list
```

缺少LFS对象时校验明确失败，不将指针文件当ZIP。完整校验核对文件集合、文件哈希、API/YAML一致性及公开断言字节；不证明上游内容本身正确。`verify --text-only` 仅供文本审阅，不能替代完整检查。CI checkout启用LFS，`make check`包含快照验证。

Git bundle保存提交和LFS指针，不包含LFS二进制对象。离线交接需要另保存对应LFS对象或原始档案，并重新执行校验；只有源码bundle不足以离线恢复平台数据。快照二进制不进入agent提交ZIP。

## 分开导出输入与验收

输出必须是全新目录；仓库内部只能落在被忽略的 `work/`。不会读取模型凭据、安装依赖或运行下载包。

```sh
.venv/bin/python scripts/platform_materials.py materialize arc-bench-lite--bookstack \
  --output work/platform-bookstack-input
.venv/bin/python scripts/platform_materials.py starter --language python \
  --output work/platform-blank-python
```

任务输出的 `input/` 来自官方需求ZIP，含YAML和全部参考图；`acceptance/` 含API公开断言和fixtures，模型生成时只传前者；需求Markdown与前置说明单独放 `docs/`。`materialization.json`保存快照身份、全部输出指纹与测试可用状态。Smoke不会伪造空的验收目录或代用本地十四条测试。

Blank保持上游语言入口、依赖清单、SDK、示例和应用模板。Python包入口读取需求目录，将生成应用写入 `--output-dir`；平台公开说明以应用根目录为工作目录，Web应用监听单端口，支持根 `deploy.sh`，模型服务由环境注入。详细契约保留在快照的原始Blank ZIP，导出后可阅读其README；不要通过执行示例来验证数据下载，也不要覆盖已有生成应用。

## 收集与执行公开测试

需要预先安装的Node与包含 `@playwright/test` 的独立 `node_modules`；实际执行还需Chromium和一个已启动、隔离数据库的本地应用。工具不自动下载依赖、不启动模型、不启动目标应用或创建业务种子数据。

```sh
# 仅加载测试、列出用例；不会启动浏览器执行业务。
.venv/bin/python scripts/platform_materials.py collect arc-bench-lite--bookstack \
  --output work/platform-bookstack-collect --dependencies /absolute/node_modules

# 对已有本地应用运行原样公开断言；会通过UI修改该应用的数据。
.venv/bin/python scripts/platform_materials.py test arc-bench-lite--bookstack \
  --output work/platform-bookstack-test --dependencies /absolute/node_modules \
  --base-url http://127.0.0.1:3000
```

URL限本机回环地址，拒绝账号口令与查询参数。每次导出新的验收副本，记录Node、Playwright、配置和输入/断言指纹，保留JSON报告、浏览器trace及失败信息；模型凭据不传给测试进程。采集数量不符、空套件、异常、skip、flaky和超时均不能报告完整通过。

本地配置只选择 `*.spec.ts`，单worker、零重试，30秒单测超时和失败trace；这是保守的本地配置，不是声称取得了平台原配置。Blank脚手架的宽泛匹配会把被其他测试导入的helper识别成测试文件，离线探针因此报错，不能机械照搬。平台实际可能另行配置，未知部分如实保留。收集报告的Playwright统计可能显示全部skipped，这是 `--list` 的表示，不是业务运行被跳过后通过。

只有实际执行且所有公开用例通过才报告 `LOCAL_PUBLIC_TESTS_GREEN`；它仍不是平台分数。Stack Overflow缺少摘要对应的用例时，当前工具会保留失败状态，不降低预期。

## 尚不能等价复刻的部分

| 层次            | 已有本地依据                                                         | 尚缺什么                                                                         |
| --------------- | -------------------------------------------------------------------- | -------------------------------------------------------------------------------- |
| 输入与图片      | 官方需求ZIP、API文本、哈希                                           | 未来版本变化；原平台输入目录是否附带额外运行期材料                               |
| 可见验收        | 475份测试及fixtures，可加载695条                                     | Smoke隐藏五条；两个Stack Overflow摘要差异；是否还有未公开注入                    |
| 应用脚手架与SDK | 三语言Blank、Python可视化SDK、示例、公开demo                         | 缺失的ARC起始包不由本地compiler代替                                              |
| 部署            | 官方入口、输出、单端口与deploy.sh契约                                | 原运行镜像、沙箱、系统依赖与资源上限的准确配置                                   |
| 数据与时钟      | YAML中的公共种子、case隔离身份、日期约定；部分测试自行安装浏览器时钟 | 服务端时钟注入、测试前数据准备和重置的完整实现；须由应用准备，不猜测数据库schema |
| 平台服务与计分  | 公开客户端、文档中的模型代理/可视化说明                              | 调度器、评测器、计费代理、评分与账号权限后端源码，公开OpenAPI未取得              |

因此当前交付是固定材料、可校验导出和公开验收的本地入口。进一步复刻应先取得缺失实现或明确契约；不靠绕过权限取得隐藏测试，不从公开客户端推测完整服务端，更不将本地采集或单个应用成功外推为平台等价。原有[独立十四条验收](results.md#当前验收标准)继续用于它自己的认证任务，与新平台任务分开。
