"""Threaded LLRP client for Zebra FX9600 RFID reader."""

import socket
import struct
import threading
import time
from dataclasses import dataclass


# LLRP protocol constants
LLRP_PORT = 5084
LLRP_VERSION = 1
HEADER_LEN = 10

# Message types (outgoing)
MSG_CLOSE_CONNECTION = 14
MSG_ADD_ROSPEC = 20
MSG_DELETE_ROSPEC = 21
MSG_START_ROSPEC = 22
MSG_STOP_ROSPEC = 23
MSG_ENABLE_ROSPEC = 24
MSG_KEEPALIVE_ACK = 72

# Message types (incoming)
MSG_CLOSE_CONNECTION_RESPONSE = 4
MSG_ADD_ROSPEC_RESPONSE = 30
MSG_DELETE_ROSPEC_RESPONSE = 31
MSG_START_ROSPEC_RESPONSE = 32
MSG_STOP_ROSPEC_RESPONSE = 33
MSG_ENABLE_ROSPEC_RESPONSE = 34
MSG_RO_ACCESS_REPORT = 61
MSG_KEEPALIVE = 62
MSG_READER_EVENT_NOTIFICATION = 63

MSG_NAMES = {
    MSG_CLOSE_CONNECTION: "CLOSE_CONNECTION",
    MSG_ADD_ROSPEC: "ADD_ROSPEC",
    MSG_DELETE_ROSPEC: "DELETE_ROSPEC",
    MSG_START_ROSPEC: "START_ROSPEC",
    MSG_STOP_ROSPEC: "STOP_ROSPEC",
    MSG_ENABLE_ROSPEC: "ENABLE_ROSPEC",
    MSG_KEEPALIVE_ACK: "KEEPALIVE_ACK",
    MSG_CLOSE_CONNECTION_RESPONSE: "CLOSE_CONNECTION_RESPONSE",
    MSG_ADD_ROSPEC_RESPONSE: "ADD_ROSPEC_RESPONSE",
    MSG_DELETE_ROSPEC_RESPONSE: "DELETE_ROSPEC_RESPONSE",
    MSG_START_ROSPEC_RESPONSE: "START_ROSPEC_RESPONSE",
    MSG_STOP_ROSPEC_RESPONSE: "STOP_ROSPEC_RESPONSE",
    MSG_ENABLE_ROSPEC_RESPONSE: "ENABLE_ROSPEC_RESPONSE",
    MSG_RO_ACCESS_REPORT: "RO_ACCESS_REPORT",
    MSG_KEEPALIVE: "KEEPALIVE",
    MSG_READER_EVENT_NOTIFICATION: "READER_EVENT_NOTIFICATION",
}

# TV parameter value sizes (bytes, not including the 1-byte type field)
TV_PARAM_SIZES = {
    1: 2,    # AntennaID
    2: 8,    # FirstSeenTimestampUTC
    3: 8,    # LastSeenTimestampUTC
    4: 8,    # FirstSeenTimestampUptime
    5: 8,    # LastSeenTimestampUptime
    6: 1,    # PeakRSSI
    7: 2,    # ChannelIndex
    8: 2,    # TagSeenCount
    9: 4,    # ROSpecID
    10: 2,   # InventoryParameterSpecID
    13: 14,  # EPC-96 (2 pad + 12 EPC)
    14: 2,   # SpecIndex
    15: 2,   # ClientRequestOpSpecResult
    16: 4,   # AccessSpecID
}

ROSPEC_ID = 1

# FX9600 FCC transmit power table: index 1=10.0 dBm to index 81=30.0 dBm (0.25 dBm steps)
POWER_INDEX_FULL = 81   # 30.0 dBm
POWER_INDEX_HALF = 21   # 15.0 dBm (~50% of max on dBm scale)


@dataclass
class TagRead:
    """Single RFID tag read event."""
    epc: str
    rssi: int
    antenna: int
    seen_count: int
    timestamp: float


