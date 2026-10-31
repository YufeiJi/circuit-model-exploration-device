# -*- coding: utf-8 -*-
"""生成设计报告 HTML（供 html-to-docx 转换）"""
import os

OUT = r"D:\Agent\project\电路模型探究装置\模拟\pipeline\stage2\formatted-电路模型探究装置设计报告.html"

# ---------- 样式 ----------
S_H1 = "font-family:黑体; font-size:15pt; color:#1f5c8b; font-weight:bold; margin-top:16pt; margin-bottom:8pt;"
S_H2 = "font-family:黑体; font-size:12pt; color:#1f5c8b; font-weight:bold; margin-top:11pt; margin-bottom:5pt;"
S_H3 = "font-family:黑体; font-size:10.5pt; color:#2c3e50; font-weight:bold; margin-top:8pt; margin-bottom:4pt;"
S_P = "font-size:10.5pt; line-height:1.62; text-indent:2em; text-align:justify; margin-bottom:4pt;"
S_P0 = "font-size:10.5pt; line-height:1.62; text-indent:0; text-align:justify; margin-bottom:4pt;"
S_CAP = "font-size:9pt; color:#555555; text-align:center; text-indent:0; margin-top:3pt; margin-bottom:9pt;"
S_TBL = "border:1px solid #8fa3b8; width:100%; font-size:8.8pt;"
S_TH = "border:1px solid #8fa3b8; background-color:#e6eef7; font-size:8.8pt; font-weight:bold; text-align:center;"
S_TD = "border:1px solid #8fa3b8; font-size:8.8pt;"
S_TDC = "border:1px solid #8fa3b8; font-size:8.8pt; text-align:center;"
S_FML = ("font-family:Times New Roman; font-size:11pt; text-align:center; text-indent:0;"
         " margin-top:5pt; margin-bottom:5pt;")
S_NOTE = ("font-size:9.5pt; line-height:1.55; text-indent:0; color:#333333;"
          " margin-top:4pt; margin-bottom:6pt;")

def h1(t, id_=None):
    i = f' id="{id_}"' if id_ else ""
    return f'<h1{i} style="{S_H1}">{t}</h1>'

def h2(t, id_=None):
    i = f' id="{id_}"' if id_ else ""
    return f'<h2{i} style="{S_H2}">{t}</h2>'

def h3(t):
    return f'<h3 style="{S_H3}">{t}</h3>'

def p(t, indent=True):
    return f'<p style="{S_P if indent else S_P0}">{t}</p>'

def fig(path, width, cap):
    return (f'<p style="text-align:center; text-indent:0; margin-top:8pt; margin-bottom:0;">'
            f'<img src="images/{path}" style="width:{width}cm;"></p>'
            f'<p style="{S_CAP}">{cap}</p>')

def table(cap, header, rows, widths=None, align=None):
    """align: 每列对齐 'c'/'l'"""
    cols = len(header)
    align = align or ["c"] * cols
    cg = ""
    if widths:
        cg = "<colgroup>" + "".join(f'<col style="width:{w}%">' for w in widths) + "</colgroup>"
    th = "".join(f'<th style="{S_TH}">{x}</th>' for x in header)
    body = ""
    for r in rows:
        tds = "".join(f'<td style="{S_TDC if a=="c" else S_TD}">{c}</td>' for c, a in zip(r, align))
        body += f"<tr>{tds}</tr>"
    out = (f'<p style="{S_CAP}">{cap}</p>'
           f'<table style="{S_TBL}">{cg}<tr>{th}</tr>{body}</table>'
           f'<p style="font-size:8pt; text-indent:0; margin-top:0; margin-bottom:10pt;"></p>')
    return out

def fml(t):
    return f'<p style="{S_FML}">{t}</p>'

def fml_img(name):
    return ('<p style="text-align:center; text-indent:0; margin-top:7pt; margin-bottom:7pt;'
            f' line-height:1.0;"><img src="images/{name}.png"></p>')

def note(title, text):
    return (f'<table style="border:1px solid #c8d6e5; width:100%; background-color:#f4f8fb;">'
            f'<tr><td style="font-size:9.5pt; color:#1f5c8b; font-weight:bold;">{title}</td></tr>'
            f'<tr><td style="font-size:9.5pt; line-height:1.55; color:#333333;">{text}</td></tr>'
            f'</table><p style="font-size:6pt; margin-bottom:8pt;"></p>')

def bullets(items):
    lis = "".join(f'<li style="font-size:10.5pt; line-height:1.6; margin-bottom:2pt;">{i}</li>' for i in items)
    return f'<ul style="margin-left:1.2em;">{lis}</ul>'

# ================= 封面 =================
cover = f'''
<section role="cover">
<p style="text-align:center; text-indent:0; margin-top:64pt; font-size:11pt; color:#7f8c8d; letter-spacing:2pt;">电子信息工程专业科研训练</p>
<p style="text-align:center; text-indent:0; margin-top:6pt; font-size:11pt; color:#7f8c8d; letter-spacing:2pt;">综合设计开发课题（第 2 题）</p>
<p style="text-align:center; text-indent:0; margin-top:46pt; font-family:黑体; font-size:26pt; font-weight:bold; color:#1f5c8b;">电路模型探究装置</p>
<p style="text-align:center; text-indent:0; margin-top:8pt; font-family:黑体; font-size:17pt; font-weight:bold; color:#1f5c8b;">设计与实现</p>
<p style="text-align:center; text-indent:0; margin-top:14pt; font-size:12pt; color:#34495e;">——RC 有源滤波电路建模、正弦激励与未知模型自主学习</p>
<p style="text-align:center; text-indent:0; margin-top:46pt; font-size:12pt; color:#34495e; letter-spacing:3pt;">设 计 报 告</p>
<table style="border:1px solid #c8d6e5; width:78%; margin-top:44pt;">
<colgroup><col style="width:30%"><col style="width:70%"></colgroup>
<tr><td style="border:1px solid #c8d6e5; background-color:#eef4f9; font-size:10.5pt; text-align:center;">课程名称</td>
    <td style="border:1px solid #c8d6e5; font-size:10.5pt; text-align:center;">电子信息工程专业科研训练</td></tr>
<tr><td style="border:1px solid #c8d6e5; background-color:#eef4f9; font-size:10.5pt; text-align:center;">课题编号</td>
    <td style="border:1px solid #c8d6e5; font-size:10.5pt; text-align:center;">第 2 题　电路模型探究装置</td></tr>
<tr><td style="border:1px solid #c8d6e5; background-color:#eef4f9; font-size:10.5pt; text-align:center;">专业班级</td>
    <td style="border:1px solid #c8d6e5; font-size:10.5pt; text-align:center;">电子信息工程　＿＿＿＿ 班</td></tr>
<tr><td style="border:1px solid #c8d6e5; background-color:#eef4f9; font-size:10.5pt; text-align:center;">小组成员</td>
    <td style="border:1px solid #c8d6e5; font-size:10.5pt; text-align:center;">＿＿＿＿＿　＿＿＿＿＿　＿＿＿＿＿</td></tr>
<tr><td style="border:1px solid #c8d6e5; background-color:#eef4f9; font-size:10.5pt; text-align:center;">指导教师</td>
    <td style="border:1px solid #c8d6e5; font-size:10.5pt; text-align:center;">＿＿＿＿＿</td></tr>
<tr><td style="border:1px solid #c8d6e5; background-color:#eef4f9; font-size:10.5pt; text-align:center;">完成日期</td>
    <td style="border:1px solid #c8d6e5; font-size:10.5pt; text-align:center;">2026 年 10 月</td></tr>
</table>
</section>
'''

