#!/usr/bin/env python3
"""Build the Korean commentary .docx for each part from denmark/analysis_md/partN/*.md.
Usage: python3 build_docx.py [PART ...]   (default: 1 2 3 4)
Output: denmark/해설서/Hverdag_paa_Noerrebro_문장분석_N부_<계절>.docx"""
import glob, os, re, sys
from docx import Document
from docx.enum.text import WD_BREAK
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Pt, RGBColor, Mm

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, '해설서')
FONT = 'Malgun Gothic'
BLUE = RGBColor(0x1F, 0x4E, 0x79)
GRAY = RGBColor(0x7F, 0x7F, 0x7F)
PARTS = {1: ('가을', 'Efterår', 'Cyklen og naboerne', 'A2'),
         2: ('겨울', 'Vinter', 'Mørke og hygge', 'B1'),
         3: ('봄', 'Forår', 'Valg og forandring', 'B1+'),
         4: ('여름', 'Sommer', 'Lyse nætter', 'B2')}
SECTIONS = ['■ 주요 단어', '■ 문법', '■ 표현', '■ 시제·어순']


def run(p, text, size=10, bold=False, italic=False, color=None):
    r = p.add_run(text)
    r.font.name = FONT
    r._element.rPr.rFonts.set(qn('w:eastAsia'), FONT)
    r.font.size = Pt(size); r.bold = bold; r.italic = italic
    if color: r.font.color.rgb = color
    return r


def inline(p, text, size, **kw):
    """Render *italic* spans inside text."""
    for i, chunk in enumerate(re.split(r'\*([^*]+)\*', text)):
        if chunk:
            run(p, chunk, size, italic=(i % 2 == 1) or kw.get('italic', False),
                bold=kw.get('bold', False), color=kw.get('color'))


def spacing(p, before=0, after=0):
    pf = p.paragraph_format; pf.space_before = Pt(before / 20); pf.space_after = Pt(after / 20)


def top_border(p):
    pPr = p._p.get_or_add_pPr()
    bdr = OxmlElement('w:pBdr'); top = OxmlElement('w:top')
    for k, v in (('val', 'single'), ('color', '1F4E79'), ('sz', '6'), ('space', '6')):
        top.set(qn('w:' + k), v)
    bdr.append(top); pPr.append(bdr)


def shade(cell, fill):
    tcPr = cell._tc.get_or_add_tcPr(); shd = OxmlElement('w:shd')
    shd.set(qn('w:val'), 'clear'); shd.set(qn('w:color'), 'auto'); shd.set(qn('w:fill'), fill)
    tcPr.append(shd)


def word_table(doc, rows):
    t = doc.add_table(rows=1, cols=3)
    t.style = 'Table Grid'
    widths = (Mm(35), Mm(53), Mm(71))
    for c, h, w in zip(t.rows[0].cells, ('단어', '기본형 / 품사', '뜻'), widths):
        c.width = w; shade(c, 'E8EEF7'); c.paragraphs[0].text = ''
        run(c.paragraphs[0], h, 9, bold=True)
    for r in rows:
        cells = t.add_row().cells
        for c, val, w in zip(cells, r, widths):
            c.width = w; inline(c.paragraphs[0], val, 9)


def heading(doc, text, level):
    h = doc.add_heading(level=level)
    run(h, text, {0: 22, 1: 16, 2: 11}[level], bold=level < 2,
        color=RGBColor(0x9B, 0x1B, 0x30) if level < 2 else RGBColor(0x40, 0x40, 0x40))
    return h


