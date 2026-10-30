# -*- coding: utf-8 -*-
"""生成《Keil 建工程与烧录指南》"""
import os
from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

# 注：本文档内容与《Keil手动建工程指南（不用CubeMX）》高度重叠，
# 2026-10-30 精简时已从仓库移除，脚本保留作历史记录，输出改到 文档\ 以免写入已删除的 归档\。
OUT = r"D:\Agent\project\电路模型探究装置\文档\Keil建工程与烧录指南.docx"
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
hr = hp.add_run("电路模型探究装置 · Keil 建工程与烧录指南")
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
    pf.space_before = Pt(14); pf.space_after = Pt(6); pf.line_spacing = 1.25
    r = p.add_run(text); r.font.size = Pt(15); r.bold = True
    r.font.color.rgb = RGBColor(0x1F, 0x33, 0x4E)
    _rf(r, "Times New Roman", HEI)


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



def fig(path, width_cm):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(6)
    p.paragraph_format.space_after = Pt(2)
    p.add_run().add_picture(path, width=Cm(width_cm))

# ------------------------------------------------------------------ 封面
for _ in range(4):
    doc.add_paragraph()
p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = p.add_run("电路模型探究装置 · 硬件实现")
r.font.size = Pt(11); r.font.color.rgb = RGBColor(0x55, 0x55, 0x55)
_rf(r, "Times New Roman", SONG)

p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
p.paragraph_format.space_before = Pt(20)
r = p.add_run("Keil 建工程与烧录指南")
r.font.size = Pt(30); r.bold = True; r.font.color.rgb = RGBColor(0x1F, 0x33, 0x4E)
_rf(r, "Times New Roman", HEI)

p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
p.paragraph_format.space_before = Pt(8)
r = p.add_run("从 CubeMX 配置到串口验证的完整流程")
r.font.size = Pt(12); r.font.color.rgb = RGBColor(0x66, 0x66, 0x66)
_rf(r, "Times New Roman", SONG)

for _ in range(7):
    doc.add_paragraph()
for line in ("配套代码：固件/App（4 个模块）＋ 固件/Core/main.c",
             "目标芯片：STM32F407VET6（168 MHz，512 KB Flash，片内 12 位 DAC/ADC）",
             "工具链：STM32CubeMX 6.x ＋ Keil MDK-ARM 5.38 ＋ 芯片自带 USB DFU（无需 ST-Link）"):
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
h1("1　先分清两套“代码”")
body("很多人卡在第一步，是因为把两套东西混为一谈了。本课题实际存在两套完全不同的代码，运行位置、语言、工具都不同：")
cap("表 1　两套代码的分工")
table(["", "设计脚本（Python）", "固件程序（C）"],
      [["运行在哪", "电脑上，跑一次出图出文档", "STM32F407 芯片内部"],
       ["语言/工具", "Python 3.13 + NumPy/SciPy/Matplotlib", "C（C99）+ Keil MDK-ARM"],
       ["干什么", "算 H(s)、画 Bode 图、蒙特卡洛、拟合算法验证", "产生正弦、采样、算幅相、辨识、显示"],
       ["能否烧进单片机", "不能，单片机不认 Python", "能，编译成 .hex/.axf 后由 ST-Link 写入"],
       ["本文档对应", "源码/ 目录（已在《完整操作过程与源码说明》中）", "固件/ 目录"]],
      [2.6, 6.4, 7.2])
body("所以“把代码导入单片机”这句话，落到操作上其实是：在 Keil 里建一个 STM32 工程，把固件/ 目录下的 C 文件加进去，"
     "编译、下载。报告里的 Python 只是用来验证算法正确、生成图表，不参与烧录。")