class RfidReader:
    """LLRP client for Zebra FX9600 RFID reader.

    Uses raw TCP sockets with binary LLRP protocol.
    Threaded: connect/read runs in background, callbacks fire from reader thread.
    """

    def __init__(self, host="192.168.50.2", port=LLRP_PORT):
        self.host = host
        self.port = port
        self._sock = None
        self._thread = None
        self._running = False
        self._lock = threading.Lock()
        self._msg_id = 0
        self._state = "disconnected"

        # Callbacks (called from reader thread — use GLib.idle_add to touch GTK)
        self.on_tag_read = None       # fn(TagRead)
        self.on_status_change = None  # fn(state: str)
        self.on_log = None            # fn(message: str)

        # Power control
        self.reduced_power = False

        # Stats
        self._total_reads = 0
        self._unique_epcs = set()
        self._read_times = []  # timestamps for reads/sec sliding window

    @property
    def state(self):
        with self._lock:
            return self._state

    def _set_state(self, new_state):
        with self._lock:
            self._state = new_state
        if self.on_status_change:
            self.on_status_change(new_state)

    def _log(self, msg):
        if self.on_log:
            self.on_log(msg)

    def _next_msg_id(self):
        self._msg_id += 1
        return self._msg_id

    # ── Public API ──

    def connect(self):
        """Connect to reader in background thread."""
        if self._running:
            return
        self._running = True
        self._msg_id = 0
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def disconnect(self):
        """Disconnect from reader."""
        self._running = False
        sock = self._sock
        if sock:
            try:
                sock.shutdown(socket.SHUT_RDWR)
            except OSError:
                pass
            try:
                sock.close()
            except OSError:
                pass
        if self._thread:
            self._thread.join(timeout=3.0)
            self._thread = None
        self._sock = None
        self._set_state("disconnected")

    def start_inventory(self):
        """Send START_ROSPEC to begin tag reads."""
        if self.state != "ready":
            self._log(f"Cannot start: state={self.state}")
            return
        self._send_rospec_cmd(MSG_START_ROSPEC, ROSPEC_ID)
        self._set_state("starting")

    def stop_inventory(self):
        """Send STOP_ROSPEC to stop tag reads."""
        if self.state != "inventorying":
            self._log(f"Cannot stop: state={self.state}")
            return
        self._send_rospec_cmd(MSG_STOP_ROSPEC, ROSPEC_ID)
        self._set_state("stopping")

    def get_stats(self):
        """Return (total_reads, unique_count, reads_per_second)."""
        with self._lock:
            now = time.time()
            cutoff = now - 5.0
            self._read_times = [t for t in self._read_times if t > cutoff]
            rate = len(self._read_times) / 5.0
            return self._total_reads, len(self._unique_epcs), rate

    def reset_stats(self):
        with self._lock:
            self._total_reads = 0
            self._unique_epcs.clear()
            self._read_times.clear()

    # ── Build LLRP messages ──

    @staticmethod
    def _make_header(msg_type, length, msg_id):
        ver_type = (LLRP_VERSION << 10) | msg_type
        return struct.pack("!HII", ver_type, length, msg_id)

    def _send_msg(self, msg_type, body=b""):
        msg_id = self._next_msg_id()
        header = self._make_header(msg_type, HEADER_LEN + len(body), msg_id)
        name = MSG_NAMES.get(msg_type, f"type_{msg_type}")
        self._log(f">> {name} (id={msg_id})")
        try:
            self._sock.sendall(header + body)
        except OSError as e:
            self._log(f"Send error: {e}")
            self._running = False

    def _send_rospec_cmd(self, msg_type, rospec_id):
        """Send a message whose body is just a ROSpecID (uint32)."""
        self._send_msg(msg_type, struct.pack("!I", rospec_id))

    def _build_add_rospec(self):
        """Build ADD_ROSPEC body: a complete ROSpec TLV for simple inventory."""
        # ROSpecStartTrigger: Null (start manually via START_ROSPEC)
        start_trigger = struct.pack("!HHB", 179, 5, 0)

        # ROSpecStopTrigger: Null (stop manually via STOP_ROSPEC)
        stop_trigger = struct.pack("!HHBI", 182, 9, 0, 0)

        # ROBoundarySpec
        boundary_inner = start_trigger + stop_trigger
        boundary = struct.pack("!HH", 178, 4 + len(boundary_inner)) + boundary_inner

        # AISpecStopTrigger: Null
        ai_stop = struct.pack("!HHBI", 184, 9, 0, 0)

        # InventoryParameterSpec: ID=1, Protocol=EPCGlobalClass1Gen2
        inv_body = struct.pack("!HB", 1, 1)
        if self.reduced_power:
            power_index = POWER_INDEX_HALF
            # RFTransmitter (TLV 223): HopTableID=1, ChannelIndex=1, TransmitPower
            rf_tx = struct.pack("!HHHHH", 223, 10, 1, 1, power_index)
            # AntennaConfiguration (TLV 222): AntennaID=0 (all)
            ant_inner = struct.pack("!H", 0) + rf_tx
            ant_config = struct.pack("!HH", 222, 4 + len(ant_inner)) + ant_inner
            inv_body += ant_config
        inv_param = struct.pack("!HH", 186, 4 + len(inv_body)) + inv_body

        # AISpec: AntennaCount=1, AntennaID=0 (all antennas)
        ai_inner = struct.pack("!HH", 1, 0) + ai_stop + inv_param
        ai_spec = struct.pack("!HH", 183, 4 + len(ai_inner)) + ai_inner

        # TagReportContentSelector: enable AntennaID + PeakRSSI + TagSeenCount
        # Bit 12=AntennaID, bit 10=PeakRSSI, bit 7=TagSeenCount
        content_sel = struct.pack("!HHH", 238, 6, 0x1480)

        # ROReportSpec: report upon each tag (trigger=1, N=1)
        report_inner = struct.pack("!BH", 1, 1) + content_sel
        report_spec = struct.pack("!HH", 237, 4 + len(report_inner)) + report_inner

        # ROSpec: ID=1, Priority=0, CurrentState=Disabled(0)
        rospec_inner = struct.pack("!IBB", ROSPEC_ID, 0, 0)
        rospec_inner += boundary + ai_spec + report_spec
        rospec = struct.pack("!HH", 177, 4 + len(rospec_inner)) + rospec_inner

        return rospec

    # ── Parse LLRP messages ──

    def _recv_exact(self, n):
        """Read exactly n bytes from socket."""
        data = b""
        while len(data) < n and self._running:
            try:
                chunk = self._sock.recv(n - len(data))
            except OSError:
                return None
            if not chunk:
                return None
            data += chunk
        return data if len(data) == n else None

    def _recv_message(self):
        """Read one LLRP message. Returns (msg_type, msg_id, body) or None."""
        header = self._recv_exact(HEADER_LEN)
        if not header:
            return None

        ver_type, length, msg_id = struct.unpack("!HII", header)
        msg_type = ver_type & 0x03FF

        body_len = length - HEADER_LEN
        if body_len > 0:
            body = self._recv_exact(body_len)
            if body is None:
                return None
        else:
            body = b""

        return msg_type, msg_id, body

    def _check_status(self, body):
        """Check LLRPStatus in response body. Returns (ok, error_msg)."""
        if len(body) < 8:
            return True, ""
        param_type = struct.unpack("!H", body[0:2])[0]
        if param_type != 287:  # Not LLRPStatus
            return True, ""
        status_code = struct.unpack("!H", body[4:6])[0]
        if status_code == 0:
            return True, ""
        desc_len = struct.unpack("!H", body[6:8])[0]
        if desc_len > 0 and len(body) >= 8 + desc_len:
            desc = body[8:8 + desc_len].decode("utf-8", errors="replace")
            return False, f"Error {status_code}: {desc}"
        return False, f"Error {status_code}"

    def _parse_tag_reports(self, body):
        """Parse RO_ACCESS_REPORT body, yielding TagRead for each tag."""
        pos = 0
        while pos + 4 <= len(body):
            param_type = struct.unpack("!H", body[pos:pos + 2])[0]
            param_len = struct.unpack("!H", body[pos + 2:pos + 4])[0]
            if param_len < 4:
                break
            if param_type == 240:  # TagReportData
                tag = self._parse_single_tag(body[pos + 4:pos + param_len])
                if tag:
                    yield tag
            pos += param_len

    def _parse_single_tag(self, data):
        """Parse a single TagReportData value into TagRead."""
        pos = 0
        epc = None
        antenna = 0
        rssi = 0
        seen_count = 0

        while pos < len(data):
            # TV parameter (bit 7 set in first byte)
            if data[pos] & 0x80:
                tv_type = data[pos] & 0x7F
                pos += 1
                size = TV_PARAM_SIZES.get(tv_type)
                if size is None:
                    break  # Unknown TV type — can't determine size
                if pos + size > len(data):
                    break

                if tv_type == 1:    # AntennaID
                    antenna = struct.unpack("!H", data[pos:pos + 2])[0]
                elif tv_type == 6:  # PeakRSSI
                    rssi = struct.unpack("!b", data[pos:pos + 1])[0]
                elif tv_type == 8:  # TagSeenCount
                    seen_count = struct.unpack("!H", data[pos:pos + 2])[0]
                elif tv_type == 13: # EPC-96 (2 bytes pad + 12 bytes EPC)
                    epc = data[pos + 2:pos + 14].hex().upper()
                pos += size

            # TLV parameter (bit 15 clear)
            else:
                if pos + 4 > len(data):
                    break
                tlv_type = struct.unpack("!H", data[pos:pos + 2])[0]
                tlv_len = struct.unpack("!H", data[pos + 2:pos + 4])[0]
                if tlv_len < 4:
                    break
                if tlv_type == 241 and pos + 6 <= len(data):  # EPCData
                    epc_bits = struct.unpack("!H", data[pos + 4:pos + 6])[0]
                    epc_bytes = (epc_bits + 7) // 8
                    if pos + 6 + epc_bytes <= len(data):
                        epc = data[pos + 6:pos + 6 + epc_bytes].hex().upper()
                pos += tlv_len

        if epc:
            return TagRead(
                epc=epc, rssi=rssi, antenna=antenna,
                seen_count=seen_count, timestamp=time.time(),
            )
        return None

    # ── Main loop ──

    def _run(self):
        """Background thread: connect, handshake, receive loop."""
        try:
            self._do_connect()
        except Exception as e:
            self._log(f"Connection failed: {e}")
            self._set_state("disconnected")
            self._running = False
            return

        while self._running:
            result = self._recv_message()
            if result is None:
                if self._running:
                    self._log("Connection lost")
                break

            msg_type, msg_id, body = result
            name = MSG_NAMES.get(msg_type, f"type_{msg_type}")

            try:
                self._handle_message(msg_type, body, name)
            except Exception as e:
                self._log(f"Error handling {name}: {e}")

        self._running = False
        self._set_state("disconnected")
        try:
            if self._sock:
                self._sock.close()
        except OSError:
            pass
        self._sock = None

    def _do_connect(self):
        """Open TCP connection to reader."""
        self._set_state("connecting")
        self._log(f"Connecting to {self.host}:{self.port}...")
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5.0)
        sock.connect((self.host, self.port))
        sock.settimeout(10.0)
        self._sock = sock
        self._log("TCP connected, waiting for reader notification...")

    def _handle_message(self, msg_type, body, name):
        """Handle an incoming LLRP message (state machine)."""
        if msg_type == MSG_KEEPALIVE:
            self._send_msg(MSG_KEEPALIVE_ACK)
            return

        if msg_type == MSG_RO_ACCESS_REPORT:
            self._handle_tag_report(body)
            return

        if msg_type == MSG_READER_EVENT_NOTIFICATION:
            self._log(f"<< {name}")
            self._send_rospec_cmd(MSG_DELETE_ROSPEC, 0)  # Delete all ROSpecs
            self._set_state("setup")
            return

        if msg_type == MSG_DELETE_ROSPEC_RESPONSE:
            ok, err = self._check_status(body)
            self._log(f"<< {name} ({'OK' if ok else err})")
            if ok:
                power = "reduced" if self.reduced_power else "full"
                self._log(f"TX power: {power}")
                self._send_msg(MSG_ADD_ROSPEC, self._build_add_rospec())
            else:
                self._log(f"Setup failed at DELETE_ROSPEC: {err}")
                self._running = False
            return

        if msg_type == MSG_ADD_ROSPEC_RESPONSE:
            ok, err = self._check_status(body)
            self._log(f"<< {name} ({'OK' if ok else err})")
            if ok:
                self._send_rospec_cmd(MSG_ENABLE_ROSPEC, ROSPEC_ID)
            else:
                self._log(f"Setup failed at ADD_ROSPEC: {err}")
                self._running = False
            return

        if msg_type == MSG_ENABLE_ROSPEC_RESPONSE:
            ok, err = self._check_status(body)
            self._log(f"<< {name} ({'OK' if ok else err})")
            if ok:
                self._set_state("ready")
                self._log("Reader ready. Press Start to begin inventory.")
            else:
                self._log(f"Setup failed at ENABLE_ROSPEC: {err}")
                self._running = False
            return

        if msg_type == MSG_START_ROSPEC_RESPONSE:
            ok, err = self._check_status(body)
            self._log(f"<< {name} ({'OK' if ok else err})")
            if ok:
                self._set_state("inventorying")
                self._log("Inventory running")
            else:
                self._log(f"START_ROSPEC failed: {err}")
                self._set_state("ready")
            return

        if msg_type == MSG_STOP_ROSPEC_RESPONSE:
            ok, err = self._check_status(body)
            self._log(f"<< {name} ({'OK' if ok else err})")
            if ok:
                self._set_state("ready")
                self._log("Inventory stopped")
            else:
                self._log(f"STOP_ROSPEC failed: {err}")
            return

        self._log(f"<< {name} (len={len(body)})")

    def _handle_tag_report(self, body):
        """Process RO_ACCESS_REPORT: extract tags, update stats, fire callback."""
        now = time.time()
        for tag in self._parse_tag_reports(body):
            with self._lock:
                self._total_reads += 1
                self._unique_epcs.add(tag.epc)
                self._read_times.append(now)
            if self.on_tag_read:
                self.on_tag_read(tag)
