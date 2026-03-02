#!/usr/bin/env bash
# Build FeralBoard firmware and flash it to ATmega4809 via serialUPDI.
# Usage: sudo bash build-and-flash.sh [--build-only | --flash-only]
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
# Source tree lives in src/ subdirectory
SRC_DIR="$SCRIPT_DIR/src"
cd "$SRC_DIR"

# ── Config ──────────────────────────────────────────────────
FQBN="MegaCoreX:megaavr:4809"
BOARD_OPTIONS="clock=internal_20MHz,pinout=48pin_standard,BOD=4v3,resetpin=gpio,bootloader=no_bootloader"
OUT_DIR="cli-build"
MEGACOREX_URL="https://mcudude.github.io/MegaCoreX/package_MCUdude_MegaCoreX_index.json"
REQUIRED_LIBS=("Adafruit BusIO" "MCP4725" "Adafruit MAX31856 library")

# Flash port (Pi 5 = AMA3, others = AMA4)
if [[ -f /proc/device-tree/model ]] && grep -q "Raspberry Pi 5" /proc/device-tree/model; then
  PORT="${PORT:-/dev/ttyAMA3}"
else
  PORT="${PORT:-/dev/ttyAMA4}"
fi
# Fallback: highest AMA (skip AMA0)
if [[ ! -e "$PORT" ]]; then
  PORT="$(ls -1 /dev/ttyAMA* 2>/dev/null | grep -E 'ttyAMA[1-9][0-9]*' | sort -V | tail -n1 || true)"
fi

AVRDUDE="/usr/local/bin/avrdude"
[[ ! -x "$AVRDUDE" ]] && AVRDUDE="avrdude"

# ── Parse args ──────────────────────────────────────────────
BUILD=true
FLASH=true
for arg in "$@"; do
  case $arg in
    --build-only) FLASH=false ;;
    --flash-only) BUILD=false ;;
    -h|--help)
      echo "Usage: sudo bash $0 [--build-only | --flash-only]"
      echo "  --build-only   Setup deps + compile, skip flashing"
      echo "  --flash-only   Skip build, flash existing hex from $OUT_DIR"
      exit 0 ;;
  esac
done

# ── 1. Install arduino-cli if missing ───────────────────────
echo "=== [1/5] Checking arduino-cli ==="
if ! command -v arduino-cli >/dev/null 2>&1; then
  echo "  Installing arduino-cli..."
  apt-get update -y
  apt-get install -y curl
  curl -fsSL https://raw.githubusercontent.com/arduino/arduino-cli/master/install.sh | sh
  install -m 755 -t /usr/local/bin bin/arduino-cli
  rm -rf bin
  echo "  Installed."
else
  echo "  Already installed: $(arduino-cli version 2>&1 | head -1)"
fi

# ── 2. Install avrdude if missing ───────────────────────────
echo "=== [2/5] Checking avrdude ==="
if ! command -v avrdude >/dev/null 2>&1 && [[ ! -x /usr/local/bin/avrdude ]]; then
  echo "  Installing avrdude..."
  apt-get update -y
  apt-get install -y avrdude
  echo "  Installed."
else
  echo "  Already installed: $($AVRDUDE -? 2>&1 | head -1 || echo 'ok')"
fi

# ── 3. Setup board core + libraries ────────────────────────
if $BUILD; then
  echo "=== [3/5] Setting up MegaCoreX core + libraries ==="
  arduino-cli config init >/dev/null 2>&1 || true
  if ! arduino-cli config dump 2>/dev/null | grep -q "$MEGACOREX_URL"; then
    arduino-cli config add board_manager.additional_urls "$MEGACOREX_URL"
  fi
  arduino-cli core update-index
  arduino-cli core install MegaCoreX:megaavr 2>/dev/null || true
  for lib in "${REQUIRED_LIBS[@]}"; do
    arduino-cli lib install "$lib" 2>/dev/null || true
  done

  # Patch: Adafruit MAX31856 library is missing clearFaultRegister() which
  # the FeralBoard firmware uses. Add it if not present.
  MAX_LIB_DIR="$(arduino-cli config dump --format json 2>/dev/null | python3 -c 'import sys,json; print(json.load(sys.stdin).get("directories",{}).get("user",""))' 2>/dev/null)/libraries/Adafruit_MAX31856_library"
  [[ ! -d "$MAX_LIB_DIR" ]] && MAX_LIB_DIR="/root/Arduino/libraries/Adafruit_MAX31856_library"
  if [[ -d "$MAX_LIB_DIR" ]] && ! grep -q "clearFaultRegister" "$MAX_LIB_DIR/Adafruit_MAX31856.h" 2>/dev/null; then
    echo "  Patching MAX31856 library (adding clearFaultRegister)..."
    sed -i 's/void setNoiseFilter(max31856_noise_filter_t noiseFilter);/void setNoiseFilter(max31856_noise_filter_t noiseFilter);\n  void clearFaultRegister(void);/' "$MAX_LIB_DIR/Adafruit_MAX31856.h"
    cat >> "$MAX_LIB_DIR/Adafruit_MAX31856.cpp" << 'PATCH'

