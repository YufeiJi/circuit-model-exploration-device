# -*- coding: utf-8 -*-
"""生成《Keil 手动建工程指南（不用 CubeMX）》"""
import os
from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

OUT = r"D:\Agent\project\电路模型探究装置\文档\Keil手动建工程指南（不用CubeMX）.docx"
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
hr = hp.add_run("电路模型探究装置 · Keil 手动建工程指南（不用 CubeMX）")
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
    r = p.add_run(text); r.font.size = Pt(11.5); r.bold = True
    r.font.color.rgb = RGBColor(0x2A, 0x45, 0x66)
    _rf(r, "Times New Roman", HEI)


def cap(text):
    p = doc.add_paragraph()
    pf = p.paragraph_format
    pf.space_before = Pt(6); pf.space_after = Pt(2); pf.line_spacing = 1.2
    pf.keep_with_next = True
    r = p.add_run(text); r.font.size = Pt(9); r.bold = True
    r.font.color.rgb = RGBColor(0x33, 0x33, 0x33)
    _rf(r, "Times New Roman", HEI)


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


def table(header, rows, widths, size=8.5):
    t = doc.add_table(rows=1, cols=len(header))
    t.style = "Table Grid"; t.alignment = WD_TABLE_ALIGNMENT.CENTER; t.autofit = False
    tblPr = t._tbl.tblPr
    lay = OxmlElement("w:tblLayout"); lay.set(qn("w:type"), "fixed"); tblPr.append(lay)
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
            put(cells[j], str(val))
    trPr = t.rows[0]._tr.get_or_add_trPr()
    th = OxmlElement("w:tblHeader"); th.set(qn("w:val"), "true"); trPr.append(th)
    # 禁止单行跨页断裂
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


# ------------------------------------------------------------------ 封面
for _ in range(4):
    doc.add_paragraph()
p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = p.add_run("电路模型探究装置 · 固件实现")
r.font.size = Pt(11); r.font.color.rgb = RGBColor(0x55, 0x55, 0x55)
_rf(r, "Times New Roman", SONG)

p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
p.paragraph_format.space_before = Pt(20)
r = p.add_run("Keil 手动建工程指南")
r.font.size = Pt(30); r.bold = True; r.font.color.rgb = RGBColor(0x1F, 0x33, 0x4E)
_rf(r, "Times New Roman", HEI)

p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
p.paragraph_format.space_before = Pt(8)
r = p.add_run("不用 CubeMX、不用 HAL，只用寄存器")
r.font.size = Pt(13); r.font.color.rgb = RGBColor(0x66, 0x66, 0x66)
_rf(r, "Times New Roman", SONG)

for _ in range(6):
    doc.add_paragraph()
for line in ("配套代码：Keil/（Core 2 个、BSP 2 个、App 8 个，共 12 个文件）",
             "目标芯片：STM32F407VET6（168 MHz，512 KB Flash，LQFP100）",
             "工具链：Keil MDK-ARM 5.38 ＋ STM32F4xx_DFP ＋ STM32CubeProgrammer（DFU 烧录）"):
    p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_after = Pt(4)
    r = p.add_run(line); r.font.size = Pt(9.5); r.font.color.rgb = RGBColor(0x44, 0x44, 0x44)
    _rf(r, "Times New Roman", SONG)

for _ in range(3):
    doc.add_paragraph()
p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = p.add_run("2026 年 10 月"); r.font.size = Pt(11)
_rf(r, "Times New Roman", SONG)
doc.add_page_break()

# ------------------------------------------------------------------ 正文
h1("1　这套代码是什么")
body("不用 CubeMX，也不用 ST 的 HAL 库。整个固件只有 12 个文件，直接读写 STM32F407 的寄存器，"
     "编译时除了 Keil 自带的 CMSIS 头文件和启动文件，不需要任何第三方库。")
cap("表 1　与 CubeMX 版的区别")
table(["对比项", "CubeMX + HAL 版", "本裸机版"],
      [["依赖", "STM32CubeF4 固件包（几十 MB）", "只要 Keil 的 STM32F4xx_DFP 器件包"],
       ["工程生成", "CubeMX 图形化配置后生成", "工程已建好，双击 .uvprojx 直接打开"],
       ["初始化代码", "MX_xxx_Init() 一堆函数", "bsp.c 里 5 个函数，逐行可读"],
       ["代码量", "编译产物 40 KB 以上", "约 12 KB"],
       ["可解释性", "HAL 内部做了什么看不到", "每个寄存器写的是什么一目了然，答辩好讲"]],
      [2.6, 6.4, 7.2])
