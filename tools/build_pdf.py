import re, glob, os, sys
from xml.sax.saxutils import escape
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (BaseDocTemplate, PageTemplate, Frame, Paragraph, Spacer,
                                PageBreak, Table, TableStyle, KeepTogether, Flowable)
from reportlab.platypus.tableofcontents import TableOfContents

ROOT = sys.argv[1]
OUT = sys.argv[2]
os.makedirs(OUT, exist_ok=True)

F = '/usr/share/fonts/truetype/freefont/'
N = '/usr/share/fonts/truetype/nanum/'
pdfmetrics.registerFont(TTFont('Serif', F + 'FreeSerif.ttf'))
pdfmetrics.registerFont(TTFont('Serif-B', F + 'FreeSerifBold.ttf'))
pdfmetrics.registerFont(TTFont('Serif-I', F + 'FreeSerifItalic.ttf'))
pdfmetrics.registerFont(TTFont('Serif-BI', F + 'FreeSerifBoldItalic.ttf'))
pdfmetrics.registerFont(TTFont('Sans', F + 'FreeSans.ttf'))
pdfmetrics.registerFont(TTFont('Sans-B', F + 'FreeSansBold.ttf'))
pdfmetrics.registerFont(TTFont('Mono', F + 'FreeMono.ttf'))
pdfmetrics.registerFont(TTFont('KR', N + 'NanumMyeongjo.ttf'))
pdfmetrics.registerFont(TTFont('KR-B', N + 'NanumMyeongjoBold.ttf'))
from reportlab.lib.fonts import addMapping
addMapping('Serif', 0, 0, 'Serif'); addMapping('Serif', 1, 0, 'Serif-B')
addMapping('Serif', 0, 1, 'Serif-I'); addMapping('Serif', 1, 1, 'Serif-BI')
addMapping('KR', 0, 0, 'KR'); addMapping('KR', 1, 0, 'KR-B')
addMapping('KR', 0, 1, 'KR'); addMapping('KR', 1, 1, 'KR-B')

INK = colors.HexColor('#1d1d1f'); GREY = colors.HexColor('#5f6368'); ACC = colors.HexColor('#8a1c1c')

HANGUL = re.compile(r'([ᄀ-ᇿ㄰-㆏가-힯　-〿＀-￯·]+(?:[  ]*[ᄀ-ᇿ㄰-㆏가-힯　-〿＀-￯]+)*)')

def kr(s):
    """escape + wrap Hangul runs in Korean font."""
    out = []
    s = re.sub(r'\s*\([一-鿿]+\)', '', s)
    for part in HANGUL.split(s):
        if not part:
            continue
        if HANGUL.fullmatch(part) and re.search(r'[가-힯㄰-㆏　-〿＀-￯]', part):
            out.append('<font name="KR">' + escape(part) + '</font>')
        else:
            out.append(escape(part))
    return ''.join(out)

def inline(s):
    s = kr(s)
    s = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', s)
    s = re.sub(r'(?<![\w*])\*(?!\s)(.+?)(?<!\s)\*(?![\w*])', r'<i>\1</i>', s)
    s = re.sub(r'`(.+?)`', r'<font name="Mono">\1</font>', s)
    s = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', s)
    return s

def S(name, **kw):
    base = dict(fontName='Serif', fontSize=10.5, leading=14.5, textColor=INK)
    base.update(kw); return ParagraphStyle(name, **base)