def add_episode(doc, path, src_path):
    lines = open(path, encoding='utf-8').read().split('\n')
    i = 0; first = True
    pending_rows = None; section = None

    def flush_table():
        nonlocal pending_rows
        if pending_rows:
            word_table(doc, pending_rows)
        pending_rows = None

    for line in lines:
        s = line.rstrip()
        if pending_rows is not None and not s.startswith('|'):
            flush_table()
        if not s.strip():
            continue
        if s.startswith('# '):
            h = heading(doc, s[2:].strip(), 1)
            if not first:
                pass
            h.paragraph_format.page_break_before = True
            first = False
        elif s.startswith('## '):
            heading(doc, s[3:].strip(), 2)
        elif s.startswith('>'):
            txt = re.sub(r'^>\s*', '', s).replace('**', '')
            p = doc.add_paragraph(); spacing(p, 200, 120)
            inline(p, txt, 9.5, color=RGBColor(0x40, 0x40, 0x40))
            pPr = p._p.get_or_add_pPr(); shd = OxmlElement('w:shd')
            shd.set(qn('w:val'), 'clear'); shd.set(qn('w:color'), 'auto'); shd.set(qn('w:fill'), 'F4F1EA')
            pPr.append(shd)
        elif s.startswith('### '):
            m = re.match(r'### (\d+)\. ([^:]+?): (.*)$', s)
            p = doc.add_paragraph(); spacing(p, 280, 60); top_border(p)
            p.paragraph_format.keep_with_next = True
            if m:
                run(p, m.group(1) + '. ', 11, bold=True, color=BLUE)
                run(p, m.group(2) + ': ', 11, bold=True)
                inline(p, m.group(3), 11, italic=True)
            else:
                run(p, s[4:], 11, bold=True)
        elif s.startswith('번역:'):
            p = doc.add_paragraph(); spacing(p, 0, 80)
            run(p, '번역  ', 10, bold=True, color=GRAY); inline(p, s[3:].strip(), 10)
        elif s.strip() in SECTIONS:
            p = doc.add_paragraph(); spacing(p, 120, 60)
            p.paragraph_format.keep_with_next = True
            run(p, s.strip(), 10, bold=True, color=BLUE)
            section = s.strip()
        elif s.startswith('|'):
            cells = [c.strip() for c in s.strip().strip('|').split('|')]
            if all(re.fullmatch(r':?-{2,}:?', c) for c in cells) or cells[:1] == ['단어']:
                continue
            while len(cells) < 3: cells.append('')
            if pending_rows is None: pending_rows = []
            pending_rows.append(cells[:2] + [' | '.join(cells[2:])])
        elif re.match(r'^\s*[-*] ', s):
            p = doc.add_paragraph(style='List Bullet'); spacing(p, 0, 40)
            inline(p, re.sub(r'^\s*[-*] ', '', s), 9.5)
        else:
            p = doc.add_paragraph(); spacing(p, 0, 40); inline(p, s.replace('**', ''), 9.5)
    flush_table()

    # append the episode's learning notes from the source script
    src = open(src_path, encoding='utf-8').read()
    if '\n## 학습 노트' in src:
        notes = src.split('\n## 학습 노트', 1)[1]
        p = doc.add_paragraph(); spacing(p, 360, 120); top_border(p)
        run(p, '이번 화 학습 노트', 12, bold=True, color=BLUE)
        rows = None
        for line in notes.split('\n'):
            s = line.strip()
            if not s or s == '---':
                if rows: word_table_notes(doc, rows); rows = None
                continue
            if s.startswith('|'):
                cells = [c.strip() for c in s.strip('|').split('|')]
                if all(re.fullmatch(r':?-{2,}:?', c) for c in cells): continue
                rows = (rows or []) + [cells]
                continue
            if rows: word_table_notes(doc, rows); rows = None
            if s.startswith('**') and s.endswith('**'):
                p = doc.add_paragraph(); spacing(p, 120, 40); run(p, s.strip('*'), 10, bold=True)
            else:
                p = doc.add_paragraph(); spacing(p, 0, 30)
                inline(p, re.sub(r'^\d+\)\s*', lambda m: m.group(0), s.replace('**', '')), 9.5)
        if rows: word_table_notes(doc, rows)


def word_table_notes(doc, rows):
    t = doc.add_table(rows=0, cols=len(rows[0])); t.style = 'Table Grid'
    for k, r in enumerate(rows):
        cells = t.add_row().cells
        for c, val in zip(cells, r):
            if k == 0: shade(c, 'E8EEF7')
            inline(c.paragraphs[0], val, 9, bold=(k == 0))


def build(part):
    season, da, theme, lv = PARTS[part]
    files = sorted(glob.glob(f'{ROOT}/analysis_md/part{part}/ep*.md'))
    if not files:
        print(f'part {part}: no analysis files'); return
    doc = Document()
    sec = doc.sections[0]
    sec.page_width, sec.page_height = Mm(210), Mm(297)
    for side in ('left_margin', 'right_margin', 'top_margin', 'bottom_margin'):
        setattr(sec, side, Mm(25))
    st = doc.styles['Normal']; st.font.name = FONT; st.font.size = Pt(10)
    st.element.rPr.rFonts.set(qn('w:eastAsia'), FONT)
    t = doc.add_paragraph(); spacing(t, 2400, 200)
    run(t, 'Hverdag på Nørrebro — 문장별 상세 분석', 22, bold=True, color=RGBColor(0x9B, 0x1B, 0x30))
    p = doc.add_paragraph(); run(p, f'{part}부 {da} ({season}) · {theme} · {lv}', 14, bold=True)
    p = doc.add_paragraph(); spacing(p, 200, 0)
    run(p, '각 대사마다 ① 한국어 번역 ② 주요 단어 ③ 문법 ④ 표현 ⑤ 시제·어순을 정리했습니다. '
           '각 화 끝에는 그 화의 학습 노트(핵심 표현·문법·현안 어휘)를 붙였습니다.', 10.5)
    for f in files:
        n = int(re.search(r'ep(\d+)', f).group(1))
        add_episode(doc, f, f'{ROOT}/episodes/part{part}/ep{n:02d}.md')
    os.makedirs(OUT, exist_ok=True)
    out = f'{OUT}/Hverdag_paa_Noerrebro_문장분석_{part}부_{season}.docx'
    doc.save(out); print(out, len(files), 'episodes')


if __name__ == '__main__':
    for a in (sys.argv[1:] or ['1', '2', '3', '4']):
        build(int(a))
