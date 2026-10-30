# -*- coding: utf-8 -*-
"""生成《烧录与上电调试实操手册》"""
import os
from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

OUT = r"D:\Agent\project\电路模型探究装置\文档\烧录与上电调试实操手册.docx"
SONG, HEI, MONO = "宋体", "黑体", "Consolas"


def _rf(run, a, e):
    rPr = run._element.get_or_add_rPr()
    rf = rPr.find(qn("w:rFonts"))
    if rf is None:
        rf = OxmlElement("w:rFonts"); rPr.insert(0, rf)
    for k, v in (("w:ascii", a), ("w:hAnsi", a), ("w:eastAsia", e), ("w:cs", a), ("w:hint", "eastAsia")):
        rf.set(qn(k), v)


_SHD = ("w:tabs", "w:suppressAutoHyphens", "w:kinsoku", "w:wordWrap", "w:overflowPunct",
        "w:topLinePunct", "w:autoSpaceDE", "w:autoSpaceDN", "w:bidi", "w:adjustRightInd",
        "w:snapToGrid", "w:spacing", "w:ind", "w:contextualSpacing", "w:mirrorIndents",
        "w:suppressOverlap", "w:jc", "w:textDirection", "w:textAlignment",
        "w:textboxTightWrap", "w:outlineLvl", "w:divId", "w:cnfStyle", "w:rPr",
        "w:sectPr", "w:pPrChange")


def _shade(par, fill="F5F6F8", bar=True):
    pPr = par._p.get_or_add_pPr()
    if bar:
        bdr = OxmlElement("w:pBdr"); left = OxmlElement("w:left")
        left.set(qn("w:val"), "single"); left.set(qn("w:sz"), "18")
        left.set(qn("w:space"), "6"); left.set(qn("w:color"), "8FA8C8")
        bdr.append(left)
        pPr.insert_element_before(bdr, *(["w:shd"] + list(_SHD)))
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear"); shd.set(qn("w:color"), "auto"); shd.set(qn("w:fill"), fill)
    pPr.insert_element_before(shd, *_SHD)


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

hp = sec.header.paragraphs[0]; hp.alignment = WD_ALIGN_PARAGRAPH.CENTER
hr = hp.add_run("电路模型探究装置 · 烧录与上电调试实操手册")
hr.font.size = Pt(8.5); hr.font.color.rgb = RGBColor(0x66, 0x66, 0x66)
_rf(hr, "Times New Roman", SONG)

fp = sec.footer.paragraphs[0]; fp.alignment = WD_ALIGN_PARAGRAPH.CENTER
for seg, fld in (("第 ", None), ("", " PAGE "), (" 页　共 ", None), ("", " NUMPAGES "), (" 页", None)):
    if fld is None:
        r = fp.add_run(seg); r.font.size = Pt(9); _rf(r, "Times New Roman", SONG)
    else:
        r = fp.add_run()
        f1 = OxmlElement("w:fldChar"); f1.set(qn("w:fldCharType"), "begin")
        it = OxmlElement("w:instrText"); it.set(qn("xml:space"), "preserve"); it.text = fld
        f2 = OxmlElement("w:fldChar"); f2.set(qn("w:fldCharType"), "separate")
        t = OxmlElement("w:t"); t.text = "1"
        f3 = OxmlElement("w:fldChar"); f3.set(qn("w:fldCharType"), "end")
        for e in (f1, it, f2, t, f3):
            r._r.append(e)
        r.font.size = Pt(9); _rf(r, "Times New Roman", SONG)


def body(text, indent=True, size=10.5, bold=False, color=None, after=3, hang=False):
    p = doc.add_paragraph()
    pf = p.paragraph_format
    if hang:
        pf.left_indent = Cm(0.74); pf.first_line_indent = Cm(-0.74)
    else:
        pf.first_line_indent = Cm(0.74) if indent else None
    pf.line_spacing = 1.55; pf.space_before = Pt(0); pf.space_after = Pt(after)
    pf.alignment = WD_ALIGN_PARAGRAPH.LEFT
    r = p.add_run(text); r.font.size = Pt(size); r.bold = bold
    if color:
        r.font.color.rgb = color
    _rf(r, "Times New Roman", SONG)
    return p


def h1(text):
    p = doc.add_paragraph(style="Heading 1")
    pf = p.paragraph_format
    pf.space_before = Pt(14); pf.space_after = Pt(6); pf.line_spacing = 1.25
    pf.keep_with_next = True
    r = p.add_run(text); r.font.size = Pt(15); r.bold = True
    r.font.color.rgb = RGBColor(0x1F, 0x33, 0x4E)
    _rf(r, "Times New Roman", HEI)
    return p


def h2(text):
    p = doc.add_paragraph(style="Heading 2")
    pf = p.paragraph_format
    pf.space_before = Pt(10); pf.space_after = Pt(4); pf.line_spacing = 1.25
    pf.keep_with_next = True
    r = p.add_run(text); r.font.size = Pt(11.5); r.bold = True
    r.font.color.rgb = RGBColor(0x2A, 0x45, 0x66)
    _rf(r, "Times New Roman", HEI)
    return p


def cap(text):
    p = doc.add_paragraph()
    pf = p.paragraph_format
    pf.space_before = Pt(6); pf.space_after = Pt(2); pf.line_spacing = 1.2
    pf.keep_with_next = True
    r = p.add_run(text); r.font.size = Pt(9); r.bold = True
    r.font.color.rgb = RGBColor(0x33, 0x33, 0x33)
    _rf(r, "Times New Roman", HEI)
    return p


def code_block(text, size=8.5, line=11.0):
    lines = text.replace("\t", "    ").rstrip("\n").split("\n")
    for i, ln in enumerate(lines):
        p = doc.add_paragraph()
        pf = p.paragraph_format
        pf.space_before = Pt(5) if i == 0 else Pt(0)
        pf.space_after = Pt(6) if i == len(lines) - 1 else Pt(0)
        pf.line_spacing = Pt(line); pf.left_indent = Cm(0.28)
        r = p.add_run(ln if ln else " ")
        r.font.size = Pt(size); _rf(r, MONO, SONG)
        _shade(p)


