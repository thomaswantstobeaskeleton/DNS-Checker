# -*- coding: utf-8 -*-
# dns_speed_test.py — Complete DNS Speed Test Application
# Eva-Dark color scheme (BallonsTranslator-Pro)

import csv
import ctypes
import os
import re
import socket
import struct
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

from PyQt5.QtCore import (
    QPoint,
    QRect,
    QSize,
    Qt,
    QThread,
    QTimer,
    pyqtSignal,
)
from PyQt5.QtGui import (
    QColor,
    QCursor,
    QFont,
    QPalette,
)
from PyQt5.QtWidgets import (
    QAbstractItemView,
    QAction,
    QApplication,
    QCheckBox,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFileDialog,
    QFormLayout,
    QFrame,
    QGroupBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QMenu,
    QMenuBar,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QSizePolicy,
    QSpinBox,
    QSplitter,
    QStatusBar,
    QTableWidget,
    QTableWidgetItem,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

# ── dnspython optional import ──────────────────────────────────────────────
try:
    import dns.message
    import dns.name
    import dns.query
    import dns.rdatatype
    import dns.resolver

    HAS_DNSPYTHON = True
except ImportError:
    HAS_DNSPYTHON = False

# ══════════════════════════════════════════════════════════════════════════════
#  COLORS
# ══════════════════════════════════════════════════════════════════════════════
COLORS: Dict[str, str] = {
    "bg_main": "#282c34",
    "bg_panel": "#21252b",
    "bg_input": "#191d24",
    "border": "#535671",
    "text": "#8e99b1",
    "text_title": "#8c97af",
    "accent": "#1E93E5",
    "accent_rgba20": "rgba(30, 147, 229, 51)",
    "accent_rgba80": "rgba(30, 147, 229, 204)",
    "scrollbar": "rgba(127,127,127,100)",
    "scrollbar_hover": "rgba(127,127,127,200)",
    "hover": "#cad7ed",
    "selected": "#cad7ed",
    "close_hover": "#E81123",
    "good": "#4ec94e",
    "ok": "#e6a817",
    "bad": "#e05252",
    "text_bright": "#c8cdd8",
    "row_alt": "#1e2229",
    "row_hover": "#2a2f3a",
    "row_selected": "#1a3a5c",
    "sidebar_text": "#6b7491",
    "bg_button": "#21252b",
}

# ══════════════════════════════════════════════════════════════════════════════
#  DNS PROVIDERS
# ══════════════════════════════════════════════════════════════════════════════
DNS_PROVIDERS: Dict[str, Tuple[str, str]] = {
    # ── Global ────────────────────────────────────────────────────────────────
    "1.1.1.1": ("Cloudflare", "Global"),
    "1.0.0.1": ("Cloudflare", "Global"),
    "8.8.8.8": ("Google", "Global"),
    "8.8.4.4": ("Google", "Global"),
    "9.9.9.9": ("Quad9", "Global"),
    "149.112.112.112": ("Quad9", "Global"),
    "208.67.222.222": ("OpenDNS", "Global"),
    "208.67.220.220": ("OpenDNS", "Global"),
    "94.140.14.14": ("AdGuard", "Global"),
    "94.140.15.15": ("AdGuard", "Global"),
    "76.76.19.19": ("Alternate DNS", "Global"),
    "76.223.122.150": ("Alternate DNS", "Global"),
    "185.228.168.168": ("CleanBrowsing", "Global"),
    "185.228.169.168": ("CleanBrowsing", "Global"),
    "84.200.69.80": ("DNS.WATCH", "Global"),
    "84.200.70.40": ("DNS.WATCH", "Global"),
    "4.2.2.1": ("Level3 / Lumen", "Global"),
    "4.2.2.2": ("Level3 / Lumen", "Global"),
    "4.2.2.3": ("Level3 / Lumen", "Global"),
    "4.2.2.4": ("Level3 / Lumen", "Global"),
    "64.6.64.6": ("Verisign", "Global"),
    "64.6.65.6": ("Verisign", "Global"),
    "77.88.8.8": ("Yandex", "Global"),
    "77.88.8.1": ("Yandex", "Global"),
    "77.88.8.2": ("Yandex Safe", "Global"),
    "77.88.8.3": ("Yandex Safe", "Global"),
    "80.80.80.80": ("Freenom", "Global"),
    "80.80.81.81": ("Freenom", "Global"),
    "199.85.126.10": ("Norton", "Global"),
    "199.85.127.10": ("Norton", "Global"),
    "156.154.70.1": ("Neustar (Sterling VA)", "Global"),
    "156.154.71.1": ("Neustar (Sterling VA)", "Global"),
    "45.90.28.0": ("NextDNS", "Global"),
    "45.90.30.0": ("NextDNS", "Global"),
    "194.242.2.2": ("Mullvad", "Global"),
    "194.242.2.3": ("Mullvad", "Global"),
    "8.26.56.26": ("Comodo", "Global"),
    "8.20.247.20": ("Comodo", "Global"),
    "195.46.39.39": ("SafeDNS", "Global"),
    "195.46.39.40": ("SafeDNS", "Global"),
    "74.82.42.42": ("Hurricane Electric", "Global"),
    "193.110.81.0": ("dns0.eu", "Global"),
    "185.253.5.0": ("dns0.eu", "Global"),
    "176.103.130.130": ("AdGuard Alt", "Global"),
    "176.103.130.131": ("AdGuard Alt", "Global"),
    "185.222.222.222": ("DNS.SB", "Global"),
    "45.11.45.11": ("DNS.SB", "Global"),
    # ── US-East / Virginia ────────────────────────────────────────────────────
    "75.75.75.75": ("Comcast Xfinity", "US-East"),
    "75.75.76.76": ("Comcast Xfinity", "US-East"),
    "68.87.85.98": ("Cox (VA Beach)", "US-East"),
    "68.87.68.168": ("Cox (Hampton)", "US-East"),
    "209.18.47.61": ("Spectrum East", "US-East"),
    "209.18.47.62": ("Spectrum East", "US-East"),
    "71.242.0.12": ("Verizon FiOS East", "US-East"),
    "71.252.0.12": ("Verizon FiOS East", "US-East"),
    "68.94.156.1": ("AT&T US-East", "US-East"),
    "68.94.157.1": ("AT&T US-East", "US-East"),
    "205.171.3.65": ("Lumen US-East", "US-East"),
    "205.171.2.65": ("Lumen US-East", "US-East"),
    "38.132.106.139": ("Windstream East", "US-East"),
    "198.206.14.241": ("Windstream Alt", "US-East"),
    "208.115.120.1": ("Lumos (Virginia)", "US-East"),
    "208.115.120.2": ("Lumos (Virginia)", "US-East"),
    "24.197.138.74": ("RCN (Virginia)", "US-East"),
    "24.197.228.3": ("RCN (Virginia)", "US-East"),
    # ── Gaming-Optimized ──────────────────────────────────────────────────────
    "76.76.2.0": ("ControlD", "Gaming"),
    "76.76.10.0": ("ControlD", "Gaming"),
    "76.76.2.11": ("ControlD Secure", "Gaming"),
    "76.76.10.11": ("ControlD Secure", "Gaming"),
    "1.1.1.2": ("Cloudflare Families", "Gaming"),
    "1.0.0.2": ("Cloudflare Families", "Gaming"),
    "1.1.1.3": ("Cloudflare Secure", "Gaming"),
    "1.0.0.3": ("Cloudflare Secure", "Gaming"),
    "9.9.9.10": ("Quad9 ECS", "Gaming"),
    "149.112.112.10": ("Quad9 ECS", "Gaming"),
    "208.67.222.123": ("OpenDNS Shield", "Gaming"),
    "208.67.220.123": ("OpenDNS Shield", "Gaming"),
    "208.67.222.2": ("Cisco Umbrella", "Gaming"),
    "208.67.220.2": ("Cisco Umbrella", "Gaming"),
    # ── Iran ─────────────────────────────────────────────────────────────────
    "10.202.10.10": ("Shecan", "Iran"),
    "10.202.10.11": ("Shecan", "Iran"),
    "10.202.10.102": ("Shecan Alt", "Iran"),
    "10.202.10.202": ("Shecan Alt", "Iran"),
    "178.22.122.100": ("Electro", "Iran"),
    "185.51.200.2": ("Radar", "Iran"),
    "185.55.224.24": ("403", "Iran"),
    "185.55.225.25": ("403", "Iran"),
    "185.55.226.26": ("403", "Iran"),
    "78.157.42.100": ("Begzar", "Iran"),
    "78.157.42.101": ("Begzar", "Iran"),
    "188.75.80.80": ("Shatel", "Iran"),
    "188.75.90.90": ("Shatel", "Iran"),
    "194.36.174.1": ("PIR DNS", "Iran"),
    "194.36.174.2": ("PIR DNS", "Iran"),
    "5.202.100.100": ("Pars Online", "Iran"),
    "5.202.100.101": ("Pars Online", "Iran"),
    "185.141.168.130": ("Host Iran", "Iran"),
    "185.141.168.131": ("Host Iran", "Iran"),
    "89.237.98.12": ("Fanap", "Iran"),
    "89.237.110.12": ("Fanap", "Iran"),
    "83.147.192.100": ("Arvan", "Iran"),
    "83.147.193.100": ("Arvan", "Iran"),
    "83.147.194.100": ("Arvan", "Iran"),
    "83.147.195.100": ("Arvan", "Iran"),
}

# ══════════════════════════════════════════════════════════════════════════════
#  CONSTANTS
# ══════════════════════════════════════════════════════════════════════════════
# Fortnite's OAuth/login endpoint — direct AWS us-east-1a, no CDN, 3s CNAME TTL.
# This is the very first non-CDN lookup Fortnite makes at launch, making it the
# most representative single domain for measuring Fortnite-relevant DNS latency.
DEFAULT_TEST_DOMAIN = "account-public-service-prod.ol.epicgames.com"
DEFAULT_TIMEOUT = 5
DEFAULT_MAX_WORKERS = 50
DEFAULT_GOOD_THRESHOLD = 100
DEFAULT_OK_THRESHOLD = 300

# Ordered preset list shown in the domain combo-box.
# Each entry: (display_label, hostname, tooltip_detail)
DOMAIN_PRESETS = [
    (
        "Fortnite — Login/Auth  ★",
        "account-public-service-prod.ol.epicgames.com",
        "OAuth2 login & token exchange. First non-CDN call Fortnite makes.\n"
        "Resolves directly to AWS us-east-1a ELBs (no Cloudflare middleman).\n"
        "CNAME TTL=3 s — great for repeated sampling. [RECOMMENDED]",
    ),
    (
        "Fortnite — Matchmaking",
        "fortnite-matchmaking-public-service-live-nac.ol.epicgames.com",
        "NA-Central matchmaking ELB. Bare A-records, no CNAME chain.\n"
        "Resolves to 44.198.247.32 / 44.199.238.103 (AWS us-east-1).\n"
        "Best choice if you care specifically about 'find-a-game' speed.",
    ),
    (
        "Fortnite — Service Discovery",
        "fn-service-discovery-live-public.ogs.live.on.epicgames.com",
        "Resolved at every Fortnite startup for service topology.\n"
        "Direct AWS us-east-1 (3.233.x / 34.197.x / 44.206.x range).",
    ),
    (
        "Fortnite — Presence / Chat",
        "presence-public-service-prod.ol.epicgames.com",
        "Online/offline presence & XMPP chat — active for the entire session.\n"
        "CNAME chain ends in *.ccec.live.use1a.on.epicgames.com (us-east-1a).",
    ),
    (
        "Fortnite — Analytics",
        "datarouter.ol.epicgames.com",
        "Telemetry / analytics — queried continuously during gameplay.\n"
        "Resolves to *.cfef.live.use1a.on.epicgames.com (us-east-1a).",
    ),
    (
        "Epic Games — General",
        "www.epicgames.com",
        "Epic Games main site. Useful as a general Epic CDN baseline.",
    ),
    (
        "Google — General",
        "www.google.com",
        "General-purpose baseline. Not Fortnite-specific.",
    ),
    (
        "Cloudflare — CDN",
        "cloudflare.com",
        "Tests DNS resolution of Cloudflare's own edge nodes.",
    ),
    (
        "Steam — API",
        "api.steampowered.com",
        "Steam API endpoint. Useful for comparing gaming-platform DNS.",
    ),
]

# module-level mutable thresholds (updated by SettingsPanel)
_good_threshold = DEFAULT_GOOD_THRESHOLD
_ok_threshold = DEFAULT_OK_THRESHOLD

PROBES = 3  # number of UDP queries per server for min/avg/max


# ══════════════════════════════════════════════════════════════════════════════
#  DATA CLASS
# ══════════════════════════════════════════════════════════════════════════════
@dataclass
class DNSResult:
    ip: str
    provider: str
    category: str
    min_ms: Optional[float] = None
    avg_ms: Optional[float] = None
    max_ms: Optional[float] = None
    jitter_ms: Optional[float] = None
    status: str = "Pending"

    @property
    def response_ms(self) -> Optional[float]:
        """Alias for avg_ms — used by legacy code."""
        return self.avg_ms

    @property
    def display_response(self) -> str:
        if self.avg_ms is None:
            return "—"
        return f"{self.avg_ms:.2f} ms"

    @property
    def gaming_tier(self) -> str:
        """S/A/B/C/D/F gaming latency tier based on avg_ms."""
        if self.avg_ms is None:
            return "—"
        if self.avg_ms <= 10:
            return "S"
        if self.avg_ms <= 25:
            return "A"
        if self.avg_ms <= 50:
            return "B"
        if self.avg_ms <= 100:
            return "C"
        if self.avg_ms <= 200:
            return "D"
        return "F"

    @property
    def tier_color(self) -> str:
        t = self.gaming_tier
        return {
            "S": "#00e5ff",
            "A": "#4ec94e",
            "B": "#a3e635",
            "C": "#e6a817",
            "D": "#f97316",
            "F": "#e05252",
            "—": "#535671",
        }.get(t, "#535671")

    @property
    def status_color(self) -> str:
        if self.status in ("Timeout", "Error", "Cancelled") or self.avg_ms is None:
            return COLORS["bad"]
        if self.avg_ms <= _good_threshold:
            return COLORS["good"]
        if self.avg_ms <= _ok_threshold:
            return COLORS["ok"]
        return COLORS["bad"]


# ══════════════════════════════════════════════════════════════════════════════
#  NUMERIC TABLE ITEM
# ══════════════════════════════════════════════════════════════════════════════
class NumericTableItem(QTableWidgetItem):
    """QTableWidgetItem that sorts numerically via Qt.UserRole data."""

    def __lt__(self, other: "NumericTableItem") -> bool:
        try:
            my_val = (
                float(self.data(Qt.UserRole))
                if self.data(Qt.UserRole) is not None
                else float("inf")
            )
            other_val = (
                float(other.data(Qt.UserRole))
                if other.data(Qt.UserRole) is not None
                else float("inf")
            )
            return my_val < other_val
        except (TypeError, ValueError):
            return super().__lt__(other)


# ══════════════════════════════════════════════════════════════════════════════
#  DNS TEST WORKER
# ══════════════════════════════════════════════════════════════════════════════
class DNSTestWorker(QThread):
    # ip, min_ms, avg_ms, max_ms, jitter_ms, status
    # all float values are -1.0 on failure
    result_ready = pyqtSignal(str, float, float, float, float, str)
    progress = pyqtSignal(int, int)
    log_message = pyqtSignal(str)
    finished = pyqtSignal()

    def __init__(
        self,
        servers: List[str],
        test_domain: str,
        timeout: int,
        max_workers: int,
    ) -> None:
        super().__init__()
        self.servers = servers
        self.test_domain = test_domain
        self.timeout = timeout
        self.max_workers = max_workers
        self._stop = False

    def stop(self) -> None:
        self._stop = True

    @staticmethod
    def _build_dns_query(domain: str) -> bytes:
        tx_id = 0x1234
        flags = 0x0100
        header = struct.pack("!HHHHHH", tx_id, flags, 1, 0, 0, 0)
        qname = b""
        for label in domain.rstrip(".").split("."):
            enc = label.encode("ascii")
            qname += bytes([len(enc)]) + enc
        qname += b"\x00"
        return header + qname + struct.pack("!HH", 1, 1)

    def _probe(self, ip: str) -> Optional[float]:
        """Single UDP DNS probe. Returns ms or None."""
        try:
            if HAS_DNSPYTHON:
                req = dns.message.make_query(self.test_domain, dns.rdatatype.A)
                t0 = time.perf_counter()
                dns.query.udp(req, ip, timeout=self.timeout)
                return (time.perf_counter() - t0) * 1000.0
            else:
                data = self._build_dns_query(self.test_domain)
                sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                sock.settimeout(self.timeout)
                try:
                    t0 = time.perf_counter()
                    sock.sendto(data, (ip, 53))
                    sock.recvfrom(512)
                    return (time.perf_counter() - t0) * 1000.0
                finally:
                    sock.close()
        except Exception:
            return None

    def test_server(self, ip: str) -> Tuple[str, float, float, float, float, str]:
        """Run PROBES queries against ip. Returns (ip, min, avg, max, jitter, status)."""
        if self._stop:
            return (ip, -1.0, -1.0, -1.0, -1.0, "Cancelled")

        timings: List[float] = []
        for i in range(PROBES):
            if self._stop:
                break
            ms = self._probe(ip)
            if ms is not None:
                timings.append(ms)
            if i < PROBES - 1:
                time.sleep(0.04)  # 40 ms gap between probes

        if not timings:
            return (ip, -1.0, -1.0, -1.0, -1.0, "Timeout")

        mn = min(timings)
        avg = sum(timings) / len(timings)
        mx = max(timings)
        jit = mx - mn
        return (ip, mn, avg, mx, jit, "OK")

    def run(self) -> None:
        total = len(self.servers)
        done = 0
        self.log_message.emit(
            f"Starting test — {total} servers | domain={self.test_domain} | "
            f"probes={PROBES} | timeout={self.timeout}s | workers={self.max_workers}"
        )
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {executor.submit(self.test_server, ip): ip for ip in self.servers}
            for future in as_completed(futures):
                if self._stop:
                    for f in futures:
                        f.cancel()
                    break
                ip, mn, avg, mx, jit, status = future.result()
                done += 1
                self.progress.emit(done, total)
                self.result_ready.emit(ip, mn, avg, mx, jit, status)
                if status == "OK":
                    self.log_message.emit(
                        f"[{done}/{total}] {ip:<20} min={mn:.2f}  avg={avg:.2f}  "
                        f"max={mx:.2f}  jitter={jit:.2f} ms  {status}"
                    )
                else:
                    self.log_message.emit(f"[{done}/{total}] {ip:<20} {status}")

        verb = "complete" if not self._stop else "stopped"
        self.log_message.emit(f"Test {verb} — {done}/{total} servers tested.")
        self.finished.emit()


# ══════════════════════════════════════════════════════════════════════════════
#  WINDOWS UTILITIES
# ══════════════════════════════════════════════════════════════════════════════
_CNW = 0x08000000  # CREATE_NO_WINDOW


def get_active_adapters() -> List[str]:
    """Return a list of active network adapter names."""
    adapters: List[str] = []
    # Try PowerShell first
    try:
        r = subprocess.run(
            [
                "powershell",
                "-NoProfile",
                "-Command",
                "Get-NetAdapter | Where-Object {$_.Status -eq 'Up'} | "
                "Select-Object -ExpandProperty Name",
            ],
            capture_output=True,
            text=True,
            timeout=6,
            creationflags=_CNW,
        )
        if r.returncode == 0:
            for line in r.stdout.strip().splitlines():
                name = line.strip()
                if name:
                    adapters.append(name)
            if adapters:
                return adapters
    except Exception:
        pass
    # Fallback: netsh
    try:
        r = subprocess.run(
            ["netsh", "interface", "show", "interface"],
            capture_output=True,
            text=True,
            timeout=6,
            creationflags=_CNW,
        )
        if r.returncode == 0:
            for line in r.stdout.splitlines():
                parts = line.split()
                if len(parts) >= 4 and parts[1].lower() == "connected":
                    adapters.append(" ".join(parts[3:]))
    except Exception:
        pass
    return adapters if adapters else ["Ethernet", "Wi-Fi"]


def apply_dns_to_adapter(
    adapter: str, primary: str, secondary: str = "8.8.8.8"
) -> Tuple[bool, str]:
    """Apply primary + secondary DNS to *adapter* via netsh."""
    try:
        r1 = subprocess.run(
            [
                "netsh",
                "interface",
                "ip",
                "set",
                "dns",
                f"name={adapter}",
                "static",
                primary,
                "primary",
            ],
            capture_output=True,
            text=True,
            timeout=12,
            creationflags=_CNW,
        )
        if r1.returncode != 0:
            return (
                False,
                f"Primary DNS failed: {r1.stderr.strip() or r1.stdout.strip()}",
            )
        r2 = subprocess.run(
            [
                "netsh",
                "interface",
                "ip",
                "add",
                "dns",
                f"name={adapter}",
                secondary,
                "index=2",
            ],
            capture_output=True,
            text=True,
            timeout=12,
            creationflags=_CNW,
        )
        if r2.returncode != 0:
            return (
                False,
                f"Secondary DNS failed: {r2.stderr.strip() or r2.stdout.strip()}",
            )
        return (True, f'DNS set to {primary} / {secondary} on "{adapter}"')
    except Exception as exc:
        return (False, str(exc))


def is_admin() -> bool:
    """Return True when the process has administrator privileges."""
    try:
        return bool(ctypes.windll.shell32.IsUserAnAdmin())
    except Exception:
        return False


# ══════════════════════════════════════════════════════════════════════════════
#  STYLESHEET
# ══════════════════════════════════════════════════════════════════════════════
_C = COLORS  # shorthand

STYLESHEET = f"""
/* ── Global ─────────────────────────────────────────────────────────────── */
QWidget {{
    background-color: {_C["bg_main"]};
    color: {_C["text"]};
    font-family: "Segoe UI", Arial, sans-serif;
    font-size: 13px;
    selection-background-color: {_C["accent"]};
    selection-color: {_C["text_bright"]};
}}
QMainWindow {{
    background-color: {_C["bg_main"]};
}}

/* ── Sidebar ─────────────────────────────────────────────────────────────── */
#sidebar {{
    background-color: {_C["bg_panel"]};
    border-right: 1px solid {_C["border"]};
    min-width: 160px;
    max-width: 160px;
}}
#sidebar QPushButton {{
    background-color: transparent;
    color: {_C["sidebar_text"]};
    border: none;
    border-left: 3px solid transparent;
    padding: 10px 16px;
    text-align: left;
    font-size: 13px;
    min-height: 36px;
}}
#sidebar QPushButton:hover {{
    background-color: {_C["row_hover"]};
    color: {_C["text_bright"]};
}}
#sidebar QPushButton[active="true"] {{
    background-color: {_C["row_selected"]};
    color: {_C["accent"]};
    border-left: 3px solid {_C["accent"]};
    font-weight: bold;
}}

/* ── Title Bar ───────────────────────────────────────────────────────────── */
#titleBar {{
    background-color: {_C["bg_panel"]};
    border-bottom: 1px solid {_C["border"]};
    min-height: 38px;
    max-height: 38px;
}}
#titleLabel {{
    color: {_C["text_title"]};
    font-size: 13px;
    font-weight: bold;
    padding-left: 4px;
    background: transparent;
}}
#minBtn, #maxBtn {{
    background-color: transparent;
    color: {_C["text"]};
    border: none;
    padding: 0px;
    min-width:  40px;
    max-width:  40px;
    min-height: 38px;
    max-height: 38px;
    font-size: 14px;
}}
#minBtn:hover, #maxBtn:hover {{
    background-color: {_C["row_hover"]};
    color: {_C["text_bright"]};
}}
#closeBtn {{
    background-color: transparent;
    color: {_C["text"]};
    border: none;
    padding: 0px;
    min-width:  46px;
    max-width:  46px;
    min-height: 38px;
    max-height: 38px;
    font-size: 15px;
}}
#closeBtn:hover {{
    background-color: {_C["close_hover"]};
    color: white;
}}

/* ── Content Area ────────────────────────────────────────────────────────── */
#contentArea {{
    background-color: {_C["bg_main"]};
}}

/* ── Panel / Section Labels ──────────────────────────────────────────────── */
#panelTitle {{
    color: {_C["text_bright"]};
    font-size: 16px;
    font-weight: bold;
    padding: 4px 0 8px 0;
    background: transparent;
}}
#sectionLabel {{
    color: {_C["text_title"]};
    font-size: 11px;
    font-weight: bold;
    letter-spacing: 1px;
    background: transparent;
}}

/* ── Generic QPushButton ─────────────────────────────────────────────────── */
QPushButton {{
    background-color: {_C["bg_button"]};
    color: {_C["text"]};
    border: 1px solid {_C["border"]};
    border-radius: 4px;
    padding: 5px 14px;
    min-height: 26px;
}}
QPushButton:hover {{
    background-color: {_C["row_hover"]};
    color: {_C["hover"]};
    border-color: {_C["accent"]};
}}
QPushButton:pressed {{
    background-color: {_C["bg_input"]};
    color: {_C["accent"]};
}}
QPushButton:disabled {{
    background-color: {_C["bg_input"]};
    color: {_C["sidebar_text"]};
    border-color: {_C["bg_input"]};
}}

/* ── Start / Stop / Apply Buttons ────────────────────────────────────────── */
#startBtn {{
    background-color: {_C["accent"]};
    color: white;
    border: none;
    font-weight: bold;
    padding: 6px 20px;
    border-radius: 4px;
    min-height: 30px;
}}
#startBtn:hover {{
    background-color: {_C["accent_rgba80"]};
    color: white;
}}
#startBtn:pressed {{
    background-color: {_C["bg_input"]};
    color: {_C["accent"]};
}}
#startBtn:disabled {{
    background-color: {_C["border"]};
    color: {_C["sidebar_text"]};
}}

#stopBtn {{
    background-color: {_C["bad"]};
    color: white;
    border: none;
    font-weight: bold;
    padding: 6px 20px;
    border-radius: 4px;
    min-height: 30px;
}}
#stopBtn:hover  {{ background-color: #f06868; color: white; }}
#stopBtn:pressed {{ background-color: {_C["bg_input"]}; color: {_C["bad"]}; }}
#stopBtn:disabled {{
    background-color: {_C["border"]};
    color: {_C["sidebar_text"]};
}}

#applyBtn {{
    background-color: {_C["good"]};
    color: #1a1a1a;
    border: none;
    font-weight: bold;
    padding: 6px 20px;
    border-radius: 4px;
    min-height: 30px;
}}
#applyBtn:hover  {{ background-color: #6de86d; color: #1a1a1a; }}
#applyBtn:pressed {{ background-color: {_C["bg_input"]}; color: {_C["good"]}; }}
#applyBtn:disabled {{
    background-color: {_C["border"]};
    color: {_C["sidebar_text"]};
}}

/* ── Inputs ──────────────────────────────────────────────────────────────── */
QLineEdit, QSpinBox {{
    background-color: {_C["bg_input"]};
    color: {_C["text_bright"]};
    border: 1px solid {_C["border"]};
    border-radius: 4px;
    padding: 4px 8px;
    min-height: 24px;
    selection-background-color: {_C["accent"]};
}}
QLineEdit:focus, QSpinBox:focus {{
    border-color: {_C["accent"]};
}}
QSpinBox::up-button, QSpinBox::down-button {{
    background-color: {_C["bg_panel"]};
    border: none;
    width: 16px;
}}
QSpinBox::up-button:hover, QSpinBox::down-button:hover {{
    background-color: {_C["row_hover"]};
}}

/* ── ComboBox ────────────────────────────────────────────────────────────── */
QComboBox {{
    background-color: {_C["bg_input"]};
    color: {_C["text_bright"]};
    border: 1px solid {_C["border"]};
    border-radius: 4px;
    padding: 4px 8px;
    min-height: 24px;
}}
QComboBox:focus {{
    border-color: {_C["accent"]};
}}
QComboBox::drop-down {{
    border: none;
    width: 22px;
}}
QComboBox QAbstractItemView {{
    background-color: {_C["bg_panel"]};
    color: {_C["text_bright"]};
    border: 1px solid {_C["border"]};
    selection-background-color: {_C["accent"]};
    outline: none;
}}

/* ── Table ───────────────────────────────────────────────────────────────── */
QTableWidget {{
    background-color: {_C["bg_main"]};
    alternate-background-color: {_C["row_alt"]};
    color: {_C["text"]};
    border: 1px solid {_C["border"]};
    gridline-color: transparent;
    outline: none;
}}
QTableWidget::item {{
    padding: 2px 6px;
    border: none;
}}
QTableWidget::item:hover {{
    background-color: {_C["row_hover"]};
}}
QTableWidget::item:selected {{
    background-color: {_C["row_selected"]};
    color: {_C["text_bright"]};
}}
QHeaderView::section {{
    background-color: {_C["bg_panel"]};
    color: {_C["text_title"]};
    border: none;
    border-bottom: 1px solid {_C["border"]};
    border-right: 1px solid {_C["border"]};
    padding: 4px 8px;
    font-weight: bold;
    font-size: 12px;
}}
QHeaderView::section:checked {{
    background-color: {_C["accent"]};
    color: white;
}}

/* ── Progress Bar ────────────────────────────────────────────────────────── */
QProgressBar {{
    background-color: {_C["bg_input"]};
    color: {_C["text_bright"]};
    border: 1px solid {_C["border"]};
    border-radius: 4px;
    text-align: center;
    min-height: 16px;
    max-height: 16px;
}}
QProgressBar::chunk {{
    background-color: {_C["accent"]};
    border-radius: 3px;
}}

/* ── Text Edit ───────────────────────────────────────────────────────────── */
QTextEdit {{
    background-color: {_C["bg_input"]};
    color: {_C["text"]};
    border: 1px solid {_C["border"]};
    border-radius: 4px;
    padding: 4px;
    selection-background-color: {_C["accent"]};
}}

/* ── Scrollbar ───────────────────────────────────────────────────────────── */
QScrollBar:vertical {{
    background: transparent;
    width: 8px;
    margin: 0;
}}
QScrollBar::handle:vertical {{
    background: {_C["scrollbar"]};
    border-radius: 4px;
    min-height: 20px;
}}
QScrollBar::handle:vertical:hover {{
    background: {_C["scrollbar_hover"]};
}}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0; background: none;
}}
QScrollBar:horizontal {{
    background: transparent;
    height: 8px;
    margin: 0;
}}
QScrollBar::handle:horizontal {{
    background: {_C["scrollbar"]};
    border-radius: 4px;
    min-width: 20px;
}}
QScrollBar::handle:horizontal:hover {{
    background: {_C["scrollbar_hover"]};
}}
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
    width: 0; background: none;
}}

/* ── Menu Bar ────────────────────────────────────────────────────────────── */
QMenuBar {{
    background-color: {_C["bg_panel"]};
    color: {_C["text"]};
    border-bottom: 1px solid {_C["border"]};
    padding: 2px 4px;
}}
QMenuBar::item {{
    background: transparent;
    padding: 4px 10px;
    border-radius: 3px;
}}
QMenuBar::item:selected {{
    background-color: {_C["row_hover"]};
    color: {_C["text_bright"]};
}}
QMenu {{
    background-color: {_C["bg_panel"]};
    color: {_C["text"]};
    border: 1px solid {_C["border"]};
    padding: 4px 0;
}}
QMenu::item {{
    padding: 5px 24px 5px 12px;
}}
QMenu::item:selected {{
    background-color: {_C["accent"]};
    color: white;
}}
QMenu::separator {{
    height: 1px;
    background-color: {_C["border"]};
    margin: 3px 8px;
}}

/* ── Status Bar ──────────────────────────────────────────────────────────── */
QStatusBar {{
    background-color: {_C["bg_panel"]};
    color: {_C["text"]};
    border-top: 1px solid {_C["border"]};
    font-size: 12px;
}}

/* ── Group Box ───────────────────────────────────────────────────────────── */
QGroupBox {{
    background-color: {_C["bg_panel"]};
    border: 1px solid {_C["border"]};
    border-radius: 6px;
    margin-top: 18px;
    padding-top: 10px;
    font-weight: bold;
    color: {_C["text_title"]};
}}
QGroupBox::title {{
    subcontrol-origin: margin;
    subcontrol-position: top left;
    left: 10px;
    top: -9px;
    padding: 0 4px;
    background-color: {_C["bg_panel"]};
    color: {_C["text_title"]};
}}

/* ── CheckBox ────────────────────────────────────────────────────────────── */
QCheckBox {{
    color: {_C["text"]};
    spacing: 6px;
    background: transparent;
}}
QCheckBox::indicator {{
    width: 14px;
    height: 14px;
    border: 1px solid {_C["border"]};
    border-radius: 3px;
    background-color: {_C["bg_input"]};
}}
QCheckBox::indicator:checked {{
    background-color: {_C["accent"]};
    border-color: {_C["accent"]};
}}
QCheckBox::indicator:hover {{
    border-color: {_C["accent"]};
}}

/* ── List Widget ─────────────────────────────────────────────────────────── */
QListWidget {{
    background-color: {_C["bg_input"]};
    color: {_C["text"]};
    border: 1px solid {_C["border"]};
    border-radius: 4px;
    outline: none;
}}
QListWidget::item {{
    padding: 4px 8px;
    min-height: 22px;
}}
QListWidget::item:hover  {{ background-color: {_C["row_hover"]}; }}
QListWidget::item:selected {{
    background-color: {_C["row_selected"]};
    color: {_C["text_bright"]};
}}

/* ── Dialog ──────────────────────────────────────────────────────────────── */
QDialog {{
    background-color: {_C["bg_main"]};
    color: {_C["text"]};
}}

/* ── Splitter ────────────────────────────────────────────────────────────── */
QSplitter::handle            {{ background-color: {_C["border"]}; }}
QSplitter::handle:horizontal {{ width: 1px;  }}
QSplitter::handle:vertical   {{ height: 1px; }}

/* ── Frame lines ─────────────────────────────────────────────────────────── */
QFrame[frameShape="4"], QFrame[frameShape="5"] {{
    color: {_C["border"]};
}}

/* ── Generic Label ───────────────────────────────────────────────────────── */
QLabel {{
    background: transparent;
    color: {_C["text"]};
}}
"""


# ══════════════════════════════════════════════════════════════════════════════
#  TITLE BAR
# ══════════════════════════════════════════════════════════════════════════════
class TitleBar(QWidget):
    def __init__(
        self, parent: Optional[QWidget] = None, title: str = "DNS Speed Test"
    ) -> None:
        super().__init__(parent)
        self.setObjectName("titleBar")
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.setFixedHeight(38)
        self._drag_pos: Optional[QPoint] = None

        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 0, 0, 0)
        layout.setSpacing(6)

        # Coloured hex dot
        dot = QLabel("⬡")
        dot.setStyleSheet(
            f"color: {COLORS['accent']}; font-size: 14px; background: transparent;"
        )
        layout.addWidget(dot)

        # Title label
        self._title_label = QLabel(title)
        self._title_label.setObjectName("titleLabel")
        layout.addWidget(self._title_label)

        layout.addStretch()

        # Min button
        self.min_btn = QPushButton("─")
        self.min_btn.setObjectName("minBtn")
        self.min_btn.setFixedSize(40, 38)
        self.min_btn.clicked.connect(self._minimize)
        layout.addWidget(self.min_btn)

        # Max button
        self.max_btn = QPushButton("□")
        self.max_btn.setObjectName("maxBtn")
        self.max_btn.setFixedSize(40, 38)
        self.max_btn.clicked.connect(self._toggle_max)
        layout.addWidget(self.max_btn)

        # Close button
        self.close_btn = QPushButton("✕")
        self.close_btn.setObjectName("closeBtn")
        self.close_btn.setFixedSize(46, 38)
        self.close_btn.clicked.connect(self._close)
        layout.addWidget(self.close_btn)

    # ── window control helpers ────────────────────────────────────────────────
    def _minimize(self) -> None:
        win = self.window()
        if win:
            win.showMinimized()

    def _toggle_max(self) -> None:
        win = self.window()
        if not win:
            return
        if win.isMaximized():
            win.showNormal()
            self.max_btn.setText("□")
        else:
            win.showMaximized()
            self.max_btn.setText("❐")

    def _close(self) -> None:
        win = self.window()
        if win:
            win.close()

    # ── drag / double-click ───────────────────────────────────────────────────
    def mousePressEvent(self, event) -> None:
        if event.button() == Qt.LeftButton:
            win = self.window()
            if win:
                self._drag_pos = event.globalPos() - win.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event) -> None:
        if event.buttons() == Qt.LeftButton and self._drag_pos is not None:
            win = self.window()
            if win and not win.isMaximized():
                win.move(event.globalPos() - self._drag_pos)
            event.accept()

    def mouseReleaseEvent(self, event) -> None:
        self._drag_pos = None

    def mouseDoubleClickEvent(self, event) -> None:
        if event.button() == Qt.LeftButton:
            self._toggle_max()