st = {
    'cover_t': S('ct', fontName='Serif-B', fontSize=34, leading=40, alignment=TA_CENTER, textColor=ACC),
    'cover_s': S('cs', fontSize=15, leading=21, alignment=TA_CENTER, textColor=INK),
    'cover_m': S('cm', fontSize=11, leading=16, alignment=TA_CENTER, textColor=GREY),
    'part': S('pt', fontName='Serif-B', fontSize=26, leading=32, alignment=TA_CENTER, textColor=ACC),
    'ep': S('ep', fontName='Serif-B', fontSize=17, leading=22, textColor=ACC, spaceAfter=4),
    'meta': S('mt', fontSize=9.5, leading=13.5, textColor=GREY, spaceAfter=8),
    'scene': S('sc', fontName='Sans-B', fontSize=9.5, leading=13, textColor=ACC, spaceBefore=12, spaceAfter=6),
    'dir': S('dr', fontName='Serif-I', fontSize=10, leading=13.5, textColor=GREY, leftIndent=24, spaceBefore=2, spaceAfter=4),
    'line': S('ln', leftIndent=24, firstLineIndent=-24, spaceAfter=3.5),
    'end': S('en', fontName='Serif-I', fontSize=10.5, alignment=TA_CENTER, textColor=ACC, spaceBefore=16),
    'h1': S('h1', fontName='Serif-B', fontSize=20, leading=26, textColor=ACC, spaceBefore=6, spaceAfter=10),
    'h2': S('h2', fontName='Serif-B', fontSize=15, leading=20, textColor=ACC, spaceBefore=14, spaceAfter=6),
    'h3': S('h3', fontName='Serif-B', fontSize=12.5, leading=17, textColor=INK, spaceBefore=10, spaceAfter=4),
    'h4': S('h4', fontName='Serif-B', fontSize=11, leading=15, spaceBefore=8, spaceAfter=3),
    'p': S('p', spaceAfter=5),
    'quote': S('q', fontSize=10, textColor=GREY, leftIndent=12, spaceAfter=6),
    'li': S('li', leftIndent=14, firstLineIndent=-9, spaceAfter=2.5),
    'li2': S('li2', leftIndent=28, firstLineIndent=-9, spaceAfter=2),
    'code': S('cd', fontName='Mono', fontSize=8.8, leading=12, leftIndent=10, textColor=INK),
    'cell': S('cl', fontSize=8.8, leading=11.5),
    'cellh': S('ch', fontName='Serif-B', fontSize=8.8, leading=11.5),
    'toc1': S('t1', fontName='Serif-B', fontSize=11.5, leading=16, spaceBefore=6),
    'toc2': S('t2', fontSize=10, leading=13.5, leftIndent=16),
}

class Bookmark(Flowable):
    def __init__(self, title, key, level):
        super().__init__(); self.title, self.key, self.level = title, key, level
        self.width = self.height = 0
    def draw(self):
        c = self.canv
        c.bookmarkPage(self.key)
        c.addOutlineEntry(self.title, self.key, level=self.level, closed=self.level == 0)

class Doc(BaseDocTemplate):
    def __init__(self, fn, header, **kw):
        super().__init__(fn, pagesize=A4, leftMargin=22*mm, rightMargin=22*mm,
                         topMargin=22*mm, bottomMargin=20*mm, **kw)
        self.header = header
        fr = Frame(self.leftMargin, self.bottomMargin, self.width, self.height, id='f')
        self.addPageTemplates([PageTemplate('main', [fr], onPage=self.deco)])
        self._bk = 0
    def deco(self, c, d):
        if d.page == 1:
            return
        c.saveState()
        c.setFont('KR' if re.search(r'[가-힯]', self.header) else 'Serif-I', 8.5); c.setFillColor(GREY)
        c.drawString(self.leftMargin, A4[1] - 13*mm, self.header)
        c.drawRightString(A4[0] - self.rightMargin, 11*mm, str(d.page))
        c.setStrokeColor(colors.HexColor('#d0d0d0')); c.setLineWidth(0.4)
        c.line(self.leftMargin, A4[1] - 15*mm, A4[0] - self.rightMargin, A4[1] - 15*mm)
        c.restoreState()
    def afterFlowable(self, f):
        if isinstance(f, Paragraph) and hasattr(f, '_toc'):
            lvl, text = f._toc
            self.notify('TOCEntry', (lvl, text, self.page))

def toc_para(text, style, lvl):
    p = Paragraph(inline(text), style); p._toc = (lvl, text); return p

SPEAKER = re.compile(r"^([A-ZÀ-ÝČĆŠŽĐ' ]+?)((?: \([^)]*\))?):\s*(.*)$")