def table(caption, header, rows, widths, size=8.5, align=None):
    if caption:
        cap(caption)
    # 页面可用宽度 21.0 - 2.4 - 2.4 = 16.2 cm，留出边框与内边距余量，硬上限 15.2 cm
    tot = sum(widths)
    if tot > 15.2:
        widths = [w * 15.2 / tot for w in widths]
    al = align or ["l"] * len(header)
    t = doc.add_table(rows=1, cols=len(header))
    t.style = "Table Grid"; t.alignment = WD_TABLE_ALIGNMENT.CENTER; t.autofit = False
    tblPr = t._tbl.tblPr
    # autofit=False 已经写入一个 tblLayout，不能再 append，否则重复元素会让 Word 拒绝导出
    lay = tblPr.find(qn("w:tblLayout"))
    if lay is None:
        lay = OxmlElement("w:tblLayout"); tblPr.append(lay)
    lay.set(qn("w:type"), "fixed")
    grid = t._tbl.find(qn("w:tblGrid"))
    for gc, w in zip(grid.findall(qn("w:gridCol")), widths):
        gc.set(qn("w:w"), str(int(Cm(w).twips)))
    tw = tblPr.find(qn("w:tblW"))
    if tw is None:
        tw = OxmlElement("w:tblW"); tblPr.append(tw)
    tw.set(qn("w:type"), "dxa"); tw.set(qn("w:w"), str(int(Cm(sum(widths)).twips)))

    idx = [0]

    def put(cell, text, bold=False, fill=None, center=False):
        cell.width = Cm(widths[idx[0]])
        p = cell.paragraphs[0]
        pf = p.paragraph_format
        pf.space_before = Pt(1.5); pf.space_after = Pt(1.5); pf.line_spacing = 1.12
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER if center else WD_ALIGN_PARAGRAPH.LEFT
        r = p.add_run(text); r.font.size = Pt(size); r.bold = bold
        _rf(r, "Times New Roman", HEI if bold else SONG)
        if fill:
            tcPr = cell._tc.get_or_add_tcPr()
            shd = OxmlElement("w:shd")
            shd.set(qn("w:val"), "clear"); shd.set(qn("w:color"), "auto"); shd.set(qn("w:fill"), fill)
            tcPr.append(shd)

    for j, htxt in enumerate(header):
        idx[0] = j
        put(t.rows[0].cells[j], htxt, bold=True, fill="E8EDF4", center=True)
    for row in rows:
        cells = t.add_row().cells
        for j, val in enumerate(row):
            idx[0] = j
            put(cells[j], str(val), center=(al[j] == "c"))
    trPr = t.rows[0]._tr.get_or_add_trPr()
    th = OxmlElement("w:tblHeader"); th.set(qn("w:val"), "true"); trPr.append(th)
    for row in t.rows:
        rp = row._tr.get_or_add_trPr()
        cs = OxmlElement("w:cantSplit"); cs.set(qn("w:val"), "true")
        rp.insert_element_before(cs, "w:trHeight", "w:tblHeader", "w:tblCellSpacing",
                                 "w:jc", "w:hidden", "w:ins", "w:del", "w:trPrChange")
    doc.add_paragraph().paragraph_format.space_after = Pt(2)


def note(title, text):
    p = doc.add_paragraph()
    pf = p.paragraph_format
    pf.left_indent = Cm(0.5); pf.space_before = Pt(4); pf.space_after = Pt(4)
    pf.line_spacing = 1.4
    r = p.add_run(title + "　"); r.font.size = Pt(9.5); r.bold = True
    r.font.color.rgb = RGBColor(0xA8, 0x4B, 0x2A)
    _rf(r, "Times New Roman", HEI)
    r2 = p.add_run(text); r2.font.size = Pt(9.5)
    r2.font.color.rgb = RGBColor(0x44, 0x44, 0x44)
    _rf(r2, "Times New Roman", SONG)
    _shade(p, "FDF6EC", bar=False)


def warn(title, text):
    p = doc.add_paragraph()
    pf = p.paragraph_format
    pf.left_indent = Cm(0.5); pf.space_before = Pt(4); pf.space_after = Pt(4)
    pf.line_spacing = 1.4
    r = p.add_run(title + "　"); r.font.size = Pt(9.5); r.bold = True
    r.font.color.rgb = RGBColor(0xB0, 0x20, 0x20)
    _rf(r, "Times New Roman", HEI)
    r2 = p.add_run(text); r2.font.size = Pt(9.5)
    r2.font.color.rgb = RGBColor(0x44, 0x44, 0x44)
    _rf(r2, "Times New Roman", SONG)
    _shade(p, "FDECEC", bar=False)


def bullets(items, size=10.5):
    for it in items:
        p = doc.add_paragraph()
        pf = p.paragraph_format
        pf.left_indent = Cm(0.86); pf.first_line_indent = Cm(-0.36)
        pf.line_spacing = 1.5; pf.space_before = Pt(0); pf.space_after = Pt(2)
        r0 = p.add_run("· "); r0.font.size = Pt(size); _rf(r0, "Times New Roman", SONG)
        r = p.add_run(it); r.font.size = Pt(size); _rf(r, "Times New Roman", SONG)


# ------------------------------------------------------------------ 封面
for _ in range(3):
    doc.add_paragraph()

p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = p.add_run("烧录与上电调试实操手册")
r.font.size = Pt(28); r.bold = True
r.font.color.rgb = RGBColor(0x1F, 0x33, 0x4E)
_rf(r, "Times New Roman", HEI)

p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
p.paragraph_format.space_before = Pt(8)
r = p.add_run("电路模型探究装置　·　从 Keil 编译产物到五级功能验证")
r.font.size = Pt(12); r.font.color.rgb = RGBColor(0x55, 0x66, 0x77)
_rf(r, "Times New Roman", SONG)

p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
p.paragraph_format.space_before = Pt(26)
r = p.add_run("STM32F407VET6　|　纯寄存器固件　|　USB DFU 烧录")
r.font.size = Pt(10.5); r.font.color.rgb = RGBColor(0x88, 0x88, 0x88)
_rf(r, "Times New Roman", SONG)

for _ in range(6):
    doc.add_paragraph()

p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = p.add_run("本手册假定你已经按 F7 编译通过（0 Error）。\n"
              "若还没有，先看《Keil 手动建工程指南（不用 CubeMX）》。")
r.font.size = Pt(10); r.font.color.rgb = RGBColor(0x66, 0x66, 0x66)
_rf(r, "Times New Roman", SONG)

p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
p.paragraph_format.space_before = Pt(18)
r = p.add_run("2026 年 10 月")
r.font.size = Pt(10.5); r.font.color.rgb = RGBColor(0x66, 0x66, 0x66)
_rf(r, "Times New Roman", SONG)

doc.add_page_break()

# ------------------------------------------------------------------ 1
h1("1　全流程一览")

body("从按下 F7 到五级验证全部通过，一共六步。下面这张表是全貌，后面每章展开一步。"
     "建议打印出来放在实验台上，做完一步勾一笔。")

