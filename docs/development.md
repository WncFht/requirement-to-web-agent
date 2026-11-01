# 操作指南：运行、续跑与度量

## 前提

- Python 3.12 venv 位于 `source/.venv`（含编译器依赖）
- Node 22（mise：`~/.local/share/mise/installs/node/22.23.2/bin`）。**构建产物必须用
  Node 22 运行**——系统 Node 24 的 ABI 与已编译的 better-sqlite3 不符（ERR_DLOPEN_FAILED）
- 模型 key 在 `.env`（gitignored）：`OPENAI_API_KEY` / `OPENAI_BASE_URL` / `MODEL`
- npm 镜像与 Playwright 下载 host 参见 `../tools/run-stage.sh`

## 全流程运行

```sh
.venv/bin/python main.py input -o ../work/<目录> [--resume]
# run_all 结束后自动：npm run db:init && npm run build，并生成 deploy.sh
```

- 单阶段：`.venv/bin/python -u 08_implement_backend_tdd.py --input input --output ../work/<目录>`
- 断点续跑：`--resume` 按哨兵产物跳过已完成阶段（08/12 要求 status GREEN）

## 环境变量

| 变量                          | 默认               | 作用                                                             |
| ----------------------------- | ------------------ | ---------------------------------------------------------------- |
| `ARC_LEGACY_E2E_SOURCE_CHECK` | 0                  | =1 回退新增的 E2E fixture 准入检查，既有 loopback URL 检查仍保留 |
| `ARC_LEGACY_REFERENCE_TESTS` | 0 | =1 不向前端设计/实现提供 input/tests 外部交互契约 |
| `ARC_LEGACY_RADIO_ASSERTIONS` | 0 | =1 回退 radio 存在性测试的选项值/checked 分离断言 |
| `ARC_LEGACY_API_SCOPE` | 0 | =1 回退 API 分解中叶子需求边界与 excess 修正提示 |
| `ARC_LEGACY_UI_PREDICATES` | 0 | =1 回退完整可见性谓词提示；UI IR 与 gate 不变 |
| `ARC_LEGACY_TEST_SANITY` | 0 | =1 回退后端恒假 header 断言的冻结前准入检查 |
| `ARC_FULL_FEEDBACK`           | 0                  | =1 恢复旧的字符串修复反馈与重复 output                           |
| `ARC_FULL_CONTEXT`            | 0                  | =1 恢复 Stage 12 未瘦身的创建调用上下文（A/B 对照）              |
| `ARC_UI_DESIGN_FRESH`         | 0                  | =1 强制 Stage 09 忽略 checkpoint 全新设计                        |
| `ARC_MODEL_TRANSPORT_RETRIES` | 2                  | 瞬态传输错误额外重试次数（退避 10/30/90s）                       |
| `ARC_REUSE_E2E_TESTS`         | 0                  | =1 复用既有 E2E 测试（重新校验，不重新生成）                     |
| `ARC_DISABLE_THINKING`        | 1（deepseek 自动） | 关闭 DeepSeek 思考模式                                           |

## 度量

- 逐阶段 token/耗时：聚合 `<输出目录>/model_calls.jsonl`（每条含 usage 与 elapsed_seconds）
- 阶段 wall time：`compiler.log` 中各 `[DONE] Completed in` 的最终值
- 正确性：`.arc/backend_tdd.json`、`.arc/ui_checks.json`、`.arc/frontend_e2e.json` 的 status 与 summary

## 启动生成的网站

```sh
cd <输出目录> && PORT=3309 npm start   # 或使用生成的 deploy.sh
```

注意：`.venv`、`node_modules` 迁移或重建后，需以 Node 22 执行
`npm rebuild better-sqlite3`（npm_config_nodedir 指向 mise Node 22 的安装目录）。

## 已知坑

- 生成测试禁止写死 localhost/127.0.0.1（运行器使用随机端口；Cookie 域不匹配会造成假失败）
- Quiz/提交类平台故障（502/断连）由 OPT-C 退避重试兜底；超过重试上限的阶段用 `--resume` 续跑
- 输出目录之间不复用 `.arc` 工件；对比实验必须使用全新输出目录

维护检查、版本与实验管理见 [maintenance.md](maintenance.md)。

## 老师原版稳定验收

默认 `input/` 已恢复教师 ZIP 原字节，哈希归 `input/source.json`；旧 pending 输入迁到 `examples/registration-pending/`，必须分开运行和记录。完整生成后额外运行 `scripts/accept_teacher.py`，命令及准入标准见 [固定验收](../acceptance/README.md)。现有阶段 GREEN 和独立验收/最终构建同时通过，才可记录为稳定运行。

`ARC_LEGACY_TEST_SANITY=1` 回退后端冻结前新增的恒假 header 断言检查；原有类型、RED/GREEN 和回归仍保留。该开关不影响固定的老师独立验收。