def episode_flow(path, part_key):
    raw = open(path, encoding='utf-8').read()
    raw = re.sub(r'<!--.*?-->', '', raw, flags=re.S)
    flow = []
    lines = raw.split('\n')
    for ln in lines:
        s = ln.rstrip()
        if not s or s == '---':
            continue
        if s.startswith('# '):
            title = s[2:].split('—', 1)[-1].strip()
            key = 'k%d' % abs(hash(path))
            flow.append(Bookmark(title, key, 1))
            flow.append(toc_para(title, st['ep'], 1))
        elif s.startswith('>'):
            flow.append(Paragraph(inline(s.lstrip('> ')), st['meta']))
        elif s.startswith('[') and s.endswith(']'):
            flow.append(Paragraph(inline(s[1:-1]), st['scene']))
        elif s.startswith('(') and s.endswith(')') and not SPEAKER.match(s):
            flow.append(Paragraph(inline(s[1:-1]), st['dir']))
        elif s.startswith('—') or s.startswith('- —'):
            flow.append(Paragraph(inline(s), st['end']))
        else:
            m = SPEAKER.match(s)
            if m:
                name, tag, text = m.groups()
                t = inline(text)
                t = re.sub(r'\(([^()]*)\)', r'<font name="Serif-I" color="#5f6368">(\1)</font>', t)
                tg = (' <font name="Serif-I" size="9" color="#5f6368">' + escape(tag.strip()) + '</font>') if tag else ''
                flow.append(Paragraph('<font name="Sans-B" size="9" color="#8a1c1c">%s</font>%s&nbsp;&nbsp;%s' % (escape(name), tg, t), st['line']))
            else:
                flow.append(Paragraph(inline(s), st['p']))
    return flow

def md_flow(path, bookmark_title=None, level=0):
    raw = open(path, encoding='utf-8').read()
    raw = re.sub(r'<!--.*?-->', '', raw, flags=re.S)
    flow = []
    if bookmark_title:
        flow.append(Bookmark(bookmark_title, 'b%d' % abs(hash(path)), level))
    lines = raw.split('\n'); i = 0
    while i < len(lines):
        s = lines[i].rstrip()
        if s.startswith('```'):
            i += 1; buf = []
            while i < len(lines) and not lines[i].startswith('```'):
                buf.append(lines[i]); i += 1
            i += 1
            box = []
            for b in buf:
                box.append(Paragraph(inline(b) if b.strip() else '&nbsp;', st['code']))
            t = Table([[box]], colWidths=[166*mm])
            t.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f4f1ec')),
                                   ('BOX', (0, 0), (-1, -1), 0.4, colors.HexColor('#d8d2c6')),
                                   ('LEFTPADDING', (0, 0), (-1, -1), 8), ('TOPPADDING', (0, 0), (-1, -1), 6),
                                   ('BOTTOMPADDING', (0, 0), (-1, -1), 6)]))
            flow.append(t); flow.append(Spacer(1, 6)); continue
        if s.startswith('|'):
            rows = []
            while i < len(lines) and lines[i].startswith('|'):
                r = lines[i].strip().strip('|').split('|')
                if not re.fullmatch(r'[\s:|-]+', lines[i]):
                    rows.append([c.strip() for c in r])
                i += 1
            ncol = max(len(r) for r in rows)
            data = []
            for ri, r in enumerate(rows):
                r += [''] * (ncol - len(r))
                data.append([Paragraph(inline(c), st['cellh'] if ri == 0 else st['cell']) for c in r])
            W = 166*mm
            lens = [max(len(r[c]) for r in rows) + 4 for c in range(ncol)]
            tot = sum(lens); cw = [max(W * l / tot, 16*mm) for l in lens]
            k = W / sum(cw); cw = [c * k for c in cw]
            t = Table(data, colWidths=cw, repeatRows=1)
            t.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#efe6e6')),
                                   ('GRID', (0, 0), (-1, -1), 0.3, colors.HexColor('#c9c9c9')),
                                   ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                                   ('LEFTPADDING', (0, 0), (-1, -1), 4), ('RIGHTPADDING', (0, 0), (-1, -1), 4)]))
            flow.append(t); flow.append(Spacer(1, 8)); continue
        i += 1
        if not s.strip():
            continue
        if s.strip() == '---':
            flow.append(Spacer(1, 6)); continue
        m = re.match(r'^(#{1,4}) (.*)', s)
        if m:
            lv = len(m.group(1)); txt = m.group(2)
            if lv == 1:
                flow.append(toc_para(txt, st['h1'], 0))
            elif lv == 2:
                flow.append(toc_para(txt, st['h2'], 1) if bookmark_title else Paragraph(inline(txt), st['h2']))
            else:
                flow.append(Paragraph(inline(txt), st['h3' if lv == 3 else 'h4']))
            continue
        if s.startswith('>'):
            flow.append(Paragraph(inline(s.lstrip('> ')), st['quote'])); continue
        m = re.match(r'^(\s*)[-*] (.*)', s)
        if m:
            ind = len(m.group(1))
            flow.append(Paragraph('•&nbsp;&nbsp;' + inline(m.group(2)), st['li2' if ind >= 2 else 'li'])); continue
        m = re.match(r'^(\s*)(\d+)\. (.*)', s)
        if m:
            flow.append(Paragraph(m.group(2) + '.&nbsp;&nbsp;' + inline(m.group(3)), st['li'])); continue
        flow.append(Paragraph(inline(s), st['p']))
    return flow