table("表 1　六步流程与完成判据",
      ["步骤", "你要做的动作", "完成判据", "耗时"],
      [["1　确认产物", "看 Build Output 与 Objects 目录", "0 Error 且 CircuitModel.hex 存在", "1 min"],
       ["2　接线", "按档位接 PA4 / PA0 / PA2 / PA3 / GND", "万用表通断确认，共地", "10 min"],
       ["3　进 DFU", "BOOT0 接 3V3，按复位", "设备管理器出现 0483:DF11", "2 min"],
       ["4　烧录", "CubeProgrammer 下载 hex", "Download verified successfully", "3 min"],
       ["5　退 DFU", "拔杜邦线，BOOT0 回 GND，按复位", "串口打出菜单横幅", "1 min"],
       ["6　验证", "逐级发串口命令", "五级全过（L1~L5）", "30 min"]],
      widths=[18, 52, 56, 14], align=["l", "l", "l", "c"])

note("顺序不能换", "先接线再烧录是错的。接线时板子带电、杜邦线插拔打火，很容易把 PA0 灌进过压。"
     "正确顺序是：先断电接线 → 再进 DFU 烧录 → 最后上电验证。")

note("有 ST-Link 就别走这条路", "如果手上有 ST-Link V2，第 4、5 章整段可以跳过——不用拨 BOOT0、"
     "不用装 CubeProgrammer，Keil 里按 F8 直接下载，还能在线调试。具体看《ST-Link 烧录与在线调试速查》。"
     "本文第 2、3、6、7、8、9、10 章对两种方式都适用。")

warn("烧录软件三选一。", "① ST-Link：Keil 里按 F8，不用另装软件；"
     "② 本项目自带的 DFU 烧录工具（工具\\DFU烧录工具\\flash.bat），不需要 CubeProgrammer，"
     "但要先用 Zadig 给它绑一次 WinUSB 驱动；"
     "③ STM32CubeProgrammer：官方工具，自带驱动，但要注册 ST 账号才能下载。三选一即可。")

# ------------------------------------------------------------------ 2
h1("2　第 1 步：确认编译产物")

h2("2.1　Build Output 里的四个判据")

body("F7 之后，Build Output 窗口最后几行必须同时满足下面四条。少一条都别往下走。")

table("表 2　Build Output 的四个判据",
      ["判据", "长什么样", "不满足说明什么"],
      [["① 错误数", "\".\\Objects\\CircuitModel.axf\" - 0 Error(s), 0 Warning(s).", "有 Error 就是没编译成功，回上一步"],
       ["② 尺寸行", "Program Size: Code=17324 RO-data=1404 RW-data=28 ZI-data=18532", "没有这行 = 根本没链接"],
       ["③ 转 hex", "FromELF: creating hex file...", "没有这行 = Create HEX File 没勾"],
       ["④ 目标行", "Target created.", "出现 Target not created = 链接失败"]],
      widths=[16, 78, 46], align=["c", "l", "l"])

body("Code 在 17~20 KB、ZI-data 在 18 KB 左右都是正常的。ZI-data 主要是三块："
     "DDS 正弦表 2 KB、ADC 采样缓冲 8 KB、栈 4 KB，加起来 14 KB，其余是各模块的静态缓冲。")

h2("2.2　Objects 目录里应该有什么")

body("去 D:\\Agent\\project\\电路模型探究装置\\Objects\\ 看一眼，下面这些文件必须都在：")

table("表 3　Objects 目录清单",
      ["文件", "大小量级", "作用", "缺了会怎样"],
      [["CircuitModel.hex", "约 60 KB 文本", "烧录用的镜像", "无法烧录，检查 Create HEX File"],
       ["CircuitModel.axf", "约 300 KB", "带调试信息的 ELF", "说明链接没跑完"],
       ["CircuitModel.map", "约 40 KB", "内存映射表，查符号地址", "不影响烧录"],
       ["CircuitModel.lnp", "约 0.5 KB", "链接器命令行，排查用", "不影响烧录"],
       ["7 个 .o + startup.o", "合计约 80 KB", "各文件目标码", "增量编译会重来"],
       ["CircuitModel.build_log.htm", "约 3 KB", "本次构建的完整日志", "不影响烧录"]],
      widths=[44, 24, 42, 34], align=["l", "c", "l", "l"])

h2("2.3　hex 文件自检三招")

body("hex 是文本格式，用记事本打开就能查。三步确认它不是个空壳：")

body("第一招，看首行。必须是", indent=True)
code_block(":020000040800F2")
body("这一行是「扩展线性地址记录」，含义是把高 16 位地址设为 0x0800。也就是说后续数据全部落在 "
     "0x08000000 起的 Flash 里。如果你的首行是 :020000040000FA，说明链接地址错了，烧进去也不跑。", indent=True)

body("第二招，看第二行前 8 个字符。", indent=True)
code_block(":1000000080480020...")
body("紧跟地址 0000 的四个字节 80 48 00 20 是小端表示的 0x20004880，即初始栈指针，"
     "落在 SRAM 范围内（0x20000000~0x20020000）。再往后四个字节是 Reset_Handler 地址，"
     "末位一定是奇数（Thumb 位），且落在 0x0800xxxx 区间。", indent=True)

body("第三招，看最后一行。", indent=True)
code_block(":00000001FF")
body("这是文件结束记录。没有它说明文件被截断了，多半是磁盘满或杀毒软件拦截。", indent=True)

h2("2.4　产物异常对照")

table("表 4　产物异常与处置",
      ["现象", "原因", "处置"],
      [["Objects 里没有 .hex", "Options → Output 里 Create HEX File 没勾", "勾上后重新 F7"],
       ["hex 只有几百字节", "启动文件没参与链接，代码没进去", "检查 startup_stm32f407xx.s 是否在工程树里"],
       ["Program Size 全是 0", "链接失败但 uVision 没报错（罕见）", "看 .map 文件，或 Clean Targets 后重建"],
       ["hex 首行是 :020000040000FA", "scatter 文件起始地址写错", "检查 CircuitModel.sct 的 LR_IROM1 0x08000000"],
       ["每次 F7 都全量重编", "Objects 被清过或 uvoptx 损坏", "无所谓，1 秒的事"]],
      widths=[46, 62, 52], align=["l", "l", "l"])

# ------------------------------------------------------------------ 3
h1("3　第 2 步：接线")

h2("3.1　三条铁律")