# ══════════════════════════════════════════════════════════════════════════════
#  SIDEBAR BUTTON
# ══════════════════════════════════════════════════════════════════════════════
class SidebarButton(QPushButton):
    def __init__(
        self, icon_text: str, label: str, parent: Optional[QWidget] = None
    ) -> None:
        super().__init__(f"  {icon_text}  {label}", parent)
        self.setCheckable(True)
        self.setToolTip(label)
        self.setCursor(QCursor(Qt.PointingHandCursor))
        self.setProperty("active", "false")

    def setActive(self, active: bool) -> None:
        self.setProperty("active", "true" if active else "false")
        self.style().unpolish(self)
        self.style().polish(self)
        self.update()


# ══════════════════════════════════════════════════════════════════════════════
#  HELPER FUNCTIONS
# ══════════════════════════════════════════════════════════════════════════════
def _ms_color(ms: Optional[float]) -> str:
    if ms is None:
        return COLORS["bad"]
    if ms <= _good_threshold:
        return COLORS["good"]
    if ms <= _ok_threshold:
        return COLORS["ok"]
    return COLORS["bad"]


def _make_ms_item(ms: Optional[float]) -> "NumericTableItem":
    """Single ms value cell (Min, Avg, Max, Jitter)."""
    item = NumericTableItem()
    if ms is not None and ms >= 0:
        item.setText(f"{ms:.2f}")
        item.setData(Qt.UserRole, ms)
        item.setForeground(QColor(_ms_color(ms)))
    else:
        item.setText("—")
        item.setData(Qt.UserRole, 999999.0)
        item.setForeground(QColor(COLORS["bad"]))
    item.setTextAlignment(Qt.AlignCenter)
    return item