h1("2　你需要准备什么")
cap("表 2　软硬件清单")
table(["类别", "项目", "说明"],
      [["软件", "Keil MDK-ARM 5.38+", "编译器选 ARM Compiler 6"],
       ["软件", "STM32F4xx_DFP 2.17", "Keil Pack Installer 中安装，装完才能选到 F407"],
       ["软件", "STM32CubeMX 6.10+", "生成时钟与外设初始化，避免手写寄存器"],
       ["软件", "ST-Link 驱动", "随 Keil 安装，插上后设备管理器出现 STLink"],
       ["硬件", "STM32F407 开发板", "需带 8 MHz 晶振；核心板 + 底板亦可"],
       ["硬件", "ST-Link V2（可选）", "有则最省事；没有就用芯片自带 USB DFU，见第 6 章"],
       ["硬件", "STM32CubeProgrammer", "DFU / 串口 ISP 烧录用，ST 官网免费"],
       ["硬件", "USB-TTL 串口模块（可选）", "接 PA2/PA3 看 printf；没有就先靠 OLED 或示波器"],
       ["硬件", "示波器", "验证 DAC 输出与电路幅频（可先用万用表交流档粗看）"]],
      [1.8, 5.4, 9.0])

h1("3　路线 A：CubeMX 生成工程（推荐）")
body("CubeMX 的价值在于把 168 MHz 时钟树、DMA 请求映射、NVIC 这些容易配错的东西一次配好，"
     "生成出来的工程直接能用 Keil 打开。下面按它左侧的栏目顺序逐项配置。")

h2("3.1　芯片与时钟")
body("新建工程 → 搜索 STM32F407VETx（你这块是 VET6，LQFP100，512 KB Flash）→ 双击进入。"
     "Clock Configuration 页：Input frequency 填 8（板载 8 MHz 晶振，25 MHz 的板子填 25），"
     "PLL Source 选 HSE，然后依次设 PLLM=8、PLLN=336、PLLP=2、PLLQ=7，"
     "把 SYSCLK 拉到 168 MHz，APB1 自动为 42 MHz、APB2 为 84 MHz。")

h2("3.2　外设配置")
cap("表 3　CubeMX 外设配置")
table(["外设", "模式", "关键参数", "引脚"],
      [["DAC", "OUT1 使能", "Trigger = TIM6 TRGO；Output Buffer 使能", "PA4"],
       ["TIM6", "内部时钟", "PSC = 0，ARR = 83（84 MHz ÷ 84 = 1 MSPS）", "—"],
       ["ADC1", "IN0 单端", "12 bit；外部触发 TIM3 TRGO；DMA Continuous", "PA0"],
       ["TIM3", "内部时钟", "PSC = 0，ARR = 167（84 MHz ÷ 168 = 500 kSPS）", "—"],
       ["USART2", "Asynchronous", "115200 8N1", "PA2 / PA3"],
       ["SYS", "Debug = Serial Wire", "保留 SWD，别选 JTAG 占引脚", "PA13/PA14"]],
      [2.4, 3.4, 7.6, 2.8])
note("采样率怎么来的", "APB1 的定时器时钟是 84 MHz。TIM6 的更新频率 = 84 MHz ÷ (ARR+1)，"
                       "取 ARR=83 正好 1 MHz；TIM3 取 ARR=167 得 500 kHz。若你把 APB1 分频改了，这两个数必须重算。")

h2("3.3　DMA 与中断")
cap("表 4　DMA 配置")
table(["外设", "Stream / Channel", "方向", "模式", "数据宽度"],
      [["DAC1_CH1", "DMA2 Stream5 / Ch7", "Memory → Peripheral", "Circular", "Half Word"],
       ["ADC1", "DMA2 Stream0 / Ch0", "Peripheral → Memory", "Circular", "Half Word"]],
      [2.6, 5.0, 4.6, 2.4, 2.2])
body("NVIC 页把 DMA2 Stream5（DAC）与 DMA2 Stream0（ADC）的中断都使能。"
     "DAC 必须是 Circular：DDS 要连续不断地输出；ADC 也是 Circular，每次采完 N 点由回调置标志。")

h2("3.4　生成工程")
body("Project Manager 页：Toolchain 选 MDK-ARM，Min Version V5；"
     "Code Generator 里务必勾选 “Generate peripheral initialization as a pair of '.c/.h' files per peripheral”。"
     "这一项决定了 hdac、hadc1 这些句柄是定义在 dac.c 里还是塞在 main.c 里——"
     "我们要替换 main.c，所以必须让它们分出去，否则会报“重复定义”。")
