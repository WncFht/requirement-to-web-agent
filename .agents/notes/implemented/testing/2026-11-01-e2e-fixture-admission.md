# Agent Note: E2E fixture 准入检查

Status: implemented

E2E 生成指令已经禁止 UI fixture 注入，但旧 test gate 只检查类型、loopback URL 和运行结果，因此 `window.__ARC_UI_FIXTURE__` 注入造成的断言失败仍可能被接受为有效 RED。`work/optg2-1101` 的冻结注册套件使用 `page.evaluate` 设置窗口变量后 reload，变量不会跨 reload 保留；实现 agent 无法通过正确业务代码修复这个测试设置。

现在在冻结测试之前拒绝 E2E 源码中的保留标识符 `__ARC_UI_FIXTURE__`。该标识符只供编译器生成的 UI 存在性测试使用，后者仍完整执行。原有 loopback URL 检查迁到同一准入函数，原先类型、行为 RED/GREEN、UI 回归和生产构建 gate 均保留。

这是标识符检查，不是完整 JavaScript 分析：注释中的同名引用也会拒绝，不宣称识别任意绕过写法。代价是对已有注入式 E2E 套件不兼容。`ARC_LEGACY_E2E_SOURCE_CHECK=1` 恢复此前 fixture 准入行为，仍保留原 URL 检查。

验证覆盖正常浏览器交互、实际失败套件拒绝、旧行为开关和 URL 检查不受开关影响。该修正没有改写原失败运行的冻结测试；原运行按负结果保留。新增准入规则尚未经过新的完整模型生成运行，不宣称它已经解决 Cookie 等其他生成缺陷。
