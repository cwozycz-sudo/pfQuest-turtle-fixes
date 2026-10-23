# pfQuest Turtle Objective Fixes

非官方 TurtleWoW 任务目标修复整合包 / Unofficial objective repair bundle.

提供可直接安装的 **pfQuest + pfQuest-turtle 完整包**，以及已有用户使用的补丁包。原作者、维护者和许可证见 [NOTICE.md](NOTICE.md)。本项目不是官方 TurtleWoW 或 pfQuest 发布。

## 下载与安装（普通玩家）

前往 [Releases](https://github.com/cwozycz-sudo/pfQuest-turtle-fixes/releases/latest)，下载名称以 `-full.zip` 结尾的文件。

1. 完全退出游戏，备份原有 `pfQuest` 和 `pfQuest-turtle` 插件目录。
2. 将压缩包内的 `pfQuest`、`pfQuest-turtle` 两个目录放入游戏的 `Interface/AddOns`，替换对应旧目录。
3. 保留原来的 `WTF` 设置目录。在角色选择界面的插件列表启用这两个插件。
4. 重新启动客户端。新增 Lua 文件需要客户端重新读取插件文件列表。

无需修改或重启游戏服务器。完整包不要求安装 Python。

如果从 GitHub 的 Code → Download ZIP 下载源码，插件在 `AddOns/` 下；推荐普通玩家使用 Releases 中已整理好的完整包。

## 修复内容

部分 Turtle 扩展条目整体替换主库记录时遗漏了任务目标关联，可能出现任务已收录、地图却没有目标提示的情况。本项目针对这类数据遗漏，对 **685 条经过筛选的记录**恢复公开上游主库已有的目标表，改善任务目标的地图展示。

修复按任务数据和保护条件筛选；覆盖记录见 [upstream-provenance.json](upstream-provenance.json) 中的 `questIds`，具体任务用例保留在回归测试里。

覆盖层在 Turtle 原有 `overwrites.lua` 之后、`patchtable.lua` 合并之前运行。只有条目仍然缺少目标表，且整条原始元数据与本版预期完全一致时才应用；已有目标、已删除条目以及后续修改过的元数据都会跳过。不会修改任务名称、已有中文文本、人物技能、服务器任务机制或玩家任务历史。

## 兼容范围与限制

- 面向 1.12.1 / Interface 11200 的 Turtle-compatible 客户端，含上游语言数据及简体中文。
- 内含 pfQuest 8.0.0 后续源码提交和 Turtle 1.18.1 数据，精确版本见 [upstream-provenance.json](upstream-provenance.json)。不包含 TBC / Wrath 专用运行文件。
- 685 是恢复目标表的记录数，**不是“全部任务百分百精确定位”的承诺**。目标关联存在也可能没有地图可投影的坐标；召唤、对话、活动、玩家对战和部分副本目标仍依赖任务说明。
- 数据筛选曾在一套兼容服务器任务定义上交叉核对，但未在官方 TurtleWoW 全部任务、语言和活动中实机验证。
- 公开包只使用公开上游代码和目标数据；不包含任何自建服务器特有任务、数据库导出、账号资料或游戏安装文件。
- 已有自定义插件修改的玩家请使用补丁安装方式，并先备份。上游整体覆盖本包可能移除覆盖层的加载行。

## 补丁安装（已有插件的玩家）

下载 `-patch.zip`，解压后运行：

```text
python install_patch.py --addons "你的游戏目录/Interface/AddOns"
python install_patch.py --addons "你的游戏目录/Interface/AddOns" --apply
```

第一行仅检查，第二行安装并备份旧 TOC。安装器保留现有 TOC 内容，只在 `patchtable.lua` 前加入 `objective-fixes.lua`；不覆盖整套插件。修改过的任务条目仍会由运行时校验跳过。

也可以将补丁内 `pfQuest-turtle/objective-fixes.lua` 复制到已安装的同名插件目录，并在 `pfQuest-turtle.toc` 的 `patchtable.lua` 前单独添加一行 `objective-fixes.lua`，然后完全退出并重开客户端。

## 运行诊断

游戏内输入以下宏可查看本次加载应用/跳过的记录数：

```lua
/run local d=pfQuestTurtleObjectiveFixes;if d then DEFAULT_CHAT_FRAME:AddMessage("Objective fixes "..d.version..": "..d.applied.." applied, "..d.skipped.." skipped") end
```

## 源码验证与打包

```text
python -m pip install -r requirements-dev.txt
python -m unittest discover -s tests -v
python tools/build_release.py
```

测试覆盖真实上游合并逻辑、685 条目标表、代表性任务回归、已有目标保护、元数据变化保护、删除记录保护、重复加载和完整安装文件引用。测试使用 Lua 5.1 主机模拟；不替代所有 1.12.1 客户端的实机测试。

问题反馈请提供任务 ID、任务阶段、客户端语言及插件版本。请勿上传账号密码、完整 WTF、私人聊天或数据库备份。

## English

An unofficial ready-to-install pfQuest + pfQuest-turtle bundle, with a conservative overlay restoring 685 independently checked whole-objective omissions using **only public upstream objective data**. Runtime guards skip existing objectives, deletions and unexpected metadata. The repair scope is data-driven; the full record list is available in the source manifest.

Download the `-full.zip` release, close the client, back up the two addon folders, replace them inside `Interface/AddOns`, enable both addons, then restart the client. No server change is required. The `-patch.zip` supports existing installations without replacing their TOC wholesale.

This is not an official TurtleWoW release, not a claim of complete quest coverage, and not a new license grant for game assets. Existing upstream MIT copyright and permission notices are retained. See NOTICE.md and the pinned source manifest.
