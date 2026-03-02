# Plan: Expedição Kiosk App

## Context

We need a new kiosk app "Expedição" for RFID-based shipping inventory validation. When selected from the Apps page, it shows a traffic-light UI with an order item list. The FX9600 RFID reader scans tags and checks them off against the order. For fast iteration, traffic lights are decoupled from digital inputs (DI0/DI1) and are directly clickable. Long-press on the title navigates back to the FeralBoard admin (home page).

## Files to Create

### 1. `kiosk_apps/expedicao/app.json`
App manifest with the `"page": "expedicao"` field (triggers custom page routing instead of kiosk greeting) and the embedded sample order JSON provided by the user.

### 2. `gui/pages/expedicao.py` — `ExpedicaoPage(Gtk.Box)`
The main page. Layout top-to-bottom:

**A. Title with long-press unlock**
- "Expedição" title in large bold white text
- EventBox with 2-second long-press timer → calls `on_unlock()` → navigates to "home"
- Same pattern as `gui/pages/kiosk.py:17-71`

**B. Traffic light row (horizontal, centered)**
- 3 large emoji buttons: 🔴 🟡 🟢 (off state: ⚫ ⚫ ⚫)
- Click one → exclusive activation (others turn ⚫)
- Tiny "Clear" button at the end → resets all to ⚫, stops RFID, resets item matches
- CSS: `.expedicao-light` (transparent bg, large font, 64x64 min size)

**C. RFID status label** (tiny, centered, below lights)
- Shows reader state with color-coded text

**D. Separator + Order header**
- Shows `Order: {order.id} | Dock {order.dock_number}` in section-title style

**E. Scrollable item list**
- Each row: circle emoji indicator + item name + EPC in tiny monospace
- Default: ⚫ neutral, matched: 🟢 green bg, unknown: 🔴 red bg
- CSS: `.expedicao-item-row`, `.expedicao-item-matched`, `.expedicao-item-unknown`

**Key methods:**
- `load_app(app_info)` — called by `_on_app_selected`, loads order, rebuilds list
- `_on_light_clicked(color)` — sets light, Yellow triggers RFID connect+inventory
- `_on_tag_read(tag)` → `GLib.idle_add(_process_tag)` — match EPC to items:
  - Known item → mark green, check if all complete → auto-Green
  - Unknown tag → add red row, auto-Red
- `_on_status_change(state)` — auto-start inventory when reader reaches "ready" while in Yellow
- `cleanup()` — stop RFID reader (called on page leave and app destroy)

**RFID integration:**
- Own `RfidReader` instance (host=192.168.50.2, port=5084, reduced_power=True)
- Callbacks marshaled to GTK via `GLib.idle_add()` (same pattern as `gui/pages/rfid.py`)

## Files to Modify

### 3. `gui/app.py`
- **Import**: `from gui.pages.expedicao import ExpedicaoPage`
- **Instantiate**: `self.expedicao_page = ExpedicaoPage(on_unlock=lambda: self.navigate_to("home"))`
- **Register**: `self.stack.add_named(self.expedicao_page, "expedicao")`
- **App pages dict**: `self._app_pages = {"expedicao": self.expedicao_page}`
- **Modify `_on_app_selected`**: check for `page` field → call `load_app()` + navigate to page; else fall through to existing greeting logic
- **Modify `navigate_to`**: when leaving "expedicao", call `cleanup()`
- **Modify `_on_destroy`**: add `self.expedicao_page.cleanup()`
- Note: "expedicao" is NOT added to `admin_pages` — header stays hidden (kiosk-style)

### 4. `gui/ipc.py`
- Add `"expedicao"` to valid pages tuple on line 55
- Update help text to include `expedicao` in navigate command

### 5. `gui/style.css`
Append new classes:
- `.expedicao-light` — transparent bg, large emoji, 64x64 min
- `.expedicao-light:hover` — subtle highlight
- `.expedicao-clear-btn` — small button styling
- `.expedicao-item-row` — dark card with border radius
- `.expedicao-item-matched` — green tint bg + green border
- `.expedicao-item-unknown` — red tint bg + red border

## Edge Cases
- **Empty order guard**: don't auto-Green when item list is empty
- **Reader disconnect during scan**: status label updates, light stays yellow, user can Clear or retry
- **Concurrent readers**: ExpedicaoPage and RfidPage have separate RfidReader instances; only one TCP connection possible — acceptable since they're never used simultaneously
- **Cleanup on navigate away**: `navigate_to()` calls `cleanup()` when leaving expedicao

## Verification
1. `pkill -f "python3.*gui/app.py" && bash scripts/run.sh &`
2. Navigate: Apps → select "Expedição"
3. Verify: title shows, traffic lights all ⚫, order items listed
4. Click each light emoji → verify exclusive toggle
5. Click Clear → verify all reset to ⚫
6. Click Yellow → verify RFID status shows connecting/inventorying
7. Scan a known tag → verify item row turns green
8. Scan all items → verify auto-Green
9. Long-press title (2s) → verify navigation to home page
10. Screenshot: `bash scripts/screenshot.sh` then read `screen.png`
