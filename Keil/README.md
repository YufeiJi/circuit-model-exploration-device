# Keil 工程 · 电路模型探究装置（STM32F407VET6）

纯寄存器实现，不用 CubeMX、不用 HAL、不用标准外设库。工程自带全部头文件与启动文件，换台电脑也能直接编译。

> 这是「Keil 部分」。项目根目录 `..\` 下还有 `模拟\`（电路设计）、`工具\`（烧录工具）、`文档\`（各类手册）、`教程-从零到跑通.pdf`。

## 怎么用

1. 双击 `CircuitModel.uvprojx`，Keil µVision 打开
2. 按 **F7** 编译，产物在 `Objects\CircuitModel.hex`
3. **有 ST-Link V2**：SWD 接 PA13(SWDIO) / PA14(SWCLK) / GND（+NRST），
   Debug 页选 `ST-Link Debugger`，Flash Download 页确认算法是 `STM32F4xx 512kB Flash`，
   按 **F8** 下载。不用拨 BOOT0，不用 CubeProgrammer。
4. **ST-Link 连不上时（DFU，已实测可用）**：BT0 针短接 3V3 → 复位 → 双击
   `..\工具\调试台\启动调试台.bat`，在「DFU 烧录」页拖入 hex 烧录
   （网页版，不需要 CubeProgrammer，也不需要装 pyusb）
   → 拔掉 BOOT0 杜邦线 → 复位。

> Flash 算法已放在 `D:\daxue\Keil5 32\ARM\Flash\STM32F4xx_512.FLM`，工程内也存了一份 `Flash\STM32F4xx_512.FLM`。
> 工程没装器件包，所以算法路径是写死的绝对路径；换机器需在 Flash Download 页重新 Add 一次。

> 前置条件：Keil 里必须装 **Keil.STM32F4xx_DFP 2.17.0**（器件包）才能正常建新工程。
> 本工程已把器件头与启动文件 vendor 到 `Drivers\CMSIS\`，**不装包也能编译**，只有建新工程时才需要。
> 器件包不随仓库分发，获取方式见 [工具说明](../工具/README.md)。本地保留安装包时可双击安装。

## 工程设置（已配好，供核对）

| 项 | 值 |
|---|---|
| 器件 | STM32F407VE（LQFP100 / 512 KB Flash / 192 KB RAM） |
| 编译器 | ARM Compiler 6（AC6） |
| C 标准 | C99 |
| 优化 | Level 1 (-O1) |
| 浮点 | Single Precision（FPU 必须开，否则进 main 就 HardFault） |
| 运行库 | MicroLIB（printf 依赖） |
| 器件宏 | `STM32F407xx` |
| Include Paths | `.\Core;.\BSP;.\App;.\Drivers\CMSIS\Device\Include;.\Drivers\CMSIS\Include` |
| 输出 | `Objects\CircuitModel.hex` |
| Scatter | `.\CircuitModel.sct`（`umfTarg=0`，不用 Target 页自动生成） |
| RTE | **一个都不勾**（头文件与启动文件已在 `Drivers\` 内，勾了会重复定义） |

## 目录

```
Keil/                            ← 本目录
├── CircuitModel.uvprojx         µVision 工程文件
├── CircuitModel.sct             链接脚本（scatter）
├── Core/
│   ├── main.c                   初始化顺序、串口命令行、printf 重定向
│   └── system_stm32f4xx.c       最小系统文件：使能 FPU、SystemCoreClock
├── BSP/
│   ├── bsp.h
│   └── bsp.c                    168 MHz 时钟、SysTick、USART2、TIM6/TIM3、DAC+DMA、ADC+DMA
├── App/
│   ├── app_dds.c/.h             32 位相位累加 DDS + 1024 点表 + 线性插值 + DMA 双缓冲
│   ├── app_meas.c/.h            ADC 采集 + Hann 窗单频 DFT 幅相提取
│   ├── app_known.c/.h           已知模型 H(s) 幅相与开环反算
│   └── app_ident.c/.h           26 点扫频 + 四模型拟合 + 分类
├── Drivers/
│   ├── CMSIS/Device/Include/    stm32f4xx.h、stm32f407xx.h、system_stm32f4xx.h
│   ├── CMSIS/Device/Source/     startup_stm32f407xx.s（栈已调到 4 KB）
│   └── CMSIS/Include/           core_cm4.h 及 8 个 CMSIS 内核头文件
├── Flash/                       STM32F4xx_512.FLM（Flash 编程算法备份）
├── Objects/                     编译产物（hex 在这里）
├── Listings/                    列表文件
└── _verify/                     本机离线构建产物（不随仓库分发，使用前核对版本）
```

## 硬件连接

| 功能 | 引脚 | 说明 |
|---|---|---|
| DAC 输出 | PA4 | 接示波器或被测电路输入 |
| ADC 输入 | PA0 | 接被测电路输出 |
| 串口 TX/RX | PA2 / PA3 | AF7，115200 8N1，需 USB-TTL 才能看 printf |
| SWD 调试 | PA13 / PA14 | 接 ST-Link V2 的 SWDIO / SWCLK |
| DFU | PA11 / PA12 | 板载 Type-C 直连，BT0 短接进 bootloader |

## 串口命令

```
?            帮助
F1000        设定频率 1000 Hz
A2.0         设定激励峰峰值 2.0 V
M            测量当前输出幅相
H            打印当前频率下已知模型的 |H|
K1.002       设定 1 kHz 校准系数
C1.5         开环控制：让已知模型输出达到 1.5 Vpp
L            未知模型自主学习（26 点扫频 + 分类 + 参数；耗时待实测）
```

## 片上资源映射（写错就出不来波形）

| 资源 | 固定映射 | 备注 |
|---|---|---|
| DAC1_CH1 | **DMA1 Stream5 Channel7** | 硬件连线，不可改；标志位在 `DMA1->HISR` bit10(HT) / bit11(TC) |
| ADC1 | **DMA2 Stream0 Channel0** | 普通模式，每次采集前重新武装 |
| DAC 触发 | TIM6 TRGO（TSEL1 = 000） | TIM6 1 MHz → DAC 1 MSPS |
| ADC 触发 | TIM3 TRGO（EXTSEL = 1000） | TIM3 500 kHz，ADC 时钟 PCLK2/4 = 21 MHz |

## 第三方文件来源

`Drivers/` 下的文件来自两个官方包，按原样收录，未做修改（`startup_stm32f407xx.s` 仅把 Stack_Size 从 0x400 改为 0x1000）：

- ST 的 CMSIS 器件头与启动文件 —— `Keil.STM32F4xx_DFP 2.17.0`，BSD-3-Clause
- Arm 的 CMSIS 内核头文件 —— `ARM.CMSIS 5.9.0`，Apache-2.0

## 相关文档

- `..\教程-从零到跑通.pdf` —— **从零到跑通的完整教程**（硬件、编译、烧录、测试、排错）
- `..\工具\调试台\README.md` —— 网页版上位机：串口调试 + DFU 烧录（已实测）
- `..\文档\ST-Link烧录与在线调试速查.pdf` —— SWD 方案（接线、Keil 配置、下载、调试、报错对照）
- `..\文档\烧录与上电调试实操手册.pdf` —— 从编译产物到五级验证的全流程
- `..\文档\Keil手动建工程指南（不用CubeMX）.pdf` —— 建工程、编译、装器件包
- `..\模拟\电路模型探究装置-设计报告.docx` —— 原理与设计推导
- `..\文档\电路模型探究装置-完整操作过程与源码说明.docx` —— 全部生成脚本与源码

> 改 `CircuitModel.uvprojx` 之前必须关掉 Keil，否则 Keil 保存时会把磁盘上的改动覆盖掉。
