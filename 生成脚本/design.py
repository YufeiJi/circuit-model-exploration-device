# -*- coding: utf-8 -*-
"""第2题 电路模型探究装置 —— 设计计算与仿真绘图"""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Rectangle

plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei"]
plt.rcParams["axes.unicode_minus"] = False
plt.rcParams["figure.dpi"] = 200
plt.rcParams["savefig.dpi"] = 300

OUT = r"D:\Agent\project\电路模型探究装置\模拟\figs"
C1 = 10e-9; C2 = 10e-9
R1 = 3.83e3; R2 = 26.1e3
RF = 30e3;  RG = 7.5e3

def H_ideal(s):
    return 5.0 / (1e-8*s**2 + 3e-4*s + 1.0)

def H_circ(s):
    K2 = 1 + RF/RG
    den = s**2*R1*R2*C1*C2 + s*(R1+R2)*C2 + 1.0   # 单位增益Sallen-Key
    return K2/den

f = np.logspace(1, 5.2, 2000)
s = 1j*2*np.pi*f
Hi = H_ideal(s); Hc = H_circ(s)
mag_i = np.abs(Hi); mag_c = np.abs(Hc)
err = (mag_c - mag_i)/mag_i*100

print("== 关键频点 ==")
for ff in [10, 100, 300, 500, 1000, 1591.5, 2000, 3000, 5000, 10000, 20000]:
    si = 1j*2*np.pi*ff
    print(f"f={ff:8.1f}Hz  |Hi|={abs(H_ideal(si)):7.4f}  |Hc|={abs(H_circ(si)):7.4f}  "
          f"err={(abs(H_circ(si))-abs(H_ideal(si)))/abs(H_ideal(si))*100:6.3f}%  "
          f"phase={np.angle(H_circ(si),deg=True):7.2f}deg")

print("\n== 极点/参数 ==")
print("wn_ideal =", np.sqrt(1e8), "Q_ideal =", np.sqrt(1e8)/3e4)
wn_c = 1/np.sqrt(R1*R2*C1*C2); Q_c = 1/(wn_c*(R1+R2)*C2)
print(f"wn_circ = {wn_c:.1f} rad/s (f0={wn_c/2/np.pi:.1f} Hz), Q_circ = {Q_c:.5f}")
print(f"K_circ = {1+RF/RG:.4f}")
print(f"f1={wn_c*(np.sqrt(1+1/(4*Q_c**2))-1/(2*Q_c))/2/np.pi:.1f}Hz  "
      f"f2={wn_c*(np.sqrt(1+1/(4*Q_c**2))+1/(2*Q_c))/2/np.pi:.1f}Hz")
print(f"DC gain dB = {20*np.log10(5):.2f} dB")
print("\n== 100Hz-3kHz 误差统计 ==")
m = (f >= 100) & (f <= 3000)
print("max|err| = %.3f %%" % np.max(np.abs(err[m])))
print("\n== 1kHz 使输出1Vpp所需输入 ==")
for target in [1.0, 1.5, 2.0]:
    print(f"  Vout={target}Vpp -> Vin={target/abs(H_circ(1j*2*np.pi*1e3)):.4f} Vpp")

# 频点表
print("\n== 表格数据 ==")
for ff in [100, 200, 300, 500, 800, 1000, 1200, 1500, 2000, 2500, 3000]:
    si = 1j*2*np.pi*ff
    a, b = abs(H_ideal(si)), abs(H_circ(si))
    print(f"| {ff} | {a:.3f} | {a:.2f} | {b:.3f} | {b:.2f} | {(b-a)/a*100:+.2f} |")

# ---------- 图3 Bode ----------
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(7.2, 6.4), sharex=True,
                               gridspec_kw={"height_ratios": [1.45, 1]})
