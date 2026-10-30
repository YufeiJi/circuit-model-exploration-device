# -*- coding: utf-8 -*-
"""生成《ST-Link V2 烧录与在线调试速查》"""
import os
from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

OUT = r"D:\Agent\project\电路模型探究装置\文档\ST-Link烧录与在线调试速查.docx"
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
hr = hp.add_run("电路模型探究装置 · ST-Link V2 烧录与在线调试速查")
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


def body(text, indent=True, size=10.5, bold=False, color=None, after=3):
    p = doc.add_paragraph()
    pf = p.paragraph_format
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
    pf.space_before = Pt(13); pf.space_after = Pt(6); pf.line_spacing = 1.25
    pf.keep_with_next = True
    r = p.add_run(text); r.font.size = Pt(14.5); r.bold = True
    r.font.color.rgb = RGBColor(0x1F, 0x33, 0x4E)
    _rf(r, "Times New Roman", HEI)
    return p


def h2(text):
    p = doc.add_paragraph(style="Heading 2")
    pf = p.paragraph_format
    pf.space_before = Pt(9); pf.space_after = Pt(4); pf.line_spacing = 1.25
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
    tot = sum(widths)
    if tot > 15.2:
        widths = [w * 15.2 / tot for w in widths]
    al = align or ["l"] * len(header)
    t = doc.add_table(rows=1, cols=len(header))
    t.style = "Table Grid"; t.alignment = WD_TABLE_ALIGNMENT.CENTER; t.autofit = False
    tblPr = t._tbl.tblPr
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


# ------------------------------------------------------------------ 标题
p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
p.paragraph_format.space_before = Pt(10)
r = p.add_run("ST-Link V2 烧录与在线调试速查")
r.font.size = Pt(22); r.bold = True
r.font.color.rgb = RGBColor(0x1F, 0x33, 0x4E)
_rf(r, "Times New Roman", HEI)

p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
p.paragraph_format.space_before = Pt(6)
r = p.add_run("替代《烧录与上电调试实操手册》第 4、5 章的 USB DFU 方案")
r.font.size = Pt(11); r.font.color.rgb = RGBColor(0x55, 0x66, 0x77)
_rf(r, "Times New Roman", SONG)

p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
p.paragraph_format.space_before = Pt(2)
r = p.add_run("STM32F407VET6　|　SWD 四线　|　Keil 内一键下载")
r.font.size = Pt(10); r.font.color.rgb = RGBColor(0x88, 0x88, 0x88)
_rf(r, "Times New Roman", SONG)

# ------------------------------------------------------------------ 1
h1("1　有了 ST-Link，哪些步骤可以扔掉")

body("原来的 DFU 方案要拨 BOOT0、装 CubeProgrammer、烧完再拨回来，一共六七个动作，"
     "而且 CubeProgrammer 还得注册 ST 账号才能下载。换成 ST-Link 之后，这些全部不需要——"
     "ST-Link 走的是芯片的 SWD 调试口，属于「在线」烧录，不用让芯片进 bootloader。")

table("表 1　DFU 与 ST-Link 的流程对比",
      ["环节", "USB DFU 方案", "ST-Link 方案"],
      [["进 bootloader", "BOOT0 短接 3V3 + 复位", "不需要"],
       ["烧录软件", "STM32CubeProgrammer（要 ST 账号）", "Keil 自带，不用另装"],
       ["烧录动作", "选 hex → Start Programming", "按一下 F8"],
       ["退出", "BOOT0 拨回 GND + 复位", "不需要，下载完自动跑"],
       ["在线调试", "做不到", "能：断点、单步、看变量、看寄存器"],
       ["排查 HardFault", "只能靠串口打印猜", "暂停看 PC / LR，一眼定位"]],
      widths=[30, 62, 66], align=["l", "l", "l"])

note("结论", "ST-Link 方案全面优于 DFU。除非板子的 SWD 口被占用或没引出来，否则都用 ST-Link。"
     "手册里第 2、3、6、7、8、9、10 章（确认产物、接线、上电看串口、五级验证、命令速查、故障总表、"
     "关键数字）完全不变，只有第 4、5 章被本文替代。")

# ------------------------------------------------------------------ 2
h1("2　接线：SWD 四根线")

