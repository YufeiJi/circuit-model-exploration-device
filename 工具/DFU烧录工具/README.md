# STM32 DFU 烧录工具

用板载 Type-C 口烧固件，不需要 ST-Link，不需要 STM32CubeProgrammer，不需要 ST 账号。

## 它是什么

STM32F407 出厂时芯片里就固化了一段 ROM bootloader。把 BOOT0 拉高再复位，芯片会把自己枚举成一个 USB 设备（VID `0483` / PID `DF11`），等电脑灌固件。

`flash_dfu.py` 就是用 Python 直接和这段 bootloader 对话的工具：读 hex、擦扇区、发数据，全程一条命令。

> 注意：这**不是**往芯片里烧的固件，是电脑端的一个小工具。芯片那边的 bootloader 是 ST 出厂就写死的，改不了也不用改。

## 三步上手

### 第 1 步：进 DFU 模式

1. 断电（拔掉 Type-C）
2. 用杜邦线把板子上排标着 **BT0** 的针接到旁边的 **3V3**
3. 插上 Type-C（插电脑，或插充电器都行，但要能连电脑才有用 —— 所以插电脑）
4. 按一下 **复位键**

顺序不能反：**先短接，后上电**。先上电再短接的话芯片已经按 BOOT0=0 启动了，改电平不生效。

进成功的标志：设备管理器 → 通用串行总线设备 → 出现 `STM32 BOOTLOADER`。

### 第 2 步：装驱动（只需做一次）

Windows 默认不给 DFU 设备装可用驱动，所以第一次要手动绑一个。

1. 下载 **Zadig**：<https://zadig.akeo.ie/>（单文件 exe，免安装）
2. 打开 Zadig → 菜单 `Options` → 勾上 **List All Devices**
3. 顶部下拉框里找到 **STM32 BOOTLOADER (0483 DF11)**
4. 右边驱动框选 **WinUSB**
5. 点 **Replace Driver**（或 Install Driver），等进度条走完
6. 拔插一次 Type-C

装完之后设备管理器里这个设备会从「通用串行总线设备」挪到「通用串行总线设备」下的 `WinUSB device`，名字可能变了，正常。

> **副作用**：绑了 WinUSB 之后，STM32CubeProgrammer 会认不出这个设备（它要自己的驱动）。两个工具选一个用。想换回来：设备管理器 → 右键该设备 → 卸载设备 → 勾「删除此设备的驱动程序软件」→ 重新插。

### 第 3 步：烧

双击 **`flash.bat`**。

它会自动去 `D:\Agent\project\电路模型探究装置\Keil\Objects\CircuitModel.hex` 找固件。看到这个就是成功：

```
==============================================================
  烧录成功。
==============================================================
```

然后：

1. 拔掉 Type-C
2. **把 BOOT0 上那根杜邦线拔掉**（或接回 GND）
3. 重新插上 Type-C
4. 按一下复位

程序立刻开始跑，串口（PA2/PA3，115200 8N1）会打出三行启动横幅。

> 第 2 步最容易忘。BOOT0 还在 3V3 的话芯片会一直停在 bootloader 里，你的程序根本不跑，串口一片安静 —— 然后你会以为是固件坏了。

## 命令行用法

```bash
# 默认：自动找 CircuitModel.hex
python flash_dfu.py

# 指定文件
python flash_dfu.py D:\some\path\firmware.hex

# 只看设备在不在
python flash_dfu.py --list

# 跳过擦除（不推荐）
python flash_dfu.py --no-verify

# 直接烧二进制
python flash_dfu.py --bin firmware.bin --addr 0x08000000
```

直接用 Python 跑的话，先把环境准备好：

```bash
pip install pyusb libusb-package
```

本目录的 `flash.bat` 已经指向预配置好的虚拟环境，双击即可，不用管这些。

## 正常输出长什么样

```
==============================================================
  STM32 DFU 烧录工具
==============================================================
  文件  D:\Agent\project\电路模型探究装置\Keil\Objects\CircuitModel.hex

==============================================================
  设备信息
==============================================================
  VID:PID     0483:DF11
  产品字符串  STM32  BOOTLOADER
  接口        0 / alt 0
  块大小      2048 字节

==============================================================
  烧录计划
==============================================================
  0x08000000  18.3 KB     18752 字节
  合计 18.3 KB

==============================================================
  擦除并写入
==============================================================
  [#########################] 100.0%  18.3 KB / 18.3 KB
  写入完成，用时 0.9 秒（20.3 KB/s）

==============================================================
  回读校验
==============================================================
  0x08000000  18.3 KB  一致
```

## 报错对照