warn("铁律一：必须共地。", "板子的 GND、USB-TTL 模块的 GND、示波器探头的地夹、被测电路的地，"
     "必须全部连在一起。只连信号线不连地，串口一定是乱码，示波器上是一条 50 Hz 的粗带。")

warn("铁律二：PA0 只能吃 0~3.3 V。", "ADC 输入绝对上限是 VDDA+0.3 V，即 3.6 V。"
     "已知模型电路增益是 5 倍，如果你把激励设成 1 Vpp 再接到它输入端，输出就是 5 Vpp，"
     "直接灌进 PA0 会打穿输入保护二极管。接已知模型前必须先把激励降到 0.4 Vpp 以下。")

warn("铁律三：断电接线。", "所有杜邦线都在板子断电时插好，再上电。带电插拔 PA4/PA0 时，"
     "杜邦线公针的抖动会在瞬间产生几伏的感应尖峰。")

h2("3.2　引脚总表")

table("表 5　本工程用到的全部引脚",
      ["功能", "引脚", "方向", "接到哪里", "备注"],
      [["DAC 激励输出", "PA4", "输出", "示波器 / 被测电路输入", "0~3.3 V 单极性，中心 1.65 V"],
       ["ADC 测量输入", "PA0", "输入", "被测电路输出", "严禁超过 3.3 V"],
       ["串口 TX", "PA2", "输出", "USB-TTL 的 RXD", "AF7，115200 8N1"],
       ["串口 RX", "PA3", "输入", "USB-TTL 的 TXD", "AF7"],
       ["USB DFU", "PA11 / PA12", "双向", "板载 Type-C 直连", "不用外接"],
       ["电源", "5V / 3V3", "—", "USB 供电", "—"],
       ["地", "GND", "—", "所有设备共地", "至少接 2 根"]],
      widths=[30, 20, 14, 44, 44], align=["l", "c", "c", "l", "l"])

note("TX 接 RX，别接反", "PA2 是单片机往外发，所以要接 USB-TTL 模块的 RXD；PA3 是单片机往里收，"
     "接模块的 TXD。接反了不会烧，但串口助手一个字符都收不到。")

h2("3.3　三档接法，按你的目的选")

body("不需要一次把全部线接上。按当前要验证的东西分三档，从简到繁。")

cap("A 档：只看串口（验证固件是否跑起来）")
table("表 6　A 档接线：只需 3 根线",
      ["板子", "USB-TTL 模块", "作用"],
      [["PA2", "RXD", "单片机发数据给电脑"],
       ["PA3", "TXD", "电脑发命令给单片机"],
       ["GND", "GND", "共地，不可省"]],
      widths=[40, 46, 74], align=["c", "c", "l"])
body("这一档只验证「固件活着、串口通、命令行能用」。PA4 和 PA0 都空着，"
     "M 命令会测到噪声，这是正常的。", indent=True)

cap("B 档：加示波器看 DAC 波形")
table("表 7　B 档接线：在 A 档基础上加一路",
      ["板子", "示波器", "作用"],
      [["PA4", "探头尖端（CH1）", "看 DAC 输出正弦"],
       ["GND", "探头地夹", "共地"]],
      widths=[40, 46, 74], align=["c", "c", "l"])
body("示波器设 DC 耦合、垂直 1 V/div、时基按频率调。你会看到一条以 1.65 V 为中心、"
     "0~3.3 V 之间摆动的正弦。注意它是阶梯状的——DAC 以 1 MSPS 更新，"
     "1 kHz 时一个周期只有 1000 个点，放大后能看到台阶，这是正常的，不是坏了。", indent=True)

cap("C 档：完整回环（做幅频测量与辨识）")
table("表 8　C 档接线：DAC 经被测网络回到 ADC",
      ["板子", "被测电路", "作用"],
      [["PA4", "网络输入端", "施加激励"],
       ["PA0", "网络输出端", "测量响应"],
       ["GND", "网络地", "共地"]],
      widths=[40, 46, 74], align=["c", "c", "l"])
body("如果只是想验证「测量链路本身通不通」，可以跳过被测网络，用一根杜邦线把 PA4 直接接到 PA0。"
     "这时 M 命令读回的 Vpp 应该等于 A 命令设定的值，误差在 3% 以内。"
     "这一步过了，再上真实网络。", indent=True)

h2("3.4　已知模型电路怎么搭")

body("已知模型的传递函数是 H(s) = 5 / (1e-8·s² + 3e-4·s + 1)，标准二阶低通形式，"
     "读出三个特征量：直流增益 K = 5、自然频率 fn = 1591.5 Hz、品质因数 Q = 1/3。"
     "因为 Q < 0.5 是过阻尼，两个极点都是实数（607.9 Hz 与 4166.6 Hz），"
     "所以幅频曲线单调下降，没有谐振峰。")

body("拓扑采用「单位增益 Sallen-Key 二阶低通 + 同相放大 ×5」两级结构。"
     "这样做的理由是把 Q 和增益解耦：单级 Sallen-Key 里 Q 由增益决定，"
     "调增益会把 Q 一起带偏，两级结构可以独立调。")

table("表 9　已知模型电路元件清单",
      ["位号", "参数", "精度 / 介质", "作用"],
      [["R1", "3.83 kΩ", "金属膜 1%", "决定 fn"],
       ["R2", "26.1 kΩ", "金属膜 1%", "决定 fn 与 Q"],
       ["C1", "10 nF", "C0G（NP0）1%", "决定 fn 与 Q"],
       ["C2", "10 nF", "C0G（NP0）1%", "决定 fn 与 Q"],
       ["Rf", "30 kΩ", "金属膜 1%", "决定增益 K"],
       ["Rg", "7.5 kΩ", "金属膜 1%", "决定增益 K"],
       ["A1 / A2", "OPA2134", "双运放一片", "低通级 + 增益级"]],
      widths=[26, 40, 48, 46], align=["c", "c", "l", "l"])

warn("电容必须是 C0G，不能用 X7R。", "C1、C2 直接决定 fn 与 Q。X7R 陶瓷电容的容值随电压和温度"
     "可以漂 ±15%，幅频特性会严重偏离理论值，100 Hz~3 kHz 内的误差会从 1% 级劣化到 15% 级，"
     "直接判不合格。买的时候认准 C0G 或 NP0 介质、1% 精度。")

body("供电注意：OPA2134 是双电源运放，典型 ±5 V 到 ±15 V。如果你的板子只有单 3.3 V，"
     "要么另配一路 ±5 V，要么换成单电源轨到轨运放（如 OPA2350、TLV2372），"
     "并把偏置抬到 VCC/2。这一点务必在搭电路前确认，否则输出会削顶。")

