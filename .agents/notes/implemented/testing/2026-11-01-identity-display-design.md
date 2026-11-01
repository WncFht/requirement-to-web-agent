# Agent Note: 登录身份必须有可见的设计输出

Status: implemented

外部只读测试明确通过 getByText(account.username,{exact:true}) 检查登录态首页时，设计提案若在首页 fixture 中提供非空 username 标量绑定，却没有任何 text/heading 消费它，则在 Stage09 拒绝并反馈。静态 My account/My 12306 不能替代用户名。ARC_LEGACY_IDENTITY_DISPLAY=1 回退此检查，其他原校验保留。

这补充已复现反例：接口与处理器正确设置 display.username，设计中却只有 My 12306 静态文案，内部 UI/E2E 通过，固定验收的所有登录成功场景看不到准确身份。检查仅覆盖原测试的已识别表达式与非空 username 绑定 fixture，不声称验证全部自然语言要求；对象型身份绑定和其他表达形式仍依赖真实固定验收。保留原需求、测试与失败候选，不修改生成物伪造成功。

设计准入只检查显示节点存在，不推断 fixture 中派生布尔条件的真实运行值：成功样例通过事件计算 isSignedIn，即使 fixture 本身未设置派生标志也仍可在生产中正确显示。可见性与精确文本最终由真实外部验收决定，不能用未执行的自然语言派生表达式误拒正确设计。