body("ST-Link V2 无论原装还是克隆版，SWD 模式只需要四根线。克隆版通常是铝合金外壳、10 针排针，"
     "丝印上找 SWDIO、SWCLK、GND 三个词，以及一个 3.3V。")

table("表 2　SWD 接线表",
      ["ST-Link 针脚", "板子引脚", "是否必需", "作用"],
      [["SWDIO", "PA13（SWDIO）", "必需", "双向数据线"],
       ["SWCLK", "PA14（SWCLK）", "必需", "时钟线，由 ST-Link 提供"],
       ["GND", "GND", "必需", "共地，不接必然连不上"],
       ["NRST", "NRST", "建议接", "让 ST-Link 能硬复位芯片，芯片跑飞时救命"],
       ["3.3V", "3.3V", "不要接", "见下方警告"],
       ["5V", "—", "绝对不接", "会烧板子"]],
      widths=[34, 40, 26, 58], align=["l", "l", "c", "l"])

warn("3.3V 那根不要接。", "如果你的板子已经用自己的 USB 口供电，再接 ST-Link 的 3.3V，"
     "就是两路电源顶在一起，轻则电压漂移烧录失败，重则把 ST-Link 或板子的 LDO 顶坏。"
     "规则是：板子自己供电，ST-Link 只出 SWDIO / SWCLK / GND 三根（加 NRST 四根）。")

body("只有板子完全没电、又没有独立供电口时，才用 ST-Link 的 3.3V 供电，并且必须拔掉板子的 USB 线。")

note("SWD 引脚不会被固件占用", "本工程的固件只操作 PA0（ADC）、PA2/PA3（串口）、PA4（DAC），"
     "没有碰 PA13/PA14。所以 ST-Link 随时能连上，不需要「Connect under Reset」这种特殊手段。")

body("如果板子上没有引出 SWD 排针，就直接飞线到芯片的 13、14 脚（LQFP100 封装的 PA13/PA14），"
     "或者找板子上标着 DIO / CLK 的测试点。")

# ------------------------------------------------------------------ 3
h1("3　装驱动")

body("ST-Link 插上电脑后，设备管理器里应该出现 STMicroelectronics STLink dongle。"
     "如果显示「未知设备」带黄色感叹号，说明驱动没装。Keil 自带驱动安装器，不用去 ST 官网下：")

code_block(r"D:\daxue\Keil5 32\ARM\STLink\USBDriver\dpinst_amd64.exe")

body("双击运行，一路 Next。或者用同目录下的批处理：")

code_block(r"D:\daxue\Keil5 32\ARM\STLink\USBDriver\stlink_winusb_install.bat")

body("装完拔插一次 ST-Link，设备管理器「通用串行总线设备」下应出现 STM32 STLink，没有感叹号即可。")

warn("克隆版固件的坑。", "淘宝买的 ST-Link V2 克隆版，固件版本可能很老（比如 V2.J17.S4），"
     "新版 Keil 会提示固件过旧甚至拒绝连接。这时用 Keil 自带的 ST-LinkUpgrade.exe 升级固件"
     "（同目录：ARM\\STLink\\ST-LinkUpgrade.exe），点 Device Connect → Yes >>>> 即可。"
     "升级有极小概率把山寨片子刷死，能连上就别升。")

# ------------------------------------------------------------------ 4
h1("4　Keil 里配调试器")

body("先关掉 Keil 再重新打开工程（重要，原因见第 7 节）。然后按 Alt+F7 打开 Options for Target。")

h2("4.1　Debug 页")

table("表 3　Debug 页设置",
      ["项", "取值"],
      [["右上角下拉框", "ST-Link Debugger"],
       ["Use", "勾选（默认已勾）"],
       ["Load Application at Startup", "勾选"],
       ["Run to main()", "勾选"]],
      widths=[56, 102], align=["l", "l"])

body("选好之后点右边的 Settings，弹出 ST-Link 设置框，核对两项：")

table("表 4　ST-Link Settings 对话框",
      ["项", "取值", "说明"],
      [["Port", "SW", "不是 JTAG。SWD 只用两根线"],
       ["Max Clock", "1.8 MHz", "克隆版建议降到 1.8M 甚至 950k，4M 常常报 RDDI-DAP Error"],
       ["Reset", "Autodetect 或 SYSRESETREQ", "默认即可"],
       ["SW Device 栏", "显示 ARM CoreSight SW-DP + IDCODE", "空白或 No target connected = 接线有问题"]],
      widths=[26, 52, 80], align=["l", "l", "l"])