PARTS = [
    ('1부_Il_Codice_di_Venezia', 'Parte prima', 'Il Codice di Venezia', '베네치아 코드 · 베네치아'),
    ('2부_Le_Chiavi_di_San_Pietro', 'Parte seconda', 'Le Chiavi di San Pietro', '성 베드로의 열쇠 · 바티칸'),
    ('3부_La_Bora', 'Parte terza', 'La Bora', '보라 · 트리에스테'),
    ('4부_La_Nebbia_di_SantAmbrogio', 'Parte quarta', "La Nebbia di Sant'Ambrogio", '성 암브로조의 안개 · 밀라노'),
]

def cover(title, sub, meta):
    return [Spacer(1, 70*mm), Paragraph('LA FENICE', st['cover_m']), Spacer(1, 6*mm),
            Paragraph(inline(title), st['cover_t']), Spacer(1, 6*mm),
            Paragraph(inline(sub), st['cover_s']), Spacer(1, 14*mm),
            Paragraph(inline(meta), st['cover_m']), PageBreak()]

def toc():
    t = TableOfContents(); t.levelStyles = [st['toc1'], st['toc2']]
    return [Paragraph(inline('Indice · 목차'), st['h1']), t, PageBreak()]

def part_flow(d, label, name, kor, with_cover_page=True):
    flow = [Bookmark('%s — %s' % (label, name), 'p' + d[:2], 0)]
    flow += [Spacer(1, 80*mm), Paragraph(label.upper(), st['cover_m']), Spacer(1, 4*mm),
             toc_para(name, st['part'], 0), Spacer(1, 4*mm), Paragraph(inline(kor), st['cover_s']), PageBreak()]
    for f in sorted(glob.glob(os.path.join(ROOT, 'episodes', d, 'E*.md'))):
        flow += episode_flow(f, d); flow.append(PageBreak())
    return flow

def build(fn, header, story):
    doc = Doc(os.path.join(OUT, fn), header, title=header, author='La Fenice')
    doc.multiBuild(story)
    print('built', fn)

which = sys.argv[3] if len(sys.argv) > 3 else 'all'

if which in ('all', 'parts'):
    for i, (d, label, name, kor) in enumerate(PARTS, 1):
        story = cover(name, kor, 'Parte %d di 4 · 12 episodi · dialoghi in italiano') + toc()
        story += part_flow(d, label, name, kor)
        build('%d부_%s.pdf' % (i, d.split('_', 1)[1]), 'La Fenice — ' + name, story)

if which in ('all', 'plan'):
    story = cover('La Fenice', '시리즈 기획서', '시리즈 바이블 · 1~4부 화별 구성') + toc()
    for f, t in [('00_시리즈_바이블.md', '시리즈 바이블'), ('01_1부_Il_Codice_di_Venezia.md', '1부 기획'),
                 ('02_2부_Le_Chiavi_di_San_Pietro.md', '2부 기획'), ('03_3부_La_Bora.md', '3부 기획'),
                 ('04_4부_La_Nebbia_di_SantAmbrogio.md', '4부 기획')]:
        story += [Bookmark(t, 'pl' + f[:2], 0)] + md_flow(os.path.join(ROOT, 'plan', f)) + [PageBreak()]
    build('0_기획서_La_Fenice.pdf', 'La Fenice — 기획서', story)

if which in ('all', 'full'):
    story = cover('La Fenice', 'Serie completa in quattro parti', '4부 × 12화 = 48화 · 이탈리아어 첩보 스릴러 대화문') + toc()
    for d, label, name, kor in PARTS:
        story += part_flow(d, label, name, kor)
    build('La_Fenice_전편.pdf', 'La Fenice — Serie completa', story)