h2("3.5　接线自检清单")

body("接完线、上电之前，用万用表蜂鸣档逐条确认：")

bullets([
    "PA4 与 PA0 之间没有短路（如果你接的是回环线，那这两点本来就该通，跳过这条）",
    "PA2 接的是 USB-TTL 的 RXD，PA3 接的是 TXD，没有接反",
    "板子 GND 与 USB-TTL 的 GND 之间蜂鸣器响",
    "板子 GND 与示波器探头地夹之间蜂鸣器响",
    "PA0 对 GND 的电阻不是 0 Ω（是 0 说明短路了）",
    "BOOT0 跳线当前在 GND 侧（烧录前才改到 3V3）",
    "被测电路自己单独上电时，输出端对地电压在 0~3.3 V 之间",
])

# ------------------------------------------------------------------ 4
h1("4　第 3 步：进 DFU")

h2("4.1　准备烧录软件")

note("可以跳过这一节", "如果不想装 CubeProgrammer，用工具目录下的「DFU烧录工具」即可："
     "双击 flash.bat 就完成烧录，只要先用 Zadig 给 STM32 BOOTLOADER 绑一次 WinUSB 驱动。"
     "下面的内容是给选择 CubeProgrammer 的人看的。")

body("CubeProgrammer 是 ST 的官方烧录工具，和 Keil、CubeMX 都不是一个东西。"
     "Keil 的 Download 按钮只认 ST-Link 调试器，而 USB DFU 走的是芯片内置 bootloader，所以需要专门的工具。")

table("表 10　烧录软件与其它工具的区别",
      ["工具", "作用", "本装置是否需要"],
      [["Keil µVision", "编译、链接、生成 hex", "需要，用来出 hex"],
       ["STM32CubeMX", "图形化配置引脚与时钟，生成初始化代码", "不需要（本工程纯寄存器）"],
       ["STM32CubeProgrammer", "通过 USB / SWD 把 hex 写进芯片", "可选，与自带 DFU 工具二选一"],
       ["Zadig", "给 DFU 设备绑 WinUSB 驱动", "用自带 DFU 工具时需要"],
       ["ST-Link 驱动", "配合 ST-Link 硬件使用", "走 SWD 才需要"]],
      widths=[44, 62, 52], align=["l", "l", "l"])

body("下载地址是 www.st.com/en/development-tools/stm32cubeprog.html。"
     "页面底部选 Windows 版压缩包，下载前需要登录 ST 账号（免费注册）。"
     "文件约 200 MB，解压后直接运行 SetupSTM32CubeProgrammer_x.x.x.exe，一路默认即可。")

note("安装时会装驱动", "安装过程中会一并装上 STM32 DFU 驱动和 ST-Link 驱动。"
     "装完必须重启一次，否则插上板子设备管理器里可能是「未知设备」。")

body("装完之后开始菜单里会有两个入口：图形界面的 STM32CubeProgrammer 和命令行的 "
     "STM32_Programmer_CLI。日常用图形界面就够了。")

h2("4.2　操作顺序")

body("STM32F407 出厂自带一段 ROM bootloader，上电时它会检查 BOOT0 引脚电平。"
     "BOOT0 = 0 时从 Flash 启动跑你的程序，BOOT0 = 1 时进入 USB DFU 模式，"
     "等待电脑通过 USB 下载固件。所以「进 DFU」这个动作，本质就是把 BOOT0 拉高再复位。")

body("按下面五步做，一步都不要省：")

bullets([
    "断电（拔掉 USB 线）",
    "找到板子上的 BOOT0 排针，通常是标着 BT0 或 BOOT0 的一根针，旁边紧挨着 3V3 和 GND",
    "用一根杜邦线（母对母）把 BOOT0 与 3V3 短接",
    "插上 USB 线供电",
    "按一下板子上的 NRST（复位）键",
])

body("顺序很重要：必须先短接再上电。如果先上电再短接，芯片已经按 BOOT0 = 0 启动了，"
     "这时候改电平不会生效，必须补按一次复位。")

h2("4.3　确认真的进了 DFU")

body("打开「设备管理器」，展开「通用串行总线设备」，应该出现一个叫 STM32 BOOTLOADER 的设备。"
     "右键 → 属性 → 详细信息 → 硬件 ID，应该看到：")

code_block("USB\\VID_0483&PID_DF11&REV_2200")

body("0483 是 STMicroelectronics 的厂商号，DF11 是 STM32 的 DFU 产品号。"
     "看到这个就说明芯片已经在 DFU 模式，等电脑发固件了。")

body("如果设备管理器里显示的是「未知设备」带黄色感叹号，说明驱动没装。"
     "装 STM32CubeProgrammer 时会一并装上 STM32 DFU 驱动，装完重插一次 USB 即可。")

h2("4.4　进不去 DFU 怎么查")

table("表 11　进 DFU 失败排查",
      ["现象", "可能原因", "处置"],
      [["设备管理器完全没反应", "USB 线是纯充电线（无数据线芯）", "换一根能传数据的线"],
       ["显示未知设备 + 黄色感叹号", "DFU 驱动未安装", "装 CubeProgrammer，或手动指定 STM32 DFU 驱动"],
       ["显示 0483:DF11 但 CubeProgrammer 连不上", "被别的软件占用", "关掉 CubeMX、Keil 的 Debug 会话"],
       ["连上了但读不到 Flash 大小", "BOOT0 没真正拉高", "万用表量 BOOT0 对 GND 是不是 3.3 V"],
       ["反复掉线", "USB 供电不足或线太长", "换主板后置 USB 口，不用 Hub"],
       ["板子上电后跑的是老程序", "BOOT0 仍是 0", "断电 → 短接 → 上电 → 复位，重来一遍"]],
      widths=[46, 50, 62], align=["l", "l", "l"])

# ------------------------------------------------------------------ 5
h1("5　第 4 步：烧录")

h2("5.1　连接")

body("打开 STM32CubeProgrammer。右上角有一排连接方式图标，选最左边的 USB（图标像 USB 插头）。"
     "点它右边的刷新按钮，Port 下拉框里应该出现一个 USART 或 USB1 的条目，选中它，点 Connect。")

table("表 12　连接参数",
      ["项", "取值", "说明"],
      [["连接方式", "USB", "不是 UART，不是 ST-LINK"],
       ["Port", "USB1", "只有一个 DFU 设备时通常就这一项"],
       ["波特率", "不用设", "USB 方式没有波特率"],
       ["RDP", "保持默认", "读保护，不要去改"]],
      widths=[30, 40, 88], align=["l", "l", "l"])

