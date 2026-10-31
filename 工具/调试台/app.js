/* ============================================================
   电路模型探究装置 —— 调试台
   串口：Web Serial API      烧录：WebUSB + DfuSe
   需要 Chromium 内核（Edge / Chrome）且运行在安全上下文
   ============================================================ */
'use strict';

/* ------------------------------------------------------------ 工具函数 */
const $ = (id) => document.getElementById(id);
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
const hex = (n, w = 2) => n.toString(16).toUpperCase().padStart(w, '0');
const pad2 = (n) => String(n).padStart(2, '0');
const now = () => {
  const d = new Date();
  return `${pad2(d.getHours())}:${pad2(d.getMinutes())}:${pad2(d.getSeconds())}.${String(d.getMilliseconds()).padStart(3, '0')}`;
};
const human = (n) => (n >= 1024 ? (n / 1024).toFixed(1) + ' KB' : n + ' B');

/* ------------------------------------------------------------ 顶栏 */
function switchTab(name) {
  document.querySelectorAll('.tab').forEach((b) => b.classList.toggle('active', b.dataset.tab === name));
  document.querySelectorAll('.panel').forEach((p) => p.classList.toggle('active', p.id === name));
  if (history.replaceState) history.replaceState(null, '', '#' + name);
}

document.querySelectorAll('.tab').forEach((b) => {
  b.addEventListener('click', () => switchTab(b.dataset.tab));
});

/* 环境能力检测 */
(function checkEnv() {
  const badge = $('envBadge');
  const hasSerial = 'serial' in navigator;
  const hasUsb = 'usb' in navigator;
  const secure = window.isSecureContext;

  if (!secure) {
    badge.textContent = '非安全上下文，需用 启动.bat 打开';
    badge.classList.add('bad');
    badge.title = '浏览器只允许在 https 或 localhost 下访问串口与 USB。直接双击 index.html 不行，请双击 启动.bat。';
    return;
  }
  if (!hasSerial && !hasUsb) {
    badge.textContent = '当前浏览器不支持 Web Serial / WebUSB';
    badge.classList.add('bad');
    badge.title = '请用 Edge 或 Chrome 打开。Firefox 不支持这两个 API。';
    return;
  }
  const parts = [];
  if (hasSerial) parts.push('串口就绪');
  if (hasUsb) parts.push('USB 就绪');
  badge.textContent = parts.join(' · ');
})();

/* ============================================================
   一、串口调试
   ============================================================ */
const S = {
  port: null,
  reader: null,
  writer: null,
  reading: false,
  bytes: 0,
  pending: '',
  lines: 0,
  // 必须复用同一个 decoder 并开 stream 模式：串口每次 read() 只给一块字节，
  // 一个汉字的三字节可能被切在两块之间，逐块新建 decoder 会把后半截当成非法字节。
  decoder: new TextDecoder('utf-8', { fatal: false }),
};

const term = $('term');
const portSel = $('portSel');

function setLed(el, cls, text) {
  el.classList.remove('on', 'busy', 'err');
  if (cls) el.classList.add(cls);
  el.querySelector('span').textContent = text;
}

function termLine(text, cls = '') {
  const wrap = document.createElement('span');
  wrap.className = 'l ' + cls;
  if ($('chkTime').checked && cls !== 'tx') {
    const ts = document.createElement('span');
    ts.className = 'ts';
    ts.textContent = '[' + now().slice(0, 8) + '] ';
    wrap.appendChild(ts);
  } else if (cls === 'tx') {
    const ts = document.createElement('span');
    ts.className = 'ts';
    ts.textContent = '[' + now().slice(0, 8) + '] ';
    wrap.appendChild(ts);
  }
  const body = document.createElement('span');
  body.textContent = text;
  wrap.appendChild(body);
  term.appendChild(wrap);
  S.lines++;

  if (S.lines > 3000) {
    for (let i = 0; i < 500; i++) term.firstChild && term.removeChild(term.firstChild);
    S.lines -= 500;
  }
  term.scrollTop = term.scrollHeight;
}

function termRaw(text, cls = 'rx') {
  if (!text) return;
  S.pending += text;
  const parts = S.pending.split(/\r\n|\r|\n/);
  S.pending = parts.pop();
  for (const p of parts) termLine(p, cls);
  if (S.pending.length > 2000) {
    termLine(S.pending, cls);
    S.pending = '';
  }
}