def make_response_item(response_ms: Optional[float], status: str) -> "NumericTableItem":
    """Legacy single-response item (used for Avg column)."""
    return _make_ms_item(response_ms)


def make_status_item(status: str, response_ms: Optional[float]) -> QTableWidgetItem:
    item = QTableWidgetItem()
    if status == "OK" and response_ms is not None:
        item.setText("✓  OK")
        item.setForeground(QColor(COLORS["good"]))
    elif status == "Timeout":
        item.setText("✕  Timeout")
        item.setForeground(QColor(COLORS["bad"]))
    elif status == "Cancelled":
        item.setText("–  Cancelled")
        item.setForeground(QColor(COLORS["text"]))
    else:
        item.setText(f"✕  {status}")
        item.setForeground(QColor(COLORS["bad"]))
    item.setTextAlignment(Qt.AlignCenter)
    return item


def _make_tier_item(result: "DNSResult") -> QTableWidgetItem:
    tier = result.gaming_tier
    color = result.tier_color
    item = QTableWidgetItem(tier)
    item.setForeground(QColor(color))
    item.setTextAlignment(Qt.AlignCenter)
    f = item.font()
    f.setBold(True)
    item.setFont(f)
    return item


# ══════════════════════════════════════════════════════════════════════════════
#  TEST PANEL
# ══════════════════════════════════════════════════════════════════════════════
class TestPanel(QWidget):
    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.setObjectName("contentArea")
        self._worker: Optional[DNSTestWorker] = None
        self._results: Dict[str, DNSResult] = {}
        self._build_ui()
        self._refresh_adapters()

    # ── UI construction ───────────────────────────────────────────────────────
    def _build_ui(self) -> None:
        ml = QVBoxLayout(self)
        ml.setContentsMargins(16, 12, 16, 12)
        ml.setSpacing(10)

        # Panel title
        title = QLabel("DNS Speed Test")
        title.setObjectName("panelTitle")
        ml.addWidget(title)

        # ── Config row ────────────────────────────────────────────────────────
        cfg = QHBoxLayout()
        cfg.setSpacing(8)

        cfg.addWidget(QLabel("Domain:"))
        self.domain_combo = QComboBox()
        self.domain_combo.setEditable(True)
        self.domain_combo.setInsertPolicy(QComboBox.NoInsert)
        self.domain_combo.setMinimumWidth(310)
        self.domain_combo.setMaximumWidth(500)
        for label, hostname, tip in DOMAIN_PRESETS:
            self.domain_combo.addItem(label, userData=hostname)
            idx = self.domain_combo.count() - 1
            self.domain_combo.setItemData(idx, tip, Qt.ToolTipRole)
        self.domain_combo.setCurrentIndex(0)
        self.domain_combo.setToolTip(DOMAIN_PRESETS[0][2])
        self.domain_combo.currentIndexChanged.connect(self._on_domain_changed)
        cfg.addWidget(self.domain_combo)

        cfg.addWidget(QLabel("Timeout:"))
        self.timeout_spin = QSpinBox()
        self.timeout_spin.setRange(1, 30)
        self.timeout_spin.setValue(DEFAULT_TIMEOUT)
        self.timeout_spin.setSuffix(" s")
        self.timeout_spin.setFixedWidth(68)
        cfg.addWidget(self.timeout_spin)

        cfg.addWidget(QLabel("Category:"))
        self.filter_combo = QComboBox()
        self.filter_combo.addItems(["All", "Global", "US-East", "Gaming", "Iran"])
        self.filter_combo.setFixedWidth(100)
        self.filter_combo.currentTextChanged.connect(self._apply_filter)
        cfg.addWidget(self.filter_combo)

        cfg.addStretch()
        ml.addLayout(cfg)

        # ── Button row ────────────────────────────────────────────────────────
        # ── Fortnite info banner ──────────────────────────────────────────────
        self._info_bar = QLabel()
        self._info_bar.setWordWrap(True)
        self._info_bar.setTextFormat(Qt.RichText)
        self._info_bar.setStyleSheet(
            f"background-color: #1a2a1a;"
            f"border: 1px solid #2a5a2a;"
            f"border-radius: 4px;"
            f"color: {COLORS['text']};"
            f"padding: 5px 10px;"
            f"font-size: 12px;"
        )
        self._update_info_bar(0)
        ml.addWidget(self._info_bar)

        btn_row = QHBoxLayout()
        btn_row.setSpacing(8)

        self.start_btn = QPushButton("▶  Start Test")
        self.start_btn.setObjectName("startBtn")
        self.start_btn.clicked.connect(self.start_test)
        btn_row.addWidget(self.start_btn)

        self.stop_btn = QPushButton("■  Stop")
        self.stop_btn.setObjectName("stopBtn")
        self.stop_btn.setEnabled(False)
        self.stop_btn.clicked.connect(self.stop_test)
        btn_row.addWidget(self.stop_btn)

        btn_row.addStretch()

        self.export_btn = QPushButton("⬇  Export CSV")
        self.export_btn.clicked.connect(self._export_csv)
        btn_row.addWidget(self.export_btn)

        self.copy_best_btn = QPushButton("⧉  Copy Best")
        self.copy_best_btn.clicked.connect(self._copy_best)
        btn_row.addWidget(self.copy_best_btn)

        ml.addLayout(btn_row)

        # ── Progress ──────────────────────────────────────────────────────────
        prog_row = QHBoxLayout()
        prog_row.setSpacing(8)
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        prog_row.addWidget(self.progress_bar, 1)
        self.progress_label = QLabel("Ready")
        self.progress_label.setFixedWidth(110)
        self.progress_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        prog_row.addWidget(self.progress_label)
        ml.addLayout(prog_row)

        # ── Table ─────────────────────────────────────────────────────────────
        self.table = QTableWidget()
        self.table.setColumnCount(10)
        self.table.setHorizontalHeaderLabels(
            [
                "#",
                "DNS Server",
                "Provider",
                "Category",
                "Min (ms)",
                "Avg (ms)",
                "Max (ms)",
                "Jitter",
                "Tier",
                "Status",
            ]
        )
        self.table.setSortingEnabled(True)
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.table.setShowGrid(False)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.verticalHeader().setVisible(False)
        self.table.verticalHeader().setDefaultSectionSize(28)
        self.table.horizontalHeader().setHighlightSections(False)
        self.table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self._table_context_menu)

        hh = self.table.horizontalHeader()
        hh.setSectionResizeMode(0, QHeaderView.Fixed)  # #
        hh.setSectionResizeMode(1, QHeaderView.Fixed)  # IP
        hh.setSectionResizeMode(2, QHeaderView.Stretch)  # Provider
        hh.setSectionResizeMode(3, QHeaderView.Fixed)  # Category
        hh.setSectionResizeMode(4, QHeaderView.Fixed)  # Min
        hh.setSectionResizeMode(5, QHeaderView.Fixed)  # Avg
        hh.setSectionResizeMode(6, QHeaderView.Fixed)  # Max
        hh.setSectionResizeMode(7, QHeaderView.Fixed)  # Jitter
        hh.setSectionResizeMode(8, QHeaderView.Fixed)  # Tier
        hh.setSectionResizeMode(9, QHeaderView.Fixed)  # Status
        self.table.setColumnWidth(0, 36)
        self.table.setColumnWidth(1, 138)
        self.table.setColumnWidth(3, 72)
        self.table.setColumnWidth(4, 80)
        self.table.setColumnWidth(5, 80)
        self.table.setColumnWidth(6, 80)
        self.table.setColumnWidth(7, 72)
        self.table.setColumnWidth(8, 46)
        self.table.setColumnWidth(9, 88)

        ml.addWidget(self.table, 1)

        # ── Best result + Apply row ───────────────────────────────────────────
        bot = QHBoxLayout()
        bot.setSpacing(8)

        self.best_label = QLabel("Best: —")
        self.best_label.setStyleSheet(
            f"color: {COLORS['text_bright']}; font-weight: bold;"
        )
        bot.addWidget(self.best_label, 1)

        bot.addWidget(QLabel("Adapter:"))
        self.adapter_combo = QComboBox()
        self.adapter_combo.setMinimumWidth(160)
        bot.addWidget(self.adapter_combo)

        ref_btn = QPushButton("↺")
        ref_btn.setFixedWidth(30)
        ref_btn.setToolTip("Refresh adapter list")
        ref_btn.clicked.connect(self._refresh_adapters)
        bot.addWidget(ref_btn)

        self.apply_btn = QPushButton("✔  Apply Best DNS")
        self.apply_btn.setObjectName("applyBtn")
        self.apply_btn.clicked.connect(self._apply_best_dns)
        bot.addWidget(self.apply_btn)

        ml.addLayout(bot)

        # Populate initial rows
        self._populate_table()

    # ── Table population ──────────────────────────────────────────────────────
    # ── Domain helpers ────────────────────────────────────────────────────────
    def _current_domain(self) -> str:
        """Return the hostname to test — either from preset data or typed text."""
        idx = self.domain_combo.currentIndex()
        if idx >= 0:
            stored = self.domain_combo.itemData(idx)
            if stored:
                return stored
        # Editable field — user typed something custom
        return self.domain_combo.currentText().strip() or DEFAULT_TEST_DOMAIN

    def _on_domain_changed(self, idx: int) -> None:
        tip = self.domain_combo.itemData(idx, Qt.ToolTipRole)
        if tip:
            self.domain_combo.setToolTip(tip)
        self._update_info_bar(idx)

    def _update_info_bar(self, idx: int) -> None:
        """Refresh the green info banner below the domain row."""
        fortnite_indices = {0, 1, 2, 3, 4}  # indices of Fortnite presets
        if idx in fortnite_indices:
            label, hostname, tip = DOMAIN_PRESETS[idx]
            short_tip = tip.split("\n")[0]
            html = (
                f'<b style="color:#4ec94e;">🎮 Fortnite mode:</b> '
                f'<span style="color:{COLORS["text_bright"]};">{hostname}</span>'
                f'<br><span style="color:{COLORS["text"]};">{short_tip}</span>'
            )
        elif idx == 5:
            html = (
                f'<b style="color:{COLORS["accent"]};">ℹ️ Epic Games general</b>'
                f" — not Fortnite-specific; tests CDN routing to epicgames.com."
            )
        else:
            _, hostname, _ = (
                DOMAIN_PRESETS[idx]
                if idx < len(DOMAIN_PRESETS)
                else ("", self._current_domain(), "")
            )
            html = (
                f'<b style="color:{COLORS["text_title"]};">ℹ️ General baseline</b>'
                f" — not Fortnite-specific. Use a Fortnite preset for gaming results."
            )
        self._info_bar.setText(html)

    def _get_filtered_servers(self) -> List[str]:
        cat = (
            self.filter_combo.currentText() if hasattr(self, "filter_combo") else "All"
        )
        if cat == "All":
            return list(DNS_PROVIDERS.keys())
        return [ip for ip, (_, c) in DNS_PROVIDERS.items() if c == cat]

    def _populate_table(self) -> None:
        self.table.setSortingEnabled(False)
        servers = self._get_filtered_servers()
        self.table.setRowCount(len(servers))

        mono = QFont("Consolas")
        mono.setPointSize(10)

        for row, ip in enumerate(servers):
            provider, category = DNS_PROVIDERS.get(ip, ("Unknown", "Unknown"))

            # col 0: rank
            num_it = QTableWidgetItem(str(row + 1))
            num_it.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            num_it.setForeground(QColor(COLORS["sidebar_text"]))
            self.table.setItem(row, 0, num_it)

            # col 1: IP
            ip_it = QTableWidgetItem(ip)
            ip_it.setForeground(QColor(COLORS["text_bright"]))
            ip_it.setFont(mono)
            self.table.setItem(row, 1, ip_it)

            # col 2: provider
            prov_it = QTableWidgetItem(provider)
            prov_it.setForeground(QColor(COLORS["text"]))
            self.table.setItem(row, 2, prov_it)

            # col 3: category (color-coded)
            if category == "Global":
                cat_color = COLORS["accent"]
            elif category == "Gaming":
                cat_color = "#00e5ff"
            else:
                cat_color = COLORS["ok"]  # US-East and Iran
            cat_it = QTableWidgetItem(category)
            cat_it.setForeground(QColor(cat_color))
            cat_it.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row, 3, cat_it)

            # cols 4-7: ms placeholders
            self.table.setItem(row, 4, _make_ms_item(None))
            self.table.setItem(row, 5, _make_ms_item(None))
            self.table.setItem(row, 6, _make_ms_item(None))
            self.table.setItem(row, 7, _make_ms_item(None))

            # col 8: tier placeholder
            tier_it = QTableWidgetItem("—")
            tier_it.setForeground(QColor(COLORS["sidebar_text"]))
            tier_it.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row, 8, tier_it)

            # col 9: status placeholder
            self.table.setItem(row, 9, make_status_item("Pending", None))

        self.table.setSortingEnabled(True)

    def _apply_filter(self) -> None:
        self._results.clear()
        self._populate_table()
        self.best_label.setText("Best: —")

    # ── Test control ──────────────────────────────────────────────────────────
    def start_test(self) -> None:
        if self._worker and self._worker.isRunning():
            return
        self._results.clear()
        self._populate_table()
        self.best_label.setText("Best: —")
        self.progress_bar.setValue(0)
        self.progress_label.setText("0 / 0")

        servers = self._get_filtered_servers()
        domain = self._current_domain()
        timeout = self.timeout_spin.value()

        self._worker = DNSTestWorker(servers, domain, timeout, DEFAULT_MAX_WORKERS)
        self._worker.result_ready.connect(self._on_result)
        self._worker.progress.connect(self._on_progress)
        self._worker.log_message.connect(self._on_log)
        self._worker.finished.connect(self._on_finished)

        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self._worker.start()

    def stop_test(self) -> None:
        if self._worker:
            self._worker.stop()
        self.stop_btn.setEnabled(False)

    # ── Worker slots ──────────────────────────────────────────────────────────
    def _on_result(
        self,
        ip: str,
        min_raw: float,
        avg_raw: float,
        max_raw: float,
        jit_raw: float,
        status: str,
    ) -> None:
        min_ms = min_raw if min_raw >= 0 else None
        avg_ms = avg_raw if avg_raw >= 0 else None
        max_ms = max_raw if max_raw >= 0 else None
        jit_ms = jit_raw if jit_raw >= 0 else None

        provider, category = DNS_PROVIDERS.get(ip, ("Unknown", "Unknown"))
        result = DNSResult(
            ip, provider, category, min_ms, avg_ms, max_ms, jit_ms, status
        )
        self._results[ip] = result

        # Find row
        row = None
        for r in range(self.table.rowCount()):
            it = self.table.item(r, 1)
            if it and it.text() == ip:
                row = r
                break
        if row is None:
            return

        self.table.setSortingEnabled(False)
        self.table.setItem(row, 4, _make_ms_item(min_ms))
        self.table.setItem(row, 5, _make_ms_item(avg_ms))
        self.table.setItem(row, 6, _make_ms_item(max_ms))
        self.table.setItem(row, 7, _make_ms_item(jit_ms))
        self.table.setItem(row, 8, _make_tier_item(result))
        self.table.setItem(row, 9, make_status_item(status, avg_ms))
        self.table.setSortingEnabled(True)

        best = self._get_best_result()
        if best:
            self.best_label.setText(
                f"Best so far: {best.ip}  |  {best.provider}  |  "
                f"min {best.min_ms:.2f}  avg {best.avg_ms:.2f}  max {best.max_ms:.2f}  jitter {best.jitter_ms:.2f} ms  |  Tier: {best.gaming_tier}"
            )

    def _on_progress(self, done: int, total: int) -> None:
        pct = int(done / total * 100) if total > 0 else 0
        self.progress_bar.setValue(pct)
        self.progress_label.setText(f"{done} / {total}")

    def _on_log(self, msg: str) -> None:
        win = self.window()
        if hasattr(win, "log_panel"):
            win.log_panel.append_log(msg)

    def _on_finished(self) -> None:
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.progress_bar.setValue(100)
        self.progress_label.setText("Done")

        # Sort by Avg DESCENDING: greatest (slowest) at top, best (fastest) at bottom
        self.table.setSortingEnabled(True)
        self.table.sortByColumn(5, Qt.DescendingOrder)

        # Re-number ranks after sort
        self.table.setSortingEnabled(False)
        for row in range(self.table.rowCount()):
            rank_item = self.table.item(row, 0)
            if rank_item:
                rank_item.setText(str(row + 1))

        # Highlight the best (last) row in gold
        best_row = self.table.rowCount() - 1
        if best_row >= 0:
            gold = QColor("#2a2200")
            gold_text = QColor("#f5c518")
            for col in range(self.table.columnCount()):
                cell = self.table.item(best_row, col)
                if cell:
                    cell.setBackground(gold)
                    if col in (0, 2, 3, 9):  # non-numeric columns
                        cell.setForeground(gold_text)

        self.table.setSortingEnabled(True)
        self.table.scrollToBottom()  # reveal the winner

        best = self._get_best_result()
        if best:
            self.best_label.setText(
                f"★  Best: {best.ip}  ({best.provider})  |  "
                f"min {best.min_ms:.2f}  avg {best.avg_ms:.2f}  max {best.max_ms:.2f}  jitter {best.jitter_ms:.2f} ms  |  Gaming Tier: {best.gaming_tier}"
            )
            self.best_label.setStyleSheet(
                f"color: #f5c518; font-weight: bold; font-size: 13px;"
            )

        win = self.window()
        if hasattr(win, "_status_bar"):
            win._status_bar.showMessage(
                f"Test complete — best DNS: {best.ip if best else 'N/A'}", 5000
            )

    # ── Best result ───────────────────────────────────────────────────────────
    def _get_best_result(self) -> Optional[DNSResult]:
        ok = [
            r
            for r in self._results.values()
            if r.status == "OK" and r.response_ms is not None
        ]
        if not ok:
            return None
        return min(
            ok,
            key=lambda r: r.response_ms if r.response_ms is not None else float("inf"),
        )

    # ── Apply DNS ─────────────────────────────────────────────────────────────
    def _apply_best_dns(self) -> None:
        if not is_admin():
            QMessageBox.warning(
                self,
                "Admin Required",
                "Applying DNS requires administrator privileges.\n"
                "Please restart the application as Administrator.",
            )
            return
        best = self._get_best_result()
        if not best:
            QMessageBox.information(
                self, "No Result", "No successful DNS results available yet."
            )
            return
        adapter = self.adapter_combo.currentText()
        if not adapter:
            QMessageBox.warning(self, "No Adapter", "No network adapter selected.")
            return
        ok, msg = apply_dns_to_adapter(adapter, best.ip)
        if ok:
            QMessageBox.information(self, "DNS Applied", msg)
        else:
            QMessageBox.critical(self, "Error", msg)

    # ── Export CSV ────────────────────────────────────────────────────────────
    def _export_csv(self) -> None:
        if not self._results:
            QMessageBox.information(self, "No Data", "Run a test first.")
            return
        path, _ = QFileDialog.getSaveFileName(
            self, "Export Results", "dns_results.csv", "CSV Files (*.csv)"
        )
        if not path:
            return
        try:
            with open(path, "w", newline="", encoding="utf-8") as f:
                w = csv.writer(f)
                w.writerow(
                    [
                        "Rank",
                        "IP",
                        "Provider",
                        "Category",
                        "Min (ms)",
                        "Avg (ms)",
                        "Max (ms)",
                        "Jitter (ms)",
                        "Tier",
                        "Status",
                    ]
                )
                for row in range(self.table.rowCount()):
                    rowdata = []
                    for col in range(self.table.columnCount()):
                        it = self.table.item(row, col)
                        rowdata.append(it.text() if it else "")
                    w.writerow(rowdata)
            QMessageBox.information(self, "Exported", f"Saved to:\n{path}")
        except Exception as exc:
            QMessageBox.critical(self, "Error", str(exc))

    # ── Copy best ─────────────────────────────────────────────────────────────
    def _copy_best(self) -> None:
        best = self._get_best_result()
        if not best:
            QMessageBox.information(self, "No Result", "No successful DNS results yet.")
            return
        QApplication.clipboard().setText(best.ip)
        win = self.window()
        if hasattr(win, "_status_bar"):
            win._status_bar.showMessage(f"Copied: {best.ip}", 3000)

    # ── Adapters ──────────────────────────────────────────────────────────────
    def _refresh_adapters(self) -> None:
        self.adapter_combo.clear()
        for a in get_active_adapters():
            self.adapter_combo.addItem(a)

    # ── Context menu ──────────────────────────────────────────────────────────
    def _table_context_menu(self, pos) -> None:
        row = self.table.rowAt(pos.y())
        if row < 0:
            return
        ip_it = self.table.item(row, 1)
        if not ip_it:
            return
        ip = ip_it.text()
        menu = QMenu(self)
        copy_act = menu.addAction("Copy IP")
        apply_act = menu.addAction("Apply as Primary DNS")
        chosen = menu.exec_(self.table.viewport().mapToGlobal(pos))
        if chosen == copy_act:
            QApplication.clipboard().setText(ip)
        elif chosen == apply_act:
            if not is_admin():
                QMessageBox.warning(
                    self, "Admin Required", "Administrator privileges required."
                )
                return
            adapter = self.adapter_combo.currentText()
            if not adapter:
                QMessageBox.warning(self, "No Adapter", "Select an adapter first.")
                return
            ok, msg = apply_dns_to_adapter(adapter, ip)
            (QMessageBox.information if ok else QMessageBox.critical)(
                self, "Apply DNS", msg
            )

    # ── Public: update thresholds ─────────────────────────────────────────────
    def update_thresholds(self, good: int, ok: int) -> None:
        global _good_threshold, _ok_threshold
        _good_threshold = good
        _ok_threshold = ok