body("代价是：时钟树、DMA 请求映射、NVIC 这些必须自己配对。下面每一处配置都给了寄存器含义，"
     "照着写不会错；写错了第 4 章有对应的排查表。")

h1("2　准备清单")

h2("2.1　先装器件包：没有它，Device 列表里根本没有 STM32F4")
body("µVision 安装包本身只带 ARM Compiler 与 CMSIS 内核头文件，不含任何厂商的器件支持。"
     "STM32F4 的芯片型号、寄存器定义、启动文件、Flash 下载算法，全部由 Keil.STM32F4xx_DFP 这一个包提供。"
     "所以新建工程时如果 Device 列表里搜不到 STM32F407，不是板子的问题，是这个包没装。")
body("三种装法，按顺序试：", indent=False)
body("① Pack Installer（有网最省事）：µVision 工具栏点 Pack Installer 图标 → 左侧 Devices 展开 "
     "STMicroelectronics → STM32F4 Series，右侧 Packs 页找到 Keil::STM32F4xx_DFP → 点 Install。"
     "国内网络常卡在 Updating pack index 不动，等五分钟没反应就换 ②。", hang=True)
body("② 离线 .pack（推荐，最稳）：已随本指南放在 "
     "工具\\Keil.STM32F4xx_DFP.2.17.0.pack（276 MB），"
     "双击即可，µVision 会自动弹出安装进度；装完关掉再重开 µVision。", hang=True)
body("③ 手动解压：把 .pack 当 zip 解开，整个文件夹放到 "
     "Keil_v5\\ARM\\PACK\\Keil\\STM32F4xx_DFP\\2.17.0\\，确认该目录下能看到 "
     "Keil.STM32F4xx_DFP.pdsc，重开 µVision 就能识别。", hang=True)
note("别装 3.x", "keil.arm.com 上最新版是 3.1.1，只有 2 MB。3.0.0 起为配合 CMSIS-Toolbox 与 CubeMX 重构，"
     "把 CMSIS Drivers、器件头文件、启动文件全删了，只留 Flash 算法与 SVD。装完 3.x 仍然找不到 "
     "stm32f4xx.h 和 startup_stm32f407xx.s，本工程必须用 2.17.0。")
body("验证：Project → New uVision Project → Device 页搜索 STM32F407，能出现 STM32F407VE（Flash 512 KB）"
     "就说明装好了，继续往下走。")

h2("2.2　软硬件清单")
cap("表 2　软硬件清单")
table(["类别", "项目", "说明"],
      [["软件", "Keil MDK-ARM 5.38+", "编译器用 ARM Compiler 6"],
       ["软件", "STM32F4xx_DFP 2.17.0", "见 2.1 节；提供器件头文件、startup、512 KB Flash 算法"],
       ["软件", "STM32CubeProgrammer", "只用它的 DFU 下载功能，不用它的代码生成"],
       ["硬件", "开发板", "STM32F407VET6（你这块丝印 STM32_F4VE）"],
       ["硬件", "杜邦线 2 根", "短接 BT0 与 3V3，进 DFU 用"],
       ["硬件", "Type-C 数据线", "板子唯一的 USB，直连 PA11/PA12"],
       ["硬件", "USB-TTL 模块（可选）", "接 PA2/PA3 看 printf；没有就先靠示波器"]],
      [1.8, 5.4, 9.0])

h1("3　打开工程（或从零重建）")
note("工程已经建好了", "直接双击 D:\\Agent\\project\\电路模型探究装置\\CircuitModel.uvprojx 就能打开，"
     "按 F7 编译出 Objects\\CircuitModel.hex。3.1～3.5 是从零重建的完整步骤——工程文件丢了、"
     "或者要在另一台电脑上重做时照着走一遍，顺带说明每个选项为什么这么设。")

h2("3.1　工程目录长什么样")
body("工程根目录 D:\\Agent\\project\\电路模型探究装置 下的结构如下。注意本工程不用 RTE："
     "器件头文件、内核头文件、启动文件都已经拷进 Drivers\\ 目录，工程自带，换台电脑也能直接编。")