function updateCount() {
  $('chipCount').textContent = human(S.bytes);
}

async function refreshPortList(selectFirst) {
  const ports = await navigator.serial.getPorts();
  portSel.innerHTML = '';
  if (!ports.length) {
    const o = document.createElement('option');
    o.value = '';
    o.textContent = '未授权任何串口';
    portSel.appendChild(o);
    return ports;
  }
  ports.forEach((p, i) => {
    const info = p.getInfo();
    const o = document.createElement('option');
    o.value = String(i);
    o.textContent = info.usbVendorId
      ? `COM 设备 ${hex(info.usbVendorId, 4)}:${hex(info.usbProductId || 0, 4)}`
      : `串口 #${i + 1}`;
    portSel.appendChild(o);
  });
  S.ports = ports;
  if (selectFirst) portSel.selectedIndex = 0;
  return ports;
}

async function pickPort() {
  try {
    const p = await navigator.serial.requestPort();
    await refreshPortList();
    const ports = await navigator.serial.getPorts();
    const idx = ports.indexOf(p);
    if (idx >= 0) portSel.value = String(idx);
    termLine('已授权串口：' + (p.getInfo().usbVendorId
      ? `${hex(p.getInfo().usbVendorId, 4)}:${hex(p.getInfo().usbProductId || 0, 4)}`
      : '未命名设备'), 'sys');
  } catch (e) {
    if (e.name !== 'NotFoundError') termLine('选择串口失败：' + e.message, 'err');
  }
}

async function openSerial() {
  const ports = S.ports && S.ports.length ? S.ports : await refreshPortList();
  const idx = Number(portSel.value);
  if (!ports.length || Number.isNaN(idx)) {
    termLine('先点「选择串口」，在弹窗里挑一个设备。', 'err');
    return;
  }
  const port = ports[idx];
  const baud = Number($('baudSel').value);

  try {
    await port.open({
      baudRate: baud,
      dataBits: 8,
      stopBits: 1,
      parity: 'none',
      flowControl: 'none',
      bufferSize: 8192,
    });
  } catch (e) {
    termLine('打开失败：' + e.message, 'err');
    if (String(e.message).includes('Failed to open')) {
      termLine('提示：端口可能被别的程序（串口助手、Keil 的 UART 窗口）占用了，先关掉它。', 'sys');
    }
    setLed($('serialLed'), 'err', '打开失败');
    return;
  }

  S.port = port;
  S.writer = port.writable.getWriter();
  S.reading = true;
  S.bytes = 0;
  S.decoder = new TextDecoder('utf-8', { fatal: false });
  updateCount();

  $('chipPort').textContent = portSel.options[portSel.selectedIndex]?.textContent || '串口';
  $('chipBaud').textContent = baud + ' 8N1';
  setLed($('serialLed'), 'on', '已连接');
  $('btnOpen').textContent = '关闭串口';
  $('btnOpen').classList.remove('primary');
  $('btnOpen').classList.add('danger');
  $('btnPickPort').disabled = true;
  portSel.disabled = true;
  $('baudSel').disabled = true;
  termLine(`串口已打开：${baud} 8N1`, 'sys');

  readLoop(port);
}

async function readLoop(port) {
  while (port.readable && S.reading) {
    let reader;
    try {
      reader = port.readable.getReader();
      S.reader = reader;
      while (true) {
        const { value, done } = await reader.read();
        if (done) break;
        if (value && value.length) {
          S.bytes += value.length;
          updateCount();
          termRaw(S.decoder.decode(value, { stream: true }), 'rx');
        }
      }
    } catch (e) {
      if (S.reading) termLine('读取中断：' + e.message, 'err');
    } finally {
      if (reader) {
        try { reader.releaseLock(); } catch (_) {}
      }
      S.reader = null;
    }
  }
}

