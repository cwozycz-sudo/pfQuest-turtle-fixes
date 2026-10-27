# 可接任务判断与历史同步修复（可选）

2026-10-27：从本地修复中提取的 MIT 许可通用代码。尚未在官方 TurtleWoW 实机验证，不自动替换现有稳定安装包。

## 手动安装

1. 备份现有 pfQuest-turtle 目录。
2. 将 availability-fixes.lua 复制到该目录，在 pfQuest-turtle.toc 最后新增同名加载行，必须在 patchtable.lua 后面。
3. 完全退出并重开客户端。
4. 在支持 `.queststatus` / `TWQUEST` 协议的服务器，使用 `/db query` 手动同步。

没有响应时保留现有历史；有效空响应清空历史；分批返回合并后更新。只记录服务器返回的已交付任务，不递归推断前置或互斥任务也完成。同步期间2秒无新分包视为结束，15秒超时；此协议没有明确结束标识，极慢分包仍有限制。

## 可选服务器条件适配

默认没有条件数据，原有可接任务筛选不变，不会隐藏其他服务器的任务，也不自动发送查询。经维护者确认服务器支持协议后，可以在本文件之前设置 `pfQuestAvailabilityAutoSync=true` 开启登录与对话结束同步。

要启用条件判断，维护者必须在本文件之前提供 `pfQuestServerRules`：

- `quests[id]={minLevel,classMask,raceMask,skillId,skillRank,exclusiveGroup,nextChain,conditionId,minRepFaction,minRep,maxRepFaction,maxRep}`
- `pre[id]={signedPrerequisiteIds}`：正数要求已交付，负数要求正在做；包含显式前置和服务器 NextQuestId 反向关联。
- `groups[groupId]={questIds}`：负数组要求全部满足；正数组互斥。
- `chains[id]={previousChainIds}`。
- 可选 `pfQuestServerFactionNames[本地化阵营名称]=factionId`，用于不返回阵营 ID 的旧客户端。

**quests 必须是该服务器的完整任务目录**，未收录任务会隐藏。条件来自服务端，不要把一台服务器的导出直接用于另一台服务器。仓库不提供私人数据库导出、角色状态或连接信息。

已有本地条件修复的维护者必须审查覆盖顺序：本模块会替换 QuestFilter 和 QueryServer。未知声望不强行拒绝；特殊 conditionId、活动脚本、限时任务状态及重复任务等未完整实现，不宣称可接任务百分百准确。此模块只控制提示，不修改服务器任务规则。

## 验证

`python tests/test_availability.py`：Lua 5.1 模拟回归，使用合成规则数据，覆盖前置、互斥、职业种族技能、声望边界、超时、空结果、分包及默认不改筛选。

删除 TOC 中新增加载行并重启客户端即可停用；已同步的历史不会自动还原。