body("点 GENERATE CODE，得到 MDK-ARM/工程名.uvprojx。")

h1("4　把代码导入 Keil")
body("“导入”在 Keil 里没有专门的按钮，实际就是三件事：把文件拷进工程目录、把文件加进分组、把目录加进头文件搜索路径。")
body("① 把 固件/App/ 整个目录拷到工程根目录（与 Core/ 同级）。", indent=False)
body("② 用 固件/Core/main.c 覆盖 Core/Src/main.c（系统时钟配置已经写在里面，不会缺函数）。", indent=False)
body("③ Keil 左侧 Project 窗口右键 Target → Manage Project Items，新建分组 App，"
     "选中它 → Add Files → 加入 app_dds.c、app_meas.c、app_known.c、app_ident.c。", indent=False)
body("④ Options for Target（Alt+F7）→ C/C++：Include Paths 里加上 ../App；C99 Mode 勾选；"
     "Optimization 选 -O1。", indent=False)
body("⑤ Target 页勾选 Use MicroLIB（printf 重定向依赖它）。", indent=False)
body("⑥ F7 编译，应当 0 Error 0 Warning。", indent=False)

note("关于中文注释乱码", "Keil 默认按本地编码读文件。若注释显示乱码，"
                          "在 Edit → Configuration → Editor → Encoding 里选 UTF-8，重新打开文件即可。")

h1("5　编译：先产出可烧录文件")
body("不管用哪种方式烧录，第一步都是让 Keil 产出可烧写的文件。Keil 默认只生成 .axf（带调试信息，给仿真器用），"
     "需要手动打开 HEX 输出：Options for Target（Alt+F7）→ Output 页 → 勾选 Create HEX File。"
     "若还想同时产出 .bin（CubeProgrammer 两种都吃，bin 更小），在 User 页的 After Build 里加一条 fromelf 命令。")
code_block('fromelf --bin --output ".\\Objects\\app.bin" ".\\Objects\\app.axf"')
body("按 F7 编译，Objects 目录下就会出现 工程名.hex 与 app.bin。这两个文件才是最终要写进芯片的东西，"
     ".axf 不要拿去烧。")

h1("6　没有 ST-Link：用芯片自带的 USB DFU")
body("STM32F407 的 System Memory 里固化了一段 ROM bootloader，支持 USB DFU——不需要任何仿真器，"
     "一根 USB 线就能烧程序。你的板子 USB 口直接接在 MCU 的 PA11/PA12（OTG_FS）上，"
     "现在插上能枚举出 U 盘就是最好的证明：USB 是直连芯片的，DFU 一定能用。")

body("你这块板子的丝印是 STM32_F4VE（DevEBox 出品），主控 STM32F407VET6：LQFP100 封装、512 KB Flash、"
     "192 KB RAM；板载 8 MHz 与 32.768 kHz 两颗晶振，另有 MicroSD 卡槽与 W25Q16 SPI Flash——"
     "后两者正是第 7 章那两个 U 盘的来源。各接口位置见图 1。")
body("两个最容易搞错的地方：一是 Flash 只有 512 KB，CubeMX 里要选 STM32F407VETx 而不是 VGTx，"
     "Keil 的下载算法也要选 STM32F4xx 512KB Flash；二是这块板没有 BOOT0 跳线帽，BOOT0 是上排第 1 根针（丝印 BT0），"
     "紧挨着两根 3V3，用杜邦线短接即可。")
fig(r"D:\Agent\project\电路模型探究装置\模拟\板卡接口标注图.png", 12.6)
cap("图 1　板卡关键接口位置（编号与下方图例对应）")

h2("6.1　三个前提")
cap("表 5　DFU 的前提条件")
table(["条件", "怎么确认", "不满足时"],
      [["BOOT0 可操作", "你这块板上没有跳线帽，BOOT0 是上排第 1 根针，标注 BT0，紧挨两根 3V3", "用杜邦线把 BT0 与 3V3 短接即可；烧完必须拔掉"],
       ["USB 是数据线", "插上能认到 U 盘，说明线没问题", "换一根手机数据线（很多充电线只有电源）"],
       ["装了 CubeProgrammer", "ST 官网免费下载，装完在开始菜单里", "装 STM32CubeProgrammer，自带 CLI"]],
      [3.6, 7.4, 5.2])