body("SW Device 那一栏是关键判据。能读到 IDCODE（一串 0x2BA01477 之类的十六进制）说明"
     "ST-Link 已经和芯片握手成功，后面才有戏。读不到就回第 2 节查接线，或者量一下板子 3.3V 有没有电。")

h2("4.2　Flash Download 页（这一步最容易漏）")

body("还是在这个 Settings 对话框里，切到 Flash Download 标签页。因为这台机器没装器件包，"
     "算法列表一开始是空的，必须手动加一次。")

body("我已经把算法文件放好了：")

code_block(r"D:\daxue\Keil5 32\ARM\Flash\STM32F4xx_512.FLM")

body("点 Add 按钮，在弹出的文件框里选上面这个文件（默认就打开在 ARM\\Flash 目录，直接能看到）。"
     "加成功后列表里应出现一行：")

code_block("STM32F4xx 512kB Flash    Start: 0x08000000    Size: 0x80000")

body("然后核对下半部分的选项：")

table("表 5　Flash Download 设置",
      ["项", "取值", "说明"],
      [["RAM for Algorithm – Start", "0x20000000", "算法运行用的 SRAM 起始"],
       ["RAM for Algorithm – Size", "0x1000", "4 KB，够用"],
       ["Programming Algorithm", "STM32F4xx 512kB Flash", "没有这行就点 Add 加上"],
       ["Erase Sectors", "勾选", "按扇区擦，比全片擦快"],
       ["Program", "勾选", "必须"],
       ["Verify", "勾选", "回读比对，能抓出坏块"],
       ["Reset and Run", "勾选", "下载完自动复位运行，省一次手动复位"]],
      widths=[52, 44, 62], align=["l", "c", "l"])

note("工程文件已经预设好了", "我把 FlashDriverDll 的算法路径写进了 CircuitModel.uvprojx，"
     "指向 D:\\daxue\\Keil5 32\\ARM\\Flash\\STM32F4xx_512.FLM。所以正常情况下你打开 Flash Download 页"
     "应该已经看到算法了，不需要 Add。只有显示空白时才手动加一次。")

# ------------------------------------------------------------------ 5
h1("5　下载：按 F8")

body("配好之后，日常流程就是：改代码 → F7 编译 → F8 下载。三个键，没有别的动作。")

body("F8 之后 Build Output 窗口应该依次出现：")

code_block('Load ".\\Objects\\\\CircuitModel.axf"\n'
           "Erase Done.\n"
           "Programming Done.\n"
           "Verify OK.\n"
           "Application running ...")

body("看到 Verify OK 就说明写进去并且校验通过了，Application running 说明芯片已经在跑你的程序。"
     "整个过程 2~3 秒。")

body("如果只想下载不调试，按 F8；如果想进调试模式（能下断点），按 Ctrl+F5。")

# ------------------------------------------------------------------ 6
h1("6　下载报错对照")

table("表 6　ST-Link 常见报错",
      ["报错信息", "原因", "处置"],
      [["No ST-Link detected", "驱动没装，或 USB 线是纯充电线", "跑 dpinst_amd64.exe；换数据线"],
       ["No target connected", "SWDIO/SWCLK 接反或没接、板子没电", "对调 SWDIO/SWCLK 试；量 3.3V"],
       ["Cannot access target", "芯片在读保护，或跑飞后关了 SWD", "Settings 里勾 Connect under Reset"],
       ["RDDI-DAP Error", "SWD 时钟太快", "Max Clock 降到 1.8 MHz 或 950 kHz"],
       ["No Algorithm found for: 08000000H", "Flash 算法没加", "第 4.2 节点 Add"],
       ["Error: Flash Download failed - Target DLL has been cancelled", "算法文件路径失效", "重新 Add 一次"],
       ["Could not stop Cortex-M device", "芯片在死循环里关不掉", "勾 Connect under Reset 再连"],
       ["Flash Timeout. Reset the Target and try it again", "Flash 被锁或供电不足", "全片擦除一次；换 USB 口"],
       ["Programming error @ 0x08000000", "Flash 写保护", "Options for Target → Utilities → 取消写保护"]],
      widths=[62, 44, 52], align=["l", "l", "l"])

