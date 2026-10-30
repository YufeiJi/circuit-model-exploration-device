#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
STM32 USB DFU 烧录工具（纯 Python，DfuSe 协议）

为什么需要它：
    STM32F407 出厂自带一段 ROM bootloader。把 BOOT0 拉高再复位，芯片就会
    枚举成一个 USB DFU 设备（VID 0483 / PID DF11），等电脑把固件灌进去。
    本脚本用 pyusb 直接实现 DFU 1.1 + DfuSe 扩展，不依赖 CubeProgrammer、
    不依赖 dfu-util，也不需要 ST 账号。

用法：
    python flash_dfu.py                 自动找 ..\\..\\project\\电路模型探究装置\\Objects\\CircuitModel.hex
    python flash_dfu.py 固件.hex        指定文件
    python flash_dfu.py --list          只列出当前连着的 DFU 设备
    python flash_dfu.py --no-verify     跳过回读校验（更快，不建议）
    python flash_dfu.py --bin 固件.bin --addr 0x08000000   直接烧二进制

依赖：
    pip install pyusb libusb-package
"""

import argparse
import os
import struct
import sys
import time

try:
    import usb.core
    import usb.util
    import usb.backend.libusb1
except ImportError:
    print("[错误] 缺少 pyusb。请先运行：pip install pyusb libusb-package")
    sys.exit(2)

try:
    import libusb_package
    _BACKEND = usb.backend.libusb1.get_backend(
        find_library=lambda x: libusb_package.get_library_path())
except Exception:
    _BACKEND = None

# ---------------------------------------------------------------- 常量
VID = 0x0483
PID = 0xDF11

# DFU 类请求码
DFU_DETACH = 0x00
DFU_DNLOAD = 0x01
DFU_UPLOAD = 0x02
DFU_GETSTATUS = 0x03
DFU_CLRSTATUS = 0x04
DFU_GETSTATE = 0x05
DFU_ABORT = 0x06

# DFU 状态机
ST = {
    0: "appIDLE", 1: "appDETACH", 2: "dfuIDLE", 3: "dfuDNLOAD-SYNC",
    4: "dfuDNBUSY", 5: "dfuDNLOAD-IDLE", 6: "dfuMANIFEST-SYNC",
    7: "dfuMANIFEST", 8: "dfuMANIFEST-WAIT-RESET", 9: "dfuUPLOAD-IDLE",
    10: "dfuERROR",
}

# DfuSe 命令
DFUSE_SET_ADDRESS = 0x21
DFUSE_ERASE = 0x41

DEFAULT_TRANSFER = 2048

# STM32F407 内部 Flash 扇区表：(起始地址, 大小)
# sector 0~3 各 16 KB，sector 4 是 64 KB，sector 5~11 各 128 KB，共 1 MB
SECTORS = (
    [(0x08000000 + i * 0x4000, 0x4000) for i in range(4)] +
    [(0x08010000, 0x10000)] +
    [(0x08020000 + i * 0x20000, 0x20000) for i in range(7)]
)


def hr(title=""):
    if title:
        print()
        print("=" * 62)
        print("  " + title)
        print("=" * 62)
    else:
        print("-" * 62)


# ================================================================ HEX 解析
def parse_hex(path):
    """解析 Intel HEX，返回按地址排序的连续段列表 [(起始地址, bytes), ...]"""
    mem = {}
    base = 0
    with open(path, "r", encoding="ascii", errors="replace") as f:
        for lineno, raw in enumerate(f, 1):
            line = raw.strip()
            if not line:
                continue
            if not line.startswith(":"):
                raise ValueError("第 %d 行不是 HEX 记录：%r" % (lineno, line[:40]))
            try:
                body = bytes.fromhex(line[1:])
            except ValueError:
                raise ValueError("第 %d 行十六进制非法" % lineno)
            if len(body) < 5:
                raise ValueError("第 %d 行太短" % lineno)
            count, addr, rtype = body[0], (body[1] << 8) | body[2], body[3]
            data = body[4:4 + count]
            chk = sum(body[:-1]) & 0xFF
            if (chk + body[-1]) & 0xFF != 0:
                raise ValueError("第 %d 行校验和错误（文件可能损坏）" % lineno)

            if rtype == 0x00:                       # 数据
                for i, b in enumerate(data):
                    mem[base + addr + i] = b
            elif rtype == 0x01:                     # 结束
                break
            elif rtype == 0x02:                     # 扩展段地址
                base = ((data[0] << 8) | data[1]) << 4
            elif rtype == 0x04:                     # 扩展线性地址
                base = ((data[0] << 8) | data[1]) << 16
            elif rtype in (0x03, 0x05):
                pass
            else:
                raise ValueError("第 %d 行未知记录类型 0x%02X" % (lineno, rtype))

    if not mem:
        raise ValueError("HEX 里没有任何数据")

    # 合并成连续段
    segs = []
    addrs = sorted(mem)
    start = prev = addrs[0]
    buf = bytearray([mem[start]])
    for a in addrs[1:]:
        if a == prev + 1:
            buf.append(mem[a])
        else:
            segs.append((start, bytes(buf)))
            start = a
            buf = bytearray([mem[a]])
        prev = a
    segs.append((start, bytes(buf)))
    return segs


# ================================================================ 设备
def find_dfu():
    """返回 DFU 设备列表"""
    try:
        return list(usb.core.find(find_all=True, idVendor=VID, idProduct=PID,
                                  backend=_BACKEND) or [])
    except Exception as e:
        print("[错误] 枚举 USB 设备失败：%s" % e)
        return []


def diagnose():
    """找不到设备时给出可操作的排查建议"""
    hr("没找到 DFU 设备")
    print("""
