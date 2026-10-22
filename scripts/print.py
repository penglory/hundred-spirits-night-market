"""Impose complete generated images. Never add or replace text on game faces."""
import json, math, re
from pathlib import Path
from xml.sax.saxutils import escape
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer,Table,TableStyle,PageBreak,CondPageBreak
from reportlab.lib.styles import ParagraphStyle
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'output/pdf'
OUT.mkdir(parents=True,exist_ok=True)
G=json.loads((ROOT/'data/game.json').read_text(encoding='utf8'))
J=json.loads((ROOT/'data/image-jobs.json').read_text(encoding='utf8'))
pdfmetrics.registerFont(TTFont('YH','C:/Windows/Fonts/msyh.ttc',subfontIndex=0))
pdfmetrics.registerFont(TTFont('YHB','C:/Windows/Fonts/msyhbd.ttc',subfontIndex=0))
pdfmetrics.registerFontFamily('YH',normal='YH',bold='YHB',italic='YH',boldItalic='YHB')
W,H=A4
def image_path(id):
    p=ROOT/'assets/final'/(id+'.png')
    if not p.exists():raise FileNotFoundError(p)
    return str(p)
def image(c,id,x,y,w,h):
    # Complete original image placed into a physical slot; no card-text overlay.
    c.drawImage(image_path(id),x,y,w,h,preserveAspectRatio=True,anchor='c',mask='auto')
def marks(c,x,y,w,h):
    c.setStrokeColor(colors.HexColor('#929292'));c.setLineWidth(.2)
    gap=0.6*mm;ln=1.3*mm
    for px,py,sx,sy in [(x,y,-1,-1),(x+w,y,1,-1),(x,y+h,-1,1),(x+w,y+h,1,1)]:
        c.line(px+sx*gap,py,px+sx*(gap+ln),py)
        c.line(px,py+sy*gap,px,py+sy*(gap+ln))
def footer(c,label):
    c.setFillColor(colors.HexColor('#555555'));c.setFont('YH',7)
    c.drawCentredString(W/2,5*mm,label)
def cards():
    deck=[]
    for j in J:
        if j['kind'] in ['property','event','role','reference-card']:
            deck.extend([(j['id'],j['backId'])]*j.get('copies',1))
    assert len(deck)==140
    c=canvas.Canvas(str(OUT/'全套卡牌_双面印制.pdf'),pagesize=A4,pageCompression=1)
    c.setTitle('百妖夜市 · 全套140张卡牌 · 长边翻转')
    cw,ch=63*mm,88*mm;gap=3*mm
    x0=(W-3*cw-2*gap)/2;y0=(H-3*ch-2*gap)/2
    for batch in range(math.ceil(len(deck)/9)):
        items=deck[batch*9:(batch+1)*9]
        for side in [0,1]:
            for i,pair in enumerate(items):
                row,col=divmod(i,3)
                if side:col=2-col
                x=x0+col*(cw+gap);y=y0+(2-row)*(ch+gap)
                image(c,pair[side],x,y,cw,ch);marks(c,x,y,cw,ch)
            footer(c,'百妖夜市 · 第'+str(batch+1)+'张纸 · '+('背面／长边翻转' if side else '正面／实际尺寸100%'))
            c.showPage()
    c.save()
def currency():
    # 134 notes, 140 x 70 mm. Same banknote copies share one front and one back.
    notes=[]
    for n in G['banknotes']:notes.extend([n['id']]*n['copies'])
    c=canvas.Canvas(str(OUT/'七种灵钱_双面印制.pdf'),pagesize=A4,pageCompression=1)
    c.setTitle('百妖夜市 · 灵钱 · 140×70毫米')
    cw,ch=140*mm,70*mm;x=(W-cw)/2;gap=8*mm;y0=(H-3*ch-2*gap)/2
    for batch in range(math.ceil(len(notes)/3)):
        for face in ['front','back']:
            for i,id in enumerate(notes[batch*3:(batch+1)*3]):
                y=y0+(2-i)*(ch+gap);image(c,id+'_'+face,x,y,cw,ch);marks(c,x,y,cw,ch)
            footer(c,'灵钱 · 第'+str(batch+1)+'张纸 · '+('正面' if face=='front' else '背面／长边翻转'))
            c.showPage()
    c.save()
