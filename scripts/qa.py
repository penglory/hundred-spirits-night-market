"""Inspection sheets: place whole original images without modifying faces."""
from pathlib import Path
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
import sys,json
root=Path(__file__).resolve().parents[1]
ids=sys.argv[1:]
if not ids:
    ids=[j['id'] for j in json.loads((root/'data/image-jobs.json').read_text(encoding='utf8')) if (root/'assets/final'/(j['id']+'.png')).exists()]
c=canvas.Canvas(str(root/'tmp/qa.pdf'),pagesize=A4)
w,h=A4
for k,id in enumerate(ids):
    col=k%2;row=(k//2)%2
    c.drawImage(str(root/'assets/final'/(id+'.png')),col*w/2+5,h-(row+1)*h/2+5,w/2-10,h/2-10,preserveAspectRatio=True,anchor='c')
    if k%4==3:c.showPage()
if len(ids)%4:c.showPage()
c.save()
