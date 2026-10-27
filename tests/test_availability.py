from pathlib import Path
from lupa.lua51 import LuaRuntime
R=Path(__file__).resolve().parents[1]/'optional/availability'
l=LuaRuntime(unpack_returned_tuples=True)
l.execute('''
frames={};now=0;sent=0;reset=0
function CreateFrame() local f={scripts={}}; function f:RegisterEvent() end;function f:SetScript(k,v) self.scripts[k]=v end;table.insert(frames,f);return f end
function GetTime() return now end
function SendChatMessage() sent=sent+1 end
function GetNumFactions() return 0 end
pfQuest={questlog={},ResetAll=function() reset=reset+1 end}
pfQuest_history={};pfQuest_config={showlowlevel='1',showfestival='1'}
pfDB={quests={data={},loc={}}}
pfDatabase={SearchQuests=function() end,GetPlayerSkillCached=function(self,id) return self.rank or false end}
bit={band=function(a,b) local n,p=0,1;while a>0 and b>0 do if a%2==1 and b%2==1 then n=n+p end;a=math.floor(a/2);b=math.floor(b/2);p=p*2 end;return n end}
function fire(e,a,b) event=e;arg1=a;arg2=b; frames[1].scripts.OnEvent() end
function tick(t) now=t;frames[1].scripts.OnUpdate() end
''')
l.execute("pfQuestServerRules={quests={},pre={},groups={},chains={}};for _,id in ipairs({1178,1180,1181,1182}) do pfQuestServerRules.quests[id]={29,0,0,0,0,0,0,0,0,0,0,0} end;pfQuestServerRules.pre[1181]={1180};pfQuestServerRules.quests[1181][7]=1182")
l.execute('for id in pairs(pfQuestServerRules.quests) do pfDB.quests.data[id]={lvl=37};pfDB.quests.loc[id]={T="test"} end')
l.execute((R/'availability-fixes.lua').read_text('utf8'))
l.execute('''
function clear() pfQuest_history={};pfQuest.questlog={};pfDatabase.rank=nil end
function show(id,level,class,race) return pfDatabase:QuestFilter(id,level or 40,class or 1,race or 1) and true or false end
clear();assert(not show(1181));pfQuest.questlog[1180]={};assert(not show(1181))
pfQuest.questlog={};pfQuest_history[1180]={0,0};assert(show(1181));assert(not show(1181,28))
pfQuest.questlog[1182]={};assert(not show(1181));clear()
local r=pfQuestServerRules
for i=100001,100007 do r.quests[i]={1,0,0,0,0,0,0,0,0,0,0,0};pfDB.quests.data[i]={lvl=37};pfDB.quests.loc[i]={T='test'} end
r.pre[100003]={100001,100002};assert(not show(100003));pfQuest_history[100002]={};assert(show(100003));clear()
r.pre[100003]={-100001};pfQuest_history[100001]={};assert(not show(100003));pfQuest.questlog[100001]={};assert(show(100003));clear()
r.quests[100001][6]=-9;r.quests[100002][6]=-9;r.groups[-9]={100001,100002};r.pre[100003]={100001}
pfQuest_history[100001]={};assert(not show(100003));pfQuest_history[100002]={};assert(show(100003));clear()
r.pre[100003]={-100001};pfQuest.questlog[100001]={};assert(not show(100003));pfQuest.questlog[100002]={};assert(show(100003));clear()
r.quests[100004][6]=9;r.groups[9]={100004,100005};pfQuest.questlog[100005]={};assert(not show(100004));clear();pfQuest_history[100005]={};assert(not show(100004));clear();assert(show(100004))
r.chains[100006]={100005};pfQuest.questlog[100005]={};assert(not show(100006));clear();assert(show(100006))
local q=r.quests[100007];q[2]=2;assert(not show(100007));assert(show(100007,40,2));q[2]=0;q[3]=2;assert(not show(100007));assert(show(100007,40,1,2));q[3]=0
q[4]=164;q[5]=100;assert(not show(100007));pfDatabase.rank=99;assert(not show(100007));pfDatabase.rank=100;assert(show(100007));q[4]=0;q[5]=0
q[9]=72;q[10]=3000;pfDatabase.serverReputation={[72]=2999};assert(not show(100007));pfDatabase.serverReputation[72]=3000;assert(show(100007));q[11]=72;q[12]=6000;pfDatabase.serverReputation[72]=6000;assert(not show(100007))
assert(not show(999999));clear()
-- Snapshot replaces inferred history, not expands prerequisite links.
pfQuest_history[1180]={};pfDatabase:QueryServer();assert(sent==1);pfDatabase:QueryServer();assert(sent==1)
fire('CHAT_MSG_ADDON','WRONG','1180');tick(1);assert(pfQuest_history[1180])
fire('CHAT_MSG_ADDON','TWQUEST','1178 ');tick(2);assert(pfQuest_history[1180]);tick(3)
assert(pfQuest_history[1178] and not pfQuest_history[1180]);assert(not show(1181));assert(reset==1)
-- Timeout preserves prior history; valid empty response really clears.
pfDatabase:QueryServer();tick(19);assert(pfQuest_history[1178]);assert(reset==1)
pfDatabase:QueryServer();fire('CHAT_MSG_ADDON','TWQUEST','');tick(22);assert(not next(pfQuest_history));assert(reset==2)
-- Multipart replies are merged and the quiet timer restarts.
pfDatabase:QueryServer();fire('CHAT_MSG_ADDON','TWQUEST','1178 ');tick(23);fire('CHAT_MSG_ADDON','TWQUEST','1180 ');tick(24);assert(reset==2);tick(25);assert(pfQuest_history[1180]);assert(show(1181))
fire('UPDATE_FACTION');tick(27);assert(pfQuest.updateQuestGivers)
''')
print('PASS: Lua 5.1 regression assertions: live quest 1181, chains, groups, active/rewarded, level, class/race, skills, reputation boundaries, snapshot timeout/empty/multipart, refresh')
# Compile every staged Lua file too.
for p in R.glob('*.lua'):l.eval('function(s) assert(loadstring(s)) end')(p.read_text('utf8'))

# Without a server adapter, keep the original filtering untouched.
l2=LuaRuntime();l2.execute("pfDatabase={QuestFilter=function() return 'original' end};function CreateFrame() return {RegisterEvent=function() end,SetScript=function() end} end")
l2.execute((R/'availability-fixes.lua').read_text('utf8'));assert l2.eval("pfDatabase:QuestFilter()")=='original'
print('PASS: public module leaves stock filtering unchanged without an adapter')
