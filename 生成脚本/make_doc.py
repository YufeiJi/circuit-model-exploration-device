# -*- coding: utf-8 -*-
"""生成《完整操作过程与源码说明》技术文档

结构：封面 → 目录域 → 15 节正文 → 附录 A 全部源码
所有源码从 源码/ 目录实时读取，保证文档与可运行代码完全一致。
"""
import os
from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

ROOT = r"D:\Agent\project\电路模型探究装置\文档"
SRC = os.path.join(ROOT, "源码")
OUT = os.path.join(ROOT, "电路模型探究装置-完整操作过程与源码说明.docx")

SONG, HEI, MONO = "宋体", "黑体", "Consolas"
CODE_FILL = "F5F6F8"

# ---------------------------------------------------------------- 基础工具
def _rf(run, ascii_f, ea_f):
    rPr = run._element.get_or_add_rPr()
    rf = rPr.find(qn("w:rFonts"))
    if rf is None:
        rf = OxmlElement("w:rFonts")
        rPr.insert(0, rf)
    rf.set(qn("w:ascii"), ascii_f)
    rf.set(qn("w:hAnsi"), ascii_f)
    rf.set(qn("w:eastAsia"), ea_f)
    rf.set(qn("w:cs"), ascii_f)
    rf.set(qn("w:hint"), "eastAsia")


def _ins(pPr, el, successors):
    pPr.insert_element_before(el, *successors)


_SHD_SUCC = ("w:tabs", "w:suppressAutoHyphens", "w:kinsoku", "w:wordWrap",
             "w:overflowPunct", "w:topLinePunct", "w:autoSpaceDE", "w:autoSpaceDN",
             "w:bidi", "w:adjustRightInd", "w:snapToGrid", "w:spacing", "w:ind",
             "w:contextualSpacing", "w:mirrorIndents", "w:suppressOverlap", "w:jc",
             "w:textDirection", "w:textAlignment", "w:textboxTightWrap",
             "w:outlineLvl", "w:divId", "w:cnfStyle", "w:rPr", "w:sectPr", "w:pPrChange")


def _shade(par, fill=CODE_FILL, bar=True):
    pPr = par._p.get_or_add_pPr()
    if bar:
        bdr = OxmlElement("w:pBdr")
        left = OxmlElement("w:left")
        left.set(qn("w:val"), "single"); left.set(qn("w:sz"), "18")
        left.set(qn("w:space"), "6"); left.set(qn("w:color"), "8FA8C8")
        bdr.append(left)
        _ins(pPr, bdr, ("w:shd",) + _SHD_SUCC)
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear"); shd.set(qn("w:color"), "auto"); shd.set(qn("w:fill"), fill)
    _ins(pPr, shd, _SHD_SUCC)


def body(text, indent=True, size=10.5, bold=False, color=None, space_after=3):
    p = doc.add_paragraph()
    pf = p.paragraph_format
    pf.first_line_indent = Cm(0.74) if indent else None
    pf.line_spacing = 1.55
    pf.space_before = Pt(0)
    pf.space_after = Pt(space_after)
    pf.alignment = WD_ALIGN_PARAGRAPH.LEFT
    r = p.add_run(text)
    r.font.size = Pt(size); r.bold = bold
    if color:
        r.font.color.rgb = color
    _rf(r, "Times New Roman", SONG)
    return p


def h1(text):
    p = doc.add_paragraph(style="Heading 1")
    pf = p.paragraph_format
    pf.space_before = Pt(14); pf.space_after = Pt(6); pf.line_spacing = 1.25
    r = p.add_run(text)
    r.font.size = Pt(15); r.bold = True
    r.font.color.rgb = RGBColor(0x1F, 0x33, 0x4E)
    _rf(r, "Times New Roman", HEI)
    return p


def h2(text):
    p = doc.add_paragraph(style="Heading 2")
    pf = p.paragraph_format
    pf.space_before = Pt(10); pf.space_after = Pt(4); pf.line_spacing = 1.25
    r = p.add_run(text)
    r.font.size = Pt(11.5); r.bold = True
    r.font.color.rgb = RGBColor(0x2A, 0x45, 0x66)
    _rf(r, "Times New Roman", HEI)
    return p


def cap(text):
    p = doc.add_paragraph()
    pf = p.paragraph_format
    pf.space_before = Pt(6); pf.space_after = Pt(2)
    pf.line_spacing = 1.2
    pf.alignment = WD_ALIGN_PARAGRAPH.LEFT
    r = p.add_run(text)
    r.font.size = Pt(9); r.bold = True
    r.font.color.rgb = RGBColor(0x33, 0x33, 0x33)
    _rf(r, "Times New Roman", HEI)
    return p


def code_block(text, size=8.0, line=10.0):
    """整段代码：每行一个段落，共享底纹与左侧竖线，可自然跨页"""
    lines = text.replace("\t", "    ").rstrip("\n").split("\n")
    for i, ln in enumerate(lines):
        p = doc.add_paragraph()
        pf = p.paragraph_format
        pf.space_before = Pt(5) if i == 0 else Pt(0)
        pf.space_after = Pt(0)
        pf.line_spacing = Pt(line)
        pf.left_indent = Cm(0.28)
        pf.first_line_indent = Cm(0)
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        r = p.add_run(ln if ln else " ")
        r.font.size = Pt(size)
        _rf(r, MONO, SONG)
        _shade(p, CODE_FILL)
        if i == len(lines) - 1:
            pf.space_after = Pt(6)


def cmd_block(text):
    code_block(text, size=8.5, line=11.5)


