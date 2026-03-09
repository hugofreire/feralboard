#!/bin/bash
#
# setup_display.sh - Configure display rotation, touch calibration,
#                    Sway background, and Plymouth splash screen
#
# Usage:
#   setup_display.sh -r <rotation> [-c <client>] [-b <background_image>]
#
# Options:
#   -r <rotation>     Screen rotation: 0, 90, 180, 270
#   -c <client>       Splash client: mercadona, ramalhos, custom (optional)
#   -b <image_path>   Custom background image path (optional)
#   -h                Show help
#
# Examples:
#   setup_display.sh -r 90 -c mercadona
#   setup_display.sh -r 270
#   setup_display.sh -r 90 -b /home/pi/my_wallpaper.png

set -euo pipefail

SWAY_CONFIG="/etc/sway/config.d/99-custom-config"
PLYMOUTH_DIR="/usr/share/desktop-base/active-theme/plymouth"
SPLASH_DIR="/home/pi/splash-screens"
CUSTOM_SPLASH_DIR="/home/pi/apps/feralboard/apps/pi-web/.pi/display-assets"
BOOT_FW="/boot/firmware"
LOG_FILE="/home/pi/logs/setup_display.log"

# Known touch device identifiers (MOSTRON needs both case variants)
TOUCH_DEVICES=(
    "8746:1:ILITEK____________EK-TI__IT"
    "9902:34054:WKS.cn_USB2IIC_CTP_CONTROL"
    "9902:34054:WKS.CN_USB2IIC_CTP_CONTROL"
    "8746:1:W.R.Inc._HID-Mouse"
    "1156:22352:QDtech_MPI7003"
)

log() {
    mkdir -p "$(dirname "$LOG_FILE")"
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a "$LOG_FILE"
}

show_usage() {
    echo "Usage: $0 -r <0|90|180|270> [-c <mercadona|ramalhos|custom>] [-b <image_path>]"
    echo ""
    echo "Options:"
    echo "  -r    Screen rotation in degrees (required)"
    echo "  -c    Client splash screens (mercadona, ramalhos, or custom)"
    echo "  -b    Custom background image path"
    echo "  -h    Show this help"
    exit 1
}

get_touch_matrix() {
    local rotation=$1
    case $rotation in
        0)   echo "1 0 0 0 1 0" ;;
        90)  echo "0 1 0 -1 0 1" ;;
        180) echo "-1 0 1 0 -1 1" ;;
        270) echo "0 -1 1 1 0 0" ;;
    esac
}

# ── 1. Update Sway config ──────────────────────────────────────────
update_sway_config() {
    local rotation=$1
    local bg_image=$2
    local touch_matrix
    touch_matrix=$(get_touch_matrix "$rotation")

    log "Updating Sway config: rotation=$rotation, background=$bg_image"

    sed -i "s/^output HDMI-A-1 transform .*/output HDMI-A-1 transform $rotation/" "$SWAY_CONFIG"
    sed -i "s|^output \* bg .* fill|output * bg $bg_image fill|" "$SWAY_CONFIG"

    for device in "${TOUCH_DEVICES[@]}"; do
        sed -i "/input \"$device\"/,/}/ s/calibration_matrix .*/calibration_matrix $touch_matrix/" "$SWAY_CONFIG"
    done

    log "Sway config updated successfully"
}

# ── 2. Update Plymouth / splash screens ────────────────────────────
update_splash_screens() {
    local client=$1

    if [ -z "$client" ]; then
        log "No client specified, skipping splash screen update"
        return
    fi

    local src_dir=""
    case $client in
        mercadona) src_dir="$SPLASH_DIR/mercadona-images" ;;
        ramalhos)  src_dir="$SPLASH_DIR/ramalhos-images" ;;
        custom)    src_dir="$CUSTOM_SPLASH_DIR" ;;
        *)
            log "ERROR: Unknown client '$client'"
            return 1
            ;;
    esac

    log "Updating splash screens for client: $client"

    cp "$src_dir/splash.png" "$BOOT_FW/splash.png"
    cp "$src_dir/splash-horizontal.png" "$BOOT_FW/splash-horizontal.png"
    cp "$src_dir/splash-horizontal.png" "$PLYMOUTH_DIR/"

    plymouth-set-default-theme text
    update-initramfs -u

    log "Splash screens updated for $client"
}

# ── 3. Render rotated fbi splash asset ─────────────────────────────
render_fbi_splash() {
    local rotation=$1

    log "Rendering fbi splash image for rotation: $rotation"

    local python_user="${SUDO_USER:-pi}"
    local python_path="/home/$python_user/.local/lib/python3.11/site-packages"

    if [ -d "$python_path" ]; then
        export PYTHONPATH="$python_path${PYTHONPATH:+:$PYTHONPATH}"
    fi

    python3 - "$rotation" "$BOOT_FW/splash.png" <<'PY'
import sys
from PIL import Image

rotation = int(sys.argv[1])
image_path = sys.argv[2]

angle_map = {
    0: 0,
    90: 270,
    180: 180,
    270: 90,
}

img = Image.open(image_path)
angle = angle_map.get(rotation, 0)
if angle:
    img = img.rotate(angle, expand=True)
img.save(image_path)
PY

    log "fbi splash image rendered successfully"
}

# ── 4. Update fbi splashscreen service ─────────────────────────────
update_fbi_service() {
    local service="/etc/systemd/system/splashscreen.service"
    perl -0pi -e 's#ExecStart=/usr/bin/fbi[^\n]*#ExecStart=/usr/bin/fbi -d /dev/fb0 --noverbose -a /boot/firmware/splash.png#' "$service"
    systemctl daemon-reload

    log "fbi splashscreen service updated"
}

ROTATION=""
CLIENT=""
BG_IMAGE=""

while getopts "r:c:b:h" opt; do
    case $opt in
        r) ROTATION=$OPTARG ;;
        c) CLIENT=$OPTARG ;;
        b) BG_IMAGE=$OPTARG ;;
        h) show_usage ;;
        *) show_usage ;;
    esac
done

if [[ -z "$ROTATION" ]]; then
    echo "Error: -r <rotation> is required"
    show_usage
fi

if [[ ! "$ROTATION" =~ ^(0|90|180|270)$ ]]; then
    echo "Error: rotation must be 0, 90, 180, or 270"
    exit 1
fi

if [ -z "$BG_IMAGE" ]; then
    BG_IMAGE="/boot/firmware/splash-horizontal.png"
fi

log "=== setup_display.sh starting ==="
log "Rotation: $ROTATION | Client: ${CLIENT:-none} | Background: $BG_IMAGE"

update_sway_config "$ROTATION" "$BG_IMAGE"
update_splash_screens "$CLIENT"
render_fbi_splash "$ROTATION"
update_fbi_service

log "=== setup_display.sh completed ==="
echo ""
echo "Display configuration updated:"
echo "  Rotation:   ${ROTATION}°"
echo "  Touch:      calibration matrix updated for all devices"
echo "  Background: $BG_IMAGE"
echo "  Client:     ${CLIENT:-unchanged}"
echo ""
echo "Restart Sway to apply changes:  swaymsg reload"
echo "Or reboot:                      sudo reboot"
