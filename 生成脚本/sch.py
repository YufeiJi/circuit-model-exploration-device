# -*- coding: utf-8 -*-
"""已知模型电路原理图（手绘，精确坐标）"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Polygon, Arc
plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei"]
plt.rcParams["axes.unicode_minus"] = False
LW = 1.7
C = "#111111"

fig, ax = plt.subplots(figsize=(10.6, 3.7))
ax.set_aspect("equal"); ax.axis("off")

def w(*pts, lw=LW):
    ax.plot([p[0] for p in pts], [p[1] for p in pts], color=C, lw=lw,
            solid_capstyle="round", solid_joinstyle="round", zorder=2)

def dot(x, y, r=0.055):
    ax.add_patch(plt.Circle((x, y), r, color=C, zorder=4))

def dot_open(x, y, r=0.06):
    ax.add_patch(plt.Circle((x, y), r, fc="white", ec=C, lw=LW, zorder=4))

def hop(x, y, r=0.11):
    ax.add_patch(Arc((x, y), 2*r, 2*r, theta1=0, theta2=180, color=C, lw=LW, zorder=3))

def res_h(x1, x2, y, label):
    w((x1, y), (x1+0.22, y)); w((x2-0.22, y), (x2, y))
    ax.add_patch(Rectangle((x1+0.22, y-0.2), (x2-x1)-0.44, 0.4, fc="white", ec=C, lw=LW, zorder=3))
    ax.text((x1+x2)/2, y+0.32, label, ha="center", va="bottom", fontsize=10)

def res_v(x, y1, y2, label):
    w((x, y1), (x, y1-0.22)); w((x, y2+0.22), (x, y2))
    ax.add_patch(Rectangle((x-0.2, y2+0.22), 0.4, (y1-y2)-0.44, fc="white", ec=C, lw=LW, zorder=3))
    ax.text(x-0.34, (y1+y2)/2, label, ha="right", va="center", fontsize=10)

def cap_h(xc, y, label):
    w((xc-0.40, y), (xc-0.075, y)); w((xc+0.075, y), (xc+0.40, y))
    for dx in (-0.075, 0.075): w((xc+dx, y-0.28), (xc+dx, y+0.28))
    ax.text(xc+0.14, y+0.34, label, ha="left", va="bottom", fontsize=10)

def cap_v(x, yc, label):
    w((x, yc+0.40), (x, yc+0.075)); w((x, yc-0.075), (x, yc-0.40))
    for dy in (-0.075, 0.075): w((x-0.28, yc+dy), (x+0.28, yc+dy))
    ax.text(x-0.38, yc+0.02, label, ha="right", va="center", fontsize=10)

def gnd(x, y):
    w((x, y), (x, y-0.15))
    for i, hw in enumerate([0.26, 0.17, 0.08]):
        w((x-hw, y-0.15-i*0.11), (x+hw, y-0.15-i*0.11))

def opamp(xl, yc, name, wdt=1.45, hh=0.62):
    ax.add_patch(Polygon([[xl, yc-hh], [xl, yc+hh], [xl+wdt, yc]], closed=True,
                         fc="white", ec=C, lw=LW, zorder=3))
    ax.text(xl+0.26, yc+0.17, "−", fontsize=14, ha="center", va="center", zorder=4)
    ax.text(xl+0.26, yc-0.17, "+", fontsize=12, ha="center", va="center", zorder=4)
    ax.text(xl+wdt/2+0.05, yc-hh-0.22, name, fontsize=9.5, ha="center", va="top")
    return xl+wdt, yc+0.28, yc-0.28

Y = 0.0
# ---------------- 输入 ----------------
dot_open(0.12, Y); ax.text(-0.02, Y-0.34, "$v_i$", fontsize=11, ha="left")
w((0.12, Y), (0.80, Y))
res_h(0.80, 2.00, Y, "$R_1$ = 3.83 kΩ")
w((2.00, Y), (3.00, Y)); dot(2.40, Y)
res_h(3.00, 4.20, Y, "$R_2$ = 26.1 kΩ")
w((4.20, Y), (5.00, Y)); dot(4.60, Y)

# ---------------- 第一级：单位增益 Sallen-Key ----------------
A1x = 5.85
o1x, p1y, n1y = opamp(A1x, Y, "A1  OPA2134")
w((5.00, Y), (5.42, Y), (5.42, p1y), (A1x, p1y))
w((o1x, Y), (8.08, Y))
w((8.32, Y), (8.60, Y))
dot(7.55, Y); dot(7.85, Y)
# 单位增益反馈
w((7.55, Y), (7.55, 0.92), (5.12, 0.92), (5.12, n1y), (A1x, n1y))
# C1
w((2.40, Y), (2.40, 1.78), (2.85, 1.78))
cap_h(3.25, 1.78, "$C_1$ = 10 nF")
w((3.65, 1.78), (7.85, 1.78), (7.85, Y))
# C2
w((4.60, Y), (4.60, -0.62))
cap_v(4.60, -1.06, "$C_2$ = 10 nF")
w((4.60, -1.46), (4.60, -1.60)); gnd(4.60, -1.60)

# ---------------- 第二级：同相放大 ×5 ----------------
A2x = 9.30
o2x, p2y, n2y = opamp(A2x, Y, "A2  OPA2134")
w((8.60, Y), (8.60, p2y), (A2x, p2y))
w((o2x, Y), (11.20, Y)); dot(11.20, Y)
dot_open(11.55, Y); ax.text(11.68, Y-0.34, "$v_o$", fontsize=11, ha="left")
# Rg（跨接：与信号线交叉处画跨线半圆）
w((A2x, n2y), (8.20, n2y)); dot(8.20, n2y)
w((8.20, n2y), (8.20, 0.13)); hop(8.20, 0.0)
res_v(8.20, -0.13, -1.15, "$R_g$ = 7.5 kΩ")
w((8.20, -1.15), (8.20, -1.30)); gnd(8.20, -1.30)
# Rf
w((8.20, n2y), (8.20, 1.62))
res_h(8.20, 11.20, 1.62, "$R_f$ = 30 kΩ")
w((11.20, 1.62), (11.20, Y))


ax.text(-0.02, -2.32, "注：A1、A2 由同一片 OPA2134 双运放实现，±9 V 供电；输入端、输出端均预留测试端口。",
        fontsize=8.6, color="#444")
ax.set_xlim(-0.2, 12.2); ax.set_ylim(-2.52, 1.95)
plt.tight_layout(); plt.savefig(r"D:\Agent\project\电路模型探究装置\模拟\figs\fig2_schematic.png",
                                bbox_inches="tight", pad_inches=0.10, dpi=300)
print("saved")