def table(header, rows, widths, size=8.5, head_fill="E8EDF4"):
    t = doc.add_table(rows=1, cols=len(header))
    t.style = "Table Grid"
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    t.autofit = False
    tblPr = t._tbl.tblPr
    lay = OxmlElement("w:tblLayout"); lay.set(qn("w:type"), "fixed"); tblPr.append(lay)
    grid = t._tbl.find(qn("w:tblGrid"))
    for gc, w in zip(grid.findall(qn("w:gridCol")), widths):
        gc.set(qn("w:w"), str(int(Cm(w).twips)))
    tw = tblPr.find(qn("w:tblW"))
    if tw is None:
        tw = OxmlElement("w:tblW"); tblPr.append(tw)
    tw.set(qn("w:type"), "dxa"); tw.set(qn("w:w"), str(int(Cm(sum(widths)).twips)))

    def put(cell, text, bold=False, fill=None, align=WD_ALIGN_PARAGRAPH.LEFT):
        cell.width = Cm(widths[cell_idx[0]])
        p = cell.paragraphs[0]
        pf = p.paragraph_format
        pf.space_before = Pt(1.5); pf.space_after = Pt(1.5); pf.line_spacing = 1.15
        p.alignment = align
        r = p.add_run(text)
        r.font.size = Pt(size); r.bold = bold
        _rf(r, "Times New Roman", SONG if not bold else HEI)
        if fill:
            tcPr = cell._tc.get_or_add_tcPr()
            shd = OxmlElement("w:shd")
            shd.set(qn("w:val"), "clear"); shd.set(qn("w:color"), "auto"); shd.set(qn("w:fill"), fill)
            tcPr.append(shd)

    cell_idx = [0]
    for j, htxt in enumerate(header):
        cell_idx[0] = j
        put(t.rows[0].cells[j], htxt, bold=True, fill=head_fill,
            align=WD_ALIGN_PARAGRAPH.CENTER)
    for row in rows:
        cells = t.add_row().cells
        for j, val in enumerate(row):
            cell_idx[0] = j
            put(cells[j], str(val), align=WD_ALIGN_PARAGRAPH.LEFT)
    # 表头行重复
    trPr = t.rows[0]._tr.get_or_add_trPr()
    th = OxmlElement("w:tblHeader"); th.set(qn("w:val"), "true"); trPr.append(th)
    doc.add_paragraph().paragraph_format.space_after = Pt(2)
    return t


def note(title, text):
    p = doc.add_paragraph()
    pf = p.paragraph_format
    pf.left_indent = Cm(0.5); pf.space_before = Pt(4); pf.space_after = Pt(4)
    pf.line_spacing = 1.4
    r = p.add_run(title + "　")
    r.font.size = Pt(9.5); r.bold = True
    r.font.color.rgb = RGBColor(0xA8, 0x4B, 0x2A)
    _rf(r, "Times New Roman", HEI)
    r2 = p.add_run(text)
    r2.font.size = Pt(9.5)
    r2.font.color.rgb = RGBColor(0x44, 0x44, 0x44)
    _rf(r2, "Times New Roman", SONG)
    _shade(p, "FDF6EC", bar=False)


def add_field(par, instr, placeholder="1"):
    r = par.add_run()
    f1 = OxmlElement("w:fldChar"); f1.set(qn("w:fldCharType"), "begin")
    it = OxmlElement("w:instrText"); it.set(qn("xml:space"), "preserve"); it.text = instr
    f2 = OxmlElement("w:fldChar"); f2.set(qn("w:fldCharType"), "separate")
    t = OxmlElement("w:t"); t.text = placeholder
    f3 = OxmlElement("w:fldChar"); f3.set(qn("w:fldCharType"), "end")
    for e in (f1, it, f2, t, f3):
        r._r.append(e)
    r.font.size = Pt(9)
    _rf(r, "Times New Roman", SONG)


# ---------------------------------------------------------------- 文档骨架
doc = Document()
sec = doc.sections[0]
sec.page_width, sec.page_height = Cm(21.0), Cm(29.7)
sec.left_margin = sec.right_margin = Cm(2.4)
sec.top_margin = Cm(2.4); sec.bottom_margin = Cm(2.2)
sec.header_distance = Cm(1.3); sec.footer_distance = Cm(1.4)
sec.different_first_page_header_footer = True

st = doc.styles["Normal"]
st.font.name = "Times New Roman"; st.font.size = Pt(10.5)
st.element.rPr.rFonts.set(qn("w:eastAsia"), SONG)

# 页眉
hp = sec.header.paragraphs[0]
hp.alignment = WD_ALIGN_PARAGRAPH.CENTER
hr = hp.add_run("电路模型探究装置 · 完整操作过程与源码说明")
hr.font.size = Pt(8.5); hr.font.color.rgb = RGBColor(0x66, 0x66, 0x66)
_rf(hr, "Times New Roman", SONG)
# 页脚 第 X 页 / 共 Y 页
fp = sec.footer.paragraphs[0]
fp.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = fp.add_run("第 "); r.font.size = Pt(9); _rf(r, "Times New Roman", SONG)
add_field(fp, " PAGE ", "1")
r = fp.add_run(" 页　共 "); r.font.size = Pt(9); _rf(r, "Times New Roman", SONG)
add_field(fp, " NUMPAGES ", "1")
r = fp.add_run(" 页"); r.font.size = Pt(9); _rf(r, "Times New Roman", SONG)

# ---------------------------------------------------------------- 封面
for _ in range(3):
    doc.add_paragraph()
p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = p.add_run("电子信息工程专业科研训练 · 综合设计开发课题（第 2 题）")
r.font.size = Pt(11); r.font.color.rgb = RGBColor(0x55, 0x55, 0x55)
_rf(r, "Times New Roman", SONG)

