# -*- coding: utf-8 -*-
"""生成公式图片（mathtext），用于 Word 报告中的行间公式"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
matplotlib.rcParams["mathtext.fontset"] = "cm"

OUT = r"D:\Agent\project\电路模型探究装置\模拟\figs"
FS = 15

F = {
 "fml1": r"$H(s)=\dfrac{5}{10^{-8}s^{2}+3\times10^{-4}s+1}$",
 "fml2": r"$H(s)=K\,\dfrac{\omega_{n}^{2}}{s^{2}+\dfrac{\omega_{n}}{Q}\,s+\omega_{n}^{2}}$",
 "fml3": r"$s_{1,2}=\dfrac{-3\times10^{4}\pm\sqrt{(3\times10^{4})^{2}-4\times10^{8}}}{2}"
         r"=-3819.7,\ \ -26180.3\ \ \mathrm{rad/s}$",
 "fml4": r"$H_{1}(s)=\dfrac{1}{s^{2}R_{1}R_{2}C_{1}C_{2}+s\,C_{2}(R_{1}+R_{2})+1}$",
 "fml5": r"$R_{1}R_{2}=\dfrac{1}{\omega_{n}^{2}C^{2}}=1.0\times10^{8},"
         r"\qquad R_{1}+R_{2}=\dfrac{1}{Q\,\omega_{n}C}=3.0\times10^{4}$",
 "fml6": r"$V_{i,pp}=\dfrac{V_{set}}{\left|H(j2\pi f)\right|}\times k_{cal}$",
}
for name, tex in F.items():
    fig = plt.figure(figsize=(0.1, 0.1))
    t = fig.text(0, 0, tex, fontsize=FS, color="#111111")
    fig.savefig(OUT + "\\" + name + ".png", dpi=300, bbox_inches="tight",
                pad_inches=0.06, facecolor="white")
    plt.close(fig)
    from PIL import Image
    w, h = Image.open(OUT + "\\" + name + ".png").size
    print(name, w, h, round(w/h, 3))
