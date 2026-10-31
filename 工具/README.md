# 工具

这个目录里放三样东西：日常用的调试台、烧录的备用方案、以及建工程要用的器件包。

| 目录 / 文件 | 用途 | 是否需要安装 |
|---|---|---|
| `调试台\` | 网页版上位机：串口调试 + DFU 烧录 | 不用装，双击 `启动调试台.bat` |
| `DFU烧录工具\` | 命令行烧录脚本（纯 Python） | 要 `pyusb` |
| `Keil.STM32F4xx_DFP.2.17.0.pack` | Keil 器件包，从零建工程用 | 本地保留，不入库 |
| `zadig-2.9.exe` | 给 DFU 设备装 WinUSB 驱动 | 本地保留，不入库 |

## 调试台（日常首选）

双击 `调试台\启动调试台.bat`，Edge 会弹出一个独立窗口，左边串口、右边烧录。

- **串口调试**：115200 8N1 连 PA2/PA3，固件的 8 条命令都做成了按钮，终端带时间戳和日志导出
- **DFU 烧录**：拖入 hex 直接烧，走浏览器原生 WebUSB，不需要 Python

细节见 [调试台说明](调试台/README.md)。

## DFU 烧录工具（备用）

网页版连不上设备时（驱动被换、被 CubeProgrammer 独占）改用这条：

```powershell
python -m pip install pyusb libusb-package
python "工具/DFU烧录工具/flash_dfu.py" "Keil/Objects/CircuitModel.hex"
```

也可以直接双击 `DFU烧录工具\flash.bat`，它会自动找 `Keil\Objects\CircuitModel.hex`。
源码与协议细节见 [DFU烧录工具说明](DFU烧录工具/README.md)。

先在 Keil 构建，再确认指定的是本次生成的 HEX。该命令会实际擦写已接入的目标板，烧录前核对接线、BOOT0 和设备身份。

## 器件包

`Keil.STM32F4xx_DFP.2.17.0.pack` 原件约 276 MiB，超出普通 Git 单文件限制，保留本地但不提交。可从 [Keil 器件包目录](https://www.keil.com/dd2/pack/) 获取匹配的版本；当前工程已包含器件头与启动文件，打开现有工程与从零建工程的需求不同。第三方软件遵循各自分发与使用条款。

注意必须用 **2.17.0**：3.x 系列删掉了器件头文件与启动文件，只留 Flash 算法，裸机工程打不开。

## 驱动

装驱动用的 `zadig-2.9.exe` 保留在本目录供本机使用，但不提交到仓库（5.1 MB 第三方文件，非本项目成果）。换一台电脑时从 [Zadig 官方网站](https://zadig.akeo.ie/) 下载即可。

只为 VID:PID 为 `0483:DF11` 的目标 DFU 设备配置驱动，选错设备会导致其他 USB 设备失灵。

## 三条烧录路线怎么选

| 路线 | 条件 | 速度 | 适合 |
|---|---|---|---|
| **ST-Link + Keil F8** | 有 ST-Link，接 PA13/PA14 | 最快 | 日常开发，还能在线调试 |
| **调试台（WebUSB）** | 有 Type-C 线，装过 WinUSB | 约 15 KB/s | 手边没有 ST-Link 时 |
| **DFU 烧录工具（命令行）** | 同上，外加 pyusb | 约 15 KB/s | 网页版连不上设备时的退路 |

前两条都不需要动 BOOT0（ST-Link 直接写 Flash）；后两条必须先让芯片进 DFU。