p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
p.paragraph_format.space_before = Pt(24)
r = p.add_run("电路模型探究装置")
r.font.size = Pt(34); r.bold = True
r.font.color.rgb = RGBColor(0x1F, 0x33, 0x4E)
_rf(r, "Times New Roman", HEI)

p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
p.paragraph_format.space_before = Pt(10)
r = p.add_run("完整操作过程与源码说明")
r.font.size = Pt(19); r.bold = True
r.font.color.rgb = RGBColor(0x2A, 0x45, 0x66)
_rf(r, "Times New Roman", HEI)

p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
p.paragraph_format.space_before = Pt(6)
r = p.add_run("——从题目解析、电路定参、图件绘制到 24 页报告成稿的全流程复现")
r.font.size = Pt(10.5); r.font.color.rgb = RGBColor(0x66, 0x66, 0x66)
_rf(r, "Times New Roman", SONG)

for _ in range(6):
    doc.add_paragraph()

for line in ("交付内容：设计报告（24 页）＋ 科研讨论会议记录表（4 份）＋ 图件 14 张 ＋ 源码 9 个文件",
             "工具链：Python 3.13 / python-docx / NumPy / SciPy / Matplotlib / html-for-docx / Word 自动化",
             "文档规模：正文 15 节 ＋ 附录 A 全部源码（1665 行）"):
    p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_after = Pt(4)
    r = p.add_run(line); r.font.size = Pt(9.5)
    r.font.color.rgb = RGBColor(0x44, 0x44, 0x44)
    _rf(r, "Times New Roman", SONG)

for _ in range(4):
    doc.add_paragraph()
p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = p.add_run("2026 年 10 月")
r.font.size = Pt(11); _rf(r, "Times New Roman", SONG)

doc.add_page_break()

# ---------------------------------------------------------------- 目录
p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
p.paragraph_format.space_before = Pt(6); p.paragraph_format.space_after = Pt(14)
r = p.add_run("目　　录")
r.font.size = Pt(18); r.bold = True; r.font.color.rgb = RGBColor(0x1F, 0x33, 0x4E)
_rf(r, "Times New Roman", HEI)

toc_p = doc.add_paragraph()
add_field(toc_p, r' TOC \o "1-2" \h \z \u ', "（在 Word 中按 F9 更新目录）")
doc.add_page_break()

# ================================================================ 正文
h1("1　交付物与源码清单")
body("本次任务的全部产物集中在 D:\Agent\project\电路模型探究装置\文档 目录下，分为三类：可直接提交的文档（设计报告、会议记录表）、"
     "文档中引用的图件、以及生成这些内容的全部源码。设计报告与会议记录表的每一个数字、每一张图都由脚本产出，"
     "因此改动脚本中的任一参数即可整篇重新生成，不存在手工排版与数据脱节的问题。")
body("下表给出交付文件的完整清单。报告为 A4 纵向、24 页，含 10 章正文、附录 A（关键代码）、附录 B（元件清单）、"
     "21 张表格与 14 张图（8 张自制插图 + 6 张公式图），并带有可更新的 Word 目录域。")

cap("表 1-1　交付文件清单")
table(["文件", "规模", "说明"],
      [["电路模型探究装置-设计报告.docx", "24 页", "设计报告正文，含目录域、页眉页脚、21 表 14 图"],
       ["电路模型探究装置-设计报告（PDF预览）.pdf", "24 页", "与 docx 同源的 PDF，便于查阅与打印"],
       ["科研讨论会议记录表-第1周.docx", "1 页", "课题调研与方案定型"],
       ["科研讨论会议记录表-第2周.docx", "1 页", "建模、仿真与首版实测"],
       ["科研讨论会议记录表-第3周.docx", "1 页", "装置硬件与幅相测量程序"],
       ["科研讨论会议记录表-第4周.docx", "1 页", "辨识算法与整机指标测试"],
       ["figs/fig1～fig8", "8 张", "总体框图、原理图、Bode 图、瞬态波形、误差曲线、四类响应、拟合结果、流程图"],
       ["figs/fml1～fml6", "6 张", "公式图（mathtext 渲染，300 dpi）"],
       ["源码/（9 个文件）", "1665 行", "全部生成脚本，见附录 A"]],
      [7.4, 2.0, 6.8])

cap("表 1-2　源码清单")
table(["文件", "行数", "作用", "运行方式"],
      [["design.py", "118", "传递函数解析、关键频点、容差蒙特卡洛、图 3/4/5", "python design.py"],
       ["unknown.py", "124", "四模型复频域拟合与 200 次蒙特卡洛，图 6/7", "python unknown.py"],
       ["blocks.py", "72", "总体框图 fig1、辨识流程图 fig8", "python blocks.py"],
       ["sch.py", "110", "已知模型电路原理图 fig2（坐标手绘）", "python sch.py"],
       ["formulas.py", "29", "6 张公式图 fml1～fml6", "python formulas.py"],
       ["build_report.py", "752", "组装报告 HTML（10 章 + 附录）", "python build_report.py"],
       ["fix_docx.py", "207", "DOCX 字体、图宽、表宽、主题修补", "python fix_docx.py <docx>"],
       ["fill_minutes.py", "244", "按模板生成 4 周会议记录表", "python fill_minutes.py"],
       ["make_report.sh", "9", "一键串联 HTML→DOCX→修补", "bash make_report.sh"]],
      [3.4, 1.3, 8.0, 3.5])

note("阅读建议", "第 3～7 节是“内容从哪来”，第 8～12 节是“文档怎么排出来”。只想复现结果，直接看第 15 节与附录 A。")

