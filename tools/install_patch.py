"""Install only the unofficial objective overlay; preserve existing addon content."""
from pathlib import Path
import argparse, datetime, json, os, re


def install(addons, source, apply=False):
    addons=Path(addons).resolve();target=(addons/'pfQuest-turtle').resolve()
    if not target.is_relative_to(addons):raise ValueError('Addon directory escapes the supplied AddOns path')
    toc=target/'pfQuest-turtle.toc'
    if not toc.is_file() or not (addons/'pfQuest/pfQuest.toc').is_file():
        raise ValueError('Both pfQuest and pfQuest-turtle must already be installed')
    if not toc.resolve().is_relative_to(addons):raise ValueError('TOC escapes supplied AddOns path')
    old=toc.read_bytes();text=old.decode('utf-8-sig');newline='\r\n' if b'\r\n' in old else '\n'
    if not re.search(r'^## Dependencies:.*pfQuest',text,re.M):raise ValueError('Unexpected Turtle addon manifest')
    entries=[s.strip() for s in text.splitlines()]
    new=old
    if 'objective-fixes.lua' not in entries:
        match=re.search(r'(?m)^patchtable\.lua\s*$',text)
        if not match:raise ValueError('Expected patchtable.lua merge step not found')
        text=text[:match.start()]+'objective-fixes.lua'+newline+text[match.start():]
        new=text.encode('utf-8')
    elif entries.index('objective-fixes.lua')>entries.index('patchtable.lua'):
        raise ValueError('Existing overlay load line occurs after merge; review load order')
    dest=target/'objective-fixes.lua';data=Path(source).read_bytes()
    if dest.exists() and dest.read_bytes()!=data:raise FileExistsError('Existing overlay differs; back it up and review before replacing')
    if dest.exists() and not dest.resolve().is_relative_to(addons):raise ValueError('Overlay escapes supplied AddOns path')
    result={'apply':apply,'tocWillChange':new!=old,'overlayWillBeAdded':not dest.exists()}
    if apply:
        if toc.read_bytes()!=old:raise RuntimeError('TOC changed concurrently')
        if new!=old:
            stamp=datetime.datetime.now().strftime('%Y%m%d-%H%M%S-%f')
            backup=target/('pfQuest-turtle.toc.before-objective-fixes-'+stamp);backup.write_bytes(old)
        if not dest.exists():
            with dest.open('xb') as f:f.write(data)
        if new!=old:
            temp=toc.with_name(toc.name+'.objective-fixes.tmp');temp.write_bytes(new);os.replace(temp,toc)
    return result


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--addons',required=True,help='Existing game Interface/AddOns directory')
    parser.add_argument('--apply',action='store_true',help='Apply patch and back up the existing TOC; default only checks')
    args=parser.parse_args();here=Path(__file__).resolve().parent
    sources=[here/'pfQuest-turtle/objective-fixes.lua',here.parent/'AddOns/pfQuest-turtle/objective-fixes.lua']
    source=next((p for p in sources if p.is_file()),None)
    if source is None:parser.error('Patch source file not found next to installer or in repository AddOns')
    print(json.dumps(install(args.addons,source,args.apply),ensure_ascii=False))
    if args.apply:print('Installation complete. Fully exit and restart the game client. No server change is required.')


if __name__=='__main__':main()