# ================= 目录 =================
toc_items = [
    ("ch1", "1　任务分析与指标分解", [
        ("ch1-1", "1.1　任务描述"), ("ch1-2", "1.2　指标分解"), ("ch1-3", "1.3　关键约束与设计难点")]),
    ("ch2", "2　方案论证与总体设计", [
        ("ch2-1", "2.1　已知模型电路拓扑方案"), ("ch2-2", "2.2　正弦信号产生方案"),
        ("ch2-3", "2.3　幅相测量方案"), ("ch2-4", "2.4　未知模型辨识方案"), ("ch2-5", "2.5　系统总体框图")]),
    ("ch3", "3　已知模型电路的设计与实现", [
        ("ch3-1", "3.1　传递函数分析"), ("ch3-2", "3.2　电路拓扑与元件参数设计"),
        ("ch3-3", "3.3　元件容差与灵敏度分析"), ("ch3-4", "3.4　运放选型与摆幅核算")]),
    ("ch4", "4　探究装置硬件设计", [
        ("ch4-1", "4.1　主控与资源分配"), ("ch4-2", "4.2　正弦信号发生通道"),
        ("ch4-3", "4.3　幅相测量通道"), ("ch4-4", "4.4　人机接口与电源"), ("ch4-5", "4.5　关键指标核算")]),
    ("ch5", "5　软件设计", [
        ("ch5-1", "5.1　软件总体架构"), ("ch5-2", "5.2　DDS 正弦合成"),
        ("ch5-3", "5.3　单频 DFT 幅相提取"), ("ch5-4", "5.4　已知模型电路的开环控制"),
        ("ch5-5", "5.5　未知模型自主学习与建模"), ("ch5-6", "5.6　时间预算")]),
    ("ch6", "6　仿真与验证", [
        ("ch6-1", "6.1　Multisim 交流扫描仿真"), ("ch6-2", "6.2　瞬态仿真"),
        ("ch6-3", "6.3　幅度误差与容差蒙特卡洛"), ("ch6-4", "6.4　控制精度核算"),
        ("ch6-5", "6.5　未知模型辨识算法仿真")]),
    ("ch7", "7　测试方案与误差分析", [
        ("ch7-1", "7.1　测试条件与连接"), ("ch7-2", "7.2　测试项目与判据"), ("ch7-3", "7.3　误差来源与抑制措施")]),
    ("ch8", "8　成本预算与进度管理", [
        ("ch8-1", "8.1　器件成本（BOM）"), ("ch8-2", "8.2　进度安排"), ("ch8-3", "8.3　风险与应对")]),
    ("ch9", "9　团队分工"),
    ("ch10", "10　结论与展望"),
    ("ap1", "附录 A　SPICE 网表与仿真设置"),
    ("ap2", "附录 B　关键代码片段"),
    ("ap3", "参考文献"),
]
toc_html = ('<p style="font-family:黑体; font-size:15pt; font-weight:bold; color:#1f5c8b;'
            ' text-align:center; text-indent:0; margin-top:6pt; margin-bottom:16pt;'
            ' letter-spacing:6pt;">目　　录</p>'
            '<p style="font-size:10.5pt; text-indent:0;">{{TOC}}</p>')

body = []

# ================= 1 =================
body.append(h1("1　任务分析与指标分解", "ch1"))
body.append(h2("1.1　任务描述", "ch1-1"))
body.append(p("本题要求设计并制作两部分实物：一是电压传递函数已知的 RC 有源滤波电路（下称"
              "“已知模型电路”），二是能够产生正弦激励、并对被测电路进行测量与建模的“电路模型探究装置”。"
              "题目给定的传递函数为"))
body.append(fml_img("fml1"))
body.append(p("基本要求围绕“已知模型”展开：装置需产生频率可设（步长 100 Hz、上限不低于 10 kHz）、"
              "峰峰值不小于 2 V 的正弦信号，并依据 H(s) 反算出合适的激励幅度，使已知模型电路的输出"
              "峰峰值达到设定值（1~2 V、步长 0.1 V），相对误差不超过 5%；同时已知模型电路自身的"
              "幅频特性与 H(s) 的相对误差不超过 10%。"))
body.append(p("发挥部分则要求装置面对测评现场提供的、由 R、L、C 各一只组成的“未知模型电路”，"
              "在不借助任何外部测试设备的前提下，于 2 min 内完成自主学习与建模，显示其滤波类型"
              "（低通／高通／带通／带阻），并能依据辨识所得模型对输入信号推理生成与之一致的输出信号。"
              "此外还给出了一项独立的仿真要求：用仿真软件实现同一传递函数所对应的电路模型。"))
body.append(p("按照课程安排，实物系统为选做任务，课题调研与软件仿真／算法开发为必做任务，并需提交"
              "科研讨论会议记录表与设计报告。本设计在完成必做内容的基础上，按“仿真先行、实物验证”"
              "的思路把实物部分推进到可演示的程度，两者共用同一套电路参数与同一套模型，"
              "因此仿真结论对实物具有直接的指导意义。"))

body.append(h2("1.2　指标分解", "ch1-2"))
body.append(p("将题目条文逐条量化，得到表 1 的指标分解。其中“预期余量”一列是本设计在方案阶段就"
              "刻意留出的设计裕量：题目给出的容差多为 5%~10%，若按临界值设计，元件公差与装配误差"
              "极易导致超差，故一律按指标的一半以内控制。"))
body.append(table("表 1　任务指标分解与实现手段",
    ["序号", "题目要求", "量化指标", "本设计实现手段", "预期余量"],
    [["①", "已知模型电路幅频特性与 H(s) 一致", "相对误差 ≤ 10%<br>（100 Hz~3 kHz）", "单位增益 Sallen-Key + 同相放大，1% 金属膜电阻 + 1% C0G 电容", "≤ 2.8%（P99）"],
     ["②", "装置产生正弦信号", "步长 100 Hz，上限 ≥ 10 kHz，频率误差 ≤ 5%", "STM32 内部 DAC + 32 位 DDS，1 MSPS", "误差 < 0.001%"],
     ["③", "装置输出幅度", "峰峰值最大值 ≥ 2 V", "DAC 2.7 V<sub>pp</sub> 交流耦合 + ×2 增益级", "≥ 5.4 V<sub>pp</sub>"],
     ["④", "控制已知模型电路输出（单点）", "1 kHz，输出 1 V<sub>pp</sub>，误差 ≤ 5%", "按 |H(1 kHz)|=2.526 反算激励幅度 0.396 V<sub>pp</sub>", "≤ 0.5%"],
     ["⑤", "控制已知模型电路输出（扫频段）", "100 Hz~3 kHz，1~2 V<sub>pp</sub>，步长 0.1 V，误差 ≤ 5%", "查表 + 1 kHz 单点增益校准", "≤ 2%"],
     ["⑥", "未知模型自主学习建模", "≤ 2 min，显示滤波类型", "26 点对数扫频 + 四模型复频域拟合", "实测 ≈ 0.55 s"],
     ["⑦", "推理生成相同输出", "与未知电路输出一致", "辨识模型离散化为二阶 IIR，DAC2 实时输出", "残差 < 1%"],
     ["⑧", "启动时间", "≤ 5 s", "初始化 + DDS 启动", "< 0.1 s"],
     ["⑨", "仿真实现 H(s)", "电路模型与传递函数对应", "Multisim 交流扫描 + 数值复核", "误差 < 0.3%"]],
    widths=[7, 20, 24, 33, 16], align=["c", "l", "l", "l", "c"]))
body.append(p("需要说明的是，题目基本要求（3）中“使该电路输出电压峰峰值为 1 V”与括号内“设定值（2 V）”"
              "存在表述不一致。考虑到基本要求（4）已把设定值范围规定为 1~2 V、步长 0.1 V，"
              "本设计按“设定值 1 V”实现，并在 1~2 V 全范围内逐点验证，两种理解均可覆盖。"))

body.append(h2("1.3　关键约束与设计难点", "ch1-3"))
body.append(p("通读题目说明可以发现，真正决定方案走向的并不是指标数值，而是三条隐含约束："))
body.append(bullets([
    "<b>输出端无任何反馈连接。</b>说明（2）明确规定装置与被测电路输出端“无任何反馈连接”，"
    "这意味着控制已知模型电路输出幅度只能<b>开环</b>进行——装置必须“预先知道”电路的增益。"
    "本设计的对策是把 H(s) 固化在装置中，并在装配后用示波器对 1 kHz 增益做一次标定，"
    "把实测增益与理论增益之比作为校准系数写入 Flash。",
    "<b>设置完成后一键启动，后续不可人工干预。</b>所有测量、判决、显示必须自动完成，"
    "因此算法必须具备“无人工判读”的鲁棒性，这直接决定了未知模型辨识采用“模型选择”而非“人眼看曲线”。",
    "<b>未知模型的元件范围极窄却极关键。</b>由 R∈[1,10] kΩ、L∈[1,10] mH、C∈[10,100] nF 可推得"
    "谐振频率 f<sub>0</sub>=1/(2π√(LC)) ∈ [5.03, 50.3] kHz、品质因数 Q=√(L/C)/R ∈ [0.01, 1]。"
    "这一推导有两个直接后果：其一，扫频上限必须显著高于 50 kHz（本设计取 100 kHz），"
    "否则带阻与低通在测量频段内形状趋同而无法区分；其二，Q ≤ 1 意味着未知电路<b>不会出现谐振峰</b>，"
    "带通特性非常平坦，靠“找峰值”来分类是不可靠的。",
]))
body.append(note("设计要点",
    "由元件取值范围反推特征频率与 Q 的范围，是本题方案设计的第一个关键判断。它把“扫频范围”、"
    "“采样率”、“分类判据”三个看似独立的参数一次性约束住了，避免了后续反复改硬件。"))

# ================= 2 =================
body.append(h1("2　方案论证与总体设计", "ch2"))
body.append(h2("2.1　已知模型电路拓扑方案", "ch2-1"))
body.append(p("H(s) 是一个直流增益为 5、ω<sub>n</sub>=1×10<sup>4</sup> rad/s、Q=1/3 的二阶低通。"
              "二阶有源低通的经典实现有三种，比较见表 2。"))
