# Agent Note: 前端保留外部交互测试契约

Status: implemented

前端上下文现在读取 input/tests 下的 TypeScript 文件，作为只读 reference_tests 传入设计与实现。老师测试通过精确可访问名称、角色和路由定位控件；仅保留 YAML 与图片会漏掉这些外部契约，导致自生成测试通过但老师无法操作。旧文件名中的需求编号不等于当前 YAML 编号，因此不按文件名裁掉其他需求的测试。

不复制、执行或修改这些文件来替代现有 gate，独立验收仍按冻结哈希检查原件。没有测试目录时上下文不变；ARC_LEGACY_REFERENCE_TESTS=1 恢复原先不读取外部测试的行为。代价是每个需求上下文增加少量原始测试文本；后续压缩需要保持定位语义和原件验收。

冻结前还拒绝已复现的角色冲突：老师显式要求 Gender radiogroup，不能以同名 select 取代。分组使用带 role 的 container，子 radio 通过静态 prop.value 与共享选择绑定表达。UI 存在性断言分别验证每个 radio 的选项值与 checked 状态；旧逻辑误把共享选择值当所有选项的 value。ARC_LEGACY_RADIO_ASSERTIONS=1 恢复旧断言生成；原失败运行及其冻结 select 测试不改写。该检查只识别直接字面量形式的外部 radiogroup 定位，不能证明所有可访问性契约已覆盖。

单元测试覆盖原文字节内容、旧编号分发与回退开关；完整生成和独立验收的结果归实验工件，不能据此预告通过。