void Adafruit_MAX31856::clearFaultRegister(void) {
  uint8_t val = readRegister8(MAX31856_CR0_REG);
  val |= MAX31856_CR0_FAULTCLR;
  writeRegister8(MAX31856_CR0_REG, val);
}
PATCH
    echo "  Patched."
  fi
  echo "  Core + libraries ready."

  # ── 4. Build ───────────────────────────────────────────────
  echo "=== [4/5] Building firmware ==="
  mkdir -p "$OUT_DIR"

  # Arduino requires the sketch dir name to match the .ino filename.
  # Copy source into a temp dir with the correct name.
  INO_FILE="$(ls -1 "$SRC_DIR"/*.ino 2>/dev/null | head -1 || true)"
  if [[ -z "$INO_FILE" ]]; then
    echo "  ERROR: No .ino file found in $SRC_DIR"
    exit 1
  fi
  INO_NAME="$(basename "$INO_FILE" .ino)"
  SKETCH_DIR="/tmp/${INO_NAME}"

  rm -rf "$SKETCH_DIR"
  cp -a "$SRC_DIR" "$SKETCH_DIR"
  # Rename .ino if the copied dir already has it (it should since we copied everything)

  echo "  Sketch: $INO_NAME"
  arduino-cli compile \
    --fqbn "$FQBN" \
    --board-options "$BOARD_OPTIONS" \
    --export-binaries \
    --output-dir "$SRC_DIR/$OUT_DIR" \
    "$SKETCH_DIR"

  rm -rf "$SKETCH_DIR"
  echo "  Build artifacts:"
  ls -lh "$SRC_DIR/$OUT_DIR"/*.hex 2>/dev/null || ls -lh "$SRC_DIR/$OUT_DIR"
else
  echo "=== [3/5] Skipped (--flash-only) ==="
  echo "=== [4/5] Skipped (--flash-only) ==="
fi

# ── 5. Flash ─────────────────────────────────────────────────
if $FLASH; then
  echo "=== [5/5] Flashing firmware ==="

  # Find the hex file
  HEX_FILE="$(ls -1 "$SRC_DIR/$OUT_DIR"/*.hex 2>/dev/null | head -1 || true)"
  if [[ -z "$HEX_FILE" || ! -f "$HEX_FILE" ]]; then
    echo "  ERROR: No .hex file found in $SRC_DIR/$OUT_DIR/"
    echo "  Run without --flash-only first to build."
    exit 1
  fi
  echo "  Hex file: $HEX_FILE"

  if [[ -z "$PORT" || ! -e "$PORT" ]]; then
    echo "  ERROR: No serial port found. Available:"
    ls -la /dev/ttyAMA* 2>/dev/null || echo "    none"
    echo "  Ensure dtoverlay=uart4 is in /boot/firmware/config.txt"
    exit 1
  fi
  echo "  Port: $PORT"

  echo "  Setting pre-programming fuse..."
  $AVRDUDE -p m4809 -c serialupdi -P "$PORT" -b 115200 \
    -U fuse5:w:0xC1:m

  echo "  Programming flash..."
  $AVRDUDE -p m4809 -c serialupdi -P "$PORT" -b 115200 \
    -e \
    -U "flash:w:${HEX_FILE}:i"

  echo "  Setting final fuses..."
  $AVRDUDE -p m4809 -c serialupdi -P "$PORT" -b 115200 \
    -U fuse0:w:0x00:m \
    -U fuse1:w:0xF4:m \
    -U fuse2:w:0x02:m \
    -U fuse5:w:0xC9:m \
    -U fuse6:w:0x06:m \
    -U fuse7:w:0x00:m \
    -U fuse8:w:0x00:m

  echo ""
  echo "  DONE - Firmware flashed successfully!"
else
  echo "=== [5/5] Skipped (--build-only) ==="
  echo ""
  echo "  DONE - Build complete. Flash later with: sudo bash $0 --flash-only"
fi