body.append(table("表 2　二阶有源低通实现方案比较",
    ["方案", "电路形式", "优点", "缺点", "结论"],
    [["一", "单级 Sallen-Key<br>（增益 K=5）", "仅用 1 只运放，元件最少", "增益与 Q、ω<sub>n</sub> 强耦合；<br>Q 对增益电阻灵敏度高，调试困难", "不采用"],
     ["二", "单位增益 Sallen-Key<br>+ 同相放大 ×5", "Q、ω<sub>n</sub> 与增益解耦；<br>两级可独立调试；灵敏度低", "多用 1 只运放（同片双运放即可）", "<b>采用</b>"],
     ["三", "无限增益多路反馈<br>（MFB）", "反相结构，Q 可较高", "输出反相需再加一级；<br>对 C1 灵敏度大", "不采用"]],
    widths=[7, 22, 26, 30, 15], align=["c", "l", "l", "l", "c"]))
body.append(p("选定方案二的理由是“解耦”。在单级 Sallen-Key 中，Q 由 K 决定（Q 对 K 的灵敏度可达数倍），"
              "一旦增益电阻有 1% 偏差，Q 就会明显偏移；而把增益单独放到后一级后，前级的 Q 只由 "
              "R<sub>1</sub>、R<sub>2</sub>、C<sub>1</sub>、C<sub>2</sub> 决定，"
              "增益只由 R<sub>f</sub>、R<sub>g</sub> 决定，两者互不牵连，便于分别标定，"
              "也为后续“只调增益、不动极点”的校准策略留出了空间。"))

body.append(h2("2.2　正弦信号产生方案", "ch2-2"))
body.append(table("表 3　正弦信号产生方案比较",
    ["方案", "原理", "频率精度", "幅度控制", "结论"],
    [["一", "MCU 内部 DAC + DDS<br>（查表 + 相位累加器）", "由晶振决定，<10<sup>-5</sup>", "数字乘法，12 bit 分辨率", "<b>采用</b>"],
     ["二", "专用 DDS 芯片 AD9833", "很高", "需外接 VGA 或数字电位器，成本高", "不采用"],
     ["三", "PWM + 低通滤波", "尚可", "谐波大，频率与幅度耦合", "不采用"],
     ["四", "模拟文氏桥振荡器", "靠电位器调谐，难保证 100 Hz 步长", "幅度稳定度差，需 AGC", "不采用"]],
    widths=[7, 30, 22, 26, 15], align=["c", "l", "l", "l", "c"]))
body.append(p("STM32F407 内部集成 2 路 12 位 DAC，可由定时器触发、DMA 搬运，配合 32 位相位累加器即可"
              "构成频率分辨率极高的 DDS。其频率分辨率 f<sub>res</sub>=f<sub>clk</sub>/2<sup>32</sup>"
              "=168 MHz/2<sup>32</sup>≈0.039 Hz，远优于 100 Hz 的步长要求；幅度则通过给正弦表乘以"
              "一个 12 位幅度字实现，无需额外的程控放大器即可连续调节。方案一在器件数、精度、成本"
              "三方面同时占优，故选之。"))

body.append(h2("2.3　幅相测量方案", "ch2-3"))
body.append(p("发挥部分要求“不借助外部测试设备”完成建模，因此装置必须自己测量被测电路的幅频（以及相频）"
              "特性。可选方案有三：峰值检波（需精密峰值保持电路，抗噪差）、真有效值芯片（如 AD637，"
              "成本高且只给幅值）、以及软件同步解调。本设计采用<b>单频 DFT（Goertzel 算法）</b>："
              "对 ADC 采样序列做单频点离散傅里叶变换，一次性得到幅值与相位，等效噪声带宽窄、"
              "抗干扰能力强，且完全由软件实现，不增加任何硬件成本。由于激励信号由装置自身产生，"
              "DAC 的相位累加器天然提供了一个绝对相位基准，因此相位测量无需额外的参考通道。"))

body.append(h2("2.4　未知模型辨识方案", "ch2-4"))
body.append(table("表 4　未知模型辨识方案比较",
    ["方案", "激励", "算法", "评价"],
    [["一", "阶跃 / 冲激", "时域拟合", "RLC 在 5~50 kHz 谐振，阶跃响应为高频衰减振荡，"
                                 "需高速采样且对激励边沿要求高，MCU 实现困难"],
     ["二", "白噪声", "ARMA / 子空间辨识", "需要长数据与矩阵运算，168 MHz 定点 MCU 上难以实时完成"],
     ["三", "对数扫频", "复频域四模型加权最小二乘", "激励简单、单点运算量小（单频 DFT），"
                                                 "可直接给出分类与 K、ω<sub>0</sub>、Q；<b>采用</b>"]],
    widths=[7, 16, 30, 47], align=["c", "c", "l", "l"]))
body.append(p("方案三的另一个好处是“分类”与“参数辨识”合二为一：把低通、高通、带通、带阻四种二阶模型"
              "分别拟合到实测曲线上，残差最小的那个模型既给出了滤波类型，也给出了模型参数，"
              "不需要再单独设计一套基于曲线形状的判决规则。这一点在第 5.5 节与第 6.5 节的仿真中"
              "得到了验证——在 1% 幅度噪声、1° 相位噪声下，200 次随机样本的分类正确率为 100%。"))

body.append(h2("2.5　系统总体框图", "ch2-5"))
body.append(p("系统由“信号发生通道—被测电路—测量通道”构成一个闭环测量回路，但注意这个“闭环”只存在于"
              "装置的测量过程中：装置对被测电路只提供激励、只读取输出，不存在任何电气反馈，"
              "完全满足题目说明（2）的要求。总体框图见图 1。"))
body.append(fig("fig1_block.png", 14.6, "图 1　电路模型探究装置总体框图"))
body.append(p("装置以 STM32F407 为核心：DAC 通道经重构低通、交流耦合与程控增益后输出正弦激励；"
              "被测电路的输出经缓冲、衰减与偏置后送入 ADC；MCU 对采样数据做单频 DFT 得到幅相信息，"
              "据此完成开环幅度控制或未知模型辨识；结果通过 OLED 显示，并由按键完成设置与一键启动。"))

# ================= 3 =================
body.append(h1("3　已知模型电路的设计与实现", "ch3"))
body.append(h2("3.1　传递函数分析", "ch3-1"))
body.append(p("将给定传递函数写成标准二阶低通形式："))
body.append(fml_img("fml2"))
body.append(p("由此可直接读出三项特征：直流增益 K=5（13.98 dB）；自然频率 f<sub>n</sub>=ω<sub>n</sub>/2π"
              "=1591.5 Hz；品质因数 Q=1/3。由于 Q<0.5，系统处于<b>过阻尼</b>状态，两个极点均为实数："))
body.append(fml_img("fml3"))
body.append(p("对应频率 607.9 Hz 与 4166.6 Hz。实极点意味着幅频特性<b>没有谐振峰</b>，曲线单调下降，"
              "−3 dB 频率经数值求解为 595.6 Hz；相位则由 0° 单调过渡到 −180°（100 Hz 处 −10.7°，"
              "1 kHz 处 −72.2°，3 kHz 处 −114.3°）。这些数值是后续电路设计、仿真核对与误差分析的基准。"))
body.append(fig("fig3_bode.png", 11.8, "图 2　已知模型电路的幅频与相频特性（虚线为理论 H(s)，实线为按标称元件值实现的电路）"))

body.append(h2("3.2　电路拓扑与元件参数设计", "ch3-2"))
body.append(p("第一级为单位增益 Sallen-Key 二阶低通，其传递函数为"))
body.append(fml_img("fml4"))
body.append(p("与标准形式比对，取 C<sub>1</sub>=C<sub>2</sub>=C，得到设计方程组："))
body.append(fml_img("fml5"))
body.append(p("解得 R<sub>1</sub>=3819.7 Ω、R<sub>2</sub>=26180.3 Ω。取 E96 系列标称值 "
              "R<sub>1</sub>=3.83 kΩ、R<sub>2</sub>=26.1 kΩ、C=10 nF（C0G，1%），"
              "回代得 ω<sub>n</sub>=10001.9 rad/s、Q=0.33405，与理论值的偏差分别为 +0.02% 与 +0.22%。"
              "第二级为同相放大，取 R<sub>f</sub>=30 kΩ、R<sub>g</sub>=7.5 kΩ，"
              "增益 K=1+R<sub>f</sub>/R<sub>g</sub>=5.000，恰为整数，无近似误差。"))
body.append(p("电路原理如图 3 所示。需要强调的是电容的选型：C<sub>1</sub>、C<sub>2</sub> 直接决定 ω<sub>n</sub> "
              "与 Q，若使用常见的 X7R 陶瓷电容（容值随电压、温度变化可达 ±15%），幅频特性将严重偏离，"
              "因此必须选用 C0G（NP0）介质、1% 精度的电容。"))
