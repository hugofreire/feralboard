# Zebra FX9600 RFID Reader — Pi Setup Guide

## Hardware

| Item | Detail |
|------|--------|
| Reader | Zebra FX9600 |
| Hostname | FX9600745327 |
| MAC address | `c4:7d:cc:74:53:27` |
| Ethernet | 100 Mb/s (reader only supports 10/100) |
| LLRP port | `5084` |

## Network Topology

```
Pi (eth0)                 FX9600
192.168.50.1  ──────────  192.168.50.2
              Ethernet
              (direct cable)

Pi (wlan0)
  └── WiFi (unchanged, do NOT touch)
```

## Key Learnings

### 1. FX9600 is in DHCP mode (not static)
The reader ships in DHCP mode and expects a DHCP server. Without one, it has no IP and is invisible to ARP scans — even though the Ethernet link (carrier) shows UP.

### 2. NetworkManager, not dhcpcd
This Pi runs **NetworkManager** (`nmcli`), not `dhcpcd`. Any config written to `/etc/dhcpcd.conf` is ignored because dhcpcd is inactive.

- Use `nmcli` to configure static IPs on eth0
- The connection profile `fx9600-link` persists across reboots

### 3. dnsmasq provides DHCP on eth0 only
We run dnsmasq as a DHCP server **bound exclusively to eth0** so it doesn't interfere with WiFi (wlan0).

- Config: `/etc/dnsmasq.d/fx9600.conf`
- The FX9600 MAC is reserved to always get `192.168.50.2`
- DHCP range for other devices: `192.168.50.100–200`

### 4. The reader takes time
- Boot time: ~2–3 minutes from power-on to network ready
- DHCP lease pickup: ~15–30 seconds after DHCP server is available
- Solid green LED = booted and running

### 5. Factory default IP won't work with direct cable
The FX9600 factory default IP is `192.168.0.254` (when set to static), but our unit is in DHCP mode. Scanning `192.168.0.0/24` found nothing.

## Quick Setup

```bash
sudo bash /home/pi/apps/fx9600/setup-eth-fx9600.sh
```

This script:
1. Checks eth0 exists and cable is connected
2. Creates a NetworkManager profile (`fx9600-link`) with static IP `192.168.50.1/24`
3. Installs/configures dnsmasq as DHCP server on eth0 only
4. Waits for FX9600 to get its lease (`192.168.50.2`)
5. Verifies ping and LLRP port 5084

## Manual Commands

### Check connectivity
```bash
ping 192.168.50.2
nc -vz 192.168.50.2 5084
curl http://192.168.50.2          # web console (HTTP 403 = needs auth)
```

### Network config
```bash
nmcli con show fx9600-link        # view connection details
nmcli con up fx9600-link          # bring up
nmcli con down fx9600-link        # bring down
nmcli con delete fx9600-link      # remove entirely
ip addr show dev eth0             # check current IP
```

### DHCP server
```bash
sudo systemctl status dnsmasq     # check status
sudo systemctl restart dnsmasq    # restart
cat /var/lib/misc/dnsmasq.leases  # view active leases
journalctl -u dnsmasq -f          # watch DHCP in real time
```

### Discovery / debugging
```bash
sudo arp-scan --interface=eth0 192.168.50.0/24   # scan subnet
cat /sys/class/net/eth0/carrier                    # 1 = cable connected
sudo ethtool eth0                                  # link speed, negotiation
```

## Files

| File | Purpose |
|------|---------|
| `setup-eth-fx9600.sh` | One-shot setup script |
| `/etc/dnsmasq.d/fx9600.conf` | DHCP config (eth0 only) |
| `/etc/dnsmasq.conf` | Main dnsmasq config (includes drop-in dir) |
| `/var/lib/misc/dnsmasq.leases` | Active DHCP leases |

## Web Console

The FX9600 web console is at `http://192.168.50.2`. Default credentials are typically:
- Username: `admin`
- Password: `change` (Zebra default)

## Troubleshooting

| Symptom | Cause | Fix |
|---------|-------|-----|
| No IP on eth0 after reboot | NM profile not active | `nmcli con up fx9600-link` |
| arp-scan finds nothing | FX9600 has no IP (DHCP mode, no server) | Ensure dnsmasq is running: `sudo systemctl start dnsmasq` |
| Carrier=1 but no ping | Reader still booting or DHCP not served | Wait 2–3 min, check `journalctl -u dnsmasq -f` |
| Ping works but LLRP port closed | Reader still initializing | Wait 30s after ping works, retry `nc -vz 192.168.50.2 5084` |
| WiFi broke | dnsmasq listening on wrong interface | Check `/etc/dnsmasq.d/fx9600.conf` has `interface=eth0` and `bind-interfaces` |
