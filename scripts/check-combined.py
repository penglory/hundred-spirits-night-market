from pathlib import Path
from pypdf import PdfReader
R=Path(__file__).resolve().parents[1]/'output/pdf'
allpdf=PdfReader(R/'全套A4印制合集.pdf')
assert len(allpdf.pages)==164
def payload(p):
    c=p.get_contents()
    return c.get_data() if c else b''
pos=0
for name in ['规则手册.pdf','完整内容图鉴.pdf','全套卡牌_双面印制.pdf','七种灵钱_双面印制.pdf']:
    if pos%2:
        assert not payload(allpdf.pages[pos]);pos+=1
    for p in PdfReader(R/name).pages:
        assert payload(p)==payload(allpdf.pages[pos]),(name,pos)
        pos+=1
for name in ['夜市地图_A4六页拼接.pdf','辅助组件_裁切印制.pdf']:
    for p in PdfReader(R/name).pages:
        assert payload(p)==payload(allpdf.pages[pos]),(name,pos)
        assert not payload(allpdf.pages[pos+1])
        pos+=2
assert pos==164
print('PASS: all combined page streams match source pages; all padding pages blank; 164 pages.')
