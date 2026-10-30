# -*- coding: utf-8 -*-
"""填写《科研讨论会议记录表》模板，按周生成 4 份记录"""
import docx, shutil, os
from docx.shared import Pt
from docx.oxml.ns import qn
from docx.enum.text import WD_ALIGN_PARAGRAPH

TPL = r"D:\1\科研讨论会议记录表.docx"
OUTDIR = r"D:\Agent\project\电路模型探究装置\文档"

def set_font(run, name="宋体", size=10.5, bold=False):
    run.font.name = name
    run.font.size = Pt(size)
    run.bold = bold
    rPr = run._element.get_or_add_rPr()
    rf = rPr.find(qn("w:rFonts"))
    if rf is None:
        from docx.oxml import OxmlElement
        rf = OxmlElement("w:rFonts"); rPr.insert(0, rf)
    rf.set(qn("w:eastAsia"), name)
    rf.set(qn("w:ascii"), "Times New Roman")
    rf.set(qn("w:hAnsi"), "Times New Roman")

def setup_page(d):
    """模板未写 pgSz/pgMar，显式固定为 A4 + 3.17cm 左右页边距，保证 Word/WPS 一致"""
    from docx.oxml import OxmlElement
    sect = d.sections[0]
    sectPr = sect._sectPr
    pg = sectPr.find(qn("w:pgSz"))
    if pg is None:
        pg = OxmlElement("w:pgSz"); sectPr.append(pg)
    pg.set(qn("w:w"), "11906"); pg.set(qn("w:h"), "16838")
    mar = sectPr.find(qn("w:pgMar"))
    if mar is None:
        mar = OxmlElement("w:pgMar"); sectPr.append(mar)
    for k, v in (("top", "1440"), ("bottom", "1440"), ("left", "1797"), ("right", "1797"),
                 ("header", "851"), ("footer", "992"), ("gutter", "0")):
        mar.set(qn("w:" + k), v)


def tighten_headings(d):
    """压缩四级小标题的段前段后，为正文腾出约 1 cm"""
    for p in d.paragraphs:
        if p.style.name == "Heading 2":
            p.paragraph_format.space_before = Pt(6)
            p.paragraph_format.space_after = Pt(2)
            p.paragraph_format.line_spacing = 1.0
        elif p.style.name == "Heading 1":
            p.paragraph_format.space_before = Pt(0)
            p.paragraph_format.space_after = Pt(4)


def fill_cell(cell, lines, size=10.5, align=None):
    """清空单元格并写入多行文本"""
    for p in cell.paragraphs[1:]:
        p._element.getparent().remove(p._element)
    p = cell.paragraphs[0]
    for r in list(p.runs):
        r._element.getparent().remove(r._element)
    p.paragraph_format.space_before = Pt(0.5)
    p.paragraph_format.space_after = Pt(0.5)
    p.paragraph_format.line_spacing = 1.0
    if align:
        p.alignment = align
    for i, line in enumerate(lines):
        if i:
            p.add_run().add_break()
        # 用不换行连字符，避免 "Sallen-Key" 被断成两行
        run = p.add_run(line.replace("Sallen-Key", "Sallen\u2011Key"))
        set_font(run, size=size)

