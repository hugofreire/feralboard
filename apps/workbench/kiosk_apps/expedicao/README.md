# Expedição - RFID Inventory Validation

Kiosk app that validates shipping orders by scanning RFID-tagged items against an expected inventory list using a Zebra FX9600 reader.

## How It Works

The app is driven by two digital inputs from the FeralBoard:

| DI0 | DI1 | State | Behavior |
|-----|-----|-------|----------|
| OFF | -   | OFF (all black) | System inactive, blank screen |
| ON  | OFF | RED | System active but scan not enabled |
| ON  | ON  | YELLOW | Order list loads, RFID scan starts |

Once scanning (yellow), the traffic light auto-transitions based on results:

- **GREEN** - All order items matched, no unknown tags. Scan stops automatically.
- **RED** - An RFID tag was detected that is not in the order. The unknown tag appears as a red row at the bottom of the list.

To start a new scan cycle after green/red, toggle DI1 off then on again.

## Traffic Light (top row)

Three large emoji circles displayed horizontally. Only one is lit at a time:

```
OFF:    [black] [black] [black]
RED:    [red]   [black] [black]
YELLOW: [black] [yellow][black]
GREEN:  [black] [black] [green]
```

## Order List (middle)

Shown only during yellow/green/red-from-scan states. Displays:

- **Header**: Order ID and dock number
- **Item rows**: Item name + EPC in monospace. Each row has a status indicator:
  - Black circle = not yet scanned
  - Green circle + green border = matched
  - Red circle + red border = unknown tag (not in order)

## RFID Reader

- **Reader**: Zebra FX9600 at `192.168.50.2:5084` (LLRP protocol)
- **Power**: Reduced (15 dBm) for close-range scanning
- **Connection**: Auto-connects when entering yellow state, auto-disconnects on green completion or state change

## Digital Inputs

- **DI0** (RX byte 4, bit 0): System enable. Must be HIGH to activate.
- **DI1** (RX byte 4, bit 1): Scan enable. When HIGH (with DI0 HIGH), starts RFID inventory.

## Navigation

- **Long-press title** (2 seconds) on "Expedição" to return to the FeralBoard admin (home page)
- Select from **Apps** page in the admin area to launch

## Order Configuration

Edit `app.json` in this directory. The `order.inventory_check.items` array defines the expected items:

```json
{
  "epc": "00000001FFFF000000008100",
  "name": "Motor Controller Unit A1"
}
```

Each item's `epc` is matched (case-insensitive) against tags read by the FX9600.

## Files

| File | Purpose |
|------|---------|
| `app.json` | App manifest + order data |
| `README.md` | This file |
| `../../gui/pages/expedicao.py` | GTK page implementation |
