# Agent Note: 动作超时的 RED 反馈指明断言顺序

Status: implemented

测试生成仍须满足原有断言式 RED，服务器/浏览器/运行时错误与动作超时不被接纳。新增提示要求在每次 click/fill/check/selectOption/press 前先 await 同一 locator 的可见性及必要的 enabled 断言，使未实现 mount 处理器导致隐藏的控件先产生断言失败。测试工作流、数据库断言和后续真实动作保留，不能以修改只读注册表或提前实现事件来绕过测试生成。

选择明确修复提示和结构化 CheckFailure，是因为完整运行遇到一个缺失控件的 click 超时后，旧反馈把已包含 JSON output 的报告嵌入异常字符串，形成重复转义的大段文本，模型连续重写仍不能形成有效 RED。当前反馈保留原报告对象和失败分类，复用已有去重/ANSI 清理；只改变诊断与指令，不放宽 require_red 或通过条件。ARC_LEGACY_RED_GUIDANCE=1 同时恢复旧提示与字符串异常。

单元测试覆盖动作超时仍被拒绝、修复提示、原报告保留、断言 RED 继续接受、真实运行时错误拒绝及回退。失败运行、修复后重放和新生成只保存在 work 目录；无需更新交接材料。