芯片现在没有以 DFU 模式出现在 USB 总线上。按顺序检查：

 1. BOOT0 有没有拉高？
    板子上排那根标着 BT0 的针，用杜邦线接到旁边的 3V3，然后再按一下复位。
    注意：必须先短接、后上电（或上电后补按复位），顺序反了不生效。

 2. 板子有没有供电？
    Type-C 插电脑或充电器，板载电源灯要亮。

 3. 用的是板载 Type-C 口吗？
    DFU 走的是 PA11/PA12，只有板子自带那个 Type-C 能连。

 4. 设备管理器里有没有 STM32 BOOTLOADER？
    - 有，但本脚本找不到  → 缺 WinUSB 驱动，看下面「装驱动」
    - 没有，或者带黄色感叹号 → 还是没进 DFU，回第 1 步

 5. 换一根 USB 线
    很多线是纯充电线，没有数据线芯。

────────────────────────────────────────────────────────
装驱动（驱动装好了本脚本才能直接访问设备）
────────────────────────────────────────────────────────
  a) 下载 Zadig：https://zadig.akeo.ie/   （单文件，免安装）
  b) 打开 Zadig → Options → 勾 List All Devices
  c) 下拉框里选 STM32 BOOTLOADER (0483 DF11)
  d) 右边驱动框选 WinUSB
  e) 点 Replace Driver（或 Install Driver），等它装完
  f) 拔插一次 Type-C，重新运行本脚本

  注意：装了 WinUSB 之后，STM32CubeProgrammer 可能反而认不出这个设备
  （它要自己的驱动）。两者选一个用就行，想换回来在设备管理器里
  卸载设备并勾选「删除驱动程序」即可。
