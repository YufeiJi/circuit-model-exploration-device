# -*- coding: utf-8 -*-
"""未知模型辨识：扫频(幅+相) -> 四模型复频域最小二乘 -> 分类与参数辨识"""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy.optimize import minimize
plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei"]
plt.rcParams["axes.unicode_minus"] = False
plt.rcParams["savefig.dpi"] = 300
OUT = r"D:\Agent\project\电路模型探究装置\模拟\figs"
TYPES = ["LP", "HP", "BP", "BR"]

def S(u, Q, typ):
    den = 1 - u**2 + 1j*u/Q
    if typ == "LP": return 1/den
    if typ == "HP": return -u**2/den
    if typ == "BP": return 1j*u/Q/den
    return (1 - u**2)/den

def Hc(f, K, f0, Q, typ): return K*S(f/f0, Q, typ)

# ---------- 图6 ----------
f = np.logspace(2.3, 5.0, 1500)
fig, axes = plt.subplots(2, 2, figsize=(7.4, 5.2), sharex=True)
meta = {"LP": ("(a) 低通：输出取 $C$", "#2471a3"), "HP": ("(b) 高通：输出取 $L$", "#c0392b"),
        "BP": ("(c) 带通：输出取 $R$", "#1e8449"), "BR": ("(d) 带阻：输出取 $L$+$C$", "#8e44ad")}
for ax, typ in zip(axes.ravel(), TYPES):
    ax.semilogx(f, 20*np.log10(np.abs(Hc(f, 1, 20000., 0.5, typ))), color=meta[typ][1], lw=2.2)
    ax.axvline(20000, color="gray", ls=":", lw=1)
    ax.axhline(-3, color="#e67e22", ls="--", lw=0.9)
    ax.set_ylim(-45, 8); ax.set_yticks([-40, -30, -20, -10, 0])
    ax.grid(True, which="both", ls=":", alpha=0.45)
    ax.set_title(meta[typ][0], fontsize=9.5)
for ax in axes[1]: ax.set_xlabel("频率 / Hz", fontsize=9)
for ax in axes[:, 0]: ax.set_ylabel("$20\\lg|H|$ / dB", fontsize=9)
plt.tight_layout(); plt.savefig(OUT + r"\fig6_types.png"); plt.close()

# ---------- 辨识 ----------
NF = 26
fsweep = np.logspace(np.log10(200), np.log10(100e3), NF)
F0G = np.logspace(np.log10(400), np.log10(3e5), 120)
QG = np.logspace(np.log10(0.008), np.log10(20), 56)
F0m, Qm = np.meshgrid(F0G, QG, indexing="ij")
F0v, Qv = F0m.ravel(), Qm.ravel()

def fit_type(typ, Hm_):
    w = 1.0/np.maximum(np.abs(Hm_)**2, 0.01**2)
    U = fsweep[None, :]/F0v[:, None]
    den = 1 - U**2 + 1j*U/Qv[:, None]
    if typ == "LP": s = 1/den
    elif typ == "HP": s = -U**2/den
    elif typ == "BP": s = 1j*U/Qv[:, None]/den
    else: s = (1 - U**2)/den
    sw = w[None, :]
    num = np.sum(sw*np.conj(s)*Hm_[None, :], axis=1)
    deno = np.sum(sw*np.abs(s)**2, axis=1)
    k = num/deno
    cost = np.sum(sw*np.abs(k[:, None]*s - Hm_[None, :])**2, axis=1)
    i = int(np.argmin(cost))
    def obj(p):
        ss = S(fsweep/10**p[0], 10**p[1], typ)
        kk = np.sum(w*np.conj(ss)*Hm_)/np.sum(w*np.abs(ss)**2)
        return float(np.sum(w*np.abs(kk*ss - Hm_)**2))
    r = minimize(obj, [np.log10(F0v[i]), np.log10(Qv[i])], method="Nelder-Mead",
                 options=dict(xatol=1e-7, fatol=1e-14, maxiter=1000))
    f0, Q = 10**r.x[0], 10**r.x[1]
    ss = S(fsweep/f0, Q, typ)
    kk = np.sum(w*np.conj(ss)*Hm_)/np.sum(w*np.abs(ss)**2)
    return float(r.fun), f0, Q, kk