def board():
    size=420*mm
    tiles=json.loads((ROOT/'data/map-tiles.json').read_text(encoding='utf8'))
    def whole(c,x,y):
        unit=size/4
        for t in tiles:image(c,t['id'],x+t['col']*unit,y+(3-t['row'])*unit,unit,unit)
    c=canvas.Canvas(str(OUT/'夜市地图_420毫米.pdf'),pagesize=(size,size))
    c.setTitle('百妖夜市 · 420毫米地图 · 完整生成原图')
    whole(c,0,0);c.showPage();c.save()
    # Six A4 sheets, 3 columns by 2 rows. Full-image clipping for physical tiling only.
    tw,th=146*mm,216*mm;stepx,stepy=137*mm,204*mm
    c=canvas.Canvas(str(OUT/'夜市地图_A4六页拼接.pdf'),pagesize=A4)
    for row in range(2):
        for col in range(3):
            ox=(W-tw)/2;oy=(H-th)/2
            c.saveState();p=c.beginPath();p.rect(ox,oy,tw,th);c.clipPath(p,stroke=0,fill=0)
            whole(c,ox-col*stepx,oy-(1-row)*stepy)
            c.restoreState();marks(c,ox,oy,tw,th)
            footer(c,'地图拼接 · 上下两排／每排三张 · 第'+str(row+1)+'排第'+str(col+1)+'列 · 100%打印')
            c.showPage()
    c.save()
def components():
    c=canvas.Canvas(str(OUT/'辅助组件_裁切印制.pdf'),pagesize=A4)
    palette=['#b85666','#bf8b34','#6b929a','#8b69a7','#537eae','#39979b']
    # Colored ownership chips: one page per player, 32 chips plus role marker and pawn.
    for i,r in enumerate(G['roles']):
        c.setFont('YHB',16);c.setFillColor(colors.HexColor('#233044'))
        c.drawString(15*mm,H-20*mm,r['name']+' · 归属与行商标记')
        for k in range(32):
            row,col=divmod(k,8);x=(20+24*col)*mm;y=H-(45+24*row)*mm
            c.setFillColor(colors.HexColor(palette[i]));c.circle(x,y,8*mm,stroke=0,fill=1)
            c.setFillColor(colors.white);c.setFont('YHB',8);c.drawCentredString(x,y-2.5,r['name'][0])
        c.setFont('YH',10);c.setFillColor(colors.HexColor('#233044'))
        c.drawString(15*mm,H-155*mm,'归属标记32枚。放在棋盘上；建筑等级另放地产卡上。')
        # Two equal faces of a foldable tent pawn, no bitmap artwork or image editing.
        for k in range(2):
            x=(30+55*k)*mm;y=45*mm;w=45*mm;h=60*mm
            c.setFillColor(colors.HexColor(palette[i]));c.rect(x,y,w,h,fill=1,stroke=0)
            c.setFillColor(colors.white);c.setFont('YHB',12);c.drawCentredString(x+w/2,y+h/2,r['name'])
            c.setFont('YH',9);c.drawCentredString(x+w/2,y+h/2-18,'行商棋子')
            marks(c,x,y,w,h)
        footer(c,'两面分别裁切，背靠背粘贴，底部折出站脚。此页按玩家印一次。')
        c.showPage()
    # One independent level token per property. Rotate or point marker at card rent row.
    c.setFont('YHB',16);c.drawString(15*mm,H-20*mm,'建筑等级 · 32枚')
    for k in range(32):
        row,col=divmod(k,4);x=(15+47*col)*mm;y=H-(45+28*row)*mm
        c.setFillColor(colors.HexColor('#f3e5c8'));c.rect(x,y,42*mm,21*mm,fill=1,stroke=1)
        c.setFillColor(colors.HexColor('#253246'));c.setFont('YHB',9);c.drawCentredString(x+21*mm,y+12*mm,'妖铺 · 华楼 · 灵阁')
        c.setFont('YH',8);c.drawCentredString(x+21*mm,y+5*mm,'指向卡面当前租金行')
    footer(c,'每处地产用一枚指示牌；挪到对应租金行，标示等级。');c.showPage()
    tokens=[]
    for i,r in enumerate(G['roles']):
        tokens.extend([(r['name'][0]+'／停业',palette[i])]*3)
        tokens.append((r['name'][0]+'／缠身',palette[i]))
        tokens.append((r['name'][0]+'／已用',palette[i]))
    tokens.extend([(s['name']+'／已用','#657383') for s in G['streets']])
    tokens.extend([('商路遇阻','#657383'),('花雨满城','#657383'),('轮数标记','#b18d3a')])
    c.setFont('YHB',16);c.drawString(15*mm,H-20*mm,'状态与轮数标记')
    for k,(label,colr) in enumerate(tokens):
        row,col=divmod(k,5);x=(12+38*col)*mm;y=H-(45+22*row)*mm
        c.setFillColor(colors.HexColor(colr));c.roundRect(x,y,34*mm,17*mm,3*mm,stroke=0,fill=1)
        c.setFillColor(colors.white);c.setFont('YHB',8);c.drawCentredString(x+17*mm,y+6*mm,label)
    c.showPage()
    c.setFillColor(colors.HexColor('#253246'));c.setFont('YHB',18);c.drawString(15*mm,H-25*mm,'夜市轮数轨')
    for k in range(24):
        row,col=divmod(k,6);x=(15+30*col)*mm;y=H-(65+35*row)*mm
        c.setFillColor(colors.HexColor('#f3e5c8'));c.roundRect(x,y,26*mm,26*mm,2*mm,stroke=1,fill=1)
        c.setFillColor(colors.HexColor('#253246'));c.setFont('YHB',16);c.drawCentredString(x+13*mm,y+9*mm,str(k+1))
    c.setFont('YH',11);c.drawString(15*mm,80*mm,'人数：2／3／4／5／6    轮数：24／21／18／16／14')
    c.drawString(15*mm,65*mm,'每轮开始：重置角色与街区能力，清除全桌持续事件。')
    c.setLineWidth(.7);c.line(15*mm,35*mm,65*mm,35*mm)
    c.setFont('YH',9);c.drawString(15*mm,28*mm,'校准线50毫米；以实际尺寸100%打印。')
    c.showPage();c.save()
