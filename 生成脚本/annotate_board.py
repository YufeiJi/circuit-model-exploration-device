# -*- coding: utf-8 -*-
"""在用户实拍图上标注关键接口：图上只放编号，文字说明集中放在下方图例"""
from PIL import Image, ImageDraw, ImageFont

SRC = r"D:\1\Tencent Files\2726257920\nt_qq\nt_data\Pic\2026-10\Thumb\4e3a1255a3e5cd5cfc5fd7a478f14713_720.jpg"
OUT = r"D:\Agent\project\电路模型探究装置\模拟\板卡接口标注图.png"

CROP = (206, 12, 1000, 568)     # 只保留板子，去掉鼠标与背景
SC = 2

im = Image.open(SRC).convert("RGB").crop(CROP)
W, H = im.size
im = im.resize((W * SC, H * SC), Image.LANCZOS)

FONT = r"C:\Windows\Fonts\msyh.ttc"
FONTB = r"C:\Windows\Fonts\msyhbd.ttc"


def font(sz, bold=False):
    return ImageFont.truetype(FONTB if bold else FONT, sz)


# 编号、原图坐标（未裁剪）、说明
MARKS = [
    ("1", (258, 52),  "复位键", "改完 BOOT0 按一下让芯片重新枚举；没有它拔插 USB 也一样"),
    ("2", (334, 60),  "3V3 双针 + BT0 针", "进 DFU 时用杜邦线把 BT0 接到 3V3，烧完必须拔掉"),
    ("3", (300, 112), "MicroSD 卡槽", "就是 Windows 里那个 F 盘（SD Flash Disk）"),
    ("4", (262, 228), "20 针 JTAG/SWD 座", "以后买 ST-Link / DAP-Link 从这里接 SWDIO、SWCLK、GND、3V3"),
    ("5", (252, 470), "Type-C 接口", "板上唯一 USB，直连 PA11/PA12：既能进 DFU，也被 MSC 例程占成 U 盘"),
    ("6", (640, 292), "STM32F407VET6", "512 KB Flash：CubeMX 选 VETx，Keil 选 512KB Flash 算法"),
    ("7", (482, 356), "8 MHz 晶振", "HSE 8 MHz，CubeMX 里 PLLM 填 8"),
]

LEG_H = 420
canvas = Image.new("RGB", (W * SC, H * SC + LEG_H), "white")
canvas.paste(im, (0, 0))
d = ImageDraw.Draw(canvas, "RGBA")

RED = (214, 40, 40, 255)
for num, (ox, oy), name, _ in MARKS:
    X = (ox - CROP[0]) * SC
    Y = (oy - CROP[1]) * SC
    r = 34
    d.ellipse([X - r, Y - r, X + r, Y + r], outline=(255, 255, 255, 255), width=7)
    d.ellipse([X - r, Y - r, X + r, Y + r], outline=RED, width=4)
    bb = d.textbbox((0, 0), num, font=font(44, True))
    tw, th = bb[2] - bb[0], bb[3] - bb[1]
    d.text((X - tw / 2 - bb[0], Y - th / 2 - bb[1]), num, font=font(44, True), fill=RED)

y = H * SC + 14
d.text((26, y), "STM32F407VET6 开发板（丝印 STM32_F4VE / DevEBox）关键接口", font=font(32, True),
       fill=(22, 44, 74))
y += 46

for num, _, name, desc in MARKS:
    d.ellipse([26, y + 4, 56, y + 34], outline=RED, width=3)
    d.text((34, y + 3), num, font=font(24, True), fill=RED)
    d.text((70, y + 2), name, font=font(26, True), fill=(30, 30, 30))
    nw = d.textbbox((70, y + 2), name, font=font(26, True))[2]
    d.text((nw + 26, y + 6), "— " + desc, font=font(22), fill=(90, 90, 90))
    y += 44

canvas.save(OUT)
print("saved", OUT, canvas.size)