cap("表 3　分组与文件对应关系")
table(["分组", "所在目录", "加入的文件", "作用"],
      [["User", "Core", "main.c、system_stm32f4xx.c", "主程序与系统文件"],
       ["BSP", "BSP", "bsp.c", "时钟、串口、定时器、DAC/ADC + DMA"],
       ["App", "App", "app_dds.c、app_meas.c、app_known.c、app_ident.c", "四个功能模块"],
       ["Drivers", "Drivers\\CMSIS\\Device\\Source", "startup_stm32f407xx.s", "中断向量表与复位入口"]],
      [2.2, 5.0, 6.6, 4.2])
body("头文件目录不加入工程，只挂在 Include Paths 上：Drivers\\CMSIS\\Device\\Include 放 stm32f4xx.h、"
     "stm32f407xx.h、system_stm32f4xx.h；Drivers\\CMSIS\\Include 放 core_cm4.h 及其依赖的 8 个 CMSIS 头文件。"
     "这两批文件分别从 Keil.STM32F4xx_DFP 2.17.0 和 ARM.CMSIS 5.9.0 里取，已经随工程打包好。")

h2("3.2　建空工程、选器件")
body("Keil 菜单 Project → New uVision Project…，目录就选 D:\\Agent\\project\\电路模型探究装置，"
     "文件名填 CircuitModel，保存。")
body("弹出 Select Device for Target 对话框：展开 STMicroelectronics → STM32F4 Series → STM32F407，"
     "选 STM32F407VE（注意是 VE 不是 VG，Flash 512 KB），点 OK。")
body("紧接着会弹出 Manage Run-Time Environment —— 本工程一个都不勾，直接点 Cancel 关掉。"
     "因为启动文件和系统文件已经放进 Drivers\\ 和 Core\\ 了，再勾一次会重复定义。")

h2("3.3　建分组、加源码")
body("Project 窗口右键 Target 1 → Manage Project Items…，按表 3 新建四个组，然后逐个 Add Files。")
body("加完检查一下：Groups 树里应该有 7 个 .c 文件 + 1 个 .s 文件，少一个都链接不过。")

h2("3.4　Options for Target 六页设置")
body("点魔术棒图标或按 Alt+F7，逐页按表 4 设置。这六项里任何一项漏了，都会在第 4 章对应到某个具体报错。")
cap("表 4　Options for Target 设置")
table(["页面", "设置项", "值", "漏了会怎样"],
      [["Target", "ARM Compiler", "Use default compiler version 6", "AC5 也能编，但语法检查更松"],
       ["Target", "Use MicroLIB", "勾选", "printf 卡死或链接报 _sys_write"],
       ["Target", "Floating Point Hardware", "Single Precision", "进 main 就 HardFault"],
       ["Output", "Create HEX File", "勾选", "Objects 里没有 hex，无法 DFU 烧录"],
       ["C/C++", "Define", "STM32F407xx", "报 #error Please select first the target device"],
       ["C/C++", "Include Paths", ".\\Core;.\\BSP;.\\App;.\\Drivers\\CMSIS\\Device\\Include;.\\Drivers\\CMSIS\\Include",
        "报 stm32f4xx.h / core_cm4.h 找不到"],
       ["C/C++", "Optimization", "Level 1 (-O1)", "-O0 也能跑，辨识慢一点"],
       ["C/C++", "C99 Mode", "勾选", "for 内定义变量会报错"],
       ["Linker", "Use Memory Layout from Target Dialog", "勾选", "报 Scatter Error: no default 'Read/Write' range selected"]],
      [2.0, 4.0, 6.4, 4.6])
body("Linker 那一项勾上之后，链接脚本由 Target 页的 Read/Write Memory Areas 自动生成："
     "IROM1 = 0x08000000 / 0x80000（512 KB Flash），IRAM1 = 0x20000000 / 0x20000（128 KB SRAM）。"
     "工程里另附了一份 CircuitModel.sct，万一那张表空了，可以在 Linker 页取消勾选、把 Scatter File 指向它。")
body("Debug 页在没有 ST-Link 时随便选（比如 Use Simulator），它只影响“点调试按钮”的行为，不影响编译和 hex 产出。")

h2("3.5　第一次编译")
body("按 F7（或 Project → Build Target）。底部 Build Output 应显示 0 Error(s)。"
     "编译完在 Objects\\CircuitModel.hex 就能看到 —— 这就是要烧进芯片的文件。")