h2("6.2　进入 DFU 模式")
body("① 用一根杜邦线把上排的 BT0 针与旁边的 3V3 针短接（母对母杜邦线最方便）；", indent=False)
body("② 按一下左上角的复位键（没有就拔插一次 USB，效果一样）；", indent=False)
body("③ 打开设备管理器，通用串行总线设备下应出现 STM32 BOOTLOADER，硬件 ID 为 USB\\VID_0483&PID_DF11。", indent=False)
body("此时原来那两个 U 盘会消失，这是正常的——芯片没跑用户程序，自然不会再模拟 U 盘。")
note("为什么必须拔掉那根线", "BT0 接着 3V3 时，芯片每次复位都会回到 ROM bootloader，程序永远跑不起来。烧完一定要拔掉这根杜邦线，再按一次复位。")

h2("6.3　用 CubeProgrammer 烧录")
cap("表 6　CubeProgrammer 操作步骤")
table(["步骤", "操作", "判断成功的标志"],
      [["1", "打开 STM32CubeProgrammer", "主界面右上角有连接方式下拉框"],
       ["2", "连接方式选 USB，Port 选 USB1", "—"],
       ["3", "点 Connect（或按 Connect 按钮）", "右侧信息栏出现 Device: STM32F407xx、Flash size 512 KB"],
       ["4", "左侧 Download 页 → 浏览选择 .hex 或 .bin", "选 bin 时 Start address 填 0x08000000；hex 会自动带地址"],
       ["5", "点 Download", "进度条走完，日志出现 Download verified successfully"],
       ["6", "BOOT0 跳回 0 V，按复位", "程序开始运行，串口打印启动信息"]],
      [1.4, 8.2, 6.6])

body("烧录时间约 5~15 s（DFU 比 ST-Link 慢，属正常）。若中途报错，先点 Disconnect 再重新 Connect，"
     "不要在半连接状态下重复点 Download。")

h2("6.4　让 Keil 顺手把烧录也做了（可选）")
body("Options for Target → User 页 → After Build/Rebuild → Run #1，填入下面这条命令，编译完自动调 CLI 烧录：")
code_block('"C:\\Program Files\\STMicroelectronics\\STM32Cube\\STM32CubeProgrammer\\bin\\STM32_Programmer_CLI.exe" '
           '-c port=USB1 -w ".\\Objects\\app.hex" -v -rst')
body("注意这条命令要求芯片此刻已经在 DFU 模式。所以实际节奏是：BOOT0=1 → 复位 → F7（编译并自动烧）→ "
     "BOOT0=0 → 复位。如果嫌麻烦，就用 6.3 的图形界面，编译和烧录分开做，反而更稳。")

h2("6.5　备选：串口 ISP")
body("若你的板子 USB 口其实是 USB-TTL（CH340/CP2102），或者手上有一只 USB-TTL 模块，也可以走串口 ISP："
     "BOOT0=1 → USB-TTL 接 PA9(MCU TX)/PA10(MCU RX) 与 GND → CubeProgrammer 连接方式选 UART、"
     "Port 选对应 COM 口、波特率 115200 → 烧完 BOOT0=0 复位。")
body("你现在设备管理器里一个 COM 口都没有，说明板子的 USB 是直连 MCU 的，不是串口芯片，所以这条路暂时用不上。")

note("关于在线调试", "没有 ST-Link / DAP-Link 就只能“编译 + 烧录 + 看串口打印”，不能打断点单步。"
                      "本固件已经把关键量都从串口打出来了（M 命令看幅相、L 命令看辨识结果），"
                      "调试信息足够定位问题；真需要单步，再补一个 ST-Link 或 DAP-Link。")