body("排错顺序建议：先看能不能读到 IDCODE（第 4.1 节），能读到就是配置问题，读不到就是接线或供电问题。"
     "这两类的原因完全不一样，先分清能省一半时间。")

# ------------------------------------------------------------------ 7
h1("7　必须知道的一件事：工程文件被改过")

body("我用脚本改了 CircuitModel.uvprojx 里的 Flash 算法路径（把器件包相对路径换成了本机绝对路径），"
     "因为器件包一直没装，原来的路径解析不到，Flash Download 页会是空的。")

warn("Keil 开着的时候改工程文件，会被覆盖。", "你刚才 Keil 是开着的。Keil 内存里保存的是旧配置，"
     "这时候如果你在 Keil 里点保存（Ctrl+S）或者关窗口时选「保存」，"
     "就会把磁盘上的新配置冲掉，Flash 算法路径又变回失效的那个。"
     "所以：先关掉 Keil（不保存），再重新打开工程。")

body("如果已经不小心覆盖了，也不影响——按第 4.2 节手动 Add 一次算法即可，只是多花一分钟。")

# ------------------------------------------------------------------ 8
h1("8　顺带解锁：在线调试")

body("这是 ST-Link 相对 DFU 最大的额外价值。以前程序跑飞了只能靠串口打印猜，"
     "现在可以停下来直接看现场。")

table("表 7　调试常用操作",
      ["操作", "快捷键", "用途"],
      [["进入调试", "Ctrl+F5", "下载并停在 main() 第一行"],
       ["全速运行", "F5", "跑起来，遇到断点停"],
       ["暂停", "停止按钮", "程序跑飞时按它，看停在哪"],
       ["单步跳过", "F10", "一行一行走，不进函数"],
       ["单步进入", "F11", "进入函数内部"],
       ["跳出函数", "Ctrl+F11", "从当前函数返回"],
       ["设断点", "行号左侧点一下", "红点，程序到这里停"],
       ["看变量", "View → Watch Windows", "把变量名敲进去，实时显示值"],
       ["看调用栈", "View → Call Stack", "程序怎么走到这里的"],
       ["看寄存器", "View → Registers", "R0~R15、xPSR、MSP/PSP"],
       ["退出调试", "Ctrl+F5", "回到编辑状态"]],
      widths=[30, 46, 82], align=["l", "l", "l"])

body("排查 HardFault 的标准动作：程序跑飞 → 点暂停 → 看 Call Stack 和 Registers 里的 PC、LR。"
     "PC 指向哪条指令，就是哪条指令触发的异常；LR 的值能看出是从哪个函数跳进去的。"
     "比在代码里到处插 printf 快得多。")

note("看不了外设寄存器是正常的", "Peripherals 菜单里的 System Viewer 需要器件包提供 SVD 文件。"
     "这台机器没装 DFP，所以那一项可能是灰的。不影响下载和基本调试，"
     "想看 DAC/ADC 寄存器就在 Watch 窗口里直接敲 DAC->DCR 这类表达式。")

# ------------------------------------------------------------------ 9
h1("9　和主手册的对应关系")

body("把两份文档的关系理清楚，免得来回翻。")

table("表 8　两份文档的分工",
      ["内容", "看哪份"],
      [["确认编译产物、hex 自检", "主手册第 2 章"],
       ["接线（DAC/ADC/串口）、已知模型电路搭法", "主手册第 3 章"],
       ["烧录", "本文第 2~5 章（替代主手册第 4、5 章）"],
       ["上电看串口、启动横幅含义", "主手册第 6 章"],
       ["五级验证 L1~L5", "主手册第 7 章"],
       ["串口命令速查", "主手册第 8 章"],
       ["按症状反查故障", "主手册第 9 章"],
       ["固件常量、已知模型特征值", "主手册第 10 章"]],
      widths=[86, 72], align=["l", "l"])

body("一句话：主手册的第 4、5 章（进 DFU、CubeProgrammer 烧录）整段作废，换成本文；其余章节照旧。")

doc.save(OUT)
print("saved", OUT)