async function closeSerial() {
  S.reading = false;
  try { if (S.reader) await S.reader.cancel(); } catch (_) {}
  try { if (S.writer) { S.writer.releaseLock(); S.writer = null; } } catch (_) {}
  try { if (S.port) await S.port.close(); } catch (_) {}
  S.port = null;
  // 把 decoder 里可能残留的半个字符冲出来
  const tail = S.decoder.decode();
  if (tail) termRaw(tail, 'rx');
  if (S.pending) { termLine(S.pending, 'rx'); S.pending = ''; }

  setLed($('serialLed'), '', '未连接');
  $('btnOpen').textContent = '打开串口';
  $('btnOpen').classList.add('primary');
  $('btnOpen').classList.remove('danger');
  $('btnPickPort').disabled = false;
  portSel.disabled = false;
  $('baudSel').disabled = false;
  termLine('串口已关闭', 'sys');
}

async function sendText(text, withNewline = true) {
  if (!S.writer) {
    termLine('串口没打开，先点「打开串口」。', 'err');
    return false;
  }
  const payload = withNewline ? text + '\r\n' : text;
  try {
    await S.writer.write(new TextEncoder().encode(payload));
    termLine('> ' + text, 'tx');
    return true;
  } catch (e) {
    termLine('发送失败：' + e.message, 'err');
    return false;
  }
}

/* ---- 串口事件绑定 ---- */
$('btnPickPort').addEventListener('click', pickPort);

$('btnOpen').addEventListener('click', async () => {
  if (S.port) await closeSerial();
  else await openSerial();
});

$('btnSend').addEventListener('click', () => {
  const v = $('sendInput').value;
  if (!v.trim()) return;
  sendText(v, $('chkNewline').checked);
  $('sendInput').value = '';
  $('sendInput').focus();
});

$('sendInput').addEventListener('keydown', (e) => {
  if (e.key === 'Enter') { e.preventDefault(); $('btnSend').click(); }
});

$('btnClear').addEventListener('click', () => {
  term.innerHTML = '';
  S.lines = 0;
  S.pending = '';
  S.bytes = 0;
  updateCount();
});

$('btnSaveLog').addEventListener('click', () => {
  const txt = [...term.querySelectorAll('.l')].map((l) => l.textContent).join('\n');
  const blob = new Blob([txt], { type: 'text/plain;charset=utf-8' });
  const a = document.createElement('a');
  a.href = URL.createObjectURL(blob);
  a.download = `串口日志-${new Date().toISOString().slice(0, 19).replace(/[:T]/g, '')}.txt`;
  a.click();
  setTimeout(() => URL.revokeObjectURL(a.href), 3000);
});

document.querySelectorAll('.cmd-btn[data-cmd]').forEach((b) => {
  b.addEventListener('click', () => sendText(b.dataset.cmd, true));
});

$('btnFreq').addEventListener('click', () => sendText('F' + $('inFreq').value, true));
$('btnAmp').addEventListener('click', () => sendText('A' + $('inAmp').value, true));
$('btnK').addEventListener('click', () => sendText('K' + $('inK').value, true));
$('btnC').addEventListener('click', () => sendText('C' + $('inC').value, true));

document.querySelectorAll('.preset[data-freq]').forEach((b) => {
  b.addEventListener('click', () => {
    $('inFreq').value = b.dataset.freq;
    sendText('F' + b.dataset.freq, true);
  });
});

document.querySelectorAll('.preset[data-amp]').forEach((b) => {
  b.addEventListener('click', () => {
    $('inAmp').value = b.dataset.amp;
    sendText('A' + b.dataset.amp, true);
  });
});

$('btnSweep').addEventListener('click', async () => {
  if (!S.writer) { termLine('串口没打开。', 'err'); return; }
  for (const f of [100, 1000, 10000]) {
    await sendText('F' + f, true);
    await sleep(350);
    await sendText('H', true);
    await sleep(350);
  }
});

$('btnBanner').addEventListener('click', () => sendText('?', true));

if ('serial' in navigator) {
  navigator.serial.addEventListener('disconnect', (e) => {
    if (S.port && e.target === S.port) {
      termLine('串口设备被拔出。', 'err');
      closeSerial();
    }
  });
  refreshPortList(false).catch(() => {});
}

/* 串口终端初始提示 */
termLine('未连接。先点「选择串口」授权设备，再点「打开串口」。', 'sys');
termLine('接线：USB-TTL 的 TX 接 PA3，RX 接 PA2，GND 共地；波特率 115200 8N1。', 'sys');
termLine('板子正常上电后会自己打出三行启动横幅，看到就说明固件在跑。', 'sys');
termLine('', 'sys');