h1("7　插上板子为什么多出两个 U 盘")
body("这不是我加的盘，也不是中病毒。你板子里现在跑的是 ST 官方的 USB 大容量存储例程（MSC），"
     "USB 设备 ID 为 VID_0483 & PID_5720 —— 0483 是 ST 的厂商号，5720 正是 STM32 的 MSC 示例。"
     "这个例程把板子上的 SPI Flash 与 SD 卡槽各模拟成一个磁盘，所以一次冒出两个盘符。")
cap("表 7　两个盘分别是什么")
table(["盘符", "设备名", "实际是什么", "容量"],
      [["E:", "MCUDWVTH SPI Flash Disk", "板载 SPI Flash（多为 W25Q16）", "2 MB"],
       ["F:", "MCUDWVTH SD Flash Disk", "SD 卡槽，没插卡", "0"]],
      [1.8, 5.4, 6.0, 2.6])
body("至于“两个 E、两个 F”：同一个逻辑单元在 Windows 里会注册成两种设备节点——"
     "一种是“可移动磁盘”（USB 大容量存储设备），一种是“便携设备”（WPD）。"
     "设备管理器与“此电脑”各显示一次，看起来就像两套盘。这属于 Windows 的显示方式，不是多出来的硬件。")
note("千万别往里拖 hex", "这两个盘只是把文件写进 SPI Flash / SD 卡，芯片里的程序一点没变。"
                          "往里面拷 .hex 不会烧录，也不会影响运行。要烧程序只有第 6 章的 DFU 或 6.5 的串口 ISP 两条路。")
body("反过来说：一旦你把自己的固件烧进去，这两个 U 盘就会消失——因为 MSC 例程被覆盖了。"
     "这是正常现象，不是板子坏了；想恢复就重新烧回 ST 的 MSC 例程。")

h1("8　上电验证（按顺序，别跳步）")
body("硬件调试最忌一上来就整机联调。按下面五步逐级验证，出错时能立刻定位到哪一级。")
cap("表 8　五级验证")
table(["步骤", "操作", "预期现象", "不通过时先查"],
      [["1 串口", "USB-TTL 接 PA2/PA3，115200，上电", "打印 ==== Circuit Model Explorer ====", "TX/RX 是否接反、波特率"],
       ["2 DAC", "输入 F1000 → A1.0，示波器看 PA4", "1 kHz、1 Vpp、偏置 1.65 V 正弦", "TIM6 是否启动、DMA 是否 Circular"],
       ["3 ADC", "PA4 用导线短接 PA0，输入 M", "读到约 1.0 Vpp", "ADC 触发源、DMA 通道"],
       ["4 开环", "接已知模型电路，输入 C1.5", "打印目标/实测/误差，误差 ≤3%", "电路增益、kcal 校准值"],
       ["5 辨识", "接未知 RLC 电路，输入 L", "约 0.6 s 后打印类型与 K、f0、Q", "激励幅度是否 ≥1.5 Vpp"]],
      [1.8, 5.6, 5.0, 3.8])

body("串口命令一览：")
code_block("?            帮助\n"
           "F1000        设定频率 1000 Hz\n"
           "A2.0         设定激励峰峰值 2.0 V\n"
           "M            测量当前输出幅相\n"
           "H            打印当前频率下已知模型的 |H|\n"
           "K1.002       设定 1 kHz 校准系数\n"
           "C1.5         开环控制：让已知模型输出达到 1.5 Vpp\n"
           "L            未知模型自主学习（26 点扫频 + 分类 + 参数）")

note("没有串口怎么办", "板子的 USB 直连 MCU，被 MSC 例程占用了。烧了新固件后 USB 就不再是 U 盘，"
                        "此时要么接一只 USB-TTL 到 PA2/PA3 看打印，要么把固件里的 printf 改成 OLED 显示。"
                        "建议先买一只 CH340 模块（十元左右），调试效率差很多。")