h1("2　运行环境与依赖")
body("全部脚本在 Windows 10/11 + Python 3.13.12 下开发，使用托管解释器，避免污染系统环境。"
     "绘图与数值计算依赖 NumPy、SciPy、Matplotlib；文档处理依赖 python-docx 与 html-for-docx；"
     "PDF 质检依赖 PyMuPDF；目录域与 PDF 导出调用本机 Word 的 COM 接口。")

h2("2.1　Python 依赖")
cmd_block('"C:/Users/Yufei Ji/.workbuddy-ai/binaries/python/versions/3.13.12/python.exe" -m pip install \\\n'
          '    numpy scipy matplotlib python-docx pymupdf pdfplumber python-pptx html-for-docx')

body("html-for-docx 是 HTML 转 DOCX 的核心库，安装后以模块方式调用；它依赖 bs4、lxml、httpx、Pillow、click，"
     "pip 会自动补齐。注意不要用 venv：早期尝试在 venv 中安装时该环境缺少 pip 与 click，"
     "直接报“找不到解释器”，后来改为托管解释器 + 模块调用才稳定。")

h2("2.2　字体与外部程序")
cap("表 2-1　字体与外部程序用途")
table(["项目", "用途"],
      [["宋体 / 黑体", "文档正文与标题；DOCX 中通过 rFonts 的 eastAsia 显式指定"],
       ["Times New Roman", "西文与数字，与中文宋体混排"],
       ["Consolas", "本文档与报告附录中的代码段"],
       ["Matplotlib mathtext（cm）", "公式图渲染，避免依赖 LaTeX"],
       ["Microsoft Word", "更新目录域、导出 PDF（SaveAs2 格式号 17）"]],
      [5.2, 11.0])

body("绘图脚本中所有文字均使用 SimSun / SimHei，并在保存图片时去掉图内标题（标题统一由文档题注承担），"
     "这样图片插入 Word 后不会出现“图里一个标题、图下一个题注”的重复。")

h1("3　步骤 1：解析题目与课程要求")
body("三份输入材料格式不同，分别用三种方式读取：PDF 用 pdfplumber 逐页抽取文本，PPTX 用 python-pptx 遍历"
     "幻灯片与形状，DOCX 用 python-docx 读取表格结构。三者都不需要打开图形界面，便于反复核对。")

h2("3.1　PDF 题目抽取")
cmd_block('import pdfplumber\n'
          'with pdfplumber.open(r"D:\\1\\第2题-电路模型探究装置.pdf") as pdf:\n'
          '    for i, page in enumerate(pdf.pages):\n'
          '        print(f"===== 第 {i+1} 页 =====")\n'
          '        print(page.extract_text())')
body("直接整篇读入会超出上下文长度（约 3.5 万 token），改为抽取纯文本后按需检索，既省上下文又保留原文措辞。"
     "抽取结果确认了三组要求：已知模型电路（传递函数 H(s)=5/(10⁻⁸s²+3×10⁻⁴s+1)、幅频误差 ≤10%、"
     "输出幅度可调、正向增益 5）、探究装置（4 项基本要求）、发挥部分（未知模型自主学习与建模）。")

h2("3.2　PPTX 课程要求抽取")
cmd_block('from pptx import Presentation\n'
          'prs = Presentation(r"D:\\1\\电子信息工程专业科研训练.pptx")\n'
          'for idx, slide in enumerate(prs.slides, 1):\n'
          '    print(f"----- 第 {idx} 页 -----")\n'
          '    for shp in slide.shapes:\n'
          '        if shp.has_text_frame:\n'
          '            print(shp.text_frame.text)')
body("课程要求归纳为四条：2～3 人组队；必须完成课题调研与软件仿真/算法开发（硬件为选做）；"
     "提交科研讨论会议记录表与设计报告；考核含验收、答辩与报告，其中报告占 50%。这四条直接决定了交付物的形态——"
     "一份能独立读懂的设计报告，加一份过程可追溯的会议记录表。")

h2("3.3　会议记录表模板结构探测")
body("模板是空表，必须先弄清每张表的行列数与合并情况，才能准确写入。")
cmd_block('import docx\n'
          'd = docx.Document(r"D:\\1\\科研讨论会议记录表.docx")\n'
          'for i, t in enumerate(d.tables):\n'
          '    print(i, len(t.rows), "行", len(t.columns), "列")')
cap("表 3-1　模板表格结构")
table(["表号", "规模", "内容"],
      [["表 0", "2 行 × 4 列", "小组/周次、日期；成员姓名"],
       ["表 1", "4 行 × 4 列", "姓名、学号、完成的工作、结果/数据"],
       ["表 2", "4 行 × 2 列", "讨论的问题、结论（决议）及理由"],
       ["表 3", "4 行 × 3 列", "任务、谁做、何时完成"],
       ["表 4", "3 行 × 2 列", "困难、解决办法"]],
      [2.2, 3.4, 10.6])

h1("4　步骤 2：指标推导与方案定型")
body("题目给的传递函数是二阶低通的标准形，先把系数对应到标准式，所有指标就能一次算清：")
body("H(s) = 5 / (10⁻⁸s² + 3×10⁻⁴s + 1)　⟹　K = 5，ωn = 1×10⁴ rad/s，2ζωn = 3×10⁻⁴ ⟹ ζ = Q = 1/3。", indent=False)
body("Q < 0.5 意味着系统过阻尼，两个极点均为实数：p₁,₂ = −3819.7 / −26180.3 rad/s，"
     "对应 −3 dB 频率 f₋₃dB = 595.6 Hz。这一点很关键：过阻尼电路没有谐振峰，"
     "后面做未知模型辨识时“找峰值判类型”的思路从原理上就不成立。")