body("如果报错，先看第 4 章的表 5，那几条覆盖了新手 90% 的问题。")

h1("4　上手必踩的坑")
cap("表 5　编译与启动阶段的典型问题")
table(["现象", "原因", "处理"],
      [["L6218E: Undefined symbol SystemInit", "只加了启动文件，没加系统文件", "把 Core/system_stm32f4xx.c 加进 User 组"],
       ["L6200E: Symbol SystemInit multiply defined", "既加了 Core 里的系统文件，又在 RTE 里勾了 Device:Startup", "RTE 全部取消勾选"],
       ["#error Please select first the target STM32F4xx device", "C/C++ → Define 里没写器件宏", "填 STM32F407xx"],
       ["下载后一上电就 HardFault / 卡死", "FPU 没开：Target 页 Floating Point 仍是 Not Used", "改成 Single Precision 重新编译"],
       ["printf 没有任何输出", "MicroLIB 没勾，或 fputc 被删", "Target 页勾 Use MicroLIB；确认 main.c 里的 fputc 还在"],
       ["编译报 stm32f4xx.h / core_cm4.h: No such file", "Include Paths 漏了 Drivers 下的两个目录", "补上 .\\Drivers\\CMSIS\\Device\\Include 与 .\\Drivers\\CMSIS\\Include"],
       ["注释全是乱码", "Keil 按 GBK 读了 UTF-8 文件", "Edit → Configuration → Editor → Encoding 选 UTF-8，重开文件"]],
      [5.2, 5.4, 5.6])

h1("5　下载：BT0 短接进 DFU")
body("这块板没有 ST-Link 接口可用，但 STM32F407 片内有 ROM bootloader，支持 USB DFU。"
     "板子的 Type-C 直连 PA11/PA12，正好就是 DFU 用的那两个脚。")
cap("表 6　烧录步骤")
table(["步骤", "操作", "判断成功的标志"],
      [["1", "用杜邦线把上排的 BT0 针与旁边的 3V3 针短接", "两根针之间导通"],
       ["2", "按一下左上角的复位键（没有就拔插一次 USB）", "设备管理器出现 STM32 BOOTLOADER（0483:DF11）"],
       ["3", "打开 CubeProgrammer，连接方式选 USB，Port 选 USB1，点 Connect", "右侧显示 STM32F407xx、Flash 512 KB"],
       ["4", "Download 页选 Objects\\CircuitModel.hex，点 Download", "日志出现 Download verified successfully"],
       ["5", "拔掉杜邦线，按复位", "程序开始运行"]],
      [1.4, 8.4, 6.4])
note("第 5 步不能省", "BT0 接着 3V3 时，芯片每次复位都回到 bootloader，程序永远起不来。拔线再复位，才算真正运行用户程序。")

h1("6　上电验证（五级）")
body("按顺序逐级验证，任何一级不过就停在那里查，不要跳步。")
cap("表 7　五级验证")
table(["步骤", "操作", "预期现象", "不通过先查"],
      [["1 串口", "USB-TTL 接 PA2/PA3，115200", "打印 ==== Circuit Model Explorer ====", "TX/RX 接反、波特率、BRR 计算"],
       ["2 DAC", "输入 F1000 回车，再 A1.0 回车，示波器看 PA4", "1 kHz、1 Vpp、偏置 1.65 V 正弦", "TIM6 是否启动、DAC DMAEN 是否置位"],
       ["3 ADC", "PA4 用杜邦线短接 PA0，输入 M", "读到约 1.0 Vpp", "ADC 触发源是否 TIM3_TRGO、DMA 是否使能"],
       ["4 开环", "接已知模型电路，输入 C1.5", "打印目标/实测/误差，误差 ≤3%", "电路增益、kcal 校准"],
       ["5 辨识", "接未知 RLC 电路，输入 L", "约 1～3 s 后打印类型与 K、f0、Q", "激励是否 ≥1.5 Vpp"]],
      [1.8, 5.6, 5.0, 3.8])

