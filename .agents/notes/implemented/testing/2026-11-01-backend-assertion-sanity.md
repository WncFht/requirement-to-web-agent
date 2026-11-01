# Agent Note: 冻结前拒绝恒假 header 断言

Status: implemented

同类准入同时拒绝 JSON.stringify(identifier) 与非 JSON 字符串字面量的相等断言：v3 将未知凭据直接与完整响应序列化结果比较，即使响应字段都正确也不可能通过。合法 JSON 字面量和 includes(secret) 的否定检查仍允许；该规则不覆盖任意 JavaScript 表达式。

老师原版运行 teacher-original-1101 的后端注册测试使用 readSafe(headers) = JSON.stringify(headers ?? {})，却断言 !readSafe(result.headers)。缺省返回 "{}" 仍为真值，所以任何合法 API 都无法通过，18 轮实现修复没有意义。

现在仅在生成阶段冻结前拒绝这一已知、可证明矛盾的语法形式，要求测试直接检查 set-cookie 属性缺失；现有 RED/GREEN、契约和无写入语义不变。原失败运行不改测试、不转绿；后续使用新运行。ARC_LEGACY_TEST_SANITY=1 恢复旧准入行为。

检查范围是直接 return JSON.stringify(variable ?? {}) 的命名函数及 assert.ok(!helper(...))，不是通用静态分析。代价是同名/影子绑定等复杂写法也可能要求重写成明确断言。有效断言和回退开关有回归；新完整运行结果归实验报告，不能仅凭准入单测宣称业务完成。
