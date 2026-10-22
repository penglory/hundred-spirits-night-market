"""Assemble complete generated tiles without overlaying any labels or artwork."""
from pathlib import Path
import json
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]
Image.MAX_IMAGE_PIXELS=200_000_000
tiles=json.loads((ROOT/'data/map-tiles.json').read_text(encoding='utf8'))
assert len(tiles)==16
assert {(t['col'],t['row']) for t in tiles}=={(x,y) for x in range(4) for y in range(4)}
board=Image.new('RGB',(5016,5016))
for tile in tiles:
    with Image.open(ROOT/'assets/final'/(tile['id']+'.png')) as im:
        assert im.size==(1254,1254)
        board.paste(im.convert('RGB'),(tile['col']*1254,tile['row']*1254))
out=ROOT/'output/map'
out.mkdir(parents=True,exist_ok=True)
board.save(out/'百妖夜市_完整地图.png')
board.resize((12000,12000),Image.Resampling.LANCZOS).save(out/'百妖夜市_12000像素放大版.png')
print('Assembled 5016px native map and 12000px enlarged export.')
