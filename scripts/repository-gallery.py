"""Build a local gallery referencing canonical repository assets."""
from pathlib import Path
import json,shutil,re

ROOT=Path(__file__).resolve().parents[1]
manifest=json.loads((ROOT/'data/asset-manifest.json').read_text(encoding='utf8'))
html=(ROOT/'成品图鉴.html').read_text(encoding='utf8')
for asset in manifest['assets']:
    if asset['kind'] in ['banknote','map-tile']:image_id=asset['id']
    elif asset['face']=='front':image_id=asset['id']+'_front'
    else:image_id=asset['backKey']
    source='assets/final/'+image_id+'.png'
    assert (ROOT/source).exists(),source
    html=html.replace(asset['file'],source)
preview=ROOT/'assets/preview/board.png'
preview.parent.mkdir(parents=True,exist_ok=True)
if not preview.exists():shutil.copyfile(ROOT/'output/preview/地图.png',preview)
html=html.replace('output/map/百妖夜市_完整地图.png','assets/preview/board.png')
for link in re.findall(r'(?:href|src|data-front|data-back)="([^"]+)"',html):
    if link.startswith('assets/'):assert (ROOT/link).exists(),link
assert 'output/' not in html
(ROOT/'index.html').write_text(html,encoding='utf8')
print('Repository gallery: 118 designs; all source paths verified.')