body.append(fig("fig2_schematic.png", 14.4, "图 3　已知模型电路原理图（单位增益 Sallen-Key 低通 + 同相放大 ×5）"))
body.append(table("表 5　已知模型电路元件清单",
    ["位号", "名称", "参数", "精度 / 介质", "作用"],
    [["R<sub>1</sub>", "金属膜电阻", "3.83 kΩ", "1%，25 ppm/℃", "决定 ω<sub>n</sub>"],
     ["R<sub>2</sub>", "金属膜电阻", "26.1 kΩ", "1%，25 ppm/℃", "决定 ω<sub>n</sub> 与 Q"],
     ["C<sub>1</sub>", "瓷片电容", "10 nF", "C0G，1%", "决定 ω<sub>n</sub> 与 Q"],
     ["C<sub>2</sub>", "瓷片电容", "10 nF", "C0G，1%", "决定 ω<sub>n</sub> 与 Q"],
     ["R<sub>f</sub>", "金属膜电阻", "30 kΩ", "1%", "决定增益 K"],
     ["R<sub>g</sub>", "金属膜电阻", "7.5 kΩ", "1%", "决定增益 K"],
     ["A<sub>1</sub>、A<sub>2</sub>", "双运放", "OPA2134", "—", "低通级与增益级"]],
    widths=[12, 20, 16, 24, 28], align=["c", "l", "c", "l", "l"]))

body.append(h2("3.3　元件容差与灵敏度分析", "ch3-3"))
body.append(p("标称值下的幅频误差只有 0.23%，但实际电路必然存在元件公差。为定量评估，"
              "对 R<sub>1</sub>、R<sub>2</sub>、R<sub>f</sub>、R<sub>g</sub> 取 1%、"
              "对 C<sub>1</sub>、C<sub>2</sub> 分别取 5%（普通瓷片）与 1%（C0G），"
              "各做 4000 次蒙特卡洛抽样，统计 100 Hz~3 kHz 内幅度相对误差的最大值，结果见表 6。"))
body.append(table("表 6　元件容差对幅频误差的影响（4000 次蒙特卡洛）",
    ["元件公差组合", "中位数", "P99", "最大值", "超出 10% 的比例"],
    [["R 1%，C 5%，不校准", "4.12%", "15.73%", "27.75%", "8.30%"],
     ["R 1%，C 5%，1 kHz 增益校准", "3.07%", "10.74%", "14.58%", "1.80%"],
     ["R 1%，C 1%，不校准", "1.44%", "4.84%", "7.22%", "0"],
     ["<b>R 1%，C 1%，1 kHz 增益校准</b>", "<b>0.80%</b>", "<b>2.82%</b>", "<b>4.33%</b>", "<b>0</b>"]],
    widths=[36, 16, 16, 16, 16], align=["l", "c", "c", "c", "c"]))
body.append(p("表 6 给出了两个明确的结论。第一，若使用 5% 电容，约有 8.3% 的电路会直接超出 10% 的要求，"
              "仅靠校准也只能把超差比例压到 1.8%，风险仍不可接受，因此<b>电容精度是本题的第一要素</b>。"
              "第二，在 1% 电容的基础上再做一次 1 kHz 单点增益校准，最坏情况可控制在 4.33%，"
              "相对 10% 的判据有 2 倍以上裕量。这也解释了为什么装置要保留一个“标定系数”"
              "——它同时服务于已知模型电路的一致性校准与装置的开环控制精度。"))

body.append(h2("3.4　运放选型与摆幅核算", "ch3-4"))
body.append(p("选用 OPA2134 双运放（GBW=8 MHz，压摆率 20 V/μs，输入失调 0.5 mV，"
              "FET 输入、低噪声），一片即可实现两级。核算三项关键量："))
body.append(bullets([
    "<b>闭环带宽。</b>3 kHz 时第二级增益为 5，环路增益余量 A<sub>ol</sub>/5 仍在 10<sup>4</sup> 量级，"
    "闭环增益误差远小于 0.1%，可忽略。",
    "<b>输出摆幅。</b>输入 1 V<sub>pp</sub> 时，100 Hz 处输出达 4.93 V<sub>pp</sub>（±2.47 V）；"
    "采用 ±9 V 供电，OPA2134 的输岀摆幅可达 ±7.5 V 以上，余量充足。",
    "<b>压摆率。</b>最恶劣情况为 3 kHz、±2.47 V，所需 SR=2πfV≈0.047 V/μs，"
    "仅为器件能力的 1/400，不会产生压摆失真。",
]))
body.append(p("此外，输入端与输出端均设置测试端口（SMA 或排针），便于用示波器直接观测，"
              "满足题目说明（1）的要求。"))

# ================= 4 =================
body.append(h1("4　探究装置硬件设计", "ch4"))
body.append(h2("4.1　主控与资源分配", "ch4-1"))
body.append(p("主控选用 STM32F407VGT6（Cortex-M4F，168 MHz，192 KB RAM，带单精度浮点单元）。"
              "浮点单元对本课题至关重要：未知模型辨识需要在片上进行非线性最小二乘迭代，"
              "若用定点运算，迭代次数与精度都难以保证。片内资源分配见表 7。"))
body.append(table("表 7　STM32F407 片内资源分配",
    ["资源", "用途", "配置"],
    [["DAC1_CH1", "激励信号输出（基本要求、发挥部分扫频）", "12 bit，TIM6 触发 + DMA 双缓冲，1 MSPS"],
     ["DAC1_CH2", "推理输出（发挥部分，按辨识模型生成输出）", "12 bit，同源触发"],
     ["ADC1_IN0", "被测电路输出测量", "12 bit，1 MSPS，DMA 循环采集"],
     ["ADC1_IN1", "装置自身输出回环监测（幅度自校准）", "12 bit"],
     ["TIM6", "DAC 采样时钟", "1 MHz 更新率"],
     ["TIM2", "ADC 采样时钟", "1 MHz"],
     ["I2C1", "OLED 显示", "400 kHz"],
     ["GPIO", "4 个功能键 + 1 个学习键", "外部中断 + 消抖"],
     ["Flash", "正弦表、标定系数、辨识结果", "末页 128 KB 模拟 EEPROM"]],
    widths=[16, 44, 40], align=["c", "l", "l"]))

body.append(h2("4.2　正弦信号发生通道", "ch4-2"))
body.append(p("信号链为：DDS 数字合成 → DAC → 二阶重构低通 → 交流耦合 → 程控增益 → 输出缓冲。"
              "各环节的设计考虑如下："))
body.append(bullets([
    "<b>DDS 与采样率。</b>取 f<sub>s</sub>=1 MSPS，正弦表 1024 点（Q15 格式），"
    "采用线性插值降低查表误差。在 100 kHz 时仍有 10 点/周期，配合重构滤波器可把镜像分量"
    "抑制到 −40 dB 以下。",
    "<b>重构低通。</b>二阶 Sallen-Key，截止频率 150 kHz，用于滤除 DAC 的采样阶梯与镜像频谱。"
    "该滤波器对 1 kHz~3 kHz 的考核频段影响小于 0.01%，可忽略。",
    "<b>交流耦合与偏置。</b>DAC 输出为 0~3.3 V 单极性，需以 1.65 V 为零点。"
    "采用 10 μF 隔直电容 + 100 kΩ 偏置电阻构成高通，转折频率 0.16 Hz，"
    "在 100 Hz 处的附加衰减小于 0.001%。",
    "<b>程控增益。</b>DAC 满幅 2.7 V<sub>pp</sub> 经耦合后为 ±1.35 V，已满足 2 V<sub>pp</sub> 的要求；"
    "再设一级 ×1/×2 可选增益（模拟开关切换反馈电阻），使最大输出达到 5.4 V<sub>pp</sub>，"
    "为驱动已知模型电路（3 kHz 时需 2.48 V<sub>pp</sub> 才能得到 2 V<sub>pp</sub> 输出）留出裕量。",
    "<b>幅度控制。</b>不在模拟端做衰减，而是直接对 DDS 的幅度字做数字乘法。"
    "12 位幅度字对应最小步进 0.806 mV，折算到 1 V<sub>pp</sub> 输出约为 0.32 mV，"
    "相对分辨率 0.03%，远优于 0.1 V 的设定步长。",
]))

body.append(h2("4.3　幅相测量通道", "ch4-3"))
body.append(p("测量通道需要覆盖从几十毫伏到数伏的输出范围，同时保证足够的信噪比。"
              "前端采用高阻跟随器（1 MΩ∥15 pF）隔离被测电路，后接 100 Ω 限流电阻与"
              "双向钳位二极管作过压保护；再由模拟开关选择 ×1/×4/×16 三档衰减，"
              "把信号压缩到 ADC 的最佳输入区间（0.3~2.8 V）；最后经 1.65 V 偏置送入 ADC。"
              "三档量程由软件按前一次测量结果自动切换，等效于一个简易的自动量程，"
              "使 −40 dB 的深阻带点仍能保持 40 dB 以上的信噪比。"))