| 报错 | 原因 | 处置 |
|---|---|---|
| 没找到 DFU 设备 | 没进 DFU，或没装驱动 | 脚本会打印完整排查步骤，照着走 |
| `Access denied` / `No backend available` | 设备在，但驱动不是 WinUSB | 用 Zadig 绑 WinUSB |
| `设备不是 DFU 类接口` | 绑错设备了（可能绑到了别的 0483 设备） | Zadig 里重选 `STM32 BOOTLOADER` |
| `芯片报错 0x0E errUNKNOWN` | 在 dfuIDLE 下发了 CLRSTATUS（旧版脚本的 bug） | 已修；若仍出现，按 NRST 让芯片回到干净状态 |
| `芯片报错 0x0F errSTALLEDPKT` | 状态机不对时发了 DNLOAD（比如没等 busy 结束） | 已修；新版每步都按 poll 等 busy 结束 |
| `等待芯片响应超时` | USB 线太长 / 供电不稳 | 换短一点的线，别过 Hub |
| 写完但程序不跑 | BOOT0 还挂在 3V3 | 挪回 GND 再复位 |
| 解析 HEX 失败 | hex 文件损坏或被截断 | 重新 F7 编译 |

## 备选方案

如果 Zadig 也搞不定（公司电脑禁装驱动之类），还有两条路：

**A. STM32CubeProgrammer**（官方）
下载：<https://www.st.com/en/development-tools/stm32cubeprog.html>，需要免费注册 ST 账号。
装完自带驱动，图形界面选 USB → USB1 → 打开 hex → Start Programming。装好之后本工具就不需要了。

**B. 看看板子支不支持 U 盘拖拽**
DevEBox 的说明里提到 Type-C「也能做 MSC 刷写」。如果板厂的 bootloader 支持，进 DFU 后电脑上会出现一个 U 盘，把 `.bin` 拖进去就烧好了，零软件零驱动。
值得先花 30 秒试一下 —— 进 DFU 后看「我的电脑」里有没有多出来一个可移动磁盘。

## 文件说明

```
DFU烧录工具/
├── flash_dfu.py    烧录主程序（HEX 解析 + DfuSe 协议）
├── flash.bat       一键运行
└── README.md       本文件
```

## 实现要点（给想改的人）

- **协议**：DFU 1.1 + ST 的 DfuSe 扩展。命令块 `0x21 + 4 字节地址` 设置写指针，然后按 2048 字节一块顺序 `DFU_DNLOAD`，每块之后 `DFU_GETSTATUS` 等状态机回到 `dfuDNLOAD-IDLE`
- **块大小**：从 DFU functional descriptor 的 `wTransferSize` 读，读不到退化成 2048
- **块编号**：block 0 专用于 DfuSe 命令（设地址 / 擦除），数据从 **block 2** 开始，block 1 由 ST 保留
- **擦除**：显式按扇区擦。内置 F407 的扇区表（16K×4 + 64K + 128K×7），按固件地址范围算出覆盖到的扇区逐个发 `0x41 + 扇区起始地址`。本固件 18.7 KB 落在 sector 0 和 1，擦两个扇区约 0.3 秒。加 `--no-erase` 可以跳过，改用 bootloader 的自动擦除
- **不做回读校验**：ST 的 bootloader 只在 `dfuIDLE` 接受 `DFU_UPLOAD`，而写完一块之后状态机停在 `dfuDNLOAD-IDLE`，此时 UPLOAD 会被 stall（实测 `Pipe error`）。所以校验改为「每块 GETSTATUS 必须返回 OK」，写入失败会立刻抛错；最终验证靠上电后串口有没有输出
- **HEX 解析**：支持记录类型 00/01/02/04，带校验和验证，多段会自动合并成连续区间

## 一个已修复的坑：.bat 必须是 CRLF 行尾

如果 `.bat` 用 LF（Unix）行尾保存，cmd.exe 会把多行粘成一行解析，报出这类莫名其妙的错：

```
系统找不到指定的路径。
'.' 不是内部或外部命令，也不是可运行的程序或批处理文件。
'thon' 不是内部或外部命令，也不是可运行的程序或批处理文件。
```

`thon` 其实是 `python` 被切断的残片。**不是环境问题，是行尾问题。**
修法：用 `open(..., newline="\r\n")` 写文件，或用编辑器把行尾转成 CRLF。

验证方法：`grep -c $'\r' flash.bat` 的结果应等于总行数。

## 协议层踩过的三个坑（改代码前先看这里）

1. **不能靠遍历端点找 DFU 接口**。DFU 接口的 `bNumEndpoints = 0`，
   `for ep in intf:` 一次都不执行，会误判成「不是 DFU 设备」。
   要直接看 `Interface` 对象自己的 `bInterfaceClass == 0xFE` / `bInterfaceSubClass == 0x01`。

2. **CLRSTATUS 只能在 dfuERROR 状态下发**。在 `dfuIDLE` 下发，芯片会直接跳进
   `dfuERROR / errUNKNOWN(0x0E)`，之后所有请求都被 stall，看起来像「驱动坏了」。
   正确做法：先 GETSTATUS 看状态，只有 state == 10 才发 CLRSTATUS。

3. **每发一个 DNLOAD / 擦除命令，都要按 GETSTATUS 返回的 poll 时间等 busy 结束**。
   ST 收到命令后立刻进入 `dfuDNBUSY(4)`，poll 通常 100 ms 左右。
   不等就发下一个请求，会得到 `errSTALLEDPKT(0x0F)`。

另外两个细节：
- DfuSe 命令固定 **5 字节**（`0x21/0x41` + 4 字节地址），不要多塞填充字节
- 不要发 `SET_INTERFACE`，ST 只认 alt 0，多发反而容易把它弄进错误态