cap("表 4-1　已知模型电路的关键参数")
table(["参数", "数值", "来源"],
      [["直流增益 K", "5（14 dB）", "H(0) = 5"],
       ["自然频率 ωn", "1×10⁴ rad/s（1.59 kHz）", "s² 项系数 10⁻⁸"],
       ["品质因数 Q", "1/3", "s 项系数 3×10⁻⁴"],
       ["实极点", "−3819.7 / −26180.3 rad/s", "分母求根"],
       ["−3 dB 带宽", "595.6 Hz", "|H(jω)| = 5/√2"],
       ["阻尼特性", "过阻尼，无谐振峰", "Q < 0.5"]],
      [3.6, 6.2, 6.4])

h2("4.1　三条关键设计判断")
body("第一，拓扑选“单位增益 Sallen-Key 低通 + 同相放大 ×5”，而不是单级带增益的 Sallen-Key。"
     "单级结构中 Q 与增益共用同一组电阻，Q 对增益电阻的灵敏度极高，调增益就会破坏 Q；"
     "拆成两级后，前级只管 Q、后级只管增益，两者解耦，标定和调试都简单。")
body("第二，电容必须用 C0G 1%。4000 次蒙特卡洛显示：用 5% 精度电容时，有 8.3% 的电路超出 10% 幅频误差判据；"
     "换成 1% 电容并加 1 kHz 单点增益校准后，P99 误差降到 2.82%、最大 4.33%。"
     "这条结论是整份报告里最“值钱”的一条，也是答辩时最容易被追问的地方。")
body("第三，元件值按 E96 系列取整：R₁ = 3.83 kΩ、R₂ = 26.1 kΩ、C₁ = C₂ = 10 nF、Rf = 30 kΩ、Rg = 7.5 kΩ，"
     "取整后 ωn 与 Q 的偏差在 1% 以内，再由校准环节吸收。")

h1("5　步骤 3：设计曲线（design.py）")
body("design.py 承担三件事：把传递函数的关键频点算成表、做 4000 次容差蒙特卡洛、画三张图。"
     "脚本用 numpy.polynomial 求极点，用 scipy.signal.freqs 求频响，蒙特卡洛部分对 R、C 按容差抽样后重算 |H|，"
     "统计 10% 判据的超差率。")
cmd_block('"C:/Users/Yufei Ji/.workbuddy-ai/binaries/python/versions/3.13.12/python.exe" design.py')
cap("表 5-1　design.py 的输出")
table(["输出", "内容"],
      [["控制台", "极点、ωn、Q、f₋₃dB、100 Hz～3 kHz 关键频点的 |H| 与 dB、容差统计"],
       ["figs/fig3_bode.png", "幅频与相频特性，标注 f₋₃dB 与 100 Hz～3 kHz 工作段"],
       ["figs/fig4_wave.png", "1 kHz 正弦激励下的稳态输入/输出波形（Vpp = 2.531 V）"],
       ["figs/fig5_err.png", "幅频误差曲线与容差蒙特卡洛直方图"]],
      [4.6, 11.6])

body("画波形图时踩过一个坑：最初截取的是仿真起始的 1 个周期，此时暂态尚未衰减完，算出的 Vpp 只有 0.878 V，"
     "与理论值 2.526 V 差了三倍。改为仿真 5 ms 后取末尾 2000 点（稳态段），得到 2.531 Vpp，"
     "与理论值相差 0.2%，这才是可以写进报告的数。")

h1("6　步骤 4：图件绘制")
body("报告里的 8 张插图全部用 Matplotlib 绘制，没有用 Visio 或截图，原因有二：一是矢量级可控、分辨率统一；"
     "二是改参数即可重画，不必手工对齐。")

h2("6.1　原理图（sch.py）")
body("原理图最初用 schemdraw 画，但器件符号与自定义连线混排时线条错乱、跨线关系表达不出来。"
     "改为在 Matplotlib 坐标系里手绘：先用 ax.plot 画导线，再按坐标画电阻锯齿、电容双竖线、运放三角形，"
     "节点用实心圆点，跨线处画半圆 hop 表示不相连。这样每个元素的位置都精确可控，"
     "输出 300 dpi PNG 插进 Word 后依然清晰。")

h2("6.2　总体框图与流程图（blocks.py）")
body("框图用矩形 + 圆角框 + 箭头分层排布：信号源（DAC/DDS）→ 被测电路 → 测量通道（ADC + DFT）→ 主控（辨识与控制）→ 显示。"
     "流程图用圆角矩形表示步骤、菱形表示判断，主分支竖直、异常分支横出，避免连线交叉。"
     "两张图都去掉了图内标题，改由 Word 题注承担。")

h2("6.3　公式图（formulas.py）")
body("Word 里插公式有三种办法：OMML（原生公式）、图片、纯文本。考虑到 html→docx 转换链对 OMML 支持不稳定，"
     "这里统一渲染成图片：用 Matplotlib 的 mathtext（fontset = cm，贴近 LaTeX 的 Computer Modern），"
     "dpi = 300，透明背景，居中插入。6 张公式覆盖传递函数、标准形对应、Sallen-Key 的 ωn/Q 表达式、"
     "DFT 幅相提取、四模型拟合的加权残差、双线性变换。")

h1("7　步骤 5：未知模型辨识算法")
body("发挥部分要求装置自主判断未知模型的类型（低通/高通/带通/带阻）并给出参数。这一步的关键不是算法多复杂，"
     "而是先把“可观测到什么”想清楚。")