/* ============================================================
   二、DFU 烧录（WebUSB + DfuSe）
   ============================================================ */

const DFU = {
  VID: 0x0483,
  PID: 0xdf11,
  DNLOAD: 0x01,
  UPLOAD: 0x02,
  GETSTATUS: 0x03,
  CLRSTATUS: 0x04,
  ABORT: 0x06,
  DFUSE_SET_ADDRESS: 0x21,
  DFUSE_ERASE: 0x41,
  DEFAULT_TRANSFER: 2048,
};

const ST_NAME = {
  0: 'appIDLE', 1: 'appDETACH', 2: 'dfuIDLE', 3: 'dfuDNLOAD-SYNC',
  4: 'dfuDNBUSY', 5: 'dfuDNLOAD-IDLE', 6: 'dfuMANIFEST-SYNC', 7: 'dfuMANIFEST',
  8: 'dfuMANIFEST-WAIT-RESET', 9: 'dfuUPLOAD-IDLE', 10: 'dfuERROR',
};

const ERR_NAME = {
  0x00: 'OK', 0x01: 'errTARGET', 0x02: 'errFILE', 0x03: 'errWRITE',
  0x04: 'errERASE', 0x05: 'errCHECK_ERASED', 0x06: 'errPROG', 0x07: 'errVERIFY',
  0x08: 'errADDRESS', 0x09: 'errNOTDONE', 0x0A: 'errFIRMWARE', 0x0B: 'errVENDOR',
  0x0C: 'errUSBR', 0x0D: 'errPOR', 0x0E: 'errUNKNOWN', 0x0F: 'errSTALLEDPKT',
};

/* STM32F407VE 内部 Flash 扇区表 */
const SECTORS = (() => {
  const s = [];
  for (let i = 0; i < 4; i++) s.push([0x08000000 + i * 0x4000, 0x4000]);
  s.push([0x08010000, 0x10000]);
  for (let i = 0; i < 7; i++) s.push([0x08020000 + i * 0x20000, 0x20000]);
  return s;
})();

const U = { dev: null, iface: 0, transfer: DFU.DEFAULT_TRANSFER, busy: false };
let FW = { segs: null, name: '', total: 0 };

/* ---- 烧录日志 ---- */
const flog = $('flog');

function log(text, cls = '') {
  const wrap = document.createElement('span');
  wrap.className = 'l ' + cls;
  const ts = document.createElement('span');
  ts.className = 'ts';
  ts.textContent = '[' + now().slice(0, 8) + '] ';
  wrap.appendChild(ts);
  const body = document.createElement('span');
  body.textContent = text;
  wrap.appendChild(body);
  flog.appendChild(wrap);
  flog.scrollTop = flog.scrollHeight;
}

function setKv(id, value, empty) {
  const el = $(id);
  el.textContent = value;
  el.classList.toggle('empty', !!empty);
}