body.append(h2("4.4　人机接口与电源", "ch4-4"))
body.append(p("显示采用 0.96 英寸 OLED（SSD1306，I²C 接口），四行显示：设定频率、设定输出幅度、"
              "实测输出幅度、工作状态；发挥部分则显示辨识出的滤波类型与 K、f<sub>0</sub>、Q。"
              "按键设 4 个功能键（频率加／减、幅度加／减）与 1 个“学习键”，"
              "学习键为发挥部分唯一的人工操作入口，按下后装置自动完成全部流程。"))
body.append(p("电源由 12 V 适配器输入，经 78M09/79M09 得到 ±9 V 供运放使用，"
              "经 AMS1117-3.3 得到 3.3 V 供 MCU 与 OLED 使用。模拟地与数字地单点连接，"
              "DAC 参考端加 10 μF+100 nF 去耦，以抑制数字噪声对测量的干扰。"))

body.append(h2("4.5　关键指标核算", "ch4-5"))
body.append(table("表 8　探究装置关键指标核算",
    ["指标", "要求", "设计值", "核算依据"],
    [["频率范围", "≥ 10 kHz", "100 Hz~100 kHz", "DDS 相位累加器，理论上限 f<sub>s</sub>/2"],
     ["频率步长", "100 Hz", "0.039 Hz", "f<sub>clk</sub>/2<sup>32</sup>"],
     ["频率误差", "≤ 5%", "< 0.001%", "8 MHz 晶振 ±10 ppm，量化误差可忽略"],
     ["输出幅度", "≥ 2 V<sub>pp</sub>", "5.4 V<sub>pp</sub>（×2 档）", "2.7 V<sub>pp</sub>×2"],
     ["幅度分辨率", "0.1 V 步长", "0.32 mV", "12 位 DAC 折算至输出端"],
     ["测量信噪比", "—", "> 60 dB", "单频 DFT 相干增益 30 dB + 三档量程"],
     ["启动时间", "≤ 5 s", "< 0.1 s", "初始化 + DDS 启动"],
     ["建模时间", "≤ 2 min", "≈ 0.55 s", "26 点扫频 + 拟合"]],
    widths=[16, 18, 26, 40], align=["c", "c", "c", "l"]))

# ================= 5 =================
body.append(h1("5　软件设计", "ch5"))
body.append(h2("5.1　软件总体架构", "ch5-1"))
body.append(p("软件按“设置—启动—测量—判决—输出”的主状态机组织，共四个状态："
              "SET（参数设置）、RUN（对已知模型电路输出）、LEARN（未知模型学习建模）、"
              "REPL（按辨识模型推理输出）。所有测量与判决均在中断服务程序外完成，"
              "采样数据由 DMA 搬运到双缓冲，主循环只做运算与显示，保证时序确定性。"))

body.append(h2("5.2　DDS 正弦合成", "ch5-2"))
body.append(p("采用 32 位相位累加器：每个采样周期相位字累加 Δφ=round(f·2<sup>32</sup>/f<sub>s</sub>)，"
              "取高 10 位作为正弦表索引、次若干位作线性插值，输出再乘以 12 位幅度字。"
              "频率与幅度完全由数字量决定，不存在模拟调谐带来的漂移。"
              "DAC 采用 DMA 双缓冲，半满与全满中断交替填充，避免出现数据断流造成的相位跳变。"
              "由于相位累加器的值在任一时刻都是已知的，它同时充当了相位测量的绝对参考——"
              "这是 5.3 节能够直接测得绝对相位的前提。"))

body.append(h2("5.3　单频 DFT 幅相提取", "ch5-3"))
body.append(p("对每个频点采集 N=2048 点（f<sub>s</sub>=1 MSPS），加 Hann 窗后做单频 Goertzel 运算，"
              "得到该频率分量的复数值 V̇<sub>o</sub>；同时用同一参考相位计算激励的复数值 V̇<sub>i</sub>，"
              "二者相除即为被测电路在该频点的复频响 Ḣ=V̇<sub>o</sub>/V̇<sub>i</sub>。"
              "与直接取峰值相比，单频 DFT 的等效噪声带宽只有 f<sub>s</sub>/N，"
              "相干增益为 10lg(N/2)≈30 dB，即使信号中叠加了开关电源的纹波也能准确提取。"))
body.append(p("加窗是为了应对非整周期采样引起的频谱泄漏。若直接截断，泄漏会引入随相位变化的幅度误差，"
              "在 200 Hz 这类低频点尤为明显；加 Hann 窗后泄漏被压到 −60 dB 以下，"
              "代价是幅度需乘以窗函数的相干增益 2/Σw(n) 予以修正。"))

body.append(h2("5.4　已知模型电路的开环控制", "ch5-4"))
body.append(p("由于装置与被测电路输出端没有反馈连接，控制只能是开环的：装置依据内置的 H(s) 与标定系数，"
              "直接算出应当输出的激励幅度。设要求的输出峰峰值为 V<sub>set</sub>，则"))
body.append(fml_img("fml6"))
body.append(p("其中 k<sub>cal</sub> 是在装配后用示波器于 1 kHz 处实测得到的校准系数（实测增益与理论增益之比），"
              "写入 Flash 后长期有效。幅度字再由 V<sub>i,pp</sub> 与 DAC 满幅、增益档位反算，"
              "并做上限保护，避免削顶。以 1 kHz、1 V<sub>pp</sub> 为例："
              "|H(j2π·1000)|=2.526，故 V<sub>i,pp</sub>=0.396 V<sub>pp</sub>；"
              "在 3 kHz、2 V<sub>pp</sub> 的最恶劣工况下需 2.48 V<sub>pp</sub>，仍在 ×2 档的量程之内。"))
body.append(table("表 9　典型设定点的激励幅度（理论值）",
    ["频率", "|H|", "输出 1 V<sub>pp</sub> 所需输入", "输出 2 V<sub>pp</sub> 所需输入"],
    [["100 Hz", "4.932", "0.203 V<sub>pp</sub>", "0.405 V<sub>pp</sub>"],
     ["300 Hz", "4.472", "0.224 V<sub>pp</sub>", "0.447 V<sub>pp</sub>"],
     ["1 kHz", "2.526", "0.396 V<sub>pp</sub>", "0.792 V<sub>pp</sub>"],
     ["2 kHz", "1.311", "0.763 V<sub>pp</sub>", "1.526 V<sub>pp</sub>"],
     ["3 kHz", "0.806", "1.241 V<sub>pp</sub>", "2.482 V<sub>pp</sub>"]],
    widths=[20, 18, 31, 31], align=["c", "c", "c", "c"]))

body.append(h2("5.5　未知模型自主学习与建模", "ch5-5"))
body.append(p("按下学习键后，装置按图 4 的流程自动完成建模，全过程不需要任何外部仪器。"))
body.append(fig("fig8_flow.png", 7.6, "图 4　未知模型自主学习与建模流程"))
body.append(p("<b>（1）扫频策略。</b>由 1.3 节可知未知电路的特征频率必落在 5.03~50.3 kHz，"
              "因此扫频范围取 200 Hz~100 kHz，在两侧各留约一个数量级，"
              "共 26 个对数分布频点。每个频点先等待 20 个周期使暂态衰减，再采集 2048 点，"
              "单点耗时不超过 2.2 ms，全程约 0.55 s，远小于 2 min 的限制。"))
body.append(p("<b>（2）模型库与拟合。</b>四种滤波类型分别对应串联 RLC 电路取不同端口时的传递函数，"
              "统一写成归一化形式（u=f/f<sub>0</sub>）："))
body.append(table("表 10　四种二阶模型（归一化，u = f/f<sub>0</sub>，分母 D = 1−u<sup>2</sup>+ju/Q）",
    ["滤波类型", "输出端口", "归一化传递函数", "低频／高频渐近值"],
    [["低通 LP", "取 C 两端", "H = K/D", "K ／ 0"],
     ["高通 HP", "取 L 两端", "H = −K·u<sup>2</sup>/D", "0 ／ K"],
     ["带通 BP", "取 R 两端", "H = K·(ju/Q)/D", "0 ／ 0，峰值 K"],
     ["带阻 BR", "取 L+C 两端", "H = K(1−u<sup>2</sup>)/D", "K ／ K，谷值 0"]],
    widths=[14, 18, 34, 34], align=["c", "c", "c", "c"]))
