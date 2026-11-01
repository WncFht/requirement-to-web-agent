# Agent Note: 场景冻结前核对会话 Cookie 名称

Status: implemented

新正确性运行的精确标签与读取故障探针通过，但模型把已存在会话的 Cookie 设为 session，实际后端实现读取 session_id。接口描述只说“session cookie”，没有给出名字；有效会话场景因此错误地冻结，前端无法合法修复。

E2E 生成上下文现在给出已通过后端阶段的实际源码和其中可识别的字面量 Cookie producer 名称。冻结前对英文标题明确声称 valid/existing/seeded session 的测试检查其直接字面量 addCookies 数组：若没有任何名字匹配后端 producer 则拒绝。原有负向未知会话测试不因此被限制，原冻结失败套件不改写。ARC_LEGACY_E2E_COOKIE_NAMES=1 恢复此前准入；源码证据仍是只读参考。

这不是通用 TypeScript 数据流分析：动态 helper、变量名和不匹配的标题形式可能无法检查；无可识别 producer 时不猜测，仍由实际 E2E 和外部验收兜底。多 Cookie 情况只证明存在匹配，不证明所有设置都正确。单元测试覆盖真实命名错误、正确名、负向场景、字面量/常量与回退；完整结果归同一正确性实验。


[计时运行反例](../../../../docs/experiments/timing-validation.json) 进一步明确覆盖边界：后端输出裸凭据时，Chromium 保存为空名称 Cookie，实际注册/会话往返通过；静态命名 producer 提取为空，检查跳过，错误的 name=value fixture 仍被冻住。不能据此将后端判为浏览器不可用，或把“所有 Cookie 必须具名”新增为教师要求。后续需在冻结前核对真实浏览器保存和回传形式，当前规则尚未实现这一能力。