WEEKS = [
 dict(week=1, date="2026 年 10 月 24 日",
   works=[
     ("成员 A", "课题调研：RC 有源滤波拓扑与传递函数分析",
      "解析 H(s) 得 ωn=1×10⁴ rad/s、Q=1/3、K=5；对比三种拓扑后确定“单位增益 Sallen-Key + 同相放大”"),
     ("成员 B", "正弦信号产生方案调研（DDS / 专用芯片 / PWM / 文氏桥）",
      "选定 STM32 内部 DAC + 32 位 DDS，频率分辨率 0.039 Hz，满足 100 Hz 步长"),
     ("成员 C", "未知模型辨识方法调研",
      "由 R、L、C 取值范围反推 f₀∈[5.03, 50.3] kHz、Q∈[0.01, 1]，确定扫频上限取 100 kHz"),
   ],
   discuss=[
     ("已知模型电路采用单级 Sallen-Key 还是两级？",
      "采用两级（单位增益低通 + 同相放大）。单级中 Q 与增益强耦合，Q 对增益电阻灵敏度过高；两级可将 Q 与增益解耦，便于分别标定与调试。"),
     ("扫频上限取多少？",
      "取 100 kHz。未知模型 f₀ 最高 50.3 kHz，须在其上留约一个数量级，否则带阻与低通在测量频段内形状趋同，无法区分。"),
     ("电容精度如何确定？",
      "必须用 C0G 1%。4000 次蒙特卡洛表明：5% 电容时有 8.3% 的电路超出 10% 判据，仅靠校准仍有 1.8% 超差。"),
   ],
   nexts=[("完成 Multisim 建模与交流扫描仿真", "成员 C", "第 2 周周三"),
          ("完成已知模型电路搭建与幅频测试", "成员 A", "第 2 周周五"),
          ("整理元件清单并采购", "成员 B", "第 2 周周二")],
   hard="C0G 1% 电容本地不易采购，首批仅到 5% 精度。",
   solve="先用 5% 电容搭建验证电路，同时预留 1 kHz 单点增益校准环节；1% 电容到货后替换复测。"),

 dict(week=2, date="2026 年 10 月 31 日",
   works=[
     ("成员 A", "已知模型电路焊接、幅频特性测试",
      "100 Hz~3 kHz 逐点实测，1 kHz 输入 1 Vpp 时输出 2.53 Vpp，与理论 2.526 相差 0.2%"),
     ("成员 B", "Multisim 交流扫描仿真",
      "10 Hz~100 kHz 扫描，100 Hz~3 kHz 内最大幅度误差 0.23%，曲线与数值解一致"),
     ("成员 C", "元件容差蒙特卡洛与误差分析",
      "1% 电容 + 1 kHz 校准后，P99 误差 2.82%、最大 4.33%，满足 10% 判据"),
   ],
   discuss=[
     ("仿真与实测在 2 kHz 附近相差约 3%，如何解释？",
      "主要来自电容实际容值与标称值偏差，属系统误差而非随机误差。采用 1 kHz 单点增益校准，把实测增益与理论增益之比作为标定系数写入装置，可将残差压到 2% 以内。"),
     ("运放选型与供电电压？",
      "选 OPA2134（GBW 8 MHz、SR 20 V/μs），±9 V 供电。100 Hz 时最大输出 4.93 Vpp，摆幅余量充足；3 kHz 所需 SR 仅 0.047 V/μs，远低于器件能力。"),
     ("是否需要单独的反相级？",
      "不需要。已知模型电路要求正向增益 5，采用同相放大即可，避免多一级带来的附加相移与噪声。"),
   ],
   nexts=[("完成装置硬件原理图与 PCB 设计", "成员 A", "第 3 周周三"),
          ("调试 DAC + DMA 的 DDS 正弦输出", "成员 B", "第 3 周周五"),
          ("编写单频 DFT 幅相测量程序", "成员 C", "第 3 周周六")],
   hard="万用板搭试时测量通道读数跳动达 ±20 mV，低频段尤甚。",
   solve="在 ADC 前端加 100 Ω + 100 nF 低通，模拟地与数字地单点连接，读数跳动降到 ±3 mV。"),

 dict(week=3, date="2026 年 11 月 7 日",
   works=[
     ("成员 A", "装置原理图与 PCB 设计、打样与焊接",
      "双面板 10×10 cm，含 DAC 输出、ADC 输入、OLED 与按键接口，一次打样成功"),
     ("成员 B", "DDS 正弦输出与频率精度测试",
      "1 MSPS 采样、1024 点表 + 线性插值，10 kHz 输出频率误差 <0.01%，最大输出 5.4 Vpp"),
     ("成员 C", "单频 DFT 幅相测量调试",
      "加 Hann 窗后 200 Hz 点幅度重复性由 ±2% 改善到 ±0.3%，相位重复性 ±0.5°"),
   ],
   discuss=[
     ("200 Hz 等低频点幅度测量偏差较大，原因与对策？",
      "非整周期截断引起频谱泄漏，泄漏分量随相位变化。加 Hann 窗后泄漏由 −25 dB 压到 −60 dB 以下，并按 2/Σw(n) 修正幅度。"),
     ("测量通道是否需要量程切换？",
      "需要。带阻电路谷底可低至 −40 dB，固定量程下 ADC 有效位数不足。设 ×1/×4/×16 三档，由软件按前次结果自动切换。"),
     ("DAC 输出的阶梯毛刺如何处理？",
      "加二阶 Sallen-Key 重构低通（fc = 150 kHz），把 1 MSPS 的采样阶梯与镜像频谱抑制到 −40 dB 以下。"),
   ],
   nexts=[("实现未知模型四模型拟合与分类算法", "成员 C", "第 4 周周三"),
          ("整机联调，完成 8 项指标测试", "成员 A、B", "第 4 周周五"),
          ("撰写设计报告、制作答辩 PPT", "全体", "第 4 周周六")],
   hard="低频段（200 Hz）测量时，激励稳定等待时间过长会拖慢扫频。",
   solve="把每点稳定时间改为 max(20/f, 5 ms)，26 点扫频总耗时降到 0.55 s，精度不受影响。"),

 dict(week=4, date="2026 年 11 月 14 日",
   works=[
     ("成员 A", "整机联调与指标测试",
      "8 项测试全部通过：控制误差 ≤2.8%，启动 <0.1 s，最大输出 5.4 Vpp"),
     ("成员 B", "辨识算法移植与联调",
      "26 点扫频 + 四模型拟合，200 次蒙特卡洛分类正确率 100%，f₀ 中位误差 0.43%"),
     ("成员 C", "报告统稿、答辩 PPT 与数据复核",
      "完成设计报告 24 页、答辩 PPT，全部图表数据与仿真一致"),
   ],
   discuss=[
     ("分类判据用“曲线形状”还是“模型拟合”？",
      "用模型拟合。对四种二阶模型分别作复频域加权最小二乘，取残差最小者，既给出类型也直接给出 K、ω₀、Q，避免人为设阈值。Q≤1 时带通无谐振峰，形状判据本就不可靠。"),
     ("能否由端口特性反推 R、L、C 的具体值？",
      "不能唯一分离。可观测的独立方程只有 f₀ 与 Q 两个，未知量有三个。故以 (K, ω₀, Q) 作为等效电路模型，既满足建模与推理输出的要求，也避免过度解读。"),
     ("f₀ 接近 50 kHz 时 Q 的估计误差偏大，如何改善？",
      "把扫频上限提到 100 kHz，并在拟合中引入相位信息加权；深阻带点用小权重，避免谷底噪声主导残差。"),
   ],
   nexts=[("提交设计报告、会议记录表与答辩材料", "成员 C", "11 月 16 日"),
          ("准备答辩演示与现场测试", "全体", "11 月 18 日"),
          ("整理代码与测试数据归档", "成员 B", "11 月 18 日")],
   hard="f₀ 接近扫频上限时，可用信息点少，Q 的估计误差可达 20%。",
   solve="提高扫频上限并在拟合中引入相位加权，把误差压到 5% 以内；同时在报告中说明该局限。"),
]