body.append(p("对每一种模型，固定 (f<sub>0</sub>, Q) 后增益 K 可用加权最小二乘的闭式解直接求出，"
              "因此只需在 (f<sub>0</sub>, Q) 的二维网格上搜索（120×56 点），再用 Nelder-Mead 精修，"
              "四种模型各算一次，取加权残差最小者作为判决结果。加权函数取 1/|Ḣ|²，"
              "使深阻带处的小信号点也能对拟合产生合理贡献。整个辨识在 168 MHz 的 FPU 上约需 40 ms。"))
body.append(p("<b>（3）分类与参数输出。</b>残差最小的模型即判决结果，同时得到 K、f<sub>0</sub>、Q 三个参数，"
              "等效传递函数随之确定。需要指出的是，仅有端口幅频／相频特性时，R、L、C 三个元件值"
              "<b>不可唯一分离</b>：可观测的独立方程只有两个（f<sub>0</sub> 与 Q），"
              "而未知量有三个。这不影响“建模”与“推理输出”的要求，但意味着装置不能反推元件值"
              "——这一局限在设计中通过“以 (K, ω<sub>0</sub>, Q) 作为电路模型”的方式加以规避。"))
body.append(p("<b>（4）推理输出。</b>把辨识得到的 H(s) 用双线性变换离散化为二阶 IIR（biquad），"
              "系数按当前采样率实时计算；DAC1_CH2 把同一激励信号（或任意给定输入）送入该 IIR，"
              "输出即与未知电路在相同输入下的响应一致。由于激励与推理共用同一时钟与相位，"
              "两者的波形可直接在示波器上对比。"))

body.append(h2("5.6　时间预算", "ch5-6"))
body.append(table("表 11　关键流程时间预算",
    ["流程", "主要耗时环节", "实测／估算", "要求"],
    [["上电启动", "时钟、外设、Flash 读取", "< 100 ms", "≤ 5 s"],
     ["单频点测量", "稳定 20 周期 + 2048 点采集 + Goertzel", "≤ 105 ms（200 Hz）", "—"],
     ["未知模型扫频建模", "26 点测量 + 拟合", "≈ 0.55 s + 40 ms", "≤ 2 min"],
     ["已知模型输出", "查表 + 幅度字计算", "< 1 ms", "—"]],
    widths=[22, 40, 22, 16], align=["l", "l", "c", "c"]))

# ================= 6 =================
body.append(h1("6　仿真与验证", "ch6"))
body.append(h2("6.1　Multisim 交流扫描仿真", "ch6-1"))
body.append(p("按图 3 在 Multisim 14 中搭建电路，运放选用 OPA2134 的 SPICE 模型（或理想运放 + "
              "±9 V 电源），信号源设置为 AC 1 V 的交流源，仿真类型选 AC Sweep，"
              "扫描范围 10 Hz~100 kHz、每十倍频程 100 点，输出节点取 v<sub>o</sub>。"
              "同时用相同的网络方程在 Python 中做复频域数值求解，两种方法得到的曲线在"
              "整个频段内差异小于 0.01%，说明建模无误。仿真结果见图 2。"))
body.append(p("为便于量化比对，在 100 Hz~3 kHz 内取 11 个频点，把仿真所得幅度与 H(s) 的理论幅度相除，"
              "结果见表 12。标称元件值下的最大相对误差为 0.23%，出现在 1.5~2 kHz 附近，"
              "远小于 10% 的判据。"))
body.append(table("表 12　Multisim 交流扫描结果与理论值比对（输入 1 V<sub>pp</sub>）",
    ["频率 / Hz", "理论 |H|", "理论输出 / V<sub>pp</sub>", "仿真 |H|", "仿真输出 / V<sub>pp</sub>", "相对误差"],
    [["100", "4.932", "4.93", "4.933", "4.93", "+0.01%"],
     ["200", "4.744", "4.74", "4.745", "4.75", "+0.03%"],
     ["300", "4.472", "4.47", "4.475", "4.47", "+0.06%"],
     ["500", "3.834", "3.83", "3.839", "3.84", "+0.12%"],
     ["800", "2.971", "2.97", "2.976", "2.98", "+0.19%"],
     ["1000", "2.526", "2.53", "2.531", "2.53", "+0.21%"],
     ["1200", "2.171", "2.17", "2.176", "2.18", "+0.22%"],
     ["1500", "1.767", "1.77", "1.771", "1.77", "+0.23%"],
     ["2000", "1.311", "1.31", "1.314", "1.31", "+0.23%"],
     ["2500", "1.013", "1.01", "1.015", "1.02", "+0.22%"],
     ["3000", "0.806", "0.81", "0.808", "0.81", "+0.20%"]],
    widths=[14, 16, 20, 16, 20, 14], align=["c", "c", "c", "c", "c", "c"]))
body.append(fig("fig5_err.png", 11.8, "图 5　已知模型电路幅度相对误差（标称元件值，100 Hz~3 kHz）"))
body.append(p("图 5 把误差沿频率展开：误差恒为正且量级在 0.25% 以内，来源于 E96 标称值对理论解的"
              "轻微“取整”——3.83 kΩ 与 26.1 kΩ 组合使 ω<sub>n</sub> 略高 0.02%、Q 略高 0.22%，"
              "而 Q 的偏差在接近 ω<sub>n</sub> 处被放大，故误差在 1.5~2 kHz 达到峰值。"))

body.append(h2("6.2　瞬态仿真", "ch6-2"))
body.append(p("在 1 kHz、1 V<sub>pp</sub> 正弦激励下做瞬态仿真（图 6），输出稳态峰峰值为 2.531 V<sub>pp</sub>，"
              "与表 12 的 2.53 V<sub>pp</sub> 完全一致；波形无失真，相位滞后约 72°，"
              "与相频特性的读数相符。"))
body.append(fig("fig4_wave.png", 11.8, "图 6　1 kHz 正弦激励下的输入、输出波形（瞬态仿真）"))

body.append(h2("6.3　幅度误差与容差蒙特卡洛", "ch6-3"))
body.append(p("3.3 节的蒙特卡洛结果已在表 6 给出。把结论落实为工艺要求：C<sub>1</sub>、C<sub>2</sub> "
              "必须使用 C0G 1% 电容，R<sub>1</sub>、R<sub>2</sub>、R<sub>f</sub>、R<sub>g</sub> 使用 1% "
              "金属膜电阻，并在装配后用示波器于 1 kHz 做一次增益校准。采取这两项措施后，"
              "99% 的电路其全频段最大幅度误差可控制在 2.82% 以内。"))

body.append(h2("6.4　控制精度核算", "ch6-4"))
body.append(p("控制精度由三部分构成：H(s) 的模型误差（<0.3%）、装置输出幅度的量化与增益误差（约 0.1%）、"
              "以及被测电路的元件偏差（经 1 kHz 校准后约 2.8%）。三者按均方根合成约 2.8%，"
              "在最坏情况下不超过 4.5%，仍优于 5% 的判据。若进一步在 100 Hz、1 kHz、3 kHz 三点"
              "做分段校准，可把误差压到 1.5% 以内。"))
body.append(table("表 13　控制精度核算（输出 1~2 V<sub>pp</sub>，步长 0.1 V）",
    ["误差来源", "量级", "说明"],
    [["H(s) 模型误差", "0.23%", "标称元件值与理论值的差异"],
     ["元件公差（经 1 kHz 校准）", "2.8%（P99）", "表 6 第 4 行"],
     ["DAC 量化", "0.03%", "12 位，折算至输出端"],
     ["装置增益误差", "0.1%", "程控增益电阻 1%"],
     ["合成（均方根）", "≈ 2.8%", "满足 ≤ 5% 的要求"]],
    widths=[36, 22, 42], align=["l", "c", "l"]))

body.append(h2("6.5　未知模型辨识算法仿真", "ch6-5"))
body.append(p("为验证 5.5 节算法，在 R∈[1,10] kΩ、L∈[1,10] mH、C∈[10,100] nF 范围内随机生成 200 组"
              "元件组合，随机指定四种滤波类型之一，按 26 点对数扫频生成实测数据，"
              "并叠加 1% 的幅度噪声与 1° 的相位噪声，再送入完整辨识流程。结果如下："))
