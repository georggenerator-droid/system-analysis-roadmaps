"""Offline check for repository Markdown links, anchors and module coverage."""
from pathlib import Path
from urllib.parse import unquote,urlsplit
import re,json,unicodedata

ROOT=Path(__file__).resolve().parents[1]

def slug(text):
    text=re.sub(r'<[^>]*>','',text).strip().lower()
    text=re.sub(r'[`*_]','',text)
    text=''.join(c for c in text if c.isalnum() or c in ' -_')
    return text.replace(' ','-')

def anchors(path):
    if path.suffix.lower()!='.md':return set()
    txt=path.read_text(encoding='utf-8')
    result=set(re.findall(r'<a\s+(?:id|name)="([^"]+)"',txt))
    result.update(slug(m) for m in re.findall(r'^#{1,6}\s+(.+)$',txt,re.M))
    return result

def check():
    errors=[];count=0
    for f in sorted(ROOT.rglob('*.md')):
        text=f.read_text(encoding='utf-8')
        text=re.sub(r'```[\s\S]*?```','',text)
        for target in re.findall(r'!?\[[^\]]*\]\(([^)]+)\)',text):
            if target.startswith(('https://','http://','mailto:')):continue
            count+=1;parsed=urlsplit(target);dest=(f.parent/unquote(parsed.path)).resolve() if parsed.path else f.resolve()
            try:dest.relative_to(ROOT)
            except ValueError:errors.append((str(f.relative_to(ROOT)),target,'outside repository'));continue
            if not dest.exists():errors.append((str(f.relative_to(ROOT)),target,'missing target'));continue
            if parsed.fragment and dest.suffix=='.md' and unquote(parsed.fragment) not in anchors(dest):errors.append((str(f.relative_to(ROOT)),target,'missing anchor'))
    ids=[]
    for folder,prefix,n in [('roadmaps/zero-to-junior/modules','J',19),('roadmaps/junior-to-middle/modules','M',15),('roadmaps/middle-plus','P',4)]:
        for f in (ROOT/folder).glob('*.md'):
            m=re.match(r'^# ([JMP]\d{2}) ',f.read_text())
            if m:ids.append(m.group(1))
        expected={f'{prefix}{i:02}' for i in (range(n) if prefix!='P' else range(1,n+1))}
        if not expected<=set(ids):errors.append((folder,'','missing module'))
    mapids=[n['id'] for route in json.loads((ROOT/'assets/source/roadmaps.json').read_text())['routes'] for phase in route['phases'] for n in phase['nodes']]
    if sorted(ids)!=sorted(mapids):errors.append(('assets/source/roadmaps.json','','map and pages differ'))
    if errors:
        for e in errors:print('ERROR',*e,sep=' | ')
        raise SystemExit(1)
    print(f'OK: {count} local links, {len(ids)} module pages, map coverage and anchors')

if __name__=='__main__':check()