/* ---- 连接设备 ---- */
async function connectUsb() {
  if (!('usb' in navigator)) {
    log('当前浏览器不支持 WebUSB，请用 Edge 或 Chrome。', 'err');
    return;
  }
  if (!window.isSecureContext) {
    log('当前页面不是安全上下文，浏览器拒绝访问 USB。请双击 启动.bat 打开。', 'err');
    return;
  }
  if (U.dev) { await disconnectUsb(); return; }

  let dev;
  try {
    dev = await navigator.usb.requestDevice({
      filters: [{ vendorId: DFU.VID, productId: DFU.PID }],
    });
  } catch (e) {
    if (e.name === 'NotFoundError') {
      log('没有选中设备。弹窗里要选 STM32 BOOTLOADER（0483:DF11）。', 'warn');
      log('如果弹窗里根本没这个设备：确认 BOOT0 已接 3V3 且按过复位，设备管理器里能看到 STM32 BOOTLOADER。', 'dim');
    } else {
      log('选择设备失败：' + e.message, 'err');
    }
    return;
  }

  try {
    await dev.open();
    if (!dev.configuration) await dev.selectConfiguration(1);

    let ifaceNo = null;
    for (const intf of dev.configuration.interfaces) {
      for (const alt of intf.alternates) {
        if (alt.interfaceClass === 0xFE && alt.interfaceSubClass === 0x01) {
          ifaceNo = intf.interfaceNumber;
          break;
        }
      }
      if (ifaceNo !== null) break;
    }
    if (ifaceNo === null) {
      for (const intf of dev.configuration.interfaces) {
        for (const alt of intf.alternates) {
          if (alt.interfaceClass === 0xFE) { ifaceNo = intf.interfaceNumber; break; }
        }
        if (ifaceNo !== null) break;
      }
    }
    if (ifaceNo === null) {
      throw new Error('设备不是 DFU 类接口，可能驱动不对或不是 STM32 bootloader');
    }

    await dev.claimInterface(ifaceNo);
    U.dev = dev;
    U.iface = ifaceNo;
    U.transfer = await readTransferSize();
    U.busy = false;

    setKv('usbName', dev.productName || 'STM32 BOOTLOADER', false);
    setKv('usbIds', `${hex(dev.vendorId, 4)}:${hex(dev.productId, 4)}`, false);
    setKv('usbVer', `${(dev.deviceVersionMajor || 0)}.${(dev.deviceVersionMinor || 0)}`, false);
    setKv('usbIface', `接口 ${U.iface} / 块 ${U.transfer} B`, false);
    $('btnUsb').textContent = '断开设备';
    $('btnUsb').classList.remove('primary');
    $('btnUsb').classList.add('danger');
    updateFlashBtn();

    log(`设备已连接：${dev.productName || 'STM32 BOOTLOADER'}`, 'ok');
    log(`接口 ${U.iface}，传输块 ${U.transfer} 字节`, 'dim');

    const st = await dfuStatus();
    setKv('usbState', `${ST_NAME[st.state] || '?'} (${st.state})`, false);
    if (st.state === 10) {
      log(`芯片当前在错误态 0x${hex(st.status)} ${ERR_NAME[st.status] || ''}，将尝试清除。`, 'warn');
      await ensureReady();
    }
  } catch (e) {
    log('打开设备失败：' + e.message, 'err');
    if (String(e.message).includes('Access denied') || String(e.message).includes('claim')) {
      log('这条报错基本都是驱动或占用问题：', 'warn');
      log('  1. 该设备要绑 WinUSB 驱动（Zadig，选 0483 DF11）', 'dim');
      log('  2. 关掉 STM32CubeProgrammer 等可能独占设备的程序', 'dim');
      log('  3. 若之前用 libusbK 绑过，重装成 WinUSB', 'dim');
    }
    try { await dev.close(); } catch (_) {}
    U.dev = null;
  }
}

async function disconnectUsb() {
  if (!U.dev) return;
  try { await U.dev.releaseInterface(U.iface); } catch (_) {}
  try { await U.dev.close(); } catch (_) {}
  U.dev = null;
  setKv('usbName', '未连接', true);
  setKv('usbIds', '—', true);
  setKv('usbVer', '—', true);
  setKv('usbIface', '—', true);
  setKv('usbState', '—', true);
  $('btnUsb').textContent = '连接 DFU 设备（0483:DF11）';
  $('btnUsb').classList.add('primary');
  $('btnUsb').classList.remove('danger');
  updateFlashBtn();
  log('设备已断开。', 'dim');
}

async function readTransferSize() {
  try {
    const r = await U.dev.controlTransferIn({
      requestType: 'standard', recipient: 'interface',
      request: 0x06, value: 0x2100, index: U.iface,
    }, 9);
    if (r.data && r.data.byteLength >= 7) {
      const size = r.data.getUint8(5) | (r.data.getUint8(6) << 8);
      if (size >= 64 && size <= 8192) return size;
    }
  } catch (_) {}
  return DFU.DEFAULT_TRANSFER;
}

/* ---- DFU 底层 ---- */
async function dfuStatus() {
  const r = await U.dev.controlTransferIn({
    requestType: 'class', recipient: 'interface',
    request: DFU.GETSTATUS, value: 0, index: U.iface,
  }, 6);
  const d = r.data;
  return {
    status: d.getUint8(0),
    poll: d.getUint8(1) | (d.getUint8(2) << 8) | (d.getUint8(3) << 16),
    state: d.getUint8(4),
  };
}

async function dfuOut(request, value, data) {
  return U.dev.controlTransferOut({
    requestType: 'class', recipient: 'interface',
    request, value, index: U.iface,
  }, data || new Uint8Array(0));
}

