"""Render exact roadmap diagrams to PNG and SVG. Requires Pillow."""
from pathlib import Path
import os, json, math, html
from PIL import Image, ImageDraw, ImageFont

ROOT=Path(__file__).resolve().parents[1]
DATA=json.loads((ROOT/'assets/source/roadmaps.json').read_text())
W=1800
INK='#173147';MUTED='#5B6D80';BG='#F5F8FC';BORDER='#DCE5EF'

def fontpath(bold=False):
    env='ROADMAP_FONT_BOLD' if bold else 'ROADMAP_FONT_REGULAR'
    if os.environ.get(env):return os.environ[env]
    candidates=(['/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf','/Library/Fonts/Arial Bold.ttf','/System/Library/Fonts/Supplemental/Arial Bold.ttf','C:/Windows/Fonts/arialbd.ttf'] if bold else ['/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf','/Library/Fonts/Arial.ttf','/System/Library/Fonts/Supplemental/Arial.ttf','C:/Windows/Fonts/arial.ttf'])
    for p in candidates:
        if Path(p).is_file():return p
    raise RuntimeError('Provide ROADMAP_FONT_REGULAR and ROADMAP_FONT_BOLD with Cyrillic support')

FONT_REG=fontpath();FONT_BOLD=fontpath(True)

class Canvas:
    def __init__(self,w,h):
        self.w=w;self.h=h;self.im=Image.new('RGB',(w,h),BG);self.d=ImageDraw.Draw(self.im)
        self.svg=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">',f'<rect width="{w}" height="{h}" fill="{BG}"/>']
    def rect(self,box,fill,stroke=None,radius=0,width=2):
        self.d.rounded_rectangle(box,radius,fill=fill,outline=stroke,width=width)
        x,y,x2,y2=box
        self.svg.append(f'<rect x="{x}" y="{y}" width="{x2-x}" height="{y2-y}" rx="{radius}" fill="{fill}" stroke="{stroke or "none"}" stroke-width="{width}"/>')
    def line(self,points,fill=BORDER,width=4):
        self.d.line(points,fill=fill,width=width,joint='curve')
        self.svg.append(f'<polyline points="'+ ' '.join(f'{x},{y}' for x,y in points)+f'" fill="none" stroke="{fill}" stroke-width="{width}" stroke-linecap="round" stroke-linejoin="round"/>')
    def text(self,x,y,t,size=30,bold=False,color=INK):
        font=ImageFont.truetype(FONT_BOLD if bold else FONT_REG,size)
        self.d.text((x,y),t,font=font,fill=color,anchor='lt')
        self.svg.append(f'<text x="{x}" y="{y}" dominant-baseline="text-before-edge" font-family="DejaVu Sans, Arial, sans-serif" font-size="{size}" font-weight="{700 if bold else 400}" fill="{color}">{html.escape(t)}</text>')
    def arrow(self,x,y1,y2,color=BORDER):
        self.line([(x,y1),(x,y2-9)],color,5)
        self.line([(x-11,y2-22),(x,y2-9),(x+11,y2-22)],color,5)
    def save(self,stem):
        (ROOT/'assets').mkdir(exist_ok=True)
        self.im.save(ROOT/'assets'/f'{stem}.png',optimize=True)
        (ROOT/'assets/source'/f'{stem}.svg').write_text('\n'.join(self.svg+['</svg>']))

def phase_height(phase):return 110+math.ceil(len(phase['nodes'])/2)*150+20

