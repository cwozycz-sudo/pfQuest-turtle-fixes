from pathlib import Path
import copy,importlib.util,json,tempfile,unittest,re
from lupa.lua51 import LuaRuntime
ROOT=Path(__file__).resolve().parents[1]
ADDONS=ROOT/'AddOns'
OVERLAY=(ADDONS/'pfQuest-turtle/objective-fixes.lua').read_text(encoding='utf-8')
MANIFEST=json.loads((ROOT/'upstream-provenance.json').read_text())


def runtime():
    l=LuaRuntime(unpack_returned_tuples=True)
    l.execute("pfDB={quests={}}; function copy(x) if type(x)~='table' then return x end local r={} for k,v in pairs(x) do r[k]=copy(v) end return r end; function equal(a,b) if type(a)~=type(b) then return false end if type(a)~='table' then return a==b end for k,v in pairs(a) do if not equal(v,b[k]) then return false end end for k in pairs(b) do if a[k]==nil then return false end end return true end")
    for p in [ADDONS/'pfQuest/db/quests.lua',ADDONS/'pfQuest-turtle/db/quests-turtle.lua']:
        l.execute(p.read_text(encoding='utf-8-sig'))
    return l


class ObjectiveRepairs(unittest.TestCase):
    def test_all_repairs_and_real_merge(self):
        l=runtime();l.execute('before=copy(pfDB.quests["data-turtle"])');l.execute(OVERLAY)
        self.assertEqual(l.globals().pfQuestTurtleObjectiveFixes.applied,685)
        for qid in MANIFEST['patch']['questIds']:
            l.globals().qid=qid
            self.assertTrue(l.eval('equal(pfDB.quests["data-turtle"][qid].obj,pfDB.quests.data[qid].obj)'))
        l.execute("for id,old in pairs(before) do local now=pfDB.quests['data-turtle'][id] if type(old)=='table' then for k,v in pairs(old) do assert(equal(v,now[k]),'existing data changed') end else assert(old==now) end end")
        # Execute the actual upstream record merge function with the two quest tables.
        s=(ADDONS/'pfQuest-turtle/patchtable.lua').read_text()
        fn=s[s.index('local function patchtable'):s.index('-- Detect a typo')]
        l.execute(fn+'\npatchtable(pfDB.quests.data,pfDB.quests["data-turtle"])')
        for qid in [185,186,187,188,190,191,192,193,194,195,196,197]:
            self.assertIsNotNone(l.globals().pfDB.quests.data[qid].obj)

    def test_existing_objective_guard(self):
        l=runtime();l.execute('pfDB.quests["data-turtle"][194].obj={U={999}}');l.execute(OVERLAY)
        self.assertEqual(l.globals().pfDB.quests['data-turtle'][194].obj.U[1],999)
        self.assertEqual(l.globals().pfQuestTurtleObjectiveFixes.applied,684)

    def test_metadata_guard(self):
        l=runtime();l.execute('pfDB.quests["data-turtle"][194].min=999');l.execute(OVERLAY)
        self.assertIsNone(l.globals().pfDB.quests['data-turtle'][194].obj)

    def test_removed_record_guard(self):
        l=runtime();l.execute('pfDB.quests["data-turtle"][194]="_"');l.execute(OVERLAY)
        self.assertEqual(l.globals().pfDB.quests['data-turtle'][194],'_')

    def test_idempotent(self):
        l=runtime();l.execute(OVERLAY);l.execute('once=copy(pfDB.quests)');l.execute(OVERLAY)
        self.assertTrue(l.eval('equal(once,pfDB.quests)'))
        self.assertEqual(l.globals().pfQuestTurtleObjectiveFixes.applied,0)

    def test_missing_database_safe(self):
        l=LuaRuntime();l.execute('pfDB={}');l.execute(OVERLAY)
        self.assertEqual(l.globals().pfQuestTurtleObjectiveFixes.applied,0)


class Distribution(unittest.TestCase):
    def test_every_manifest_reference_exists(self):
        for addon in ['pfQuest','pfQuest-turtle']:
            root=ADDONS/addon
            for p in root.rglob('*'):
                if p.suffix=='.toc':
                    refs=[s.strip() for s in p.read_text(encoding='utf-8-sig').splitlines() if s.strip() and not s.lstrip().startswith('#')]
                elif p.suffix=='.xml':
                    refs=re.findall(r'file=["\']([^"\']+)["\']',p.read_text(encoding='utf-8-sig'))
                else:continue
                for ref in refs:
                    target=(p.parent/ref.replace('\\','/')).resolve()
                    self.assertTrue(target.is_relative_to(root.resolve()),str(p)+' -> '+ref)
                    self.assertTrue(target.is_file(),str(p)+' -> '+ref)
        toc=(ADDONS/'pfQuest-turtle/pfQuest-turtle.toc').read_text()
        self.assertLess(toc.index('overwrites.lua'),toc.index('objective-fixes.lua'))
        self.assertLess(toc.index('objective-fixes.lua'),toc.index('patchtable.lua'))

    def test_mit_notices_retained(self):
        for addon in ['pfQuest','pfQuest-turtle']:
            text=(ADDONS/addon/'LICENSE').read_text()
            self.assertIn('Eric Mauser (Shagu)',text)
            self.assertIn('Permission is hereby granted, free of charge',text)
        self.assertIn('Eric Mauser (Shagu)',(ROOT/'LICENSE').read_text())

    def test_patch_installer_preserves_content(self):
        spec=importlib.util.spec_from_file_location('installer',ROOT/'tools/install_patch.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
        with tempfile.TemporaryDirectory() as d:
            addons=Path(d);t=addons/'pfQuest-turtle';t.mkdir();(addons/'pfQuest').mkdir();(addons/'pfQuest/pfQuest.toc').write_text('fixture')
            toc=t/'pfQuest-turtle.toc';old=b'## Dependencies: pfQuest\noverwrite-custom.lua\npatchtable.lua\n';toc.write_bytes(old)
            source=ADDONS/'pfQuest-turtle/objective-fixes.lua'
            m.install(addons,source);self.assertEqual(toc.read_bytes(),old)
            m.install(addons,source,True);self.assertIn('overwrite-custom.lua',toc.read_text())
            self.assertEqual(len(list(t.glob('*.before-objective-fixes-*'))),1)
            once=toc.read_bytes();m.install(addons,source,True);self.assertEqual(toc.read_bytes(),once)
            self.assertEqual(len(list(t.glob('*.before-objective-fixes-*'))),1)


if __name__=='__main__':unittest.main()