async function clearStatus() {
  try { await dfuOut(DFU.CLRSTATUS, 0, null); } catch (_) {}
}

async function ensureReady() {
  let st = await dfuStatus();
  if (st.state === 10) {
    await clearStatus();
    await sleep(50);
    st = await dfuStatus();
    if (st.state === 10) {
      throw new Error(`芯片卡在错误态清不掉（0x${hex(st.status)} ${ERR_NAME[st.status] || '?'}）。按一下板子的 NRST 再试。`);
    }
  }
  return st.state;
}

async function waitDone(timeoutMs = 25000, label = '') {
  const t0 = Date.now();
  let st = await dfuStatus();
  while (st.state === 4) {
    await sleep(Math.max(st.poll, 5));
    st = await dfuStatus();
    if (Date.now() - t0 > timeoutMs) {
      throw new Error(`等芯片写 Flash 超时${label ? '（' + label + '）' : ''}，状态一直 busy`);
    }
  }
  if (st.state === 10) {
    throw new Error(`芯片报错 0x${hex(st.status)} ${ERR_NAME[st.status] || '?'}。常见原因：写保护、地址非法、扇区没擦`);
  }
  return st;
}

async function setAddress(addr) {
  const buf = new Uint8Array(5);
  buf[0] = DFU.DFUSE_SET_ADDRESS;
  new DataView(buf.buffer).setUint32(1, addr, true);
  await dfuOut(DFU.DNLOAD, 0, buf);
  await waitDone(8000, 'set address');
}

async function erasePage(addr) {
  const buf = new Uint8Array(5);
  buf[0] = DFU.DFUSE_ERASE;
  new DataView(buf.buffer).setUint32(1, addr, true);
  await dfuOut(DFU.DNLOAD, 0, buf);
  await waitDone(45000, 'erase');
}

async function writeBlock(block, data) {
  await dfuOut(DFU.DNLOAD, block, data);
  await waitDone(20000, 'block ' + block);
}

async function leaveDfu() {
  try { await dfuOut(DFU.DNLOAD, 0, null); } catch (_) { return; }
  const t0 = Date.now();
  while (Date.now() - t0 < 20000) {
    try {
      const st = await dfuStatus();
      if ([6, 7, 8].includes(st.state)) return;
    } catch (_) { return; }
    await sleep(50);
  }
}

/* ---- HEX 解析 ---- */
function parseHex(text) {
  const mem = new Map();
  let base = 0;
  const lines = text.split(/\r?\n/);

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i].trim();
    if (!line) continue;
    if (line[0] !== ':') throw new Error(`第 ${i + 1} 行不是 HEX 记录：${line.slice(0, 40)}`);

    const raw = line.slice(1);
    if (raw.length % 2 !== 0) throw new Error(`第 ${i + 1} 行十六进制长度不是偶数`);
    const body = new Uint8Array(raw.length / 2);
    for (let j = 0; j < body.length; j++) {
      const v = parseInt(raw.substr(j * 2, 2), 16);
      if (Number.isNaN(v)) throw new Error(`第 ${i + 1} 行十六进制非法`);
      body[j] = v;
    }
    if (body.length < 5) throw new Error(`第 ${i + 1} 行太短`);

    const count = body[0];
    const addr = (body[1] << 8) | body[2];
    const rtype = body[3];
    const data = body.slice(4, 4 + count);

    let sum = 0;
    for (let j = 0; j < body.length - 1; j++) sum += body[j];
    if (((sum & 0xFF) + body[body.length - 1]) & 0xFF) {
      throw new Error(`第 ${i + 1} 行校验和错误（文件可能损坏）`);
    }

    if (rtype === 0x00) {
      for (let j = 0; j < data.length; j++) mem.set(base + addr + j, data[j]);
    } else if (rtype === 0x01) {
      break;
    } else if (rtype === 0x02) {
      base = ((data[0] << 8) | data[1]) << 4;
    } else if (rtype === 0x04) {
      base = ((data[0] << 8) | data[1]) << 16;
    } else if (rtype === 0x03 || rtype === 0x05) {
      /* 起始地址记录，忽略 */
    } else {
      throw new Error(`第 ${i + 1} 行未知记录类型 0x${hex(rtype)}`);
    }
  }

  if (!mem.size) throw new Error('HEX 里没有任何数据');

  const addrs = [...mem.keys()].sort((a, b) => a - b);
  const segs = [];
  let start = addrs[0];
  let prev = addrs[0];
  let buf = [mem.get(addrs[0])];

  for (let k = 1; k < addrs.length; k++) {
    const a = addrs[k];
    if (a === prev + 1) {
      buf.push(mem.get(a));
    } else {
      segs.push([start, Uint8Array.from(buf)]);
      start = a;
      buf = [mem.get(a)];
    }
    prev = a;
  }
  segs.push([start, Uint8Array.from(buf)]);
  return segs;
}