def roadmap(route):
    heights=[phase_height(p) for p in route['phases']]
    H=294+sum(heights)+48*(len(heights)-1)+180
    c=Canvas(W,H);col=route['color']
    c.text(96,54,'СИСТЕМНЫЙ АНАЛИЗ / УЧЕБНАЯ КАРТА',25,True,col)
    size=64 if len(route['title'])<25 else 57
    c.text(92,111,route['title'],size,True)
    c.text(96,205,route['subtitle'],29,color=MUTED)
    y=294
    for idx,(p,ph) in enumerate(zip(route['phases'],heights)):
        optional=p.get('optional',False)
        color='#A66B13' if optional else col
        c.rect((86,y,W-86,y+ph),'#FFF9EA' if optional else '#FFFFFF',BORDER,24,2)
        c.rect((112,y+24,170,y+82),color,radius=15)
        c.text(125,y+38,f'{idx+1:02}',26,True,'#FFFFFF')
        c.text(194,y+24,p['title'],33,True)
        c.text(194,y+70,p['summary'],24,color=MUTED)
        nodes=p['nodes']
        for n,node in enumerate(nodes):
            row=n//2;side=n%2
            if n==len(nodes)-1 and len(nodes)%2:x=520
            else:x=112+side*802
            cy=y+112+row*150;cw=774;ch=132
            c.rect((x,cy,x+cw,cy+ch),'#F4F7FD' if not optional else '#FFF3D5',BORDER,16,2)
            c.text(x+22,cy+18,node['id'],28,True,color)
            c.text(x+111,cy+18,node['title'],29,True)
            c.text(x+111,cy+66,node['note'],24,color=MUTED)
            if node.get('checkpoint'):
                label=node['checkpoint'];tw=ImageFont.truetype(FONT_BOLD,19).getlength(label)+22
                c.rect((x+cw-tw-17,cy+99,x+cw-17,cy+123),color,radius=7)
                c.text(x+cw-tw-6,cy+101,label,17,True,'#FFFFFF')
        if idx+1<len(heights):c.arrow(W//2,y+ph+5,y+ph+44,color)
        y+=ph+48
    c.rect((86,H-127,W-86,H-49),col,radius=20)
    c.text(115,H-104,route['endpoint'],32,True,'#FFFFFF')
    c.text(96,H-29,'Материалы, задания и критерии сдачи — в страницах Markdown. Версия 1.1 · 16.10.2026',19,color=MUTED)
    c.save(route['key']+'-map')

def overview():
    c=Canvas(1800,1260)
    c.text(91,54,'СИСТЕМНЫЙ АНАЛИЗ',25,True,'#315EEE')
    c.text(86,110,'Два маршрута обучения',64,True)
    c.text(91,207,'От первого требования до самостоятельного ведения изменения',29,color=MUTED)
    for k,r in enumerate(DATA['routes']):
        x=86+k*840;cw=788;col=r['color']
        c.rect((x,284,x+cw,1110),'#FFFFFF',BORDER,25,2)
        title='С нуля до Junior' if k==0 else 'Junior → Middle / Middle+'
        c.text(x+26,313,title,37,True,col)
        c.text(x+26,372,'19 блоков · 348 часов' if k==0 else '15 блоков + 4 темы по выбору',25,color=MUTED)
        y=438
        for i,p in enumerate(r['phases']):
            color='#A66B13' if p.get('optional') else col
            c.rect((x+25,y,x+cw-25,y+84),'#FFF5DA' if p.get('optional') else '#F2F6FC',radius=15)
            c.text(x+44,y+15,f'{i+1:02}',24,True,color)
            # Short labels remain readable at GitHub content width.
            labels=(['Подготовка и устройство IT','Задача и требования','Процессы, модели, данные','SQL и форматы сообщений','API, интеграции, интерфейс','Постановка и защита'] if k==0 else ['Диагностика и требования','Архитектура, данные, API','События и надёжность','Безопасность и эксплуатация','Выпуск и защита','Middle+ под рабочую задачу'])
            c.text(x+96,y+16,labels[i],28,True)
            ids=p['nodes'];codes=ids[0]['id']+'–'+ids[-1]['id']
            c.text(x+96,y+52,codes,20,color=MUTED)
            if i<5:c.arrow(x+cw//2,y+86,y+104,col)
            y+=108
    c.text(90,1155,'Каждый блок: материалы → практика → самопроверка → ревью',29,True)
    c.text(91,1200,'Подробные карты и ссылки на задания открываются внутри маршрутов.',21,color=MUTED)
    c.save('overview')

if __name__=='__main__':
    for route in DATA['routes']:roadmap(route)
    overview()
    print('Rendered 3 PNG maps and 3 editable SVG maps')
