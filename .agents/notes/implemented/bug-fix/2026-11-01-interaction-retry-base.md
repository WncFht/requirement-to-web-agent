# Agent Note: 交互重试基于已接受状态

Status: implemented

交互提案失败后不会写入已接受状态。纠错上下文现在明确要求相对 existing_interactions 重新提交本需求所需的完整新记录，不能只提交针对 previous_response 的补丁。原版 v4 的注册提案先因复制首页会话读取而超额，随后只返回事件增量、引用尚未接受的触发器，最终返回空关联而失败。

校验器、三次预算、义务与记录合并语义不变；ARC_LEGACY_INTERACTION_RETRY=1 恢复旧纠错提示。该说明只作用于交互分解，不改变固定 P/Q 提案。单元测试覆盖失败后提示的基准；完整运行结果另行记录。

提示和纠错同时给出 source/event/action 字符串记录的 JSON 例子。reviewed 运行连续三次把 triggers 写成 UI-ID 到事件名映射，只有字段路径错误不足以纠正模型。例子不转换或接受旧式简写，既有形状校验仍拒绝它。
