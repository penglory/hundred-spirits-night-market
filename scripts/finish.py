"""Validate printable assets, merge A4 sections with duplex-safe padding, package deliverables."""
from pathlib import Path
import json,hashlib,re,zipfile,sys
from PIL import Image
Image.MAX_IMAGE_PIXELS=200_000_000
from pypdf import PdfReader,PdfWriter
R=Path(__file__).resolve().parents[1]
mode=sys.argv[1] if len(sys.argv)>1 else 'check'
jobs=json.loads((R/'data/image-jobs.json').read_text(encoding='utf8'))
manifest=json.loads((R/'data/asset-manifest.json').read_text(encoding='utf8'))
assert manifest['generatedCount']==154
assert len(manifest['assets'])==252
for a in manifest['assets']:
    p=R/a['file']
    assert p.exists(),p
    with Image.open(p) as im:im.verify()
backs={}
for a in manifest['assets']:
    if a['face']=='back' and a['kind']!='banknote':backs.setdefault(a['backKey'],set()).add(a['sha256'])
assert len(backs)==13
assert all(len(v)==1 for v in backs.values())
for j in jobs:
    assert (R/'assets/final'/(j['id']+'.png')).exists(),j['id']
html=(R/'成品图鉴.html').read_text(encoding='utf8')
for link in re.findall(r'(?:href|src|data-front|data-back)="([^"]+)"',html):
    if link.startswith('output/'):assert (R/link).exists(),link
assert html.count('<figure ')==118
pdfdir=R/'output/pdf'
counts={p.name:len(PdfReader(p).pages) for p in pdfdir.glob('*.pdf')}
for n,k in {'规则手册.pdf':4,'完整内容图鉴.pdf':7,'全套卡牌_双面印制.pdf':32,'七种灵钱_双面印制.pdf':90,'夜市地图_420毫米.pdf':1,'夜市地图_A4六页拼接.pdf':6,'辅助组件_裁切印制.pdf':9}.items():assert counts[n]==k,(n,counts.get(n))
if mode!='merge':assert counts['全套A4印制合集.pdf']==164
sizes={}
for p in (R/'output/map').glob('*.png'):
    with Image.open(p) as im:sizes[p.name]=list(im.size)
report={'status':'PASS','uniqueGeneratedImages':154,'pairedAndTilePNGs':252,'galleryDesigns':118,'reusedCardBacks':13,'identicalBackCopies':True,'physicalCards':140,'physicalBanknotes':134,'pdfPages':counts,'mapPixels':sizes,'scope':'文件完整性、PNG可读性、同类背面一致性、图鉴链接和PDF页数；不替代视觉校对或实桌平衡测试。'}
(R/'data/final-check.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
if mode=='merge':
    w=PdfWriter();sections=[]
    for name in ['规则手册.pdf','完整内容图鉴.pdf','全套卡牌_双面印制.pdf','七种灵钱_双面印制.pdf']:
        if len(w.pages)%2:w.add_blank_page(width=595.2756,height=841.8898)
        start=len(w.pages)+1;w.append(str(pdfdir/name));sections.append((name,start,len(w.pages),'长边双面'))
    for name in ['夜市地图_A4六页拼接.pdf','辅助组件_裁切印制.pdf']:
        if len(w.pages)%2:w.add_blank_page(width=595.2756,height=841.8898)
        start=len(w.pages)+1
        for page in PdfReader(pdfdir/name).pages:
            w.add_page(page);w.add_blank_page(width=595.2756,height=841.8898)
        sections.append((name,start,len(w.pages),'已插空白背页'))
    w.add_metadata({'/Title':'百妖夜市 · 全套A4印制合集 · 长边双面 · 实际大小100%'})
    w.write(pdfdir/'全套A4印制合集.pdf');w.close()
    text='# 全套A4印制合集页码\n\n全册可按实际大小100%、长边双面打印。地图和辅助组件每页后插入空白背页。卡牌、纸币的正反面已匹配。不同材料请按下面页码分段打印。\n\n|部分|起页|止页|说明|\n|---|---:|---:|---|\n'
    text+='\n'.join('|'+n+'|'+str(a)+'|'+str(b)+'|'+t+'|' for n,a,b,t in sections)
    (R/'docs/合集页码.md').write_text(text+'\n',encoding='utf8')
if mode=='zip':
    target=R/'百妖夜市_完整印制包.zip'
    files=[R/'README.md',R/'成品图鉴.html']
    files+=list((R/'docs').glob('*.md'))
    files+=[R/'data'/n for n in ['game.json','asset-manifest.json','final-check.json','image-jobs.json','map-tiles.json','visual-review.json'] if (R/'data'/n).exists()]
    files+=[p for p in (R/'output').rglob('*') if p.is_file() and 'preview' not in p.parts]
    with zipfile.ZipFile(target,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=1,allowZip64=True) as z:
        for p in files:z.write(p,Path('百妖夜市')/p.relative_to(R))
    with zipfile.ZipFile(target) as z:
        assert z.testzip() is None
        assert len(z.namelist())==len(files)
    print(json.dumps({'zip':str(target),'files':len(files),'bytes':target.stat().st_size},ensure_ascii=False))
print(json.dumps(report,ensure_ascii=False))