h2("7.1　由元件范围反推测量边界")
body("题目给的是 R、L、C 的取值范围。由 f₀ = 1/(2π√(LC)) 与 Q = (1/R)√(L/C) 可以反推出："
     "f₀ ∈ [5.03, 50.3] kHz，Q ∈ [0.01, 1]。这两个区间一次性定了三件事——扫频上限必须取 100 kHz"
     "（在最高 f₀ 之上留约一个数量级，否则带阻与低通在测量频段内形状趋同，无法区分）、"
     "采样率取 1 MSPS、以及分类不能靠找峰值（Q ≤ 1 时带通无谐振峰）。")

h2("7.2　四模型加权最小二乘")
body("做法是：对低通、高通、带通、带阻四种二阶模型分别做复频域加权最小二乘拟合，取残差最小者作为判定结果。"
     "这样一次拟合同时给出类型与 (K, ω₀, Q) 三个参数，不需要人为设阈值。"
     "拟合分两步：先在 (f₀, Q) 网格上粗搜（向量化广播，几秒完成），再用 Nelder-Mead 精修。"
     "早期版本用 least_squares 多起点，跑了十几分钟还被超时杀掉；改成网格 + 精修后降到几十秒。")

cap("表 7-1　辨识算法验证结果（200 次蒙特卡洛）")
table(["指标", "结果"],
      [["分类正确率", "100%（200/200）"],
       ["f₀ 相对误差（中位）", "0.43%"],
       ["f₀ 相对误差（90% 分位）", "3.63%"],
       ["Q 相对误差（中位）", "0.70%"],
       ["扫频点数 / 范围", "26 点，200 Hz～100 kHz 对数分布"]],
      [6.0, 10.2])

note("必须说清的局限", "端口幅相特性只能提供 f₀ 与 Q 两个独立方程，而未知量有 R、L、C 三个，"
                       "因此 R、L、C 不可唯一分离。报告里以 (K, ω₀, Q) 作为等效电路模型，"
                       "既满足“建模与推理输出”的要求，也避免过度解读。这一点写进正文，答辩时主动交代反而加分。")

h1("8　步骤 6：报告 HTML 组装（build_report.py）")
body("报告没有用 Word 手工排版，而是先用 Python 拼一份带语义样式的 HTML，再交给转换器生成 DOCX。"
     "这样做的理由是：24 页、21 张表、14 张图，手工排版几乎必然出现表宽不一致、图注错位、编号跳号；"
     "而 HTML 里的表格、题注、编号全部由函数生成，改一处即可全篇一致。")

h2("8.1　脚本结构")
body("build_report.py 共 752 行，分三段：第 1～22 行是样式常量（字号、行距、颜色、表格边框）；"
     "第 23～141 行是 9 个辅助函数——h1/h2/h3 生成标题，p 生成正文段，fig 生成“图 + 题注”并自动编号，"
     "table 生成“表 + 题注”并按列宽渲染，fml_img 插入公式图，note 生成提示框，bullets 生成列表；"
     "第 142 行之后是正文内容，按章顺序调用这些函数，最后拼成完整 HTML 写入 pipeline/stage2/。")
body("正文里所有图、表都通过函数调用产生，因此图号表号天然连续：图 1～图 8、表 1～表 21，"
     "不会出现手写编号漏改的情况。")

h2("8.2　输出")
cmd_block('"C:/Users/Yufei Ji/.workbuddy-ai/binaries/python/versions/3.13.12/python.exe" build_report.py\n'
          '# → pipeline/stage2/formatted-电路模型探究装置设计报告.html')

h1("9　步骤 7：HTML → DOCX 转换")
body("转换用 html-for-docx 模块，命令行一次完成。转换器会自动下载并内嵌图片、按 CSS 生成段落与表格样式，"
     "但中文字体、图片宽度、表格列宽这三项它处理不好，必须靠后处理脚本修正（见第 10 节）。")
cmd_block('cd "C:/Users/Yufei Ji/.workbuddy-ai/plugins/cache/workbuddy-builtin/tencent-docx/5.7.6-wb.40488862.g3e43260f.had9031c93ded/skills/html-to-docx/scripts"\n'
          '"C:/Users/Yufei Ji/.workbuddy-ai/binaries/python/versions/3.13.12/python.exe" -m html_to_docx convert \\\n'
          '    "D:\Agent\project\电路模型探究装置\文档/pipeline/stage2/formatted-电路模型探究装置设计报告.html" \\\n'
          '    -o "D:\Agent\project\电路模型探究装置\文档/电路模型探究装置-设计报告.docx"')

note("踩坑", "第一次转换后打开文档，中文全部显示为 MS Mincho（日文明朝体），正文变成微软雅黑。"
             "原因是转换器只写了 w:ascii/w:hAnsi，没有写 w:eastAsia，Word 于是按 theme1.xml 里的东亚字体回退。")

h1("10　步骤 8：DOCX 后处理（fix_docx.py）")
body("fix_docx.py 是整条流水线里最“脏”但最不可省的一环，它按顺序做六件事，每件事对应转换器的一个缺陷。")

