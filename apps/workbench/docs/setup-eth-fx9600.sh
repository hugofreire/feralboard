#!/usr/bin/env bash
# setup-eth-fx9600.sh — Configure direct Ethernet link between Pi and FX9600
# Run with: sudo bash setup-eth-fx9600.sh
set -euo pipefail

IFACE="eth0"
PI_IP="192.168.50.1"
FX_IP="192.168.50.2"
CIDR="24"
LLRP_PORT=5084
CON_NAME="fx9600-link"
FX_MAC="c4:7d:cc:74:53:27"
DNSMASQ_CONF="/etc/dnsmasq.d/fx9600.conf"

RED='\033[0;31m'
GRN='\033[0;32m'
YEL='\033[1;33m'
NC='\033[0m'

ok()   { echo -e "  ${GRN}[OK]${NC} $*"; }
fail() { echo -e "  ${RED}[FAIL]${NC} $*"; }
info() { echo -e "  ${YEL}[..]${NC} $*"; }

# ── Must be root ─────────────────────────────────────────────────────
if [[ $EUID -ne 0 ]]; then
  fail "Run as root:  sudo bash $0"
  exit 1
fi
ok "Running as root"

# ── Step 1: Check interface exists ───────────────────────────────────
echo ""
echo "── Step 1: Check interface ──────────────────────────────────"
if ! ip link show "$IFACE" &>/dev/null; then
  fail "Interface $IFACE not found. Available interfaces:"
  ip -br link
  exit 1
fi
ok "Interface $IFACE exists"

# ── Step 2: Check cable (carrier) ────────────────────────────────────
echo ""
echo "── Step 2: Check cable ──────────────────────────────────────"
ip link set "$IFACE" up 2>/dev/null || true
sleep 2

CARRIER=$(cat "/sys/class/net/$IFACE/carrier" 2>/dev/null || echo 0)
if [[ "$CARRIER" == "1" ]]; then
  ok "Cable detected on $IFACE"
else
  fail "No cable detected on $IFACE — plug in the Ethernet cable to the FX9600"
  echo ""
  info "Waiting up to 15s for cable..."
  for i in $(seq 1 15); do
    sleep 1
    CARRIER=$(cat "/sys/class/net/$IFACE/carrier" 2>/dev/null || echo 0)
    if [[ "$CARRIER" == "1" ]]; then
      ok "Cable detected after ${i}s"
      break
    fi
    printf "."
  done
  echo ""
  CARRIER=$(cat "/sys/class/net/$IFACE/carrier" 2>/dev/null || echo 0)
  if [[ "$CARRIER" != "1" ]]; then
    fail "Still no cable. Aborting — check physical connection."
    exit 1
  fi
fi

# ── Step 3: Configure static IP via NetworkManager ───────────────────
echo ""
echo "── Step 3: Assign static IP ($PI_IP/$CIDR on $IFACE) ───────"

if ! command -v nmcli &>/dev/null; then
  fail "nmcli not found — NetworkManager is required"
  exit 1
fi

# Remove existing connection profile if present, then recreate
if nmcli -t -f NAME con show 2>/dev/null | grep -q "^${CON_NAME}$"; then
  nmcli con delete "$CON_NAME" &>/dev/null
  info "Removed old '$CON_NAME' profile"
fi

nmcli con add \
  con-name "$CON_NAME" \
  ifname "$IFACE" \
  type ethernet \
  ipv4.addresses "${PI_IP}/${CIDR}" \
  ipv4.method manual \
  &>/dev/null

nmcli con up "$CON_NAME" &>/dev/null
sleep 1

ASSIGNED=$(ip -4 -o addr show dev "$IFACE" | grep -c "$PI_IP" || true)
if [[ "$ASSIGNED" -ge 1 ]]; then
  ok "$PI_IP/$CIDR assigned to $IFACE (persistent via NetworkManager)"
else
  fail "Could not assign IP"
  ip -4 addr show dev "$IFACE"
  exit 1
fi

# ── Step 4: DHCP server for FX9600 ──────────────────────────────────
echo ""
echo "── Step 4: DHCP server (dnsmasq on $IFACE) ─────────────────"

# Install dnsmasq if missing
if ! command -v dnsmasq &>/dev/null; then
  info "Installing dnsmasq..."
  apt-get install -y dnsmasq &>/dev/null
fi

mkdir -p /etc/dnsmasq.d

# Write config (eth0 only — does NOT touch wlan0)
cat > "$DNSMASQ_CONF" <<EOF
# DHCP server for FX9600 on eth0 only
# Does NOT affect wlan0 or any other interface
interface=$IFACE
bind-interfaces

dhcp-range=192.168.50.100,192.168.50.200,255.255.255.0,24h
dhcp-option=3,$PI_IP

# Give FX9600 a fixed IP based on its MAC
dhcp-host=$FX_MAC,$FX_IP,FX9600
EOF

# Ensure main config includes drop-in dir
if ! grep -q "conf-dir=/etc/dnsmasq.d" /etc/dnsmasq.conf 2>/dev/null; then
  echo "conf-dir=/etc/dnsmasq.d/,*.conf" >> /etc/dnsmasq.conf
fi

systemctl restart dnsmasq
systemctl enable dnsmasq &>/dev/null
ok "dnsmasq running — DHCP serving on $IFACE only"
info "FX9600 ($FX_MAC) will get fixed IP $FX_IP"

# ── Step 5: Wait for FX9600 ─────────────────────────────────────────
echo ""
echo "── Step 5: Ping FX9600 at $FX_IP ───────────────────────────"
info "FX9600 is in DHCP mode — waiting for it to pick up lease..."

FOUND=0
for i in $(seq 1 30); do
  if ping -c 1 -W 1 "$FX_IP" &>/dev/null; then
    FOUND=1
    break
  fi
  printf "."
  sleep 2
done
echo ""

if [[ "$FOUND" -eq 1 ]]; then
  ok "Ping $FX_IP succeeded"
else
  fail "Ping $FX_IP failed after 60s"
  info "FX9600 may still be booting. Try: ping $FX_IP"
  echo ""
fi

# ── Step 6: Check LLRP port ─────────────────────────────────────────
echo ""
echo "── Step 6: Check LLRP port $LLRP_PORT ──────────────────────"
if command -v nc &>/dev/null; then
  if nc -z -w 3 "$FX_IP" "$LLRP_PORT" 2>/dev/null; then
    ok "LLRP port $LLRP_PORT is open on $FX_IP — ready for RFID!"
  else
    fail "LLRP port $LLRP_PORT not reachable (reader may still be booting)"
  fi
else
  info "netcat (nc) not installed — skipping port check"
  info "Install with: sudo apt install netcat-openbsd"
fi

# ── Summary ──────────────────────────────────────────────────────────
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  Pi:    $PI_IP  ($IFACE)"
echo "  FX9600: $FX_IP  (via DHCP reservation, MAC $FX_MAC)"
echo "  LLRP:  port $LLRP_PORT"
echo ""
echo "  Quick test commands:"
echo "    ping $FX_IP"
echo "    nc -vz $FX_IP $LLRP_PORT"
echo "    curl http://$FX_IP   (reader web console)"
echo ""
echo "  Manage connection:"
echo "    nmcli con show $CON_NAME"
echo "    nmcli con down $CON_NAME"
echo "    nmcli con delete $CON_NAME"
echo ""
echo "  DHCP leases:"
echo "    cat /var/lib/misc/dnsmasq.leases"
echo "    journalctl -u dnsmasq -f"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
