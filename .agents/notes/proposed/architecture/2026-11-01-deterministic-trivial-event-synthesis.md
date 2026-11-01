# Agent Note: 平凡事件的确定性合成

Status: proposed

## 问题

Stage 11 的 Event P/Q 调用（20 次）与 Stage 12 的部分创建调用中，相当比例的事件是
同构的"输入框 → 更新一个变量"绑定：例如 `register-agreement-change` 的完整 handler 只有
`context.update({"form.agreement": Boolean(context.input.checked)})`。这类事件仍各消耗
一次模型调用（Stage 11 约 3K token/次、Stage 12 约 27.6K token/次）。

## 拟议选择

在 Stage 11 → 12 之间加一条确定性合成规则（lowering pass 语义）：当事件的设计记录
满足「动作集合仅含 update 且目标变量为输入型绑定的直接镜像、无 API 调用、无条件分支」
时，直接从 IR 模板合成 handler 文件，跳过模型调用。模式不匹配的事件仍走原模型路径。
验收：合成事件必须通过与模型事件完全相同的 gate（typecheck + 回归 + E2E）。

## 可观察的验收与风险

- 预期：Stage 11 调用数 20 → ~10，Stage 12 创建调用数相应减少；token 再降 10–15%。
- 风险：模式覆盖不全导致合成 handler 语义偏差——由既有 gate 兜底（失败自动回退
  模型路径重试，需要在实现里显式支持该回退）。
- 前置测量：统计最近一次运行中满足模式的事件占比。

Status 保持 proposed 直到完成一次带合成的全流程运行并确认 GREEN。
