-- Client-side hints only. Server remains authoritative for accepting quests.
local rules=pfQuestServerRules
if rules then
-- Keep the engine's precomputed race/class reject set in sync with this server.
for id,r in pairs(rules.quests) do
  local q=pfDB.quests.data[id]
  if q then
    q.min=r[1]
    q.class=r[2]~=0 and r[2] or nil
    q.race=r[3]~=0 and r[3] or nil
  end
end
if pfDatabase.BuildStaticRejectSet then pfDatabase:BuildStaticRejectSet() end
local abs=math.abs
local function done(id) return pfQuest_history and pfQuest_history[id] end
local function active(id) return pfQuest.questlog and pfQuest.questlog[id] end
local function occupied(id) return active(id) or done(id) end

function pfDatabase:ServerQuestPrerequisites(id)
  local required=rules.pre[id]
  if not required then return true end
  for _,signed in ipairs(required) do
    local prev=abs(signed)
    local matches=(signed>0 and done(prev)) or (signed<0 and active(prev))
    if matches then
      local group=rules.quests[prev][6]
      if group<0 then
        for _,other in ipairs(rules.groups[group]) do
          if signed>0 and not done(other) then return false end
          if signed<0 and not active(other) then return false end
        end
      end
      return true
    end
  end
  return false
end

function pfDatabase:QuestFilter(id,level,class,race)
  local r=rules.quests[id]
  -- Upstream may contain quests not installed on this server.
  if not r then return end
  local q=pfDB.quests.data[id]
  if not q or not pfDB.quests.loc[id] then return end
  if occupied(id) then return end
  if level<r[1] then return end
  if r[2]~=0 and bit.band(r[2],class)==0 then return end
  if r[3]~=0 and bit.band(r[3],race)==0 then return end
  if r[4]>0 and r[5]>0 then
    local rank=self:GetPlayerSkillCached(r[4])
    if not rank or rank<r[5] then return end
  end
  if not self:ServerQuestPrerequisites(id) then return end
  if r[6]>0 then
    for _,other in ipairs(rules.groups[r[6]]) do
      if other~=id and occupied(other) then return end
    end
  end
  if r[7]>0 and occupied(r[7]) then return end
  for _,prev in ipairs(rules.chains[id] or {}) do if active(prev) then return end end
  -- Reputation API differs across 1.12 extensions: only reject known values.
  local rep=self.serverReputation or {}
  if r[9]>0 and rep[r[9]] and rep[r[9]]<r[10] then return end
  if r[11]>0 and rep[r[11]] and rep[r[11]]>=r[12] then return end
  if q.lvl and q.lvl<level-4 and pfQuest_config.showlowlevel=="0" then return end
  if q.event and pfQuest_config.showfestival=="0" then return end
  return true
end

local scan=pfDatabase.SearchQuests
function pfDatabase:SearchQuests(meta,maps)
  self.serverReputation={}
  for i=1,GetNumFactions() do
    local name,_,_,_,_,value,_,_,header,_,_,_,_,id=GetFactionInfo(i)
    id=id or (pfQuestServerFactionNames and pfQuestServerFactionNames[name])
    if id and not header then self.serverReputation[id]=value end
  end
  return scan(self,meta,maps)
end

end -- optional server-specific rule adapter

-- Manual snapshot via /db query; automatic sync requires an explicit opt-in.
-- Never infer completion from prerequisite/close links. Never erase on timeout.
local sync=CreateFrame("Frame")
local pending,received,lastPacket,start,history
local function begin()
  if pending then return end
  pending=true;received=false;start=GetTime();lastPacket=start;history={}
  SendChatMessage(".queststatus","GUILD")
end
pfDatabase.QueryServer=function() begin() end
sync:RegisterEvent("PLAYER_ENTERING_WORLD")
sync:RegisterEvent("CHAT_MSG_ADDON")
sync:RegisterEvent("UPDATE_FACTION")
sync:RegisterEvent("SKILL_LINES_CHANGED")
sync:RegisterEvent("QUEST_LOG_UPDATE")
sync:RegisterEvent("QUEST_FINISHED")
local initial,refreshAt,resyncAt
sync:SetScript("OnEvent",function()
  if pfQuestAvailabilityAutoSync and event=="PLAYER_ENTERING_WORLD" and not initial then initial=GetTime()+3 end
  if pfQuestAvailabilityAutoSync and event=="QUEST_FINISHED" then resyncAt=GetTime()+3 end
  if event=="CHAT_MSG_ADDON" and pending and arg1=="TWQUEST" then
    received=true;lastPacket=GetTime()
    for id in string.gfind(arg2 or "","%d+") do
      id=tonumber(id)
      history[id]=(pfQuest_history and pfQuest_history[id]) or {0,0}
    end
  elseif event~="CHAT_MSG_ADDON" then
    refreshAt=GetTime()+1
  end
end)
sync:SetScript("OnUpdate",function()
  local now=GetTime()
  if initial and initial>0 and now>=initial then initial=0;begin() end
  if resyncAt and now>=resyncAt and not pending then resyncAt=nil;begin() end
  if pending and ((received and now-lastPacket>=2) or now-start>=15) then
    pending=false
    if received then
      pfQuest_history=history
      pfQuest_questcache={}
      pfQuest:ResetAll()
    end
    history=nil
  end
  if refreshAt and now>=refreshAt then
    refreshAt=nil
    pfQuest.updateQuestGivers=true
  end
end)
