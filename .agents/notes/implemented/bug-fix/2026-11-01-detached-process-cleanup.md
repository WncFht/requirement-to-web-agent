# Agent Note: 中断时清理自建进程组的子服务

Status: implemented

POSIX 中断清理在停止所属子进程前，通过 ps 的 PID/PPID 表记录其后代，再向原进程组和记录的后代发送终止信号，等待后发送 KILL 兜底。Playwright 的 backend/Vite webServer 可能另建进程组，原 killpg 不能覆盖；只依赖普通同组后代测试曾漏掉该反例。

只记录并清理所属进程的实际后代，不按端口、全局 node 名称或工作区路径批量杀进程。Windows 保留 taskkill /T，缺少 ps 时保留原进程组清理；ARC_LEGACY_PROCESS_CLEANUP=1 回退原 POSIX 行为。此快照不能捕获快照后新建并立即被重新托管的所有守护进程，不构成系统级容器隔离。

真实进程测试让超时子进程启动新 session 的后台心跳服务，并同时启动无关同类心跳进程；要求所属后台服务停止、无关进程继续。原普通后代、超时、跨平台清理测试继续保留。该修复不改变模型输入或生成测试，只防止中断污染后续实验。