# ══════════════════════════════════════════════════════════════════════════════
#  SERVERS PANEL
# ══════════════════════════════════════════════════════════════════════════════
class ServersPanel(QWidget):
    servers_changed = pyqtSignal()

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.setObjectName("contentArea")
        self._build_ui()
        self._refresh_list()

    def _build_ui(self) -> None:
        ml = QVBoxLayout(self)
        ml.setContentsMargins(16, 12, 16, 12)
        ml.setSpacing(10)

        title = QLabel("DNS Server Management")
        title.setObjectName("panelTitle")
        ml.addWidget(title)

        # Search
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Search by IP, provider or category…")
        self.search_edit.textChanged.connect(self._filter_list)
        ml.addWidget(self.search_edit)

        splitter = QSplitter(Qt.Horizontal)

        # ── Left: list + buttons ──────────────────────────────────────────────
        left = QWidget()
        ll = QVBoxLayout(left)
        ll.setContentsMargins(0, 0, 0, 0)
        ll.setSpacing(6)

        sec = QLabel("SERVER LIST")
        sec.setObjectName("sectionLabel")
        ll.addWidget(sec)

        self.list_widget = QListWidget()
        self.list_widget.currentItemChanged.connect(self._show_server_info)
        ll.addWidget(self.list_widget, 1)

        row1 = QHBoxLayout()
        row1.setSpacing(6)
        add_btn = QPushButton("＋ Add")
        add_btn.clicked.connect(self._add_server)
        row1.addWidget(add_btn)
        rem_btn = QPushButton("－ Remove")
        rem_btn.clicked.connect(self._remove_selected)
        row1.addWidget(rem_btn)
        ll.addLayout(row1)

        row2 = QHBoxLayout()
        row2.setSpacing(6)
        imp_btn = QPushButton("⬆ Import")
        imp_btn.clicked.connect(self._import_servers)
        row2.addWidget(imp_btn)
        exp_btn = QPushButton("⬇ Export")
        exp_btn.clicked.connect(self._export_servers)
        row2.addWidget(exp_btn)
        rst_btn = QPushButton("↺ Reset")
        rst_btn.clicked.connect(self._reset_defaults)
        row2.addWidget(rst_btn)
        ll.addLayout(row2)

        splitter.addWidget(left)

        # ── Right: info ───────────────────────────────────────────────────────
        right = QWidget()
        rl = QVBoxLayout(right)
        rl.setContentsMargins(8, 0, 0, 0)
        rl.setSpacing(6)

        info_hdr = QLabel("SERVER DETAILS")
        info_hdr.setObjectName("sectionLabel")
        rl.addWidget(info_hdr)

        self.info_ip = QLabel("IP: —")
        self.info_prov = QLabel("Provider: —")
        self.info_cat = QLabel("Category: —")
        for lbl in (self.info_ip, self.info_prov, self.info_cat):
            lbl.setStyleSheet(f"color: {COLORS['text_bright']};")
            rl.addWidget(lbl)

        rl.addStretch()

        self.count_label = QLabel()
        self.count_label.setStyleSheet(
            f"color: {COLORS['sidebar_text']}; font-size: 12px;"
        )
        rl.addWidget(self.count_label)

        splitter.addWidget(right)
        splitter.setSizes([320, 200])
        ml.addWidget(splitter, 1)

    # ── Helpers ───────────────────────────────────────────────────────────────
    def _update_count(self) -> None:
        total = len(DNS_PROVIDERS)
        glob = sum(1 for _, (_, c) in DNS_PROVIDERS.items() if c == "Global")
        iran = sum(1 for _, (_, c) in DNS_PROVIDERS.items() if c == "Iran")
        self.count_label.setText(f"Total: {total}  |  Global: {glob}  |  Iran: {iran}")

    def _refresh_list(self, filter_text: str = "") -> None:
        self.list_widget.clear()
        ft = filter_text.lower()
        for ip, (provider, category) in DNS_PROVIDERS.items():
            if (
                ft
                and ft not in ip.lower()
                and ft not in provider.lower()
                and ft not in category.lower()
            ):
                continue
            item = QListWidgetItem(f"{ip}  —  {provider}  [{category}]")
            item.setData(Qt.UserRole, ip)
            item.setForeground(
                QColor(COLORS["accent"] if category == "Global" else COLORS["ok"])
            )
            self.list_widget.addItem(item)
        self._update_count()

    def _filter_list(self) -> None:
        self._refresh_list(self.search_edit.text().strip())

    def _show_server_info(self, current, _previous) -> None:
        if current is None:
            self.info_ip.setText("IP: —")
            self.info_prov.setText("Provider: —")
            self.info_cat.setText("Category: —")
            return
        ip = current.data(Qt.UserRole)
        provider, category = DNS_PROVIDERS.get(ip, ("Unknown", "Unknown"))
        self.info_ip.setText(f"IP: {ip}")
        self.info_prov.setText(f"Provider: {provider}")
        self.info_cat.setText(f"Category: {category}")

    # ── CRUD ──────────────────────────────────────────────────────────────────
    def _add_server(self) -> None:
        dlg = QDialog(self)
        dlg.setWindowTitle("Add DNS Server")
        dlg.setModal(True)
        dlg.resize(340, 190)
        form = QFormLayout(dlg)
        form.setSpacing(10)
        form.setContentsMargins(16, 16, 16, 16)

        ip_edit = QLineEdit()
        ip_edit.setPlaceholderText("e.g. 1.2.3.4")
        prov_edit = QLineEdit()
        prov_edit.setPlaceholderText("e.g. My Provider")
        cat_combo = QComboBox()
        cat_combo.addItems(["Global", "Iran"])

        form.addRow("IP Address:", ip_edit)
        form.addRow("Provider:", prov_edit)
        form.addRow("Category:", cat_combo)

        btns = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        btns.accepted.connect(dlg.accept)
        btns.rejected.connect(dlg.reject)
        form.addRow(btns)

        if dlg.exec_() == QDialog.Accepted:
            ip = ip_edit.text().strip()
            prov = prov_edit.text().strip() or "Custom"
            cat = cat_combo.currentText()
            if not re.match(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$", ip):
                QMessageBox.warning(
                    self, "Invalid IP", f'"{ip}" is not a valid IPv4 address.'
                )
                return
            DNS_PROVIDERS[ip] = (prov, cat)
            self._refresh_list()
            self.servers_changed.emit()

    def _remove_selected(self) -> None:
        item = self.list_widget.currentItem()
        if item is None:
            QMessageBox.information(
                self, "Nothing Selected", "Select a server to remove."
            )
            return
        ip = item.data(Qt.UserRole)
        reply = QMessageBox.question(
            self,
            "Confirm Remove",
            f"Remove DNS server {ip}?",
            QMessageBox.Yes | QMessageBox.No,
        )
        if reply == QMessageBox.Yes:
            DNS_PROVIDERS.pop(ip, None)
            self._refresh_list()
            self.servers_changed.emit()

    def _import_servers(self) -> None:
        path, _ = QFileDialog.getOpenFileName(
            self, "Import Servers", "", "Text Files (*.txt);;All Files (*)"
        )
        if not path:
            return
        added = load_servers_from_file(path)
        self._refresh_list()
        self.servers_changed.emit()
        QMessageBox.information(
            self, "Import Complete", f"Added {added} new server(s) from:\n{path}"
        )

    def _export_servers(self) -> None:
        path, _ = QFileDialog.getSaveFileName(
            self, "Export Servers", "dns_servers.txt", "Text Files (*.txt)"
        )
        if not path:
            return
        try:
            with open(path, "w", encoding="utf-8") as f:
                for ip, (provider, category) in DNS_PROVIDERS.items():
                    f.write(f"{ip}\t{provider}\t{category}\n")
            QMessageBox.information(
                self, "Exported", f"Saved {len(DNS_PROVIDERS)} servers to:\n{path}"
            )
        except Exception as exc:
            QMessageBox.critical(self, "Error", str(exc))

    def _reset_defaults(self) -> None:
        reply = QMessageBox.question(
            self,
            "Reset Servers",
            "Reset to the built-in defaults?  Custom servers will be lost.\n"
            "(The application will need to be restarted.)",
            QMessageBox.Yes | QMessageBox.No,
        )
        if reply == QMessageBox.Yes:
            QMessageBox.information(
                self,
                "Reset",
                "Please restart the application to restore all default servers.",
            )


# ══════════════════════════════════════════════════════════════════════════════
#  SETTINGS PANEL
# ══════════════════════════════════════════════════════════════════════════════
class SettingsPanel(QWidget):
    settings_changed = pyqtSignal(int, int)  # good_threshold, ok_threshold

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.setObjectName("contentArea")
        self._build_ui()

    def _build_ui(self) -> None:
        ml = QVBoxLayout(self)
        ml.setContentsMargins(16, 12, 16, 12)
        ml.setSpacing(12)

        title = QLabel("Settings")
        title.setObjectName("panelTitle")
        ml.addWidget(title)

        # ── Test Configuration ────────────────────────────────────────────────
        test_grp = QGroupBox("Test Configuration")
        test_form = QFormLayout(test_grp)
        test_form.setSpacing(8)
        test_form.setContentsMargins(12, 18, 12, 12)

        self.s_domain = QLineEdit(DEFAULT_TEST_DOMAIN)
        self.s_timeout = QSpinBox()
        self.s_timeout.setRange(1, 60)
        self.s_timeout.setValue(DEFAULT_TIMEOUT)
        self.s_timeout.setSuffix(" s")
        self.s_workers = QSpinBox()
        self.s_workers.setRange(1, 200)
        self.s_workers.setValue(DEFAULT_MAX_WORKERS)
        self.s_workers.setToolTip("Number of parallel worker threads")

        test_form.addRow("Test Domain:", self.s_domain)
        test_form.addRow("Timeout:", self.s_timeout)
        test_form.addRow("Max Workers:", self.s_workers)
        ml.addWidget(test_grp)

        # ── Response Thresholds ───────────────────────────────────────────────
        thresh_grp = QGroupBox("Response Thresholds")
        thresh_form = QFormLayout(thresh_grp)
        thresh_form.setSpacing(8)
        thresh_form.setContentsMargins(12, 18, 12, 12)

        self.good_spin = QSpinBox()
        self.good_spin.setRange(1, 10000)
        self.good_spin.setValue(DEFAULT_GOOD_THRESHOLD)
        self.good_spin.setSuffix(" ms")

        self.ok_spin = QSpinBox()
        self.ok_spin.setRange(1, 10000)
        self.ok_spin.setValue(DEFAULT_OK_THRESHOLD)
        self.ok_spin.setSuffix(" ms")

        good_lbl = QLabel("≤ this  →  fast (green)")
        good_lbl.setStyleSheet(f"color: {COLORS['good']}; font-weight: bold;")
        ok_lbl = QLabel("≤ this  →  acceptable (orange)")
        ok_lbl.setStyleSheet(f"color: {COLORS['ok']}; font-weight: bold;")
        bad_lbl = QLabel("Above OK threshold  →  slow (red)")
        bad_lbl.setStyleSheet(f"color: {COLORS['bad']};")

        good_row = QHBoxLayout()
        good_row.addWidget(self.good_spin)
        good_row.addWidget(good_lbl)
        good_row.addStretch()

        ok_row = QHBoxLayout()
        ok_row.addWidget(self.ok_spin)
        ok_row.addWidget(ok_lbl)
        ok_row.addStretch()

        thresh_form.addRow("Good threshold:", good_row)
        thresh_form.addRow("OK threshold:", ok_row)
        thresh_form.addRow(bad_lbl)
        ml.addWidget(thresh_grp)

        # ── System Status ─────────────────────────────────────────────────────
        sys_grp = QGroupBox("System Status")
        sys_lay = QVBoxLayout(sys_grp)
        sys_lay.setContentsMargins(12, 18, 12, 12)
        sys_lay.setSpacing(6)

        admin_ok = is_admin()
        dns_ok = HAS_DNSPYTHON

        a_lbl = QLabel(
            f"{'✔' if admin_ok else '✘'}  Administrator: "
            f"{'Yes — DNS apply enabled' if admin_ok else 'No — DNS apply disabled'}"
        )
        a_lbl.setStyleSheet(f"color: {COLORS['good'] if admin_ok else COLORS['bad']};")

        d_lbl = QLabel(
            f"{'✔' if dns_ok else '⚠'}  dnspython: "
            f"{'Available — accurate UDP timing' if dns_ok else 'Not installed — using socket fallback'}"
        )
        d_lbl.setStyleSheet(f"color: {COLORS['good'] if dns_ok else COLORS['ok']};")

        hint = QLabel("     pip install dnspython")
        hint.setStyleSheet(
            f"color: {COLORS['sidebar_text']}; font-family: Consolas, monospace; font-size: 12px;"
        )
        hint.setVisible(not dns_ok)

        sys_lay.addWidget(a_lbl)
        sys_lay.addWidget(d_lbl)
        sys_lay.addWidget(hint)
        ml.addWidget(sys_grp)

        # ── Save button ───────────────────────────────────────────────────────
        save_btn = QPushButton("💾  Save Settings")
        save_btn.setObjectName("startBtn")
        save_btn.clicked.connect(self._save)
        ml.addWidget(save_btn)

        ml.addStretch()

    def _save(self) -> None:
        good = self.good_spin.value()
        ok = self.ok_spin.value()
        if good >= ok:
            QMessageBox.warning(
                self,
                "Invalid",
                "Good threshold must be strictly less than OK threshold.",
            )
            return
        self.settings_changed.emit(good, ok)
        QMessageBox.information(self, "Saved", "Settings applied.")


# ══════════════════════════════════════════════════════════════════════════════
#  LOG PANEL
# ══════════════════════════════════════════════════════════════════════════════
class LogPanel(QWidget):
    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.setObjectName("contentArea")
        self._build_ui()

    def _build_ui(self) -> None:
        ml = QVBoxLayout(self)
        ml.setContentsMargins(16, 12, 16, 12)
        ml.setSpacing(8)

        title = QLabel("Activity Log")
        title.setObjectName("panelTitle")
        ml.addWidget(title)

        self.log_edit = QTextEdit()
        self.log_edit.setReadOnly(True)
        self.log_edit.setFont(QFont("Consolas", 10))
        ml.addWidget(self.log_edit, 1)

        btn_row = QHBoxLayout()
        btn_row.addStretch()
        clear_btn = QPushButton("🗑  Clear")
        clear_btn.clicked.connect(self.log_edit.clear)
        btn_row.addWidget(clear_btn)
        copy_btn = QPushButton("⧉  Copy All")
        copy_btn.clicked.connect(self._copy_all)
        btn_row.addWidget(copy_btn)
        ml.addLayout(btn_row)

    def append_log(self, msg: str) -> None:
        ts = time.strftime("%H:%M:%S")
        html = (
            f'<span style="color:{COLORS["sidebar_text"]}">[{ts}]</span> '
            f'<span style="color:{COLORS["text"]}">{msg}</span>'
        )
        self.log_edit.append(html)
        sb = self.log_edit.verticalScrollBar()
        sb.setValue(sb.maximum())

    def _copy_all(self) -> None:
        QApplication.clipboard().setText(self.log_edit.toPlainText())
        win = self.window()
        if hasattr(win, "_status_bar"):
            win._status_bar.showMessage("Log copied to clipboard.", 2000)


# ══════════════════════════════════════════════════════════════════════════════
#  MAIN WINDOW
# ══════════════════════════════════════════════════════════════════════════════
class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setMinimumSize(900, 600)
        self.resize(1120, 720)
        self.setWindowTitle("DNS Speed Test")
        self.setMouseTracking(True)

        # resize state
        self._resize_edge: str = ""
        self._resize_start_pos: Optional[QPoint] = None
        self._resize_start_rect: Optional[QRect] = None

        self._build_ui()
        self._build_menus()
        self._switch_panel(0)

    # ── Build UI ──────────────────────────────────────────────────────────────
    def _build_ui(self) -> None:
        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # Title bar
        self.title_bar = TitleBar(self, "DNS Speed Test")
        root.addWidget(self.title_bar)

        # Menu bar as plain widget (NOT setMenuBar)
        self.menu_bar = QMenuBar(self)
        self.menu_bar.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        root.addWidget(self.menu_bar)

        # Body
        body = QWidget()
        body_lay = QHBoxLayout(body)
        body_lay.setContentsMargins(0, 0, 0, 0)
        body_lay.setSpacing(0)

        # Sidebar
        self.sidebar = QWidget()
        self.sidebar.setObjectName("sidebar")
        self.sidebar.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)
        sb_lay = QVBoxLayout(self.sidebar)
        sb_lay.setContentsMargins(0, 8, 0, 8)
        sb_lay.setSpacing(2)

        panels_meta = [
            ("🔍", "Test"),
            ("🌐", "Servers"),
            ("⚙", "Settings"),
            ("📋", "Log"),
        ]
        self.sidebar_buttons: List[SidebarButton] = []
        for idx, (icon, label) in enumerate(panels_meta):
            btn = SidebarButton(icon, label, self.sidebar)
            btn.clicked.connect(lambda _checked, i=idx: self._switch_panel(i))
            sb_lay.addWidget(btn)
            self.sidebar_buttons.append(btn)

        sb_lay.addStretch()
        ver = QLabel("v1.0")
        ver.setAlignment(Qt.AlignCenter)
        ver.setStyleSheet(f"color: {COLORS['sidebar_text']}; font-size: 11px;")
        sb_lay.addWidget(ver)
        body_lay.addWidget(self.sidebar)

        # Content stack
        self.content_area = QWidget()
        self.content_area.setObjectName("contentArea")
        ca_lay = QVBoxLayout(self.content_area)
        ca_lay.setContentsMargins(0, 0, 0, 0)
        ca_lay.setSpacing(0)

        self.test_panel = TestPanel(self.content_area)
        self.servers_panel = ServersPanel(self.content_area)
        self.settings_panel = SettingsPanel(self.content_area)
        self.log_panel = LogPanel(self.content_area)

        for panel in (
            self.test_panel,
            self.servers_panel,
            self.settings_panel,
            self.log_panel,
        ):
            ca_lay.addWidget(panel)
            panel.hide()

        body_lay.addWidget(self.content_area, 1)
        root.addWidget(body, 1)

        # Status bar as widget
        self._status_bar = QStatusBar()
        self._status_bar.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self._status_bar.showMessage("Ready")
        root.addWidget(self._status_bar)

        # Connect child signals
        self.servers_panel.servers_changed.connect(self._on_servers_changed)
        self.settings_panel.settings_changed.connect(self._on_settings_changed)

    def statusBar(self) -> QStatusBar:  # type: ignore[override]
        return self._status_bar

    # ── Menus ─────────────────────────────────────────────────────────────────
    def _build_menus(self) -> None:
        # File
        file_menu = self.menu_bar.addMenu("File")
        act_imp = QAction("Import Servers…", self)
        act_imp.triggered.connect(self.servers_panel._import_servers)
        file_menu.addAction(act_imp)
        act_exp = QAction("Export Servers…", self)
        act_exp.triggered.connect(self.servers_panel._export_servers)
        file_menu.addAction(act_exp)
        file_menu.addSeparator()
        act_exit = QAction("Exit", self)
        act_exit.triggered.connect(self.close)
        file_menu.addAction(act_exit)

        # Test
        test_menu = self.menu_bar.addMenu("Test")
        act_start = QAction("Start Test\tF5", self)
        act_start.setShortcut("F5")
        act_start.triggered.connect(self.test_panel.start_test)
        test_menu.addAction(act_start)
        act_stop = QAction("Stop Test\tF6", self)
        act_stop.setShortcut("F6")
        act_stop.triggered.connect(self.test_panel.stop_test)
        test_menu.addAction(act_stop)
        test_menu.addSeparator()
        act_apply = QAction("Apply Best DNS", self)
        act_apply.triggered.connect(self.test_panel._apply_best_dns)
        test_menu.addAction(act_apply)
        act_copy = QAction("Copy Best DNS", self)
        act_copy.triggered.connect(self.test_panel._copy_best)
        test_menu.addAction(act_copy)

        # View
        view_menu = self.menu_bar.addMenu("View")
        for idx, label in enumerate(("Test", "Servers", "Settings", "Log")):
            act = QAction(label, self)
            act.triggered.connect(lambda _checked, i=idx: self._switch_panel(i))
            view_menu.addAction(act)

        # Help
        help_menu = self.menu_bar.addMenu("Help")
        act_about = QAction("About", self)
        act_about.triggered.connect(self._show_about)
        help_menu.addAction(act_about)

    def _show_about(self) -> None:
        QMessageBox.about(
            self,
            "About DNS Speed Test",
            "<b>DNS Speed Test</b><br>"
            "Version 1.0<br><br>"
            "Multi-threaded UDP DNS latency tester with eva-dark theme.<br><br>"
            f"dnspython: <b>{'Available' if HAS_DNSPYTHON else 'Not installed'}</b><br>"
            f"Administrator: <b>{'Yes' if is_admin() else 'No'}</b>",
        )

    # ── Panel switching ───────────────────────────────────────────────────────
    def _switch_panel(self, idx: int) -> None:
        panels = [
            self.test_panel,
            self.servers_panel,
            self.settings_panel,
            self.log_panel,
        ]
        for i, panel in enumerate(panels):
            panel.setVisible(i == idx)
        for i, btn in enumerate(self.sidebar_buttons):
            btn.setActive(i == idx)

    # ── Child signal handlers ─────────────────────────────────────────────────
    def _on_servers_changed(self) -> None:
        self.test_panel._apply_filter()
        self._status_bar.showMessage("Server list updated.", 3000)

    def _on_settings_changed(self, good: int, ok: int) -> None:
        self.test_panel.update_thresholds(good, ok)
        self._status_bar.showMessage(
            f"Thresholds updated — Good ≤ {good} ms, OK ≤ {ok} ms", 3000
        )

    # ── Borderless window resize ──────────────────────────────────────────────
    def _get_resize_edge(self, pos: QPoint) -> str:
        border = 6
        x, y = pos.x(), pos.y()
        w, h = self.width(), self.height()
        left = x < border
        right = x > w - border
        top = y < border
        bottom = y > h - border
        if top and left:
            return "tl"
        if top and right:
            return "tr"
        if bottom and left:
            return "bl"
        if bottom and right:
            return "br"
        if left:
            return "l"
        if right:
            return "r"
        if top:
            return "t"
        if bottom:
            return "b"
        return ""

    _CURSOR_MAP = {
        "": Qt.ArrowCursor,
        "l": Qt.SizeHorCursor,
        "r": Qt.SizeHorCursor,
        "t": Qt.SizeVerCursor,
        "b": Qt.SizeVerCursor,
        "tl": Qt.SizeFDiagCursor,
        "br": Qt.SizeFDiagCursor,
        "tr": Qt.SizeBDiagCursor,
        "bl": Qt.SizeBDiagCursor,
    }

    def mousePressEvent(self, event) -> None:
        if event.button() == Qt.LeftButton:
            edge = self._get_resize_edge(event.pos())
            if edge:
                self._resize_edge = edge
                self._resize_start_pos = event.globalPos()
                self._resize_start_rect = self.geometry()
                event.accept()
                return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event) -> None:
        if (
            self._resize_edge
            and self._resize_start_pos is not None
            and self._resize_start_rect is not None
        ):
            delta = event.globalPos() - self._resize_start_pos
            dx, dy = delta.x(), delta.y()
            r = QRect(self._resize_start_rect)
            edge = self._resize_edge
            if "r" in edge:
                r.setRight(r.right() + dx)
            if "b" in edge:
                r.setBottom(r.bottom() + dy)
            if "l" in edge:
                r.setLeft(r.left() + dx)
            if "t" in edge:
                r.setTop(r.top() + dy)
            if r.width() >= self.minimumWidth() and r.height() >= self.minimumHeight():
                self.setGeometry(r)
            event.accept()
            return
        # Update cursor shape
        edge = self._get_resize_edge(event.pos())
        self.setCursor(QCursor(self._CURSOR_MAP.get(edge, Qt.ArrowCursor)))
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event) -> None:
        self._resize_edge = ""
        self._resize_start_pos = None
        self._resize_start_rect = None
        super().mouseReleaseEvent(event)