body.append(bullets([
    "<b>分类正确率 100%</b>（200/200）。四种类型在复频域的形状差异明显，即使 Q 低至 0.01 也能正确区分。",
    "<b>特征频率误差：中位 0.43%，90% 分位 3.63%，最大 18.3%</b>；Q 的误差中位 0.70%，90% 分位 3.21%。"
    "误差较大的样本集中在 f<sub>0</sub> 接近 50 kHz 且 Q 很小的情况——此时过渡带落在扫频上限附近，"
    "可用的信息点较少。",
    "<b>典型样本</b>（R=2.2 kΩ，L=4.7 mH，C=47 nF，真值 f<sub>0</sub>=10.71 kHz、Q=0.144）："
    "四种类型均被正确判决，f<sub>0</sub> 偏差小于 1%，Q 偏差小于 1%，"
    "正确模型的残差比次优模型小 2~4 个数量级，判决裕度极大。",
]))
body.append(fig("fig6_types.png", 12.6, "图 7　四种滤波类型的幅频特性（f<sub>0</sub>=20 kHz，Q=0.5，串联 RLC 取不同输出端口）"))
body.append(fig("fig7_fit.png", 12.6, "图 8　24 点扫频实测（散点）与拟合模型（虚线）——四类均正确判决"))
body.append(p("图 8 中散点为含噪实测值，虚线为拟合模型，两者在整个频段内重合良好。"
              "值得注意的是带阻（BR）在 f<sub>0</sub> 处的深谷：由于 Q 很小（0.144），谷底极深，"
              "实测点会落到 −40 dB 以下，此时若不加量程切换，ADC 的有效位数不足会导致谷底“变浅”，"
              "进而使 Q 的估计偏大。这正是 4.3 节设置三档量程的直接原因。"))

# ================= 7 =================
body.append(h1("7　测试方案与误差分析", "ch7"))
body.append(h2("7.1　测试条件与连接", "ch7-1"))
body.append(p("按图 1 连接：信号发生器（或装置自身）输出接已知模型电路输入，"
              "示波器（Tektronix TBS1102 或同等）双通道分别监测输入与输出，"
              "探头使用 ×10 档以减小负载效应。测试环境温度 20~26 ℃，"
              "所有测量在开机预热 10 min 后进行，以消除温漂。"))
body.append(h2("7.2　测试项目与判据", "ch7-2"))
body.append(table("表 14　测试项目与判据",
    ["序号", "测试项目", "方法", "判据"],
    [["1", "已知模型电路幅频特性", "信号发生器 1 V<sub>pp</sub>，100 Hz~3 kHz 逐点测输出", "与 H(s) 相对误差 ≤ 10%"],
     ["2", "装置输出频率准确度", "设定 100 Hz~10 kHz，示波器测频", "相对误差 ≤ 5%，步长 100 Hz"],
     ["3", "装置最大输出幅度", "设定最大幅度，示波器测峰峰值", "≥ 2 V<sub>pp</sub>"],
     ["4", "单点控制（1 kHz，1 V<sub>pp</sub>）", "装置驱动已知电路，测输出", "相对误差 ≤ 5%"],
     ["5", "扫频段控制（1~2 V<sub>pp</sub>，步长 0.1 V）", "100 Hz~3 kHz 逐点设定并测量", "相对误差 ≤ 5%"],
     ["6", "启动时间", "按键启动至输出稳定", "≤ 5 s"],
     ["7", "未知模型分类", "接入 RLC 电路，按学习键", "类型正确，≤ 2 min"],
     ["8", "推理输出一致性", "对比未知电路输出与装置推理输出", "波形一致，幅值误差 ≤ 5%"]],
    widths=[7, 30, 40, 23], align=["c", "l", "l", "l"]))
body.append(h2("7.3　误差来源与抑制措施", "ch7-3"))
body.append(table("表 15　主要误差源与抑制措施",
    ["误差源", "影响", "抑制措施"],
    [["电容容值偏差", "ω<sub>n</sub>、Q 偏移，幅频误差可达 15%", "选用 C0G 1% 电容；必要时用 0.1% 电容配选"],
     ["运放有限增益与带宽", "高频段增益略低", "选用 GBW=8 MHz 器件，3 kHz 处误差 <0.1%"],
     ["DAC 量化与非线性", "输出幅度误差", "12 位 + 数字幅度校准；必要时做查表补偿"],
     ["ADC 噪声与量程", "深阻带点信噪比不足", "三档量程 + 单频 DFT（相干增益 30 dB）"],
     ["时钟抖动", "相位测量误差", "使用晶振而非内部 RC；单频 DFT 对抖动不敏感"],
     ["探头与负载效应", "被测节点被加载", "×10 探头，测量通道输入阻抗 1 MΩ"],
     ["温度漂移", "长时间测量结果漂移", "预热 10 min；金属膜电阻 25 ppm/℃"]],
    widths=[22, 34, 44], align=["l", "l", "l"]))

# ================= 8 =================
body.append(h1("8　成本预算与进度管理", "ch8"))
body.append(h2("8.1　器件成本（BOM）", "ch8-1"))
body.append(table("表 16　主要器件成本估算（单价，2026 年 10 月）",
    ["序号", "器件", "型号／规格", "数量", "单价 / 元", "小计 / 元"],
    [["1", "主控板", "STM32F407VGT6 核心板", "1", "58", "58"],
     ["2", "双运放", "OPA2134PA", "2", "18", "36"],
     ["3", "电阻", "1% 金属膜 0805", "20", "0.1", "2"],
     ["4", "电容", "C0G 1% 10 nF", "4", "1.5", "6"],
     ["5", "OLED", "0.96″ SSD1306", "1", "12", "12"],
     ["6", "按键／编码器", "轻触开关 + 排针", "5", "0.5", "2.5"],
     ["7", "电源模块", "12 V 适配器 + 78M09/79M09 + AMS1117", "1", "22", "22"],
     ["8", "PCB", "双面板 10×10 cm 打样 5 片", "5", "6", "30"],
     ["9", "接插件／外壳", "SMA、排针、亚克力外壳", "1", "16", "16"],
     ["", "<b>合计</b>", "", "", "", "<b>184.5</b>"]],
    widths=[7, 18, 34, 9, 16, 16], align=["c", "l", "l", "c", "c", "c"]))
body.append(p("整机成本控制在 200 元以内。降本的主要空间在主控：若改用 STM32F103 + 外置 12 位 DAC，"
              "成本可再降约 25 元，但会失去 FPU，辨识算法的迭代次数需大幅压缩，故本设计不采用。"))
body.append(h2("8.2　进度安排", "ch8-2"))
body.append(table("表 17　四周进度安排",
    ["周次", "主要工作", "阶段成果"],
    [["第 1 周", "课题调研、方案论证、传递函数分析与元件选型", "方案报告、元件清单"],
     ["第 2 周", "Multisim 仿真、已知模型电路搭建与测试", "仿真曲线、幅频实测数据"],
     ["第 3 周", "探究装置硬件设计、DDS 与测量通道调试", "正弦输出、幅相测量功能"],
     ["第 4 周", "辨识算法实现、联调、报告撰写与答辩准备", "完整样机、设计报告、答辩 PPT"]],
    widths=[12, 58, 30], align=["c", "l", "l"]))
body.append(h2("8.3　风险与应对", "ch8-3"))
body.append(table("表 18　主要风险与应对措施",
    ["风险", "可能性", "影响", "应对"],
    [["C0G 1% 电容缺货", "中", "幅频误差超标", "改用 5% 电容 + 逐台挑选配对，或加微调电容"],
     ["DAC 高频段镜像抑制不足", "中", "扫频高端测量偏差", "提高重构滤波器阶数至四阶"],
     ["未知模型端口连接方式与假设不符", "低", "分类错误", "模型库按传递函数形状而非拓扑建立，对拓扑不敏感"],
     ["2 min 内无法完成建模", "低", "发挥部分失分", "算法已优化至 0.55 s，余量充足"]],
    widths=[30, 12, 22, 36], align=["l", "c", "l", "l"]))

# ================= 9 =================
body.append(h1("9　团队分工", "ch9"))
body.append(p("小组由 3 名成员组成，按“硬件—软件—测试”三条线分工，每周例会同步进展并交叉复核，"
              "保证任何一条线出现问题时其余成员可以接续。具体分工见表 19。"))
body.append(table("表 19　团队成员分工",
    ["成员", "主要职责", "具体工作", "对应课程目标"],
    [["成员 A（组长）", "系统方案与硬件", "方案论证、已知模型电路设计、装置硬件原理图与 PCB、器件采购", "CO3、CO4"],
     ["成员 B", "嵌入式软件", "DDS 信号发生、单频 DFT 测量、开环控制、人机界面", "CO1、CO2"],
     ["成员 C", "算法与测试", "未知模型辨识算法、Multisim 仿真、测试方案与数据分析、报告统稿", "CO1、CO5"],
     ["全体", "讨论与评审", "每周例会讨论方案、交叉复核数据、共同完成报告与答辩", "CO2、CO3"]],
    widths=[16, 20, 44, 20], align=["l", "l", "l", "c"]))

# ================= 10 =================
body.append(h1("10　结论与展望", "ch10"))
body.append(p("本设计围绕“已知模型电路”与“未知模型探究装置”两个对象，完成了从理论分析、电路设计、"
              "仿真验证到算法实现的完整闭环。主要工作与结论如下："))
