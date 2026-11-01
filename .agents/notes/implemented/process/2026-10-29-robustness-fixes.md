# Agent Note: 首轮全流程跑通的鲁棒性修正

Status: implemented

## 实际选择

2026-10-29 首次完整运行时对教师参考实现做的一批修正（全部记录于 upstream.patch）：

- 模型超时 120s → 600s；`ARC_DISABLE_THINKING` 开关（deepseek 自动置 1）；
- E2E 生成指令与检查：原生 select 的候选项用 option 断言而非不存在的 placeholder 行为；
- E2E 禁止写死 localhost/127.0.0.1（运行器使用随机端口；Cookie 域不匹配会造成假失败）；
- E2E 生成参考集缩小（去掉重复的 UI 测试源码，UI 回归仍完整执行）；
- `ARC_REUSE_E2E_TESTS=1`：显式复用既有 E2E 测试（重新校验而非重新生成）；
- 新增 `main.py` 平台入口（run_all → db:init → build → deploy.sh）；04 号步骤补入 run_all。

## 理由

这些都是跑通第一轮时实际阻塞的问题：教师环境脚本按特定端口/域假设编写，
模型网络抖动在 120s 超时下频繁中断，04 号脚本在原始 run_all 中缺席导致义务校验被跳过。

## 代价与验证

- 修正均不改变业务场景与验收口径；50/50 编译器自测、13/13 后端、9/9 UI、7/7 E2E、
  9/9 独立验收、生产构建全部通过（2026-10-29 运行）。
- 已知缺口：首轮运行期间模型网络错误导致注册/登录三条 E2E 由人工按同风格补写
  （首页四条由模型生成）；`frontend_e2e.json` 如实记录 authorship，不宣称全部模型生成。
