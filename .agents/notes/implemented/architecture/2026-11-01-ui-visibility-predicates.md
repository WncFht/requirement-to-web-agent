# Agent Note: UI 可见性表达完整业务条件

Status: implemented

teacher-original-1101-v2 的 UI IR 把登录入口只绑定 auth.loaded=true，因此 signedIn fixture 同时要求登录/注册链接可见；需求则明确登录后隐藏。实现模型遵守需求隐藏链接，固定 IR 存在性测试却失败。不是删一个测试能解决的问题。

UI 设计指令现在要求 prop.visible 表达完整业务谓词。现有 IR 一条条件只能比较一个变量，合取条件必须变为独立 boolean binding，由事件维护并在各 fixture 显式赋值。认证示例强调 signed-in 与 signed-out 的互斥可见性，图片不能覆盖文本业务条件。

没有放松任何 gate，也没有自动改写现有设计/测试；重新生成必须保留旧失败工件。ARC_LEGACY_UI_PREDICATES=1 恢复旧提示词，IR schema 不变。代价是依赖设计模型正确维护派生绑定，独立老师验收仍是最终判据；完整结果归运行记录。