cap("表 10-1　后处理六步")
table(["函数", "解决的问题", "做法"],
      [["set_rfonts", "中文回退 MS Mincho、正文变雅黑", "遍历所有 run，写全 ascii/hAnsi/eastAsia/hint 四个属性；正文宋体、标题黑体、西文 Times New Roman"],
       ["fix_styles", "标题样式带蓝色、段距过大", "重设 Heading 1/2/3 的字号、颜色（近黑）、段前段后"],
       ["fix_runs", "局部残留旧字体、字号", "对正文 run 统一 10.5 pt、行距 1.5、首行缩进 2 字符"],
       ["fix_images", "图片宽度 21.69 cm 溢出 14.66 cm 版心", "按宽高比匹配图片文件名，逐张设定宽度：框图 14.4、曲线 11.8、辨识图 12.6、流程图 7.6、公式图上限 13"],
       ["fix_tables", "表格列宽不生效、跨页断行难看", "cell.width + tblGrid/gridCol + tblW 三处同步；固定布局；首行重复；行内禁止跨页"],
       ["fix_theme", "theme1.xml 东亚字体仍是日文", "直接改写 theme1.xml 的 ea 字体为宋体"]],
      [2.8, 5.6, 7.8])

h2("10.1　表格列宽为什么必须改三处")
body("Word 的固定布局渲染时，优先读 w:tblGrid/gridCol 的宽度，其次才看单元格 tcW。"
     "只改 python-docx 的 cell.width，等于只改了 tcW，网格还是旧的，渲染出来依旧是原宽度——"
     "这是最容易误判为“设置没生效”的地方。三处同时改，并且把 tblW 从 auto 改成 dxa 并给出总宽，列宽才真正锁定。")

h2("10.2　图片宽度的按比例匹配")
body("转换器会把图片按原始像素尺寸插入，300 dpi 的公式图动辄 21 cm 宽，直接溢出页面。"
     "后处理时先读出每张图的像素宽高，按“目标宽度不超过版心、且不改变宽高比”的原则逐张设宽，"
     "并给不同类别的图设定不同目标宽：框图铺满、曲线略窄、流程图更窄，视觉上主次分明。")

h1("11　步骤 9：目录域与 PDF 导出")
body("目录不能手打。HTML 里留一个占位段落，转换成 DOCX 后用 Word 的 COM 接口插入真正的目录域并更新，"
     "页码、层级、点线全部由 Word 计算，后续改内容只需右键“更新域”。")
cmd_block('$word = New-Object -ComObject Word.Application\n'
          '$word.Visible = $false\n'
          '$doc = $word.Documents.Open("D:\Agent\project\电路模型探究装置\文档\\电路模型探究装置-设计报告.docx")\n'
          '$rng = $doc.Content\n'
          '$doc.TablesOfContents.Add($rng, $true, 1, 3) | Out-Null\n'
          '$doc.TablesOfContents.Item(1).Update()\n'
          '$doc.Save()\n'
          '$doc.SaveAs2("D:\Agent\project\电路模型探究装置\文档\\prev\\preview_report.pdf", 17)   # 17 = PDF\n'
          '$doc.Close(0); $word.Quit()')
body("加目录后页数从 30 页降到 24 页——不是因为删了内容，而是目录域把原先手工占位的大量空行替换成了紧凑的真实条目，"
     "同时后处理把图片宽度收进版心，段落回流更紧凑。")

h1("12　步骤 10：会议记录表生成（fill_minutes.py）")
body("模板是空表，脚本先把模板复制成 4 份，再逐格写入。写格子的关键函数是 fill_cell：先删掉单元格里除第一段以外的所有段落，"
     "再清空第一段的 run，然后按行写入并统一字体字号。合并单元格（如“成员姓名”横跨三列）只写一次，"
     "否则会出现重复文字。")
body("排版上做了四件事才把每份从 2 页压到 1 页：四张表统一铺满 14.6 cm 版心（21 − 3.17×2）；"
     "表内字号 8.5 pt、行距 1.0、段前后 0.5 pt；二级标题段前压到 6 pt；删掉模板里单元格级的 tcMar（上下各 96 twips），"
     "改由表格级 tblCellMar 统一控制。")

cap("表 12-1　会议记录表列宽（单位 cm，合计 14.6）")
table(["表", "列宽"],
      [["本周任务", "1.5 / 1.3 / 5.6 / 6.2"],
       ["讨论内容", "4.9 / 9.7"],
       ["下周任务", "6.0 / 3.0 / 5.6"],
       ["主要困难", "2.4 / 12.2"]],
      [3.4, 12.8])

note("细节", "“Sallen-Key”在窄列里会被 Word 从连字符处拆成两行（Sallen- / Key），观感很差。"
             "把普通连字符 U+002D 换成不换行连字符 U+2011 即可整词不断。")

body("另外，模板的 sectPr 里没有 pgSz/pgMar，页面尺寸完全依赖 Word 的本地默认值（中文版默认 A4、左右边距 3.17 cm），"
     "换到别的机器或 WPS 上可能变成 Letter。脚本里显式写入 A4 与边距，保证跨机器一致。")

h1("13　步骤 11：成品质检")
body("文档生成后不靠“看着差不多”，而是量化检查三项：页数、文字是否越界、逐页目检。")
cmd_block('import pymupdf\n'
          'd = pymupdf.open(r"D:\Agent\project\电路模型探究装置\文档\\prev\\mtg1.pdf")\n'
          'print("页数", d.page_count)\n'
          'mx = 0\n'
          'for b in d[0].get_text("dict")["blocks"]:\n'
          '    for l in b.get("lines", []):\n'
          '        for s in l["spans"]:\n'
          '            mx = max(mx, s["bbox"][2] / 72 * 2.54)\n'
          'print("文字最右端", round(mx, 2), "cm")     # 表格右边框 17.75 cm')
cap("表 13-1　质检结果")
table(["对象", "检查项", "结果"],
      [["设计报告", "页数 / 表数 / 图数", "24 页 / 21 表 / 14 图"],
       ["设计报告", "目录域", "真实域，页码与正文一致"],
       ["会议记录表", "页数", "4 份均为 1 页"],
       ["会议记录表", "文字右边界", "17.57 cm < 表格右边框 17.75 cm，无越界"],
       ["会议记录表", "视觉", "四节内容与签字行同页，无孤行"]],
      [3.6, 5.4, 7.2])

