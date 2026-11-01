# Agent Note: 单选组必须实际包含其控件

Status: implemented

UI 存在性测试在每个可见 display fixture 中，要求 IR 声明的 radiogroup 能通过实际角色与精确标签定位到自身 test ID，并且从该组内按 radio 角色及精确选项标签能定位到对应输入。检查覆盖 IR 的后代控件，可保留额外布局包装，但不能把 role/test ID 仅挂在标签列而将单选项放在组外。

选择实际浏览器包含关系，是因为全新候选的 IR 将 Male/Female 放在 Gender 组内，页面却把组属性放在左侧标签上；现有单控件可见性、标签、类型、value 与 checked 均通过，老师组内定位失败。新检查补充该缺口，不修改老师测试或冻结断言，也不限制无关布局。Stage10 和后续 Stage12 提示都保留这一语义，最终回归仍执行新增检查。

ARC_LEGACY_RADIO_CONTAINMENT=1 回退新增断言及提示，已有 radio value/checked 与精确标签检查各由原开关控制。新增测试检查正确分组、额外布局层与回退，真实失败页面的隔离重放用于核对新 gate 确实拒绝错误；完整运行结果仅保存在 work。