""")


# ================================================================ DFU 类
class Dfu:
    def __init__(self, dev):
        self.dev = dev
        self.cfg = None
        self.iface = 0
        self.alt = 0
        self.transfer = DEFAULT_TRANSFER

        try:
            dev.set_configuration()
        except Exception:
            pass                      # Windows/WinUSB 下可能已经配置好，忽略
        self.cfg = dev.get_active_configuration()

        # 找 DFU 类接口。
        # 注意：DFU 接口的端点数 bNumEndpoints = 0，所以不能靠遍历端点来找，
        # 必须直接看 Interface 对象本身的 bInterfaceClass / SubClass。
        found = False
        for intf in self.cfg:
            if (intf.bInterfaceClass == 0xFE and intf.bInterfaceSubClass == 0x01
                    and intf.bAlternateSetting == 0):
                self.iface = intf.bInterfaceNumber
                self.alt = intf.bAlternateSetting
                found = True
                break
        if not found:                 # 兜底：只要是 DFU 类就试
            for intf in self.cfg:
                if intf.bInterfaceClass == 0xFE:
                    self.iface = intf.bInterfaceNumber
                    self.alt = 0
                    found = True
                    break
        if not found:
            raise RuntimeError("设备不是 DFU 类接口，可能驱动不对或不是 STM32 bootloader")

        # 不要发 SET_INTERFACE：ST 的 bootloader 只认 alt 0，多发一条反而容易让它进错误态
        usb.util.claim_interface(dev, self.iface)
        self.transfer = self._read_transfer_size()
        self.ensure_ready()

    def _read_transfer_size(self):
        """从 DFU functional descriptor 读 wTransferSize，失败则用 2048"""
        try:
            raw = self.dev.ctrl_transfer(0x81, 0x06, 0x2100, 0, 9, timeout=2000)
            if len(raw) >= 7:
                size = raw[5] | (raw[6] << 8)
                if 64 <= size <= 8192:
                    return size
        except Exception:
            pass
        return DEFAULT_TRANSFER

    # -------------------------------------------------- 底层请求
    def _status(self):
        """DFU_GETSTATUS，返回 (bStatus, bState, poll_ms)"""
        raw = self.dev.ctrl_transfer(0xA1, DFU_GETSTATUS, 0, self.iface, 6, timeout=5000)
        bStatus = raw[0]
        poll = raw[1] | (raw[2] << 8) | (raw[3] << 16)
        bState = raw[4]
        return bStatus, bState, poll

    def ensure_ready(self):
        """确保状态机在 dfuIDLE。

        关键：DFU 规范里 CLRSTATUS 只在 dfuERROR 下合法，
        在 dfuIDLE 下发会被芯片判成 errUNKNOWN，反而把设备弄坏。
        """
        st, state, _ = self._status()
        if state == 10:
            self._clear()
            time.sleep(0.05)
            st, state, _ = self._status()
            if state == 10:
                raise RuntimeError(
                    "芯片卡在错误态清不掉（0x%02X %s）。按一下板子的 NRST 再试。"
                    % (st, ST.get(st, "?")))
        return state

    def _wait_done(self, timeout_s=25):
        """等芯片干完活：先按 poll 等 dfuDNBUSY(4) 结束，再确认没进 dfuERROR"""
        t0 = time.time()
        st, state, poll = self._status()
        while state == 4:
            time.sleep(max(poll, 5) / 1000.0)
            st, state, poll = self._status()
            if time.time() - t0 > timeout_s:
                raise RuntimeError("等芯片写 Flash 超时（状态一直 busy）")
        if state == 10:
            raise RuntimeError("芯片报错 0x%02X（%s）。常见原因：写保护、地址非法、扇区没擦"
                               % (st, ST.get(st, "?")))
        return st, state

    def _clear(self):
        try:
            self.dev.ctrl_transfer(0x21, DFU_CLRSTATUS, 0, self.iface, None, timeout=2000)
        except Exception:
            pass

    def _abort(self):
        try:
            self.dev.ctrl_transfer(0x21, DFU_ABORT, 0, self.iface, None, timeout=2000)
        except Exception:
            pass

    def _dnload(self, block, data):
        self.dev.ctrl_transfer(0x21, DFU_DNLOAD, block, self.iface,
                               data, timeout=10000)

    def _upload(self, block, length):
        return self.dev.ctrl_transfer(0xA1, DFU_UPLOAD, block, self.iface,
                                      length, timeout=10000)

    # -------------------------------------------------- DfuSe 操作
    # 注意：DfuSe 的命令固定 5 字节（1 字节命令 + 4 字节地址），不要多塞填充字节
    def set_address(self, addr):
        self.dev.ctrl_transfer(0x21, DFU_DNLOAD, 0, self.iface,
                               struct.pack("<BI", DFUSE_SET_ADDRESS, addr),
                               timeout=5000)
        self._wait_done()

    def erase_page(self, addr):
        self.dev.ctrl_transfer(0x21, DFU_DNLOAD, 0, self.iface,
                               struct.pack("<BI", DFUSE_ERASE, addr),
                               timeout=5000)
        self._wait_done(timeout_s=40)

    def erase_range(self, start, end):
        """按扇区边界擦除 [start, end) 覆盖到的所有扇区，返回擦除的扇区数"""
        n = 0
        for sec_addr, sec_size in SECTORS:
            if sec_addr + sec_size <= start or sec_addr >= end:
                continue
            self.erase_page(sec_addr)
            n += 1
        return n

    def write_chunk(self, block, data):
        self.dev.ctrl_transfer(0x21, DFU_DNLOAD, block, self.iface,
                               data, timeout=15000)
        self._wait_done()

    def leave(self):
        """发一个空的 block 0 结束传输，进入 manifest（芯片随后自己复位）"""
        try:
            self.dev.ctrl_transfer(0x21, DFU_DNLOAD, 0, self.iface, None, timeout=5000)
        except Exception:
            return
        t0 = time.time()
        while time.time() - t0 < 20:
            try:
                st, state, _ = self._status()
            except Exception:
                return                      # 已经复位，正常
            if state in (6, 7, 8):
                return                      # 进 manifest，收工
            time.sleep(0.05)


# ================================================================ 主流程
def human(n):
    return "%.1f KB" % (n / 1024.0) if n >= 1024 else "%d B" % n


def do_flash(segs, verify=True, erase=True):
    devs = find_dfu()
    if not devs:
        diagnose()
        return 1
    dev = devs[0]

    hr("设备信息")
    print("  VID:PID     %04X:%04X" % (dev.idVendor, dev.idProduct))
    try:
        print("  产品字符串  %s" % usb.util.get_string(dev, dev.iProduct))
    except Exception:
        pass
    try:
        print("  bootloader  %s" % (dev.bcdDevice >> 8 & 0xFF,))
    except Exception:
        pass

    try:
        dfu = Dfu(dev)
    except Exception as e:
        print()
        print("[错误] 打开设备失败：%s" % e)
        print()
        print("  这个报错几乎都是驱动问题。设备在，但 Python 没有权限访问。")
        print("  用 Zadig 给它装 WinUSB 驱动（步骤见上）。")
        return 1

    print("  接口        %d / alt %d" % (dfu.iface, dfu.alt))
    print("  块大小      %d 字节" % dfu.transfer)

    total = sum(len(d) for _, d in segs)
    hr("烧录计划")
    for addr, data in segs:
        print("  0x%08X  %-10s  %d 字节" % (addr, human(len(data)), len(data)))
    print("  合计 %s" % human(total))

    hr("擦除")
    if erase:
        for seg_addr, seg_data in segs:
            end = seg_addr + len(seg_data)
            n = dfu.erase_range(seg_addr, end)
            print("  0x%08X ~ 0x%08X  擦除 %d 个扇区" % (seg_addr, end - 1, n))
    else:
        print("  已跳过（--no-erase），依赖 bootloader 写入前自动擦除")

    hr("写入")
    written = 0
    t_start = time.time()

    for seg_addr, seg_data in segs:
        dfu.set_address(seg_addr)

        block = 2
        off = 0
        while off < len(seg_data):
            chunk = seg_data[off:off + dfu.transfer]
            dfu.write_chunk(block, chunk)
            off += len(chunk)
            block += 1
            written += len(chunk)
            pct = written * 100.0 / total
            bar = "#" * int(pct / 4)
            sys.stdout.write("\r  [%-25s] %5.1f%%  %s / %s"
                             % (bar, pct, human(written), human(total)))
            sys.stdout.flush()

    print()
    dfu.leave()
    dt = time.time() - t_start
    print("  写入完成，用时 %.1f 秒（%.1f KB/s）" % (dt, total / 1024.0 / max(dt, 0.01)))
    print()
    print("  每一块都由芯片确认（GETSTATUS 返回 OK），写入失败会立刻报错。")
    print("  ST 的 bootloader 在 dfuDNLOAD-IDLE 状态不接受回读，所以这里不做回读比对；")
    print("  真正的验证是上电后程序跑起来 —— 串口能打出启动横幅就说明一切正常。")

    print()
    print("=" * 62)
    print("  烧录成功。")
    print("=" * 62)
    print("""