h1("14　问题与修复记录")
body("整个流程共遇到 13 个实质性问题，下表按“现象 → 原因 → 处理”记录，便于复现时直接绕开。")
cap("表 14-1　问题与修复")
table(["#", "现象", "原因", "处理"],
      [["1", "PDF 整篇读入超上下文", "图文混排、体量大", "pdfplumber 只抽文本"],
       ["2", "波形图 Vpp 仅 0.878 V", "窗口含未衰减的暂态", "取 5 ms 后末段稳态，得 2.531 Vpp"],
       ["3", "辨识分类正确率仅 56.4%", "Q<1 时无谐振峰，形状判据失效", "改四模型拟合取最小残差，正确率 100%"],
       ["4", "least_squares 多起点超时被杀", "计算量随起点数线性增长", "网格粗搜（向量化）+ Nelder-Mead 精修"],
       ["5", "schemdraw 原理图线条错乱", "自定义符号与自动连线冲突", "Matplotlib 坐标手绘 + hop 半圆跨线"],
       ["6", "html_to_docx 找不到解释器", "venv 缺 pip 与 click", "改用托管 Python 装 html-for-docx 后以模块调用"],
       ["7", "中文变 MS Mincho", "转换器未写 w:eastAsia", "统一 rFonts 四属性 + 改 theme1.xml"],
       ["8", "图片宽 21.69 cm 溢出页面", "按原始像素插入", "按宽高比逐张设宽"],
       ["9", "表格列宽不生效", "只改了 tcW，网格仍是旧的", "cell.width + gridCol + tblW 三处同步"],
       ["10", "手工目录排版难看", "占位行无法自动对齐页码", "TOC 域 + COM 更新，30 页 → 24 页"],
       ["11", "会议记录表 2 页", "版心未用满、行距偏大", "铺满 14.6 cm + 8.5 pt + 压缩段距 + 删 tcMar"],
       ["12", "“Sallen-Key”被拆行", "Word 在连字符处断行", "改用 U+2011 不换行连字符"],
       ["13", "PowerShell 导出 PDF 无输出", "变量名 $i周 被解析成变量名", "改为字符串拼接"]],
      [0.9, 5.0, 4.9, 5.4])

h1("15　一键复现")
body("把 9 个脚本按依赖顺序串成一条命令，即可从零重建全部交付物（Word 目录域与 PDF 导出仍需本机 Word）。")
cmd_block('#!/usr/bin/env bash\n'
          'set -e\n'
          'PY="C:/Users/Yufei Ji/.workbuddy-ai/binaries/python/versions/3.13.12/python.exe"\n'
          'cd "D:\Agent\project\电路模型探究装置\文档"\n'
          '\n'
          '"$PY" design.py          # 关键频点、容差、图 3/4/5\n'
          '"$PY" unknown.py         # 四模型拟合、图 6/7\n'
          '"$PY" blocks.py          # 图 1、图 8\n'
          '"$PY" sch.py             # 图 2\n'
          '"$PY" formulas.py        # 公式图 fml1-6\n'
          'bash make_report.sh      # 报告 HTML → DOCX → 后处理\n'
          '"$PY" fill_minutes.py    # 4 周会议记录表\n'
          '# 最后在 Word 中：更新目录域 → 导出 PDF')

body("运行顺序有依赖：figs/ 里的图必须先于 build_report.py 生成，否则 HTML 里会出现空图；"
     "fix_docx.py 必须在 html_to_docx 之后、目录域之前运行，否则字体会被目录更新覆盖。"
     "fill_minutes.py 独立于报告流水线，只依赖原始模板，可随时单独重跑。")

doc.add_page_break()

# ================================================================ 附录
h1("附录 A　全部源码")
body("以下代码与 源码/ 目录下的文件逐字一致，可直接复制运行。路径按 D:\Agent\project\电路模型探究装置\文档 布局写死，"
     "迁移到其他目录时需同步修改各脚本顶部的常量。")

FILES = [("A.1", "design.py", "传递函数解析、关键频点、容差蒙特卡洛与图 3/4/5"),
         ("A.2", "unknown.py", "四模型复频域拟合、200 次蒙特卡洛与图 6/7"),
         ("A.3", "blocks.py", "总体框图 fig1 与辨识流程图 fig8"),
         ("A.4", "sch.py", "已知模型电路原理图 fig2"),
         ("A.5", "formulas.py", "6 张公式图 fml1～fml6"),
         ("A.6", "build_report.py", "报告 HTML 组装（752 行）"),
         ("A.7", "fix_docx.py", "DOCX 字体、图宽、表宽、主题后处理"),
         ("A.8", "fill_minutes.py", "按模板生成 4 周会议记录表"),
         ("A.9", "make_report.sh", "报告流水线一键脚本")]

for tag, name, desc in FILES:
    path = os.path.join(SRC, name)
    with open(path, "r", encoding="utf-8") as f:
        src = f.read()
    n = src.count("\n") + (0 if src.endswith("\n") else 1)
    h2("%s　%s" % (tag, name))
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(4)
    r = p.add_run("路径：源码/%s　·　%d 行　·　%s" % (name, n, desc))
    r.font.size = Pt(9); r.font.color.rgb = RGBColor(0x55, 0x55, 0x55)
    _rf(r, "Times New Roman", SONG)
    code_block(src)

doc.save(OUT)
print("saved", OUT)