styles={
 'body':ParagraphStyle('body',fontName='YH',fontSize=10,leading=17,wordWrap='CJK',spaceAfter=8,textColor=colors.HexColor('#24313e')),
 'h1':ParagraphStyle('h1',fontName='YHB',fontSize=22,leading=30,spaceAfter=16,textColor=colors.HexColor('#24313e')),
 'h2':ParagraphStyle('h2',fontName='YHB',fontSize=14,leading=22,spaceBefore=12,spaceAfter=8,keepWithNext=False),
 'cell':ParagraphStyle('cell',fontName='YH',fontSize=8,leading=13,wordWrap='CJK')
}
def para(s,style='body'):
    s=escape(s)
    s=re.sub(r'\*\*(.*?)\*\*',r'<b>\1</b>',s)
    return Paragraph(s,styles[style])
def markdown_pdf(src,target):
    story=[];lines=(ROOT/src).read_text(encoding='utf8').splitlines();i=0
    while i<len(lines):
        line=lines[i].strip();i+=1
        if not line:continue
        if line.startswith('|'):
            rows=[]
            while True:
                if not re.fullmatch(r'[\s|:\-]+',line):rows.append([para(v.strip(),'cell') for v in line.strip('|').split('|')])
                if i>=len(lines) or not lines[i].strip().startswith('|'):break
                line=lines[i].strip();i+=1
            n=len(rows[0])
            if n==9:weights=[.6,.6,1.4,.7,.8,.8,.8,.8,.8]
            elif n==5:weights=[.6,1.1,1.2,5,.5]
            elif n==3:weights=[.6,1.5,5]
            else:weights=[1]*n
            widths=[174*mm*w/sum(weights) for w in weights]
            table=Table(rows,colWidths=widths,repeatRows=1,hAlign='LEFT')
            table.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#e9dfc7')),('VALIGN',(0,0),(-1,-1),'TOP'),('GRID',(0,0),(-1,-1),.3,colors.HexColor('#c9c9c9')),('LEFTPADDING',(0,0),(-1,-1),4),('RIGHTPADDING',(0,0),(-1,-1),4),('TOPPADDING',(0,0),(-1,-1),5),('BOTTOMPADDING',(0,0),(-1,-1),5)]))
            story.extend([table,Spacer(1,8)])
        elif line.startswith('# '):story.append(para(line[2:],'h1'))
        elif line.startswith('## '):story.extend([CondPageBreak(130),para(line[3:],'h2')])
        else:story.append(para(line.removeprefix('- ')))
    def page(c,d):footer(c,'百妖夜市 · 试玩版 · '+str(d.page))
    SimpleDocTemplate(str(OUT/target),pagesize=A4,leftMargin=18*mm,rightMargin=18*mm,topMargin=16*mm,bottomMargin=16*mm,title=target,fontName='YH').build(story,onFirstPage=page,onLaterPages=page)
if __name__=='__main__':
    import sys
    mode=sys.argv[1] if len(sys.argv)>1 else 'all'
    if mode in ['all','rules']:
        markdown_pdf('docs/规则手册.md','规则手册.pdf')
        markdown_pdf('docs/地产卡牌图鉴.md','完整内容图鉴.pdf')
    if mode in ['all','cards']:cards()
    if mode in ['all','currency']:currency()
    if mode in ['all','map']:board()
    if mode in ['all','components']:components()
    print('PDF assembly complete: '+mode)
