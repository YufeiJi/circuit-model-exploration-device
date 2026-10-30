# 工具与安装包

DFU 工具源码见 [DFU烧录工具](DFU烧录工具/README.md)。在项目根目录运行：

```powershell
python -m pip install pyusb libusb-package
python "工具/DFU烧录工具/flash_dfu.py" "Keil/Objects/CircuitModel.hex"
```

先在 Keil 构建，再确认指定的是本次生成的 HEX。该命令会实际擦写已接入的目标板，烧录前核对接线、BOOT0 和设备身份。

`Keil.STM32F4xx_DFP.2.17.0.pack` 原件约 276 MiB，超出普通 Git 单文件限制，保留本地但不提交。可从 [Keil 器件包目录](https://www.keil.com/dd2/pack/) 获取匹配的版本；当前工程已包含器件头与启动文件，打开现有工程与从零建工程的需求不同。第三方软件遵循各自分发与使用条款。

装驱动用的 Zadig 未随仓库分发（单文件 5 MB，非本项目成果），需要时从 [Zadig 官方网站](https://zadig.akeo.ie/) 下载。只为 VID:PID 为 `0483:DF11` 的目标 DFU 设备配置驱动，选错设备会导致其他 USB 设备失灵。