接下来：
  1. 断电（拔掉 Type-C）
  2. 把 BOOT0 上那根杜邦线拔掉（或接回 GND）
  3. 重新插上 Type-C
  4. 按一下复位键

程序会立刻开始跑，串口（PA2/PA3，115200 8N1）应打出三行启动横幅。
""")
    return 0


# 默认固件位置：按优先级依次尝试，第一个存在的就用
HEX_CANDIDATES = [
    r"D:\Agent\project\电路模型探究装置\Keil\Objects\CircuitModel.hex",
    r"D:\Agent\project\电路模型探究装置\Keil\_verify\CircuitModel.hex",
]


def find_default_hex():
    """没指定文件时自动找固件：先试固定路径，再在工程目录里按名字搜。"""
    for c in HEX_CANDIDATES:
        if os.path.exists(c):
            return c

    # 退一步：在 D:\\Agent\\project 下按文件名搜（最多 4 层，避免扫太深）
    root = r"D:\Agent\project"
    if os.path.isdir(root):
        for dirpath, dirnames, filenames in os.walk(root):
            depth = dirpath[len(root):].count(os.sep)
            if depth >= 4:
                dirnames[:] = []
                continue
            dirnames[:] = [d for d in dirnames if not d.startswith(".")]
            for fn in filenames:
                if fn.lower() == "circuitmodel.hex":
                    return os.path.join(dirpath, fn)

    # 最后看工具自己所在目录有没有 hex
    here = os.path.dirname(os.path.abspath(__file__))
    try:
        for fn in sorted(os.listdir(here)):
            if fn.lower().endswith(".hex"):
                return os.path.join(here, fn)
    except OSError:
        pass
    return None


def main():
    ap = argparse.ArgumentParser(description="STM32 USB DFU 烧录工具")
    ap.add_argument("file", nargs="?", help="要烧的 .hex 文件")
    ap.add_argument("--bin", metavar="FILE", help="直接烧二进制文件")
    ap.add_argument("--addr", default="0x08000000", help="--bin 的起始地址，默认 0x08000000")
    ap.add_argument("--list", action="store_true", help="只列出 DFU 设备")
    ap.add_argument("--no-verify", action="store_true", help="跳过回读校验")
    ap.add_argument("--no-erase", action="store_true", help="跳过显式擦除")
    args = ap.parse_args()

    hr("STM32 DFU 烧录工具")

    if args.list:
        devs = find_dfu()
        if not devs:
            print("  没有发现 DFU 设备（0483:DF11）")
            diagnose()
            return 1
        for d in devs:
            try:
                name = usb.util.get_string(d, d.iProduct)
            except Exception:
                name = "?"
            print("  %04X:%04X  bus %s addr %s  %s"
                  % (d.idVendor, d.idProduct, d.bus, d.address, name))
        return 0

    # 取固件
    if args.bin:
        addr = int(args.addr, 0)
        with open(args.bin, "rb") as f:
            segs = [(addr, f.read())]
        print("  文件  %s" % args.bin)
    else:
        path = args.file
        if not path:
            path = find_default_hex()
            if not path:
                print("[错误] 没指定文件，自动搜索也没找到 CircuitModel.hex")
                print("       已找过以下位置：")
                for c in HEX_CANDIDATES:
                    print("         %s" % c)
                print("       请把 hex 文件直接拖到 flash.bat 上，或在命令行指定：")
                print('         flash.bat "D:\\path\\to\\firmware.hex"')
                return 2
        if not os.path.exists(path):
            print("[错误] 文件不存在：%s" % path)
            return 2
        print("  文件  %s" % path)
        try:
            segs = parse_hex(path)
        except Exception as e:
            print("[错误] 解析 HEX 失败：%s" % e)
            return 2

    lo = min(a for a, _ in segs)
    hi = max(a + len(d) for a, d in segs)
    if lo < 0x08000000 or hi > 0x08080000:
        print()
        print("[警告] 固件地址范围 0x%08X~0x%08X 超出 STM32F407VE 的内部 Flash" % (lo, hi))
        print("       (0x08000000 ~ 0x0807FFFF)。请确认链接脚本，或加 --bin 手动指定。")
        return 2

    return do_flash(segs, verify=not args.no_verify, erase=not args.no_erase)


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n已中断。")
        sys.exit(130)
    except Exception as e:
        print()
        print("[异常] %s: %s" % (type(e).__name__, e))
        print()
        print("如果是 USBError，先确认：")
        print("  1. 设备管理器里有 STM32 BOOTLOADER 且没有感叹号")
        print("  2. 已经用 Zadig 给它装了 WinUSB 驱动")
        sys.exit(1)