body("连上之后，右侧信息栏会显示芯片信息。核对三项：")

table("表 13　芯片信息核对",
      ["字段", "应该是", "对不上说明"],
      [["Device", "STM32F407xx / STM32F4x7", "接的不是 F407，或 BOOT0 没拉高"],
       ["Device ID", "0x413", "0x413 才是 F405/F407/F415/F417 系列"],
       ["Flash size", "512 KBytes", "读成 0 说明通信有问题"],
       ["Voltage", "约 3.3 V", "低于 2.7 V 会烧录失败"]],
      widths=[34, 46, 78], align=["l", "l", "l"])

h2("5.2　擦除（推荐做）")

body("左侧点开 Erasing & Programming。如果之前烧过别的程序，先做一次全片擦除，"
     "避免旧数据残留导致奇怪问题。选 Full chip erase，点 Start Erasing。"
     "512 KB 大约 5~10 秒。")

body("如果只是重复烧同一个工程，可以跳过擦除，直接下载——CubeProgrammer 会自动按扇区擦。")

h2("5.3　下载")

body("同一页面往下，File path 右边的浏览按钮，选中：")

code_block("D:\\Agent\\project\\电路模型探究装置\\Objects\\CircuitModel.hex")

body("然后确认三个勾选框：")

table("表 14　下载选项",
      ["选项", "是否勾选", "原因"],
      [["Verify programming", "必须勾", "下载后回读比对，能抓出坏块"],
       ["Run after programming", "可以不勾", "勾了会自动跳转，但 BOOT0 还在 3V3 时跳不过去"],
       ["Skip flash erase before programming", "不勾", "让它自己擦，省心"]],
      widths=[62, 30, 66], align=["l", "c", "l"])

body("点 Start Programming。进度条走完，日志区出现绿色字样：")

code_block("File download complete\n"
           "File download verified successfully")

body("看到这两行就成功了。如果只出现第一行没有第二行，说明校验失败，"
     "多半是 Flash 有坏块或者供电不稳，重烧一次；连续失败就换块板子。")

h2("5.4　退出 DFU")

warn("这一步最容易忘。", "烧完必须把 BOOT0 拨回 GND 再复位，否则芯片会一直停在 bootloader 里，"
     "你的程序根本不会跑，串口一片安静，然后你会以为是固件有问题，白查一小时。")

bullets([
    "拔掉 USB 线（断电）",
    "把 BOOT0 上的杜邦线从 3V3 拔下来，插到 GND（或者直接拔掉整根线，多数板子有下拉电阻）",
    "插回 USB 线",
    "按一下 NRST 键",
])

body("这时候芯片从 0x08000000 开始执行，也就是你刚烧进去的向量表，程序开始跑。")

h2("5.5　烧录报错对照")

table("表 15　CubeProgrammer 常见报错",
      ["报错", "原因", "处置"],
      [["No STM32 target found", "没进 DFU，或 USB 线无数据线芯", "回第 4 章重进 DFU，换线"],
       ["Error: Activating device: KO", "BOOT0 电平不对，或芯片被读保护", "量 BOOT0 电压；必要时用 Full chip erase 解保护"],
       ["Dev target not reset", "复位引脚被外部拉死", "检查 NRST 有没有被别的电路拉住"],
       ["File download complete 但 verify 失败", "供电不稳或 Flash 坏块", "换 USB 口重烧；连换两次失败换板"],
       ["Connection lost during download", "USB 线太长或经过 Hub", "直连主板后置 USB 口"],
       ["读到的 Flash 只有 128 KB", "接的是 F401/F411 之类", "确认板子型号是 F407VE"]],
      widths=[56, 50, 52], align=["l", "l", "l"])

# ------------------------------------------------------------------ 6
h1("6　第 5 步：上电看串口")

h2("6.1　串口助手设置")

table("表 16　串口参数",
      ["项", "取值"],
      [["端口", "USB-TTL 模块对应的 COM 号（设备管理器里查）"],
       ["波特率", "115200"],
       ["数据位", "8"],
       ["停止位", "1"],
       ["校验", "None"],
       ["流控", "全部关闭（RTS/CTS、XON/XOFF 都不勾）"],
       ["编码", "UTF-8 或 GBK 都行（固件只发 ASCII）"],
       ["发送结尾", "加回车换行（\\r\\n），否则命令不会被执行"]],
      widths=[30, 128], align=["l", "l"])

note("一定要加回车", "固件的命令解析是在收到 \\r 或 \\n 时才触发执行的。串口助手里如果发送结尾设成「无」，"
     "你打 F1000 它只会攒在缓冲区里，永远不执行。这是最常见的「命令没反应」原因。")

h2("6.2　上电后应该看到什么")

body("按一下 NRST，串口窗口应该立刻打出：")

code_block("==== Circuit Model Explorer (STM32F407VET6, bare-metal) ====\n"
           "SYSCLK = 168000000 Hz, DAC fs = 1000000 SPS, ADC fs = 500000 SPS, N = 4096\n"
           "Ready. Type ? for help.")

body("这三行信息量很大，逐条读：")

table("表 17　启动横幅的含义",
      ["字段", "值", "说明"],
      [["SYSCLK", "168000000", "PLL 锁定了，时钟树对。若是 16000000 说明 PLL 没起来"],
       ["DAC fs", "1000000", "TIM6 分频对，DAC 每秒更新 100 万次"],
       ["ADC fs", "500000", "TIM3 分频对"],
       ["N", "4096", "每次采集 4096 点，窗口 8.192 ms"]],
      widths=[30, 40, 88], align=["l", "c", "l"])

body("按 ? 再回车，应该回显两行帮助。能回显就说明接收方向也通了。")

h2("6.3　串口没输出怎么查")

table("表 18　串口无输出排查（按概率排序）",
      ["检查项", "怎么查", "说明"],
      [["① BOOT0 是否回到 GND", "万用表量 BOOT0 对 GND 应为 0 V", "最常见原因，占一半以上"],
       ["② TX/RX 是否接反", "PA2 接模块 RXD，PA3 接模块 TXD", "接反了收不到任何字符"],
       ["③ 是否共地", "量板子 GND 与模块 GND 通断", "不共地必然乱码或无输出"],
       ["④ 波特率", "确认助手设的是 115200", "设成 9600 会看到一堆乱码"],
       ["⑤ COM 口选错", "设备管理器看哪个 COM 是 USB-TTL", "插拔一次看哪个 COM 消失"],
       ["⑥ 板子有没有供电", "板载电源灯亮不亮", "USB 线是纯充电线时灯也亮但不通数据"],
       ["⑦ 固件是不是真烧进去了", "重新烧一次，看 verify 结果", "verify 失败说明镜像没进去"],
       ["⑧ 芯片是否 HardFault", "接 ST-Link 看 PC 停在哪", "通常是 FPU 没开，检查 SystemInit"]],
      widths=[38, 62, 58], align=["l", "l", "l"])