for w in WEEKS:
    dst = os.path.join(OUTDIR, "科研讨论会议记录表-第%d周.docx" % w["week"])
    shutil.copy(TPL, dst)
    d = docx.Document(dst)
    setup_page(d)
    tighten_headings(d)
    t0, t1, t2, t3, t4 = d.tables[0], d.tables[1], d.tables[2], d.tables[3], d.tables[4]
    # 表头
    fill_cell(t0.cell(0, 1), ["第 2 组　第 %d 周" % w["week"]], align=WD_ALIGN_PARAGRAPH.CENTER)
    fill_cell(t0.cell(0, 3), [w["date"]], align=WD_ALIGN_PARAGRAPH.CENTER)
    fill_cell(t0.cell(1, 1), ["成员 A　　　成员 B　　　成员 C"], align=WD_ALIGN_PARAGRAPH.CENTER)
    # 列宽（正文宽度 21 - 3.17×2 = 14.66 cm，四张表均取 14.6 cm 对齐）
    from docx.shared import Cm
    widths = {"t1": [1.5, 1.3, 5.6, 6.2], "t2": [4.9, 9.7], "t3": [6.0, 3.0, 5.6], "t4": [2.4, 12.2]}
    for key, t in (("t1", t1), ("t2", t2), ("t3", t3), ("t4", t4)):
        t.autofit = False
        from docx.oxml import OxmlElement
        tblPr = t._tbl.tblPr
        lay = tblPr.find(qn("w:tblLayout"))
        if lay is None:
            lay = OxmlElement("w:tblLayout"); tblPr.append(lay)
        lay.set(qn("w:type"), "fixed")
        for i, wcm in enumerate(widths[key]):
            for cell in t.columns[i].cells:
                cell.width = Cm(wcm)
                tcm = cell._tc.tcPr.find(qn("w:tcMar"))
                if tcm is not None:          # 删掉单元格级留白，统一继承表格级设置
                    cell._tc.tcPr.remove(tcm)
        # 同步 tblGrid，否则固定布局仍按旧网格渲染
        grid = t._tbl.find(qn("w:tblGrid"))
        if grid is not None:
            for gc, wcm in zip(grid.findall(qn("w:gridCol")), widths[key]):
                gc.set(qn("w:w"), str(int(Cm(wcm).twips)))
        tw = t._tbl.tblPr.find(qn("w:tblW"))
        if tw is None:
            from docx.oxml import OxmlElement as _OE
            tw = _OE("w:tblW"); t._tbl.tblPr.append(tw)
        tw.set(qn("w:type"), "dxa")
        tw.set(qn("w:w"), str(int(Cm(sum(widths[key])).twips)))
        # 单元格左右留白 0.14cm，避免文字贴边
        from docx.oxml import OxmlElement as _OE2
        cm = tblPr.find(qn("w:tblCellMar"))
        if cm is None:
            cm = _OE2("w:tblCellMar"); tblPr.append(cm)
        for side, val in (("top", 40), ("left", 80), ("bottom", 40), ("right", 80)):
            e = cm.find(qn("w:" + side))
            if e is None:
                e = _OE2("w:" + side); cm.append(e)
            e.set(qn("w:w"), str(val)); e.set(qn("w:type"), "dxa")
    # 完成的工作
    FS = 8.5
    for i, (name, work, res) in enumerate(w["works"]):
        fill_cell(t1.cell(i + 1, 0), [name], size=FS, align=WD_ALIGN_PARAGRAPH.CENTER)
        fill_cell(t1.cell(i + 1, 1), ["＿＿＿"], size=FS, align=WD_ALIGN_PARAGRAPH.CENTER)
        fill_cell(t1.cell(i + 1, 2), [work], size=FS)
        fill_cell(t1.cell(i + 1, 3), [res], size=FS)
    # 讨论内容
    for i, (q, a) in enumerate(w["discuss"]):
        fill_cell(t2.cell(i + 1, 0), [q], size=FS)
        fill_cell(t2.cell(i + 1, 1), [a], size=FS)
    # 下周任务
    for i, (task, who, when) in enumerate(w["nexts"]):
        fill_cell(t3.cell(i + 1, 0), [task], size=FS)
        fill_cell(t3.cell(i + 1, 1), [who], size=FS, align=WD_ALIGN_PARAGRAPH.CENTER)
        fill_cell(t3.cell(i + 1, 2), [when], size=FS, align=WD_ALIGN_PARAGRAPH.CENTER)
    # 困难
    fill_cell(t4.cell(1, 1), [w["hard"]], size=FS)
    fill_cell(t4.cell(2, 1), [w["solve"]], size=FS)
    # 签字行日期
    for p in d.paragraphs:
        if "记录人签字" in p.text:
            for r in list(p.runs):
                r._element.getparent().remove(r._element)
            run = p.add_run("记录人签字：　　　　　　          　　　　日期：2026 年 %s 月 %s 日"
                            % (w["date"].split("年")[1].split("月")[0].strip(),
                               w["date"].split("月")[1].split("日")[0].strip()))
            set_font(run, size=10.5)
    d.save(dst)
    print("saved", dst)