# ══════════════════════════════════════════════════════════════════════════════
#  FILE LOADER
# ══════════════════════════════════════════════════════════════════════════════
def load_servers_from_file(path: str) -> int:
    """Read DNS servers from a text file; add new ones to DNS_PROVIDERS.

    File format (one per line, whitespace / comma / semicolon separated):
        <IP>  [<Provider>  [<Category>]]
    Lines starting with '#' are ignored.
    Returns the count of newly added servers.
    """
    added = 0
    try:
        with open(path, "r", encoding="utf-8") as fh:
            for raw in fh:
                line = raw.strip()
                if not line or line.startswith("#"):
                    continue
                parts = re.split(r"[\t,;]+", line)
                ip = parts[0].strip()
                if not re.match(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$", ip):
                    continue
                if ip not in DNS_PROVIDERS:
                    provider = parts[1].strip() if len(parts) > 1 else "Custom"
                    category = parts[2].strip() if len(parts) > 2 else "Global"
                    if category not in ("Global", "Iran"):
                        category = "Global"
                    DNS_PROVIDERS[ip] = (provider, category)
                    added += 1
    except Exception:
        pass
    return added


# ══════════════════════════════════════════════════════════════════════════════
#  ENTRY POINT
# ══════════════════════════════════════════════════════════════════════════════
def main() -> None:
    # HiDPI
    if hasattr(Qt, "AA_EnableHighDpiScaling"):
        QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    if hasattr(Qt, "AA_UseHighDpiPixmaps"):
        QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

    app = QApplication(sys.argv)
    app.setStyleSheet(STYLESHEET)
    app.setApplicationName("DNS Speed Test")
    app.setApplicationVersion("1.0")

    win = MainWindow()
    win.show()

    # Auto-load optional server file alongside the script
    default_file = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "dns_servers.txt"
    )
    if os.path.isfile(default_file):
        n = load_servers_from_file(default_file)
        if n > 0:
            win.log_panel.append_log(
                f"Loaded {n} additional server(s) from dns_servers.txt"
            )
            win._status_bar.showMessage(
                f"Loaded {n} server(s) from dns_servers.txt", 4000
            )

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