body("排查顺序建议从 ① 往下。前三条能覆盖 90% 的情况。")

# ------------------------------------------------------------------ 7
h1("7　第 6 步：五级验证")

body("五级验证是一层一层往上搭的：每一级只引入一个新的不确定因素，"
     "这样一旦出问题，原因一定在刚引入的那一环。跳级验证是最费时间的做法。")

h2("7.1　L1 串口与命令行")

table("表 19　L1 验证",
      ["项目", "内容"],
      [["接线", "A 档（PA2/PA3/GND 三根线）"],
       ["操作", "上电 → 看横幅 → 发 ? → 发 F1000 → 发 A1.0"],
       ["期望", "横幅三行 + 帮助两行 + 「f = 1000.0 Hz」+「Vin = 1.000 Vpp」"],
       ["判据", "每条命令都有对应回显，没有 unknown cmd"],
       ["不过怎么办", "查表 18"]],
      widths=[26, 132], align=["l", "l"])

body("这一级过了，说明时钟、串口、命令解析、DDS 参数接口全都是好的。")

h2("7.2　L2 DAC 波形")

table("表 20　L2 验证",
      ["项目", "内容"],
      [["接线", "B 档（A 档 + 示波器接 PA4 与 GND）"],
       ["操作", "发 F1000 → 发 A2.0"],
       ["期望", "1 kHz 正弦，峰峰值约 2.0 V，中心 1.65 V，在 0~3.3 V 内摆动"],
       ["判据", "频率误差 < 1%，幅度误差 < 10%"],
       ["不过怎么办", "见下方三条"]],
      widths=[26, 132], align=["l", "l"])

body("波形不对时按这三条查：")

bullets([
    "完全是一条直线 1.65 V：DMA 没跑起来。查 DAC 的 DMA 请求线是不是 DMA1 Stream5 Channel7，"
    "这个映射是硬件固定的，配成 DMA2 就一个点都出不来。",
    "有波形但频率是设定值的整数倍或分数：TIM6 的 ARR 算错了，应该等于 84−1（84 MHz / 1 MHz）。",
    "幅度明显偏小且顶部削平：DAC 输出缓冲驱动能力不足，或者负载太重。空载测一次对照。",
])

h2("7.3　L3 ADC 回环")

table("表 21　L3 验证",
      ["项目", "内容"],
      [["接线", "C 档的最简形式：一根杜邦线把 PA4 直接接到 PA0"],
       ["操作", "发 F1000 → 发 A1.0 → 发 M"],
       ["期望", "「Vout = 1.0000 Vpp, phase = xxx deg」"],
       ["判据", "Vpp 与设定值误差 < 3%（同一条线上的自环，理论误差只来自 ADC 量化）"],
       ["不过怎么办", "见下方"]],
      widths=[26, 132], align=["l", "l"])

body("M 命令读回 0 或者 timeout：先确认 PA0 真的接到了 PA4（用万用表量通断），"
     "再确认 ADC 的 DMA 是 DMA2 Stream0 Channel0。如果读到的是设定值的一半，"
     "多半是 ADC 采样率配置错了导致频谱混叠。")

body("相位一栏在自环时应该是接近 0° 的固定值（具体数值取决于采集窗口起点的随机相位，"
     "每次 M 可能不同），这是正常的——单次采集没有绝对时间参考，相位只在同一次采集内可比。")

h2("7.4　L4 已知模型开环控制")

table("表 22　L4 验证",
      ["项目", "内容"],
      [["接线", "C 档：PA4 → 已知模型输入，已知模型输出 → PA0"],
       ["前置", "先把激励降到 0.4 Vpp 以下（发 A0.3），再接线，防过压"],
       ["操作", "发 F1000 → 发 C1.0 → 发 M → 发 C2.0 → 发 M"],
       ["期望", "「target 1.000 -> Vin 0.396 -> Vout 1.00x Vpp (err x.xx%)」"],
       ["判据", "err 绝对值 < 5%"],
       ["不过怎么办", "见下方"]],
      widths=[26, 132], align=["l", "l"])

body("这一级验证的是「装置知不知道被测电路的增益」。原理是：已知模型的 |H| 是可以解析算出来的，"
     "1 kHz 处 |H| = 2.526，所以要得到 1.0 Vpp 输出，输入得是 1.0 / 2.526 = 0.396 Vpp。"
     "固件就是这么反算的，然后实际测一次输出，把误差打出来。")

body("误差偏大时的处理顺序：")

bullets([
    "误差在 5%~10%：先做一次校准。实测 1 kHz 的 Vout，除以理论值 2.526，得到实际增益比，"
    "发 K<这个比值>，再发一次 C 看误差是否收敛。",
    "误差超过 20%：检查已知模型电路本身。重点看 C1、C2 是不是 C0G，运放供电是否正常，"
    "输出有没有削顶（用示波器直接看网络输出）。",
    "误差是固定比例的偏大或偏小：多半是 DAC 满幅标定值不准。固件里 DDS_DAC_FULL_VPP 取的是 2.70 V，"
    "如果你的板子实际是 2.55 V，所有幅度都会按比例偏。",
])

h2("7.5　L5 未知模型辨识")

table("表 23　L5 验证",
      ["项目", "内容"],
      [["接线", "同 L4，但把已知模型换成你要辨识的 RLC 网络"],
       ["操作", "发 L，等 1 秒左右"],
       ["期望", "type = Low-pass / High-pass / Band-pass / Band-reject，以及 K、f0、Q、err"],
       ["判据", "类型与网络实际拓扑一致；f0 与元件算出的理论值误差 < 10%；err < 0.05"],
       ["不过怎么办", "见下方"]],
      widths=[26, 132], align=["l", "l"])

body("L 命令会做 26 点对数扫频，从 200 Hz 到 100 kHz，每点采集 8.192 ms 并做单频 DFT，"
     "全程 0.5~0.8 秒。然后把低通、高通、带通、带阻四种二阶模型分别拟合，"
     "取对数域残差最小的那个作为结论——类型和参数是同时给出的，不是先判类型再算参数。")