ax1.semilogx(f, 20*np.log10(mag_i), "k--", lw=1.6, label="理论 $H(s)$")
ax1.semilogx(f, 20*np.log10(mag_c), color="#c0392b", lw=2.0, label="电路实现（标称值）")
ax1.axvspan(100, 3000, color="#3498db", alpha=0.08)
ax1.text(160, 1.0, "考核频段 100 Hz ~ 3 kHz", color="#2471a3", fontsize=9)
ax1.axhline(20*np.log10(5), color="gray", ls=":", lw=1)
ax1.annotate("14.0 dB (K=5)", xy=(12, 14), xytext=(12, 8), fontsize=8, color="gray")
ax1.set_ylabel("幅度 $|H|$ / dB"); ax1.set_ylim(-45, 20)
ax1.grid(True, which="both", ls=":", alpha=0.45); ax1.legend(loc="lower left", fontsize=9)


ax2.semilogx(f, np.angle(Hi, deg=True), "k--", lw=1.4, label="理论")
ax2.semilogx(f, np.angle(Hc, deg=True), color="#c0392b", lw=1.8, label="电路实现")
ax2.axvspan(100, 3000, color="#3498db", alpha=0.08)
ax2.set_ylabel("相位 / (°)"); ax2.set_xlabel("频率 $f$ / Hz")
ax2.set_yticks([0, -45, -90, -135, -180]); ax2.set_ylim(-190, 10)
ax2.grid(True, which="both", ls=":", alpha=0.45); ax2.legend(loc="lower left", fontsize=9)
ax2.set_xlim(10, 1.6e5)
plt.tight_layout(); plt.savefig(OUT + r"\fig3_bode.png"); plt.close()

# ---------- 图5 误差 ----------
f2 = np.linspace(100, 3000, 400)
H2 = H_circ(1j*2*np.pi*f2); H2i = H_ideal(1j*2*np.pi*f2)
e2 = (np.abs(H2)-np.abs(H2i))/np.abs(H2i)*100
fig, ax = plt.subplots(figsize=(7.2, 3.4))
ax.plot(f2, e2, color="#c0392b", lw=2)
ax.axhline(0, color="k", lw=0.8)
ax.axhline(10, color="#e67e22", ls="--", lw=1.2, label="容差上限 +10 %")
ax.axhline(-10, color="#e67e22", ls="--", lw=1.2, label="容差下限 −10 %")
ax.fill_between(f2, -10, 10, color="#27ae60", alpha=0.07)
ax.set_xlabel("频率 $f$ / Hz"); ax.set_ylabel("幅度相对误差 / %")
ax.set_ylim(-12, 12); ax.grid(ls=":", alpha=0.5)
ax.legend(fontsize=8, loc="lower left")

plt.tight_layout(); plt.savefig(OUT + r"\fig5_err.png"); plt.close()
print("\nmax err 100-3000Hz =", np.max(np.abs(e2)))

# ---------- 图4 时域波形 ----------
fs = 2e6; T = 3e-3
t = np.arange(0, T, 1/fs)
fi = 1e3
vin = 0.5*np.sin(2*np.pi*fi*t)          # 1Vpp
# 用二阶系统的时域响应（状态空间精确仿真）
wn = wn_c; Q = Q_c; K = 1+RF/RG
from scipy.signal import lti, lsim
sys1 = lti([K*wn**2], [1, wn/Q, wn**2])
_, yout, _ = lsim(sys1, vin, t)
fig, ax = plt.subplots(figsize=(7.2, 3.2))
ax.plot(t*1e3, vin, color="#2471a3", lw=1.5, label="输入 $v_i$ (1 V$_{pp}$)")
ax.plot(t*1e3, yout, color="#c0392b", lw=1.8, label="输出 $v_o$ (≈2.53 V$_{pp}$)")
ax.set_xlabel("时间 / ms"); ax.set_ylabel("电压 / V"); ax.grid(ls=":", alpha=0.5)
ax.legend(fontsize=8, loc="upper right", ncol=2); ax.set_xlim(0, 3)

plt.tight_layout(); plt.savefig(OUT + r"\fig4_wave.png"); plt.close()
print("Vout pp (1kHz,1Vpp in) =", yout[-500:].max()-yout[-500:].min())