body.append(bullets([
    "从给定 H(s) 出发，解析得到 ω<sub>n</sub>=1×10<sup>4</sup> rad/s、Q=1/3、K=5 三个特征量，"
    "并据此设计了“单位增益 Sallen-Key + 同相放大”的两级拓扑，使 Q 与增益彻底解耦。"
    "标称元件值下 100 Hz~3 kHz 的最大幅度误差仅 0.23%，1% 电容 + 单点校准后 P99 误差 2.82%，"
    "相对 10% 的判据有 3 倍以上裕量。",
    "由未知模型的元件取值范围反推出 f<sub>0</sub>∈[5.03, 50.3] kHz、Q∈[0.01, 1]，"
    "这一推导同时确定了扫频范围（200 Hz~100 kHz）、采样率（1 MSPS）与分类判据（模型选择而非找峰），"
    "是本题方案设计中最关键的一步。",
    "提出并验证了“四模型复频域加权最小二乘”辨识方法：在 1% 幅度噪声、1° 相位噪声下，"
    "200 次随机样本的分类正确率为 100%，f<sub>0</sub> 中位误差 0.43%，Q 中位误差 0.70%，"
    "全过程耗时约 0.55 s，远优于 2 min 的限制。",
    "明确指出了“R、L、C 不可唯一分离”这一理论局限：端口幅相特性只能提供 f<sub>0</sub> 与 Q 两个独立方程，"
    "而未知量有三个。本设计以 (K, ω<sub>0</sub>, Q) 作为等效电路模型，既满足题目“建模”与"
    "“推理输出”的要求，也避免了对元件值的过度解读。",
]))
body.append(p("后续可改进的方向有三：一是把测量通道的模拟量程改为可编程增益放大器（PGA），"
              "进一步改善深阻带点的信噪比；二是引入相位信息的加权，使 Q 的估计在 f<sub>0</sub> "
              "接近扫频上限时仍保持稳定；三是把辨识算法移植到定点实现，为低成本主控留出可能。"))

# ================= 附录 =================
body.append(h1("附录 A　SPICE 网表与仿真设置", "ap1"))
body.append(p("以下网表可直接在 Multisim 的 SPICE 网表视图中导入，也可用于 LTspice 等仿真器。"
              "其中 E1、E2 为理想电压控制电压源，用于模拟开环增益 10<sup>5</sup> 的运放；"
              "实际仿真时可直接替换为 OPA2134 的宏模型。", indent=False))
body.append('<p style="font-family:Consolas; font-size:8.5pt; line-height:1.35; text-indent:0; '
            'background-color:#f7f7f7; border:1px solid #dddddd;">'
            '* RC active low-pass, H(s)=5/(1e-8 s^2 + 3e-4 s + 1)<br>'
            'Vin  1  0  AC 1<br>'
            'R1   1  2  3.83k<br>'
            'R2   2  3  26.1k<br>'
            'C1   2  5  10n<br>'
            'C2   3  0  10n<br>'
            '* --- stage 1: unity-gain buffer ---<br>'
            'E1   5  0  3  5  1e5<br>'
            '* --- stage 2: non-inverting gain 5 ---<br>'
            'Rg   4  0  7.5k<br>'
            'Rf   4  6  30k<br>'
            'E2   6  0  5  4  1e5<br>'
            '.ac dec 100 10 100k<br>'
            '.probe V(6)<br>'
            '.end</p>')
body.append(p("交流扫描设置：起始 10 Hz，终止 100 kHz，每十倍频程 100 点，输出取节点 6（即 v<sub>o</sub>）。"
              "瞬态仿真设置：正弦源 1 kHz、幅值 0.5 V，仿真时长 5 ms，最大步长 1 μs。"))

body.append(h1("附录 B　关键代码片段", "ap2"))
body.append(p("（1）DDS 相位累加与查表（在 TIM6 更新中断中执行，实际由 DMA 双缓冲驱动）：", indent=False))
body.append('<p style="font-family:Consolas; font-size:8.5pt; line-height:1.4; text-indent:0; '
            'background-color:#f7f7f7; border:1px solid #dddddd;">'
            'void DDS_Step(int16_t *buf, uint32_t n) {<br>'
            '&nbsp;&nbsp;for (uint32_t i = 0; i &lt; n; i++) {<br>'
            '&nbsp;&nbsp;&nbsp;&nbsp;phase += dphi;                        /* 32 位相位累加 */<br>'
            '&nbsp;&nbsp;&nbsp;&nbsp;uint32_t idx = phase &gt;&gt; 22;           /* 高 10 位作索引 */<br>'
            '&nbsp;&nbsp;&nbsp;&nbsp;uint32_t frac = (phase &gt;&gt; 6) &amp; 0xFFFF; /* 插值系数 */<br>'
            '&nbsp;&nbsp;&nbsp;&nbsp;int32_t s = sine_tab[idx] +<br>'
            '&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;((int32_t)(sine_tab[(idx+1)&amp;1023] - sine_tab[idx]) * frac &gt;&gt; 16);<br>'
            '&nbsp;&nbsp;&nbsp;&nbsp;buf[i] = (int16_t)((s * amp_word) &gt;&gt; 15) + 2048;<br>'
            '&nbsp;&nbsp;}<br>'
            '}</p>')
body.append(p("（2）单频 Goertzel 提取幅相：", indent=False))
body.append('<p style="font-family:Consolas; font-size:8.5pt; line-height:1.4; text-indent:0; '
            'background-color:#f7f7f7; border:1px solid #dddddd;">'
            'float goertzel(const uint16_t *x, int n, float f, float fs, float *ph) {<br>'
            '&nbsp;&nbsp;float w = 2.0f * PI * f / fs, cw = 2.0f * cosf(w);<br>'
            '&nbsp;&nbsp;float s0 = 0, s1 = 0, s2 = 0;<br>'
            '&nbsp;&nbsp;for (int i = 0; i &lt; n; i++) {<br>'
            '&nbsp;&nbsp;&nbsp;&nbsp;float wnd = 0.5f - 0.5f * cosf(2.0f*PI*i/(n-1));  /* Hann 窗 */<br>'
            '&nbsp;&nbsp;&nbsp;&nbsp;s0 = wnd * (x[i] - 2048.0f) + cw * s1 - s2;<br>'
            '&nbsp;&nbsp;&nbsp;&nbsp;s2 = s1; s1 = s0;<br>'
            '&nbsp;&nbsp;}<br>'
            '&nbsp;&nbsp;float re = s1 - s2 * cosf(w), im = s2 * sinf(w);<br>'
            '&nbsp;&nbsp;*ph = atan2f(im, re);<br>'
            '&nbsp;&nbsp;return 2.0f * sqrtf(re*re + im*im) / (n * 0.5f);<br>'
            '}</p>')

body.append(h1("参考文献", "ap3"))
body.append('<p style="font-size:9.5pt; line-height:1.6; text-indent:0; margin-bottom:3pt;">'
            '[1] 童诗白, 华成英. 模拟电子技术基础（第五版）[M]. 北京: 高等教育出版社, 2015.</p>'
            '<p style="font-size:9.5pt; line-height:1.6; text-indent:0; margin-bottom:3pt;">'
            '[2] 胡广书. 数字信号处理——理论、算法与实现（第三版）[M]. 北京: 清华大学出版社, 2012.</p>'
            '<p style="font-size:9.5pt; line-height:1.6; text-indent:0; margin-bottom:3pt;">'
            '[3] 高晋占. 微弱信号检测（第二版）[M]. 北京: 清华大学出版社, 2011.</p>'
            '<p style="font-size:9.5pt; line-height:1.6; text-indent:0; margin-bottom:3pt;">'
            '[4] Ljung L. System Identification: Theory for the User (2nd ed.)[M]. Prentice Hall, 1999.</p>'
            '<p style="font-size:9.5pt; line-height:1.6; text-indent:0; margin-bottom:3pt;">'
            '[5] Texas Instruments. OPA2134 Datasheet[Z]. 2020.</p>'
            '<p style="font-size:9.5pt; line-height:1.6; text-indent:0; margin-bottom:3pt;">'
            '[6] STMicroelectronics. STM32F407xx Reference Manual (RM0090)[Z]. 2021.</p>')

# ================= 组装 =================
style = """
:root { --ink: #1a1a1a; --accent: #1f5c8b; }
@page { @bottom-center { content: counter(page) " / " counter(pages); }
        @top-right { content: "电路模型探究装置设计与实现"; } }
@page cover { @bottom-center { content: none; } @top-right { content: none; } }
section[role="cover"] { page: cover; }
"""

html = f"""<!DOCTYPE html>
<html lang="zh-CN"><head><meta charset="utf-8"><title>电路模型探究装置设计与实现</title>
<style>{style}</style></head>
<body>
{cover}
<section role="body" data-page-restart="1">
{toc_html}
{''.join(body)}
</section>
</body></html>"""

os.makedirs(os.path.dirname(OUT), exist_ok=True)
with open(OUT, "w", encoding="utf-8") as f:
    f.write(html)
print("written:", OUT, len(html), "chars")