/* ---- 文件载入 ---- */
async function loadFile(file) {
  try {
    const text = await file.text();
    const segs = parseHex(text);
    const total = segs.reduce((s, [, d]) => s + d.length, 0);
    const lo = Math.min(...segs.map(([a]) => a));
    const hi = Math.max(...segs.map(([a, d]) => a + d.length));

    if (lo < 0x08000000 || hi > 0x08080000) {
      log(`警告：地址范围 0x${hex(lo, 8)}~0x${hex(hi, 8)} 超出 STM32F407VE 内部 Flash（0x08000000~0x0807FFFF）。`, 'warn');
    }

    FW = { segs, name: file.name, total };
    setKv('fileInfo', file.name, false);
    setKv('fileRange', `0x${hex(lo, 8)} ~ 0x${hex(hi, 8)}`, false);
    setKv('fileSize', `${human(total)}（${total} 字节）`, false);
    setKv('fileSegs', `${segs.length} 段` + (segs.length > 1 ? '：' + segs.map(([a, d]) => `0x${hex(a, 8)}/${d.length}B`).join('，') : ''), false);

    const dz = $('dropZone');
    dz.classList.add('has-file');
    dz.innerHTML = `<b>${file.name}</b><span>${human(total)} · ${segs.length} 段 · 点击可换一个</span>`;

    log(`已载入 ${file.name}：${human(total)}，${segs.length} 段`, 'ok');
    for (const [a, d] of segs) log(`  0x${hex(a, 8)}  ${human(d.length)}  ${d.length} 字节`, 'dim');
    updateFlashBtn();
  } catch (e) {
    log('解析 HEX 失败：' + e.message, 'err');
    FW = { segs: null, name: '', total: 0 };
    updateFlashBtn();
  }
}

function updateFlashBtn() {
  $('btnFlash').disabled = !(U.dev && FW.segs && !U.busy);
}

/* ---- 烧录主流程 ---- */
async function doFlash() {
  if (!U.dev || !FW.segs) return;
  U.busy = true;
  updateFlashBtn();
  $('btnUsb').disabled = true;

  const wrap = $('progWrap');
  const bar = $('progBar');
  wrap.className = 'progress';
  bar.style.width = '0%';
  $('progText').textContent = '准备中';
  $('progPct').textContent = '0%';

  const t0 = Date.now();

  try {
    log('—— 开始烧录 ——', 'step');
    const state = await ensureReady();
    setKv('usbState', `${ST_NAME[state] || '?'} (${state})`, false);
    log(`状态机 ${ST_NAME[state] || '?'}，可以开始。`, 'dim');

    /* 擦除 */
    log('擦除：', 'step');
    let erased = 0;
    for (const [segAddr, segData] of FW.segs) {
      const end = segAddr + segData.length;
      for (const [secAddr, secSize] of SECTORS) {
        if (secAddr + secSize <= segAddr || secAddr >= end) continue;
        await erasePage(secAddr);
        erased++;
        log(`  擦除扇区 0x${hex(secAddr, 8)}（${human(secSize)}）`, 'dim');
      }
    }
    log(`擦除完成，共 ${erased} 个扇区。`, 'ok');

    /* 写入 */
    log('写入：', 'step');
    let written = 0;
    for (const [segAddr, segData] of FW.segs) {
      await setAddress(segAddr);
      let block = 2;
      let off = 0;
      while (off < segData.length) {
        const chunk = segData.slice(off, off + U.transfer);
        await writeBlock(block, chunk);
        off += chunk.length;
        block++;
        written += chunk.length;

        const pct = (written * 100) / FW.total;
        bar.style.width = pct.toFixed(1) + '%';
        $('progPct').textContent = pct.toFixed(0) + '%';
        $('progText').textContent = `${human(written)} / ${human(FW.total)}`;
        await sleep(0);
      }
    }

    /* 收尾 */
    log('结束传输，等芯片进入 manifest…', 'dim');
    await leaveDfu();

    const dt = (Date.now() - t0) / 1000;
    const speed = FW.total / 1024 / Math.max(dt, 0.01);

    wrap.classList.add('done');
    bar.style.width = '100%';
    $('progPct').textContent = '100%';
    $('progText').textContent = `完成 · ${dt.toFixed(1)} 秒 · ${speed.toFixed(1)} KB/s`;

    log(`烧录完成：${FW.total} 字节，${dt.toFixed(1)} 秒（${speed.toFixed(1)} KB/s）`, 'ok');
    log('每一块都由芯片返回状态确认；ST bootloader 在 dfuDNLOAD-IDLE 下不接受回读，因此不做回读比对。', 'dim');
    log('', '');
    log('接下来：断电 → 拔掉 BOOT0 那根线 → 重新上电 → 复位。', 'warn');
    log('程序会立刻运行，切到「串口调试」应能看到三行启动横幅。', 'warn');

    U.busy = false;
    $('btnUsb').disabled = false;
    try {
      await disconnectUsb();
    } catch (_) {}
  } catch (e) {
    wrap.classList.add('fail');
    $('progText').textContent = '失败：' + e.message;
    log('烧录中断：' + e.message, 'err');
    U.busy = false;
    $('btnUsb').disabled = false;
    updateFlashBtn();
  }
}

