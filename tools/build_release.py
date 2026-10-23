"""Build full and patch archives exclusively from this public repository."""
from pathlib import Path
import hashlib,json,zipfile

ROOT=Path(__file__).resolve().parents[1]
VERSION='1.0.0'


def archive(path, files):
    with zipfile.ZipFile(path,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for arc,source in sorted(files):
            info=zipfile.ZipInfo(arc,(2026,10,23,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED
            info.external_attr=0o100644 << 16;z.writestr(info,source.read_bytes())


def main():
    out=ROOT/'dist';out.mkdir(exist_ok=True)
    common=[(name,ROOT/name) for name in ['LICENSE','NOTICE.md','README.md','CHANGELOG.md','upstream-provenance.json']]
    full=common+[(p.relative_to(ROOT/'AddOns').as_posix(),p) for p in (ROOT/'AddOns').rglob('*') if p.is_file()]
    patch=common+[('pfQuest-turtle/objective-fixes.lua',ROOT/'AddOns/pfQuest-turtle/objective-fixes.lua'),('install_patch.py',ROOT/'tools/install_patch.py'),('licenses/pfQuest-MIT.txt',ROOT/'AddOns/pfQuest/LICENSE'),('licenses/pfQuest-turtle-MIT.txt',ROOT/'AddOns/pfQuest-turtle/LICENSE')]
    paths=[]
    for label,files in [('full',full),('patch',patch)]:
        path=out/('pfQuest-turtle-fixes-'+VERSION+'-'+label+'.zip');archive(path,files);paths.append(path)
    checks=''.join(hashlib.sha256(p.read_bytes()).hexdigest()+'  '+p.name+'\n' for p in paths)
    (out/'SHA256SUMS.txt').write_text(checks,encoding='utf-8')
    print(json.dumps({p.name:p.stat().st_size for p in paths}))


if __name__=='__main__':main()
