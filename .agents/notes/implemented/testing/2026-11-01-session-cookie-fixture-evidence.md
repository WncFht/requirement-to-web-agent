# Agent Note: 场景冻结前核对会话 Cookie 名称

Status: implemented

新正确性运行的精确标签与读取故障探针通过，但模型把已存在会话的 Cookie 设为 session，实际后端实现读取 session_id。接口描述只说“session cookie”，没有给出名字；有效会话场景因此错误地冻结，前端无法合法修复。

E2E 生成上下文现在给出已通过后端阶段的实际源码和其中可识别的字面量 Cookie producer 名称。冻结前对英文标题明确声称 valid/existing/seeded session 的测试检查其直接字面量 addCookies 数组：若没有任何名字匹配后端 producer 则拒绝。原有负向未知会话测试不因此被限制，原冻结失败套件不改写。ARC_LEGACY_E2E_COOKIE_NAMES=1 恢复此前准入；源码证据仍是只读参考。

这不是通用 TypeScript 数据流分析：动态 helper、变量名和不匹配的标题形式可能无法检查；无可识别 producer 时不猜测，仍由实际 E2E 和外部验收兜底。多 Cookie 情况只证明存在匹配，不证明所有设置都正确。单元测试覆盖真实命名错误、正确名、负向场景、字面量/常量与回退；完整结果归同一正确性实验。