h1("9　常见错误对照")
cap("表 9　烧录与运行阶段的典型问题")
table(["现象", "原因", "处理"],
      [["设备管理器找不到 STM32 BOOTLOADER", "没进 DFU：BOOT0 没拉高或没复位", "BOOT0=1 后必须复位一次，芯片才会重新枚举"],
       ["CubeProgrammer 点 Connect 报 No STM32 device", "芯片不在 DFU 模式，或 USB 线只有电源", "确认硬件 ID 是 0483:DF11；换数据线"],
       ["Download 到一半报错", "连接中断或 Flash 未擦除", "Disconnect → 重新 Connect → 勾 Full chip erase 再烧"],
       ["烧完不运行", "BT0 还接着 3V3", "拔掉杜邦线，按复位"],
       ["CubeProgrammer 显示 512 KB，怀疑买到假货", "VET6 本来就是 512 KB（VG 才是 1 MB）", "无需处理，正常"],
       ["hdac 重定义 / multiple definition", "CubeMX 未勾 pair of .c/.h files", "回 CubeMX 勾上重新生成"],
       ["printf 无输出", "未勾 MicroLIB 或 fputc 被删", "勾 MicroLIB，保留 main.c 中的 fputc"],
       ["DAC 输出恒定不变", "TIM6 未 Start 或 DMA 非 Circular", "检查 DDS_Init 中 HAL_TIM_Base_Start(&htim6)"],
       ["输出频率差一倍", "TIM6 的 ARR 与 APB1 时钟不匹配", "按 定时器时钟/(ARR+1) 重算"],
       ["测量值随频率大幅漂移", "重构低通截止太低或 ADC 量程不够", "先直连示波器看 DAC 原始输出，再查前端"],
       ["辨识恒为 Low-pass", "激励太小、噪声主导", "把 A 设到 1.5~2 Vpp 再 L"]],
      [5.0, 5.0, 6.2])

h1("10　固件文件说明")
cap("表 10　各文件职责与调用关系")
table(["文件", "职责", "被谁调用"],
      [["board.h", "声明 CubeMX 生成的 hdac/hadc1/htim3/htim6/huart2", "全部模块"],
       ["app_dds.c/.h", "32 位相位累加、1024 点 Q15 正弦表 + 线性插值、DAC DMA 双缓冲", "main、app_ident"],
       ["app_meas.c/.h", "ADC DMA 采集、去直流、Hann 窗单频 DFT、幅相输出", "main、app_ident"],
       ["app_known.c/.h", "已知模型 |H|、相位、开环反算 Vin", "main"],
       ["app_ident.c/.h", "26 点扫频、四模型拟合、分类与参数输出", "main"],
       ["main.c", "时钟、外设初始化、串口命令行", "—"]],
      [3.2, 8.6, 4.4])

body("模块之间是单向依赖：main 调用四个模块，app_ident 只依赖 dds 与 meas，不反向调用 main。"
     "因此你可以单独把 app_dds 拿到别的工程里用，不牵动其他文件。")

h1("11　与设计报告的一致性")
body("固件里的每一个参数都能在报告里找到出处，答辩被问到“为什么是这个数”时可以直接翻到对应章节。")
cap("表 11　关键参数对照")
table(["参数", "固件中的值", "报告出处"],
      [["DAC 更新率", "1 MSPS（TIM6，ARR=83）", "4.2 节 正弦信号发生通道"],
       ["正弦表", "1024 点，Q15，线性插值", "4.2 节"],
       ["ADC 采样率 / 点数", "500 kSPS / 4096 点（8.192 ms 窗）", "4.3 节 幅相测量通道"],
       ["窗函数", "Hann，幅度按 2/Σw 修正", "5.3 节 单频 DFT"],
       ["扫频点", "26 点，200 Hz~100 kHz 对数分布", "5.5 节 未知模型辨识"],
       ["稳定时间", "max(20/f, 5 ms)", "5.5 节"],
       ["辨识模型", "LP/HP/BP/BR 四模型取最小残差", "5.5 节"],
       ["已知模型 H(s)", "K=5，ωn=1e4，Q=1/3", "3.1 节 传递函数分析"]],
      [4.4, 6.4, 5.4])

note("提醒", "固件里的 DAC 满幅按 2.70 Vpp 折算（DDS_DAC_FULL_VPP），这是实测标定值。"
             "换板子或换供电后应重新测一次，否则 C 命令给出的激励会整体偏大或偏小。")

doc.save(OUT)
print("saved", OUT)
