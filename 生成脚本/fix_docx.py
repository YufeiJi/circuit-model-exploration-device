# -*- coding: utf-8 -*-
"""后处理：统一中文字体（宋体/黑体），修正主题字体与默认字体"""
import sys
from docx import Document
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
from docx.shared import Cm, Pt
import zipfile, shutil, os, re

BODY_EA = "宋体"
HEAD_EA = "黑体"
LATIN = "Times New Roman"

def set_rfonts(el, ascii_=None, hAnsi=None, ea=None, cs=None, hint_ea=True):
    rPr = el
    rf = rPr.find(qn("w:rFonts"))
    if rf is None:
        rf = OxmlElement("w:rFonts")
        rPr.insert(0, rf)
    if ascii_ is not None:
        rf.set(qn("w:ascii"), ascii_)
    if hAnsi is not None:
        rf.set(qn("w:hAnsi"), hAnsi)
    if ea is not None:
        rf.set(qn("w:eastAsia"), ea)
    if cs is not None:
        rf.set(qn("w:cs"), cs)
    if hint_ea:
        rf.set(qn("w:hint"), "eastAsia")

def fix_styles(doc):
    st = doc.styles.element
    # docDefaults
    rpr_def = st.find(qn("w:docDefaults"))
    if rpr_def is not None:
        rpr = rpr_def.find(qn("w:rPrDefault"))
        if rpr is not None:
            r = rpr.find(qn("w:rPr"))
            if r is not None:
                set_rfonts(r, LATIN, LATIN, BODY_EA, LATIN)
    for s in doc.styles:
        name = s.name or ""
        try:
            rpr = s.element.get_or_add_rPr()
        except Exception:
            continue
        if name.startswith("Heading") or name in ("Title", "Subtitle"):
            set_rfonts(rpr, "Arial", "Arial", HEAD_EA, "Arial")
        elif name in ("Normal", "Body Text", "List Paragraph"):
            set_rfonts(rpr, LATIN, LATIN, BODY_EA, LATIN)

def is_heading_para(p):
    try:
        return (p.style.name or "").startswith("Heading")
    except Exception:
        return False

def fix_runs(doc):
    def walk(paras):
        for p in paras:
            head = is_heading_para(p)
            for r in p.runs:
                rpr = r._element.get_or_add_rPr()
                rf = rpr.find(qn("w:rFonts"))
                ea = rf.get(qn("w:eastAsia")) if rf is not None else None
                asc = rf.get(qn("w:ascii")) if rf is not None else None
                # 代码块保持 Consolas
                if asc and "Consolas" in asc:
                    if ea is None or ea in ("MS Mincho", "Microsoft YaHei", "微软雅黑"):
                        set_rfonts(rpr, None, None, BODY_EA, None)
                    continue
                set_rfonts(rpr,
                           asc if asc and asc not in ("MS Mincho",) else LATIN,
                           asc if asc and asc not in ("MS Mincho",) else LATIN,
                           HEAD_EA if head else BODY_EA,
                           None)
    walk(doc.paragraphs)
    for t in doc.tables:
        for row in t.rows:
            for c in row.cells:
                walk(c.paragraphs)
    for sec in doc.sections:
        for part in (sec.header, sec.footer):
            walk(part.paragraphs)

def fix_images(doc):
    """图片尺寸：插图按映射宽度，公式图按 300dpi 原始尺寸（上限 13cm）"""
    from PIL import Image
    import glob, os
    from docx.shared import Cm
    from docx.enum.text import WD_ALIGN_PARAGRAPH
    figw = {"fig1_block.png": 14.4, "fig2_schematic.png": 14.4, "fig3_bode.png": 11.8,
            "fig4_wave.png": 11.8, "fig5_err.png": 11.8, "fig6_types.png": 12.6,
            "fig7_fit.png": 12.6, "fig8_flow.png": 7.6}
    ratios = {}
    for f in glob.glob(r"D:\Agent\project\电路模型探究装置\文档//figs//*.png"):
        w, h = Image.open(f).size
        ratios[os.path.basename(f)] = (round(w/h, 3), w/300.0*2.54)
    used = []
    for s in doc.inline_shapes:
        r = round(s.width/s.height, 3)
        best, bd = None, 9
        for name, (rr, nw) in ratios.items():
            if name in used:
                continue
            if abs(rr-r) < bd:
                best, bd = name, abs(rr-r)
        if best is None or bd > 0.07:
            print("  ! 未匹配图片 ratio=", r)
            continue
        used.append(best)
        natw = ratios[best][1]
        wcm = figw.get(best)
        if wcm is None:                       # 公式图
            wcm = min(natw, 13.0)
        s.width = Cm(wcm)
        s.height = Cm(wcm/r)
        print("  img %-20s ratio=%.3f -> %.1fcm" % (best, r, wcm))
    for p in doc.paragraphs:
        if p._element.findall('.//' + qn('w:drawing')):
            pf = p.paragraph_format
            pf.space_before = Pt(6)
            pf.space_after = Pt(0)
            pf.line_spacing = 1.0
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER


def fix_tables(doc):
    # 各表列宽百分比（按表号）
    W = {
        "表1": [7, 20, 24, 33, 16], "表2": [7, 22, 26, 30, 15], "表3": [7, 30, 22, 26, 15],
        "表4": [7, 14, 30, 49], "表5": [12, 20, 16, 24, 28], "表6": [36, 16, 16, 16, 16],
        "表7": [16, 44, 40], "表8": [16, 18, 26, 40], "表9": [20, 18, 31, 31],
        "表10": [14, 18, 34, 34], "表11": [22, 40, 22, 16], "表12": [14, 16, 20, 16, 20, 14],
        "表13": [36, 22, 42], "表14": [7, 30, 40, 23], "表15": [22, 34, 44],
        "表16": [7, 18, 34, 9, 16, 16], "表17": [12, 58, 30], "表18": [30, 12, 22, 36],
        "表19": [16, 20, 44, 20],
    }
    TOTAL = 14.66  # cm
    body = doc.element.body
    last_cap = None
    n = 0
    for child in body.iterchildren():
        tag = child.tag.split("}")[-1]
        if tag == "p":
            txt = "".join(t.text or "" for t in child.iter(qn("w:t"))).strip()
            if txt.startswith("表"):
                import re as _re
                m = _re.match(r"表\s*(\d+)", txt)
                if m:
                    last_cap = "表" + m.group(1)
        elif tag == "tbl":
            n += 1
            t = doc.tables[n - 1]
            pct = W.get(last_cap)
            rows = t.rows
            if not rows:
                continue
            trPr = rows[0]._tr.get_or_add_trPr()
            if trPr.find(qn("w:tblHeader")) is None:
                trPr.append(OxmlElement("w:tblHeader"))
            for r in rows:
                tp = r._tr.get_or_add_trPr()
                if tp.find(qn("w:cantSplit")) is None:
                    tp.append(OxmlElement("w:cantSplit"))
            if pct and len(pct) == len(t.columns):
                t.autofit = False
                tblPr = t._tbl.tblPr
                lay = tblPr.find(qn("w:tblLayout"))
                if lay is None:
                    lay = OxmlElement("w:tblLayout")
                    tblPr.append(lay)
                lay.set(qn("w:type"), "fixed")
                for i, p in enumerate(pct):
                    wcm = Cm(TOTAL * p / 100.0)
                    for cell in t.columns[i].cells:
                        cell.width = wcm
                print("  tbl %s widths %s" % (last_cap, pct))



def fix_theme(path):
    """替换 theme1.xml 中的东亚字体，避免 MS Mincho 回退"""
    tmp = path + ".tmp"
    with zipfile.ZipFile(path, "r") as zin, zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as zout:
        for item in zin.infolist():
            data = zin.read(item.filename)
            if item.filename.startswith("word/theme/"):
                txt = data.decode("utf-8")
                txt = re.sub(r'(<a:minorFont>\s*<a:latin typeface=")[^"]*(")', r"\g<1>Times New Roman\2", txt)
                txt = re.sub(r'(<a:minorFont>.*?<a:ea typeface=")[^"]*(")', r"\g<1>" + BODY_EA + r"\2", txt, flags=re.S)
                txt = re.sub(r'(<a:majorFont>\s*<a:latin typeface=")[^"]*(")', r"\g<1>Arial\2", txt)
                txt = re.sub(r'(<a:majorFont>.*?<a:ea typeface=")[^"]*(")', r"\g<1>" + HEAD_EA + r"\2", txt, flags=re.S)
                data = txt.encode("utf-8")
            zout.writestr(item, data)
    shutil.move(tmp, path)

if __name__ == "__main__":
    path = sys.argv[1]
    doc = Document(path)
    fix_styles(doc)
    fix_runs(doc)
    fix_images(doc)
    fix_tables(doc)
    doc.save(path)
    fix_theme(path)
    print("fonts fixed:", path)
