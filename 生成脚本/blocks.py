# -*- coding: utf-8 -*-
"""系统框图 / 流程图（版式修正）"""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Rectangle
plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei"]
plt.rcParams["axes.unicode_minus"] = False
plt.rcParams["savefig.dpi"] = 300
OUT = r"D:\Agent\project\电路模型探究装置\模拟\figs"

def box(ax, x, y, w, h, txt, fc="#eaf2f8", ec="#2c6fa8", fs=9, bold=False):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.008,rounding_size=0.015",
                                fc=fc, ec=ec, lw=1.3))
    ax.text(x+w/2, y+h/2, txt, ha="center", va="center", fontsize=fs,
            fontweight="bold" if bold else "normal", linespacing=1.45)

def wire(ax, pts, color="#333333", lw=1.35, arrow=True, ls="-"):
    pts = np.array(pts, float)
    ax.plot(pts[:, 0], pts[:, 1], color=color, lw=lw, ls=ls, solid_capstyle="round", zorder=1)
    if arrow:
        ax.add_patch(FancyArrowPatch(tuple(pts[-2]), tuple(pts[-1]), arrowstyle="-|>",
                                     mutation_scale=12, color=color, lw=lw,
                                     shrinkA=0, shrinkB=0, zorder=2))

# ============ 图1 ============
fig, ax = plt.subplots(figsize=(8.6, 4.3))
ax.set_xlim(0, 1); ax.set_ylim(0.33, 0.95); ax.axis("off")
box(ax, 0.02, 0.63, 0.155, 0.19, "人机接口\nOLED + 4 键\n+ 学习键", fc="#fdf2e9", ec="#ca6f1e", fs=8.4)
box(ax, 0.245, 0.61, 0.195, 0.245, "STM32F407\nDDS 正弦合成\n扫频 / 幅相测量\n模型辨识", fc="#e8f6ef", ec="#1e8449", fs=8.6, bold=True)
box(ax, 0.505, 0.715, 0.145, 0.125, "DAC 12 bit\n$f_s$ = 1 MSPS", fs=8.4)
box(ax, 0.700, 0.715, 0.135, 0.125, "重构低通\n+ 程控增益", fs=8.4)
box(ax, 0.885, 0.635, 0.105, 0.235, "被测\n电路", fc="#f5eef8", ec="#7d3c98", fs=9)
box(ax, 0.700, 0.455, 0.135, 0.125, "缓冲 / 衰减\n+ 偏置", fs=8.4)
box(ax, 0.505, 0.455, 0.145, 0.125, "ADC 12 bit\n1 MSPS", fs=8.4)
box(ax, 0.02, 0.455, 0.155, 0.105, "电源 12 V → ±9 V / 3.3 V", fc="#f2f3f4", ec="#616a6b", fs=7.6)

wire(ax, [(0.175, 0.725), (0.245, 0.725)])
wire(ax, [(0.440, 0.778), (0.505, 0.778)])
wire(ax, [(0.650, 0.778), (0.700, 0.778)])
wire(ax, [(0.835, 0.778), (0.885, 0.778)])
ax.text(0.860, 0.793, "$v_i$", fontsize=8.5, ha="center")
wire(ax, [(0.9375, 0.635), (0.9375, 0.518), (0.835, 0.518)])
ax.text(0.952, 0.575, "$v_o$", fontsize=8.5, ha="center")
wire(ax, [(0.700, 0.518), (0.650, 0.518)])
wire(ax, [(0.505, 0.518), (0.3425, 0.518), (0.3425, 0.61)])
ax.text(0.352, 0.545, "幅/相数据", fontsize=7.8, color="#555")
wire(ax, [(0.0975, 0.560), (0.0975, 0.63)], ls="-")
ax.add_patch(Rectangle((0.008, 0.425), 0.858, 0.445, fill=False, ec="#8a8a8a", ls="--", lw=1.0))
plt.tight_layout(); plt.savefig(OUT + r"\fig1_block.png", bbox_inches="tight", pad_inches=0.12); plt.close()

# ============ 图8 ============
fig, ax = plt.subplots(figsize=(5.0, 6.9))
ax.set_xlim(0, 1); ax.set_ylim(0.085, 1.0); ax.axis("off")
steps = [
    ("按下唯一“学习键”，启动学习建模", "#eaf2f8", "#2c6fa8"),
    ("输出 26 点对数扫频正弦 200 Hz~100 kHz\n每频点采集 512 点", "#e8f6ef", "#1e8449"),
    ("单频 DFT 提取 $\\dot V_o/\\dot V_i$\n得到幅频 $|H|$ 与相频 $\\varphi$", "#e8f6ef", "#1e8449"),
    ("对 4 种二阶模型分别作\n复频域加权最小二乘拟合", "#fdf2e9", "#ca6f1e"),
    ("比较残差 $J$，取 $J_{\\min}$ 对应模型\n→ 判定低通 / 高通 / 带通 / 带阻", "#fdf2e9", "#ca6f1e"),
    ("输出 $K,\\ \\omega_0,\\ Q$，得等效模型 $H(s)$", "#f5eef8", "#7d3c98"),
    ("OLED 显示滤波类型与参数\n按 $H(s)$ 推理生成输出信号", "#f5eef8", "#7d3c98"),
]
y = 0.965; h = 0.098; gap = 0.028
for i, (txt, fc, ec) in enumerate(steps):
    box(ax, 0.055, y-h, 0.89, h, txt, fc=fc, ec=ec, fs=8.5)
    if i < len(steps)-1:
        wire(ax, [(0.5, y-h), (0.5, y-h-gap)], color="#555")
    y -= (h+gap)
plt.tight_layout(); plt.savefig(OUT + r"\fig8_flow.png", bbox_inches="tight", pad_inches=0.10); plt.close()
print("ok")