h1("7　常见错误（运行阶段）")
cap("表 8　运行阶段问题")
table(["现象", "原因", "处理"],
      [["DAC 输出恒定 1.65 V", "TIM6 没启动，DMA 收不到请求", "检查 tim6_start() 是否在 dac_dma_start() 之后调用"],
       ["DAC 输出恒定不变、没有任何波形", "DAC1_CH1 的请求线硬件固定为 DMA1_Stream5_Ch7，若配成 DMA2 则永远等不到请求",
        "改用 DMA1_Stream5，AHB1ENR 开 DMA1EN；Stream5 标志位在 HISR 的 bit10(HT)/bit11(TC)"],
       ["输出频率正好差一倍", "ARR 与定时器时钟不匹配", "TIM6：ARR = 84 MHz/1 MHz − 1 = 83"],
       ["波形有台阶、毛刺", "重构低通没接或截止太高", "接 150 kHz 二阶 Sallen-Key 重构滤波器"],
       ["串口乱码", "晶振不是 8 MHz 或 BRR 算错", "BRR = PCLK1/baud ≈ 365（42 MHz/115200）"],
       ["测量值随频率大幅漂移", "ADC 采样时间太短、前端驱动不足", "SMPR2 从 3 周期改到 15 周期"],
       ["辨识恒为 Low-pass", "激励太小、噪声主导", "A 设到 1.5~2 Vpp 再 L"],
       ["L 命令卡住不动", "扫频等待时间累加", "26 点 × max(20/f,5 ms) ≈ 0.34 s，加四模型网格拟合共 1～3 s，属正常"]],
      [4.8, 5.6, 5.8])

h1("8　代码结构与运行流程")
cap("表 9　文件职责")
table(["文件", "职责", "关键点"],
      [["Core/main.c", "初始化顺序、串口命令行、printf 重定向", "fputc 直接写 USART2->DR"],
       ["Core/system_stm32f4xx.c", "使能 FPU、SystemCoreClock", "不做时钟配置，只补 startup 需要的符号"],
       ["BSP/bsp.c", "时钟 168 MHz、SysTick、USART2、TIM6/TIM3、DAC/ADC + DMA", "所有寄存器配置集中在这里"],
       ["App/app_dds.c", "相位累加、查表插值、DMA 双缓冲重填", "在 DMA1_Stream5 中断里填另一半"],
       ["App/app_meas.c", "ADC 采集 + Hann 窗单频 DFT", "采满 4096 点由 DMA 中断置标志"],
       ["App/app_known.c", "H(s) 幅相、开环反算 Vin", "纯数学，不碰硬件"],
       ["App/app_ident.c", "26 点扫频 + 四模型拟合 + 分类", "网格粗搜 + 局部细化"]],
      [4.2, 7.4, 4.6])

body("两条数据流是并行的，互不阻塞：")
body("① 输出链：TIM6（1 MHz 更新）→ DAC1_CH1 → DMA1_Stream5 循环搬运 2048 点 → PA4。"
     "每搬完一半进一次中断，把刚空出来的 1024 点按当前频率重算。", indent=False)
body("② 输入链：TIM3（500 kHz）→ ADC1 触发 → DMA2_Stream0 搬 4096 点 → 采满进中断 → 主循环算 DFT。", indent=False)
body("主循环本身只做一件事：收串口命令。所以 DAC 输出和 ADC 采集都不会被命令处理打断。")

h1("9　与设计报告的一致性")
cap("表 10　关键参数对照")
table(["参数", "代码中的值", "报告出处"],
      [["系统时钟", "168 MHz（PLL M=8 N=336 P=2）", "4.1 节 主控与资源分配"],
       ["DAC 更新率", "1 MSPS（TIM6 ARR=83）", "4.2 节 正弦信号发生通道"],
       ["正弦表", "1024 点 Q15 + 线性插值", "4.2 节"],
       ["ADC 采样率 / 点数", "500 kSPS（TIM3 ARR=167）/ 4096 点", "4.3 节 幅相测量通道"],
       ["窗函数", "Hann，幅度按 2/Σw 修正", "5.3 节 单频 DFT"],
       ["扫频点", "26 点，200 Hz~100 kHz 对数分布", "5.5 节 未知模型辨识"],
       ["稳定时间", "max(20/f, 5 ms)", "5.5 节"],
       ["辨识模型", "LP/HP/BP/BR 四模型取最小残差", "5.5 节"]],
      [4.4, 6.6, 5.2])

note("答辩小抄", "被问到“为什么 DAC 用 TIM6 而不是软件触发”，答：软件触发频率抖动大，1 MSPS 下抖动几十纳秒就会让"
                 "输出频率误差到 0.1% 量级；定时器硬件触发把抖动压到时钟周期级。")

doc.save(OUT)
print("saved", OUT)