/* ---- 烧录页事件 ---- */
$('btnUsb').addEventListener('click', connectUsb);
$('btnFlash').addEventListener('click', doFlash);

$('dropZone').addEventListener('click', () => $('fileInput').click());
$('fileInput').addEventListener('change', (e) => {
  if (e.target.files[0]) loadFile(e.target.files[0]);
});

['dragenter', 'dragover'].forEach((ev) => {
  $('dropZone').addEventListener(ev, (e) => {
    e.preventDefault();
    $('dropZone').classList.add('over');
  });
});
['dragleave', 'drop'].forEach((ev) => {
  $('dropZone').addEventListener(ev, (e) => {
    e.preventDefault();
    $('dropZone').classList.remove('over');
  });
});
$('dropZone').addEventListener('drop', (e) => {
  const f = e.dataTransfer.files[0];
  if (f) loadFile(f);
});

$('btnClearLog').addEventListener('click', () => { flog.innerHTML = ''; });

$('btnSaveLog2').addEventListener('click', () => {
  const txt = [...flog.querySelectorAll('.l')].map((l) => l.textContent).join('\n');
  const blob = new Blob([txt], { type: 'text/plain;charset=utf-8' });
  const a = document.createElement('a');
  a.href = URL.createObjectURL(blob);
  a.download = `烧录日志-${new Date().toISOString().slice(0, 19).replace(/[:T]/g, '')}.txt`;
  a.click();
  setTimeout(() => URL.revokeObjectURL(a.href), 3000);
});

if ('usb' in navigator) {
  navigator.usb.addEventListener('disconnect', (e) => {
    if (U.dev && e.device === U.dev) {
      log('设备已拔出。', 'warn');
      U.dev = null;
      setKv('usbName', '已拔出', true);
      setKv('usbState', '—', true);
      $('btnUsb').textContent = '连接 DFU 设备（0483:DF11）';
      $('btnUsb').classList.add('primary');
      $('btnUsb').classList.remove('danger');
      updateFlashBtn();
    }
  });
}

/* ---- 启动提示 ---- */
log('调试台就绪。', 'dim');
log('步骤：BOOT0 接 3V3 → 插 Type-C → 点上方按钮选设备 → 拖入 hex → 开始烧录。', 'dim');
if (!('usb' in navigator)) {
  log('当前浏览器没有 WebUSB，烧录页不可用。请用 Edge / Chrome。', 'err');
}

/* ---- 支持 #flash / #serial 直达 ---- */
(function initTab() {
  const h = location.hash.replace('#', '');
  if (h === 'flash' || h === 'serial') switchTab(h);
})();
