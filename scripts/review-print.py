from pathlib import Path
from reportlab.pdfgen import canvas
from PIL import Image
R=Path(__file__).resolve().parents[1]
P=R/'output/preview'
groups=[]
groups.append([P/f'图鉴-{i}.png' for i in [1,3,5,7]])
cards=[P/f'卡牌-{i:02}.png' for i in range(3,31)]
groups.extend(cards[i:i+8] for i in range(0,len(cards),8))
money=[P/f'灵钱-{i:02}.png' for i in [17,18,33,34,49,50,65,66,77,78,85,86,89,90]]
groups.extend(money[i:i+8] for i in range(0,len(money),8))
groups.append([P/f'拼接-{i}.png' for i in range(2,6)])
groups.append([P/f'组件-{i}.png' for i in range(2,7)])
c=canvas.Canvas(str(R/'tmp/print-review.pdf'),pagesize=(1200,1600))
for g in groups:
    cols=2 if len(g)<=4 else 4
    rows=2
    cw=1200/cols;ch=800
    for i,p in enumerate(g):
        x=(i%cols)*cw;y=1600-(i//cols+1)*ch
        c.setFont('Helvetica',12);c.drawString(x+8,y+10,p.stem.encode('ascii','replace').decode())
        c.drawImage(str(p),x+6,y+30,cw-12,ch-36,preserveAspectRatio=True,anchor='c')
    c.showPage()
c.save()