def identify(Hm_):
    out = []
    for typ in TYPES:
        c, f0, Q, k = fit_type(typ, Hm_)
        out.append((c, typ, f0, Q, k))
    out.sort(key=lambda x: x[0])
    return out[0], out

rng = np.random.default_rng(2026)
rows = []
for _ in range(200):
    typ = rng.choice(TYPES)
    R = 10**rng.uniform(3, 4); L = 10**rng.uniform(-3, -2); C = 10**rng.uniform(-8, -7)
    f0t = 1/(2*np.pi*np.sqrt(L*C)); Qt = np.sqrt(L/C)/R
    m = Hc(fsweep, 1.0, f0t, Qt, typ)
    m = m*(1 + 0.01*rng.standard_normal(NF))*np.exp(1j*np.deg2rad(1.0*rng.standard_normal(NF)))
    best, _ = identify(m)
    rows.append((typ, best[1], f0t, Qt, best[2], best[3]))

ok = np.mean([r[0] == r[1] for r in rows])
f0e = np.array([abs(r[4]-r[2])/r[2]*100 for r in rows])
Qe = np.array([abs(r[5]-r[3])/r[3]*100 for r in rows])
print("样本数 %d  分类正确率 %.1f%%" % (len(rows), ok*100))
print("f0 误差: 中位 %.2f%%  90%%分位 %.2f%%  最大 %.2f%%" % (np.median(f0e), np.percentile(f0e, 90), f0e.max()))
print("Q  误差: 中位 %.2f%%  90%%分位 %.2f%%  最大 %.2f%%" % (np.median(Qe), np.percentile(Qe, 90), Qe.max()))
print("f0<2%%: %.1f%%   Q<5%%: %.1f%%   Q<10%%: %.1f%%" % ((f0e < 2).mean()*100, (Qe < 5).mean()*100, (Qe < 10).mean()*100))
print("误判:", [(r[0], r[1], round(r[2])) for r in rows if r[0] != r[1]][:6])

print("\n典型样本 (R=2.2k, L=4.7mH, C=47nF):")
demo = []
for typ in TYPES:
    R, L, C = 2.2e3, 4.7e-3, 47e-9
    f0t = 1/(2*np.pi*np.sqrt(L*C)); Qt = np.sqrt(L/C)/R
    m = Hc(fsweep, 1.0, f0t, Qt, typ)*(1+0.01*rng.standard_normal(NF))
    best, allc = identify(m)
    print(f"  {typ}: f0={f0t:.0f}Hz Q={Qt:.3f} -> {best[1]} f0={best[2]:.0f}Hz Q={best[3]:.3f} "
          f"K={abs(best[4]):.3f} | " + " ".join(f"{c[1]}:{c[0]:.2e}" for c in allc))
    demo.append((typ, best, m))

fig, axes = plt.subplots(2, 2, figsize=(7.4, 5.0), sharex=True)
ff = np.logspace(np.log10(200), np.log10(100e3), 600)
for ax, (typ, best, m) in zip(axes.ravel(), demo):
    c = meta[typ][1]
    ax.semilogx(fsweep, 20*np.log10(np.abs(m)), "o", ms=3.6, color=c, label="扫频实测")
    ax.semilogx(ff, 20*np.log10(np.abs(Hc(ff, best[4], best[2], best[3], best[1]))),
                "--", lw=1.2, color="#111111", label=f"拟合 {best[1]}")
    ax.set_ylim(-45, 8); ax.set_yticks([-40, -30, -20, -10, 0])
    ax.grid(True, which="both", ls=":", alpha=0.45)
    ax.set_title(f"真实 {typ} → 判决 {best[1]}   $f_0$={best[2]/1e3:.2f} kHz, $Q$={best[3]:.2f}", fontsize=8.5)
    ax.legend(fontsize=6.5, loc="lower left")
for ax in axes[1]: ax.set_xlabel("频率 / Hz", fontsize=9)
for ax in axes[:, 0]: ax.set_ylabel("$20\\lg|H|$ / dB", fontsize=9)
plt.tight_layout(); plt.savefig(OUT + r"\fig7_fit.png"); plt.close()