note("为什么不靠找峰值判类型", "本题元件范围 R∈[1,10] kΩ、L∈[1,10] mH、C∈[10,100] nF，"
     "推出来的 Q 落在 0.01~1 之间。Q ≤ 1 时带通根本没有谐振峰，"
     "「看有没有峰」这个判据在原理上就不成立。所以必须用四模型拟合比残差的办法。")

body("err 偏大（> 0.1）时，通常是这几个原因：")

bullets([
    "扫频段没覆盖到特征频率。如果 f0 低于 200 Hz 或高于 100 kHz，拟合会外推，残差必然大。",
    "激励幅度太大导致运放削顶，测到的幅频在高频段被压平。降幅度重测。",
    "被测网络输出超过 3.3 V，ADC 削顶。这是最隐蔽的一种，波形上看不出来，但幅频曲线会整体压平。",
    "PA0 上叠了直流偏置。MEAS_Capture 会去直流，但如果偏置大到让信号贴住 0 V 或 3.3 V 轨，去直流也救不回来。",
])

# ------------------------------------------------------------------ 8
h1("8　串口命令速查")

table("表 24　全部命令",
      ["命令", "参数", "作用", "典型回显"],
      [["?", "无", "打印帮助", "两行命令说明"],
       ["F<f>", "频率 Hz，如 F1000", "设定激励频率", "f = 1000.0 Hz"],
       ["A<vpp>", "峰峰值 V，如 A2.0", "设定激励幅度", "Vin = 2.000 Vpp"],
       ["M", "无", "测量当前输出的幅相", "Vout = x.xxxx Vpp, phase = xx.x deg"],
       ["H", "无", "打印当前频率下已知模型的理论 |H|", "|H(1000.0 Hz)| = 2.5260 (8.05 dB)"],
       ["K<k>", "0.2~5.0，如 K1.002", "设定 1 kHz 校准系数", "kcal = 1.0020"],
       ["C<vout>", "目标 Vpp，如 C1.5", "开环控制输出达到目标", "target ... -> Vin ... -> Vout ... (err x.xx%)"],
       ["L", "无", "未知模型自主学习", "learning... 然后 type / K / f0 / Q / err"]],
      widths=[22, 40, 52, 44], align=["l", "l", "l", "l"])

note("命令格式的坑", "字母大小写都行（固件会自动转大写），但字母和数字之间不能有空格。"
     "写 F 1000 会被当成参数 0 处理，回显 f = 0.0 Hz。正确写法是 F1000 连着写。")

# ------------------------------------------------------------------ 9
h1("9　故障总表")

body("把所有环节的症状汇总在这里，出问题时按症状反查。")

table("表 25　症状反查表",
      ["症状", "最可能的位置", "先查这一条"],
      [["串口一片安静", "BOOT0 或接线", "BOOT0 是否回到 GND（表 18 ①）"],
       ["串口全是乱码", "波特率或共地", "助手是否 115200、是否共地"],
       ["发命令没反应", "发送结尾", "串口助手是否加了回车换行"],
       ["回显 unknown cmd", "命令格式", "字母数字之间是否有空格"],
       ["PA4 一直是 1.65 V 直线", "DAC DMA", "是否 DMA1 Stream5 Ch7"],
       ["PA4 有波但频率不对", "TIM6", "ARR 是否为 84−1"],
       ["PA4 波形削顶", "负载或幅度", "空载测一次对照"],
       ["M 命令 timeout", "ADC DMA", "是否 DMA2 Stream0 Ch0，PA0 是否接好"],
       ["M 读数偏小一半", "ADC 采样率", "TIM3 ARR 是否为 168−1"],
       ["C 命令误差 20% 以上", "已知模型电路", "C1/C2 是否 C0G，运放供电"],
       ["C 命令误差 5~10%", "幅度标定", "做一次 K 校准"],
       ["L 命令 err 很大", "扫频段或削顶", "f0 是否在 200 Hz~100 kHz 内，是否削顶"],
       ["烧录 verify 失败", "供电或 Flash", "换 USB 口重烧"],
       ["CubeProgrammer 连不上", "DFU 模式", "回第 4 章重进 DFU"]],
      widths=[46, 40, 72], align=["l", "l", "l"])

# ------------------------------------------------------------------ 10
h1("10　关键数字备忘")

body("实验台上不用翻代码，这些数字记住或抄在纸上就够了。")

table("表 26　固件关键常量",
      ["量", "值", "出处"],
      [["系统时钟", "168 MHz", "HSE 8 MHz × 336 / 8 / 2"],
       ["APB1 / APB2", "42 MHz / 84 MHz", "定时器时钟 84 MHz"],
       ["DAC 更新率", "1 MSPS", "TIM6：84 MHz / 84"],
       ["ADC 采样率", "500 kSPS", "TIM3：84 MHz / 168"],
       ["正弦表点数", "1024", "DDS_TAB_LEN"],
       ["每次采集点数", "4096（8.192 ms）", "MEAS_N"],
       ["DAC 满幅", "2.70 Vpp", "DDS_DAC_FULL_VPP，实测标定值"],
       ["ADC 参考", "3.30 V", "MEAS_VREF"],
       ["扫频范围", "200 Hz ~ 100 kHz，26 点", "IDENT_F_LO / IDENT_F_HI / IDENT_NPTS"],
       ["栈大小", "4 KB", "startup 文件 Stack_Size = 0x1000"]],
      widths=[38, 52, 68], align=["l", "c", "l"])

table("表 27　已知模型电路特征值",
      ["量", "值", "备注"],
      [["传递函数", "H(s) = 5 / (1e-8·s² + 3e-4·s + 1)", "标准二阶低通"],
       ["直流增益 K", "5（13.98 dB）", "由 Rf/Rg = 30k/7.5k 决定"],
       ["自然频率 fn", "1591.5 Hz", "ωn = 1e4 rad/s"],
       ["品质因数 Q", "1/3（过阻尼）", "两实极点：607.9 Hz 与 4166.6 Hz"],
       ["−3 dB 频率", "595.6 Hz", "数值求解"],
       ["|H(1 kHz)|", "2.526", "开环反算用的基准"],
       ["1 kHz 相位", "−72.2°", "参考值"],
       ["输出 1 Vpp 所需输入", "0.396 Vpp", "1.0 / 2.526"]],
      widths=[40, 62, 56], align=["l", "c", "l"])

body("以上数值全部来自固件源码与设计报告，两边一致。如果实测对不上，先怀疑接线与元件，"
     "再怀疑固件——固件已经过离线工具链验证，编译产物与源码严格对应。")

doc.save(OUT)
print("saved", OUT)
