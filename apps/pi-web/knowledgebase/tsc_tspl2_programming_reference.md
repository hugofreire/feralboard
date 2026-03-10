# TSC TSPL/TSPL2 Programming Language Reference

> Extracted from: *TSPL/TSPL2 Programming Language Programming Manual* (189 pages)
> TSC AUTO ID Technology Co., Ltd. -- Covers all TSC bar code printer series

---

## Product Overview

TSPL and TSPL2 are the programming languages used to control TSC thermal label printers. Commands are sent as plain ASCII text terminated by CR+LF (0x0D 0x0A). Spaces (ASCII 32) are ignored in command lines. Expressions are enclosed in double quotes (ASCII 34) with a maximum length of 2048 bytes.

### Language Variants

- **TSPL** -- Original language for legacy printer models (TTP-243, TTP-342, TDP-643 Plus, etc.)
- **TSPL2** -- Enhanced language for newer models (TTP-244, TTP-245, TTP-343, TTP-246M, TTP-344M, TDP-245, M23, etc.)

Key differences: TSPL2 adds True Type Font support (font "0" and "ROMAN.TTF"), additional codepages (Windows 1250/1252/1253/1254), `BACKFEED` (vs `BACKUP`), `SET TEAR` (vs `SET STRIPER`), and 256-color PCX support.

### Supported Printer Models

The manual covers 39+ printer series including: TTP-243, TTP-244, TTP-244CE, TTP-245, TTP-245C, TTP-246M, TTP-247, TTP-248M, TTP-2410M, TDP-225, TDP-245, TDP-643 Plus, TDP-643R Plus, TTP-342, TTP-343, TTP-343C, TTP-344M, TTP-345, TTP-346M, TTP-384M, TTP-644M, M23, and their Plus/E/G/M sub-variants.

### Coordinate System

- **Origin (0,0):** Upper-left corner of the label (varies with DIRECTION setting)
- **Units:** Dots (default), inches, or millimeters
- **Resolution:** 203 DPI (1 mm = 8 dots), 300 DPI (1 mm = 12 dots)
- Positions are specified as `x` (horizontal) and `y` (vertical) in dots unless otherwise noted

---

## Setup and System Commands

### SIZE -- Define Label Dimensions

```
SIZE m,n                   (inches)
SIZE m mm,n mm             (millimeters)
SIZE m dot,n dot           (dots, firmware v6.27+)
```

| Parameter | Description |
|---|---|
| m | Label width |
| n | Label length |

Max width varies by model: 72 mm (M23), 104 mm (TTP-243 series), 106 mm (TTP-342 series), 108 mm (TTP-245/246M series), 219.5 mm (TTP-384M).

### GAP -- Set Label Gap Distance

```
GAP m,n                    (inches)
GAP m mm,n mm              (millimeters)
```

| Parameter | Description |
|---|---|
| m | Gap distance between two labels. 0 <= m <= 1 inch (0-25.4 mm) |
| n | Offset distance of the gap. n <= label length |
| 0,0 | Continuous label (no gap) |

### GAPDETECT -- Automatic Gap Calibration

```
GAPDETECT [x, y]
```

Feeds paper through gap sensor to determine label and gap sizes. If x,y parameters are omitted, the printer calibrates automatically.

### BLINEDETECT -- Automatic Black Mark Calibration

```
BLINEDETECT [x, y]
```

Feeds paper through black mark sensor to calibrate label and black mark sizes.

### AUTODETECT -- Automatic Sensor Calibration

```
AUTODETECT [x, y]
```

Automatically detects both gap and black mark sensors. Do not set GAP or BLINE commands when using AUTODETECT. *(Firmware v6.86EZ+)*

| Parameter | Description |
|---|---|
| x | Paper length (in dots) |
| y | Gap length (in dots) |

### BLINE -- Set Black Mark Parameters

```
BLINE m,n                  (inches)
BLINE m mm,n mm            (millimeters)
```

| Parameter | Description |
|---|---|
| m | Height of black line. 0 <= m <= 1 inch (0-25.4 mm) |
| n | Extra label feeding length. 0 <= n <= label length |
| 0,0 | Continuous label |

### OFFSET -- Label Feeding Offset

```
OFFSET m                   (inches)
OFFSET m mm                (millimeters)
```

| Parameter | Description |
|---|---|
| m | Offset distance. -1 <= m <= 1 inch. Used in peel-off/cutter mode to adjust label stop position |

### SPEED -- Print Speed

```
SPEED n
```

| Parameter | Description |
|---|---|
| n | Speed in inches per second. Available speeds vary by model: 1, 1.5, 2, 2.5, 3, 3.5, 4, 5, 6, 8, 10, 12 IPS |

### DENSITY -- Print Darkness

```
DENSITY n
```

| Parameter | Description |
|---|---|
| n | Darkness level 0-15 (0=lightest, 15=darkest). Default: 8 |

### DIRECTION -- Print Direction and Mirror

```
DIRECTION n[,m]
```

| Parameter | Description |
|---|---|
| n | 0 or 1 (print orientation/direction) |
| m | 0 = normal image (default), 1 = mirror image |

### REFERENCE -- Set Label Origin Point

```
REFERENCE x, y
```

| Parameter | Description |
|---|---|
| x | Horizontal coordinate (in dots) |
| y | Vertical coordinate (in dots) |

### SHIFT -- Vertical Position Adjustment

```
SHIFT n
```

| Parameter | Description |
|---|---|
| n | Vertical offset in dots. 203 DPI: -203 to 203; 300 DPI: -300 to 300 |

### COUNTRY -- Keyboard Layout

```
COUNTRY n
```

Sets keyboard layout for KP-200 portable keyboard. Values: 001 (USA), 002 (Canadian-French), 033 (French), 044 (UK), 049 (German), etc.

### CODEPAGE -- Character Set

```
CODEPAGE n
```

| Type | Values |
|---|---|
| 7-bit code pages | USA, BRI, GER, FRE, DAN, ITA, SPA, SWE, SWI |
| 8-bit code pages | 437 (US), 850 (Multilingual), 852 (Slavic), 860 (Portuguese), 863 (Canadian/French), 865 (Nordic), 857 (Turkish, TSPL2 only) |
| Windows code pages | 1250 (Central Europe), 1252 (Latin I), 1253 (Greek), 1254 (Turkish) -- TSPL2 only |

### CLS -- Clear Image Buffer

```
CLS
```

Must be placed after the SIZE command. Clears the image buffer before drawing new label content.

### FEED -- Feed Label Forward

```
FEED n
```

| Parameter | Description |
|---|---|
| n | Feed length in dots. 1 <= n <= 9999 |

### BACKFEED / BACKUP -- Feed Label in Reverse

```
BACKFEED n                 (TSPL2 printers)
BACKUP n                   (TSPL printers)
```

| Parameter | Description |
|---|---|
| n | Reverse feed length in dots. 1 <= n <= 9999 |

### FORMFEED -- Feed to Next Label

```
FORMFEED
```

Feeds label to the beginning of the next label.

### HOME -- Feed to Origin

```
HOME
```

Feeds label until the internal sensor determines the origin. SIZE and GAP must be defined before use.

### PRINT -- Print Labels

```
PRINT m [,n]
```

| Parameter | Description |
|---|---|
| m | Number of label sets to print. 1 <= m <= 999999999. Use -1 to reprint last label |
| n | Number of copies per label set. 1 <= n <= 999999999 |

### SOUND -- Beeper Control

```
SOUND level, interval
```

| Parameter | Description |
|---|---|
| level | Sound level: 0-9 |
| interval | Sound interval: 1-4095 |

### CUT -- Activate Cutter

```
CUT
```

Immediately cuts the label without back feeding.

### LIMITFEED -- Maximum Feed Distance

```
LIMITFEED n                (inches)
LIMITFEED n mm             (millimeters)
```

Sets maximum feeding length for gap detection. If the printer cannot locate a gap within this distance, the red LED flashes and feeding stops. Default: 10 inches.

### SELFTEST -- Print Printer Info

```
SELFTEST
```

Prints a self-test page with printer configuration information.

---

## Label Formatting Commands

### BAR -- Draw a Bar (Filled Rectangle)

```
BAR x, y, width, height
```

| Parameter | Description |
|---|---|
| x | Upper-left x-coordinate (dots) |
| y | Upper-left y-coordinate (dots) |
| width | Bar width (dots) |
| height | Bar height (dots). Max recommended: 12 dots at 4" width |

### BARCODE -- Print 1D Barcodes

```
BARCODE X, Y, "code type", height, human readable, rotation, narrow, wide, "code"
```

| Parameter | Description |
|---|---|
| X, Y | Barcode position (dots) |
| code type | Barcode symbology (see table below) |
| height | Bar code height (dots) |
| human readable | 0 = not readable, 1 = human readable text below barcode |
| rotation | 0, 90, 180, 270 degrees clockwise |
| narrow | Width of narrow element (dots) |
| wide | Width of wide element (dots) |
| code | Barcode data content |

**Supported 1D Barcode Types:**

| Code Type | Symbology | Max Digits | Narrow:Wide Ratios |
|---|---|---|---|
| `128` | Code 128 (auto subset switching) | unlimited | 1:1 (10x) |
| `128M` | Code 128 (manual subset switching) | unlimited | 1:1 (10x) |
| `EAN128` | EAN/UCC-128 (auto subset switching) | unlimited | 1:1 (10x) |
| `25` | Interleaved 2 of 5 | unlimited | 1:2, 1:3, 2:5 |
| `25C` | Interleaved 2 of 5 with check digit | unlimited | 1:2, 1:3, 2:5 |
| `39` | Code 39 (full ASCII for TSPL2, standard for TSPL) | unlimited | 1:2, 1:3, 2:5 |
| `39C` | Code 39 with check digit | unlimited | 1:2, 1:3, 2:5 |
| `39S` | Code 39 standard (TSPL2) | unlimited | 1:2, 1:3, 2:5 |
| `93` | Code 93 | unlimited | 1:3 |
| `EAN13` | EAN-13 | 12 | 1:1 (8x) |
| `EAN13+2` | EAN-13 with 2-digit add-on | 14 | 1:1 (8x) |
| `EAN13+5` | EAN-13 with 5-digit add-on | 17 | 1:1 (8x) |
| `EAN8` | EAN-8 | 7 | 1:1 (8x) |
| `EAN8+2` | EAN-8 with 2-digit add-on | 9 | 1:1 (8x) |
| `EAN8+5` | EAN-8 with 5-digit add-on | 12 | 1:1 (8x) |
| `CODA` | Codabar | unlimited | 1:2, 1:3, 2:5 |
| `POST` | Postnet | 5, 9, or 11 | 1:1 (1x) |
| `UPCA` | UPC-A | 11 | 1:1 (8x) |
| `UPCA+2` | UPC-A with 2-digit add-on | 13 | 1:1 (8x) |
| `UPCA+5` | UPC-A with 5-digit add-on | 16 | 1:1 (8x) |
| `UPCE` | UPC-E | 6 | 1:1 (8x) |
| `UPCE+2` | UPC-E with 2-digit add-on | 8 | 1:1 (8x) |
| `UPCE+5` | UPC-E with 5-digit add-on | 11 | 1:1 (8x) |
| `CPOST` | China Post | unlimited | 3:7 (1x) |
| `MSI` | MSI | unlimited | 1:3 |
| `MSIC` | MSI with check digit | unlimited | 1:3 |
| `PLESSEY` | Plessey | unlimited | 1:3 |
| `ITF14` | ITF-14 | 13 | 1:2, 1:3, 2:5 |
| `EAN14` | EAN-14 | 13 | 1:1 (8x) |
| `11` | Code 11 | unlimited | 1:2, 1:3, 2:5 |

**Example:**
```
BARCODE 100,100,"39",96,1,0,2,4,"1000"
BARCODE 10,10,"128M",48,1,0,2,2,"!104!096ABCD!101EFGH"
```

### BITMAP -- Draw Bitmap Image Data

```
BITMAP X, Y, width, height, mode, bitmap data...
```

| Parameter | Description |
|---|---|
| X, Y | Image position (dots) |
| width | Image width in bytes (not dots) |
| height | Image height in dots |
| mode | 0 = OVERWRITE, 1 = OR, 2 = XOR |
| bitmap data | Raw bitmap data bytes |

### BOX -- Draw Rectangle Outline

```
BOX X_start, Y_start, X_end, Y_end, line thickness
```

| Parameter | Description |
|---|---|
| X_start, Y_start | Upper-left corner (dots) |
| X_end, Y_end | Lower-right corner (dots) |
| line thickness | Line thickness (dots). Max recommended: 12 mm at 4" width |

### CIRCLE -- Draw Circle

```
CIRCLE X_start, Y_start, diameter, thickness
```

| Parameter | Description |
|---|---|
| X_start, Y_start | Upper-left corner position (dots) |
| diameter | Circle diameter (dots) |
| thickness | Circle line thickness (dots) |

### TEXT -- Print Text

```
TEXT X, Y, "font", rotation, x-multiplication, y-multiplication, "content"
```

| Parameter | Description |
|---|---|
| X, Y | Text position (dots) |
| font | Font name (see table below) |
| rotation | 0, 90, 180, 270 degrees clockwise |
| x-multiplication | Horizontal magnification 1-10. For font "0", specifies width in points |
| y-multiplication | Vertical magnification 1-10. For True Type fonts, specifies height in points |
| content | Text string. Use `\["]` to include double-quote characters |

**Available Fonts:**

| Font | Description |
|---|---|
| `0` | Monotype CG Triumvirate Bold Condensed (stretchable, TSPL2 only) |
| `1` | 8 x 12 fixed pitch dot font |
| `2` | 12 x 20 fixed pitch dot font |
| `3` | 16 x 24 fixed pitch dot font |
| `4` | 24 x 32 fixed pitch dot font |
| `5` | 32 x 48 fixed pitch dot font |
| `6` | 14 x 19 fixed pitch dot font (OCR-B) |
| `7` | 21 x 27 fixed pitch dot font (OCR-B) |
| `8` | 14 x 25 fixed pitch dot font (OCR-A) |
| `ROMAN.TTF` | Monotype CG Triumvirate Bold Condensed, fixed proportion (TSPL2 only) |

**Example:**
```
TEXT 100,100,"5",0,1,1,"Hello World"
TEXT 100,200,"ROMAN.TTF",0,1,20,"True Type Font"
TEXT 100,300,"0",0,12,24,"Scalable Font"
```

### REVERSE -- Reverse Image Region

```
REVERSE X_start, Y_start, X_width, Y_height
```

Inverts black/white in the specified rectangular region. Max recommended reversed area height: 12 mm at 4" width.

### ERASE -- Clear Image Region

```
ERASE X_start, Y_start, X_width, Y_height
```

Clears a specified rectangular region in the image buffer.

### PUTBMP -- Print BMP Image File

```
PUTBMP X, Y, "filename"
```

Prints a previously downloaded BMP format image at the specified position.

### PUTPCX -- Print PCX Image File

```
PUTPCX X, Y, "filename"
```

Prints a previously downloaded PCX format image. TSPL supports 2-color PCX; TSPL2 supports 256-color PCX.

---

## 2D Barcode Commands

### QRCODE -- QR Code

```
QRCODE X, Y, ECC Level, cell width, mode, rotation, [model, mask,] "data string"
```

| Parameter | Description |
|---|---|
| X, Y | Upper-left corner position (dots) |
| ECC Level | Error correction: L (7%), M (15%), Q (25%), H (30%) |
| cell width | Module size: 1-10 |
| mode | A = Auto encode, M = Manual encode |
| rotation | 0, 90, 180, 270 degrees |
| model | M1 = original (default), M2 = enhanced |
| mask | S0-S8, default S7 |

**Data capacity (Model 2, Version 40-L):** Numeric: 7,089 / Alphanumeric: 4,296 / Binary: 2,953 / Kanji: 1,817

**Manual mode data prefixes:** `A` = Alphanumeric, `N` = Numeric, `B` + 4-digit length = Binary, `K` = Kanji. Use `!` to switch between modes.

**Example:**
```
QRCODE 10,10,H,4,A,0,"ABCabc123"
QRCODE 100,10,M,7,M,0,M1,S1,"ATHE FIRMWARE HAS BEEN UPDATED"
```

### DMATRIX -- DataMatrix

```
DMATRIX x, y, width, height, [xm, row, col,] expression
```

| Parameter | Description |
|---|---|
| x, y | Start position (dots) |
| width, height | Expected barcode area size (dots) |
| xm | Module size (dots) |
| row | Symbol row size: 10-144 |
| col | Symbol column size: 10-144 |

Only ECC200 error correction is supported.

**Example:**
```
DMATRIX 10,110,400,400,"DMATRIX EXAMPLE 1"
DMATRIX 310,110,400,400,x6,"DMATRIX EXAMPLE 2"
```

### PDF417

```
PDF417 x, y, width, height, rotate, [option], expression
```

| Parameter | Description |
|---|---|
| x, y | Start position (dots) |
| width, height | Expected barcode area size (dots) |
| rotate | 0, 90, 180, 270 degrees |

**Options (placed between rotate and expression):**

| Option | Description |
|---|---|
| P0/P1 | Data compression: 0 = auto, 1 = binary |
| E0-E8 | Error correction level (0-8) |
| M0/M1 | Center pattern: 0 = upper-left, 1 = centered |
| Ux,y,c | Human readable at position x,y with c chars per line |
| W2-W9 | Module width (dots) |
| H4-H99 | Bar height (dots) |
| R | Maximum number of rows |
| C | Maximum number of columns |
| T0/T1 | Truncation: 0 = no, 1 = yes |
| Lm | Expression length (1-2048) |

**Example:**
```
PDF417 50,50,400,200,0,"Without Options"
PDF417 50,50,600,600,0,E4,W4,H4,R25,"Error correction level:4"
```

### AZTEC

```
AZTEC x, y, rotate, [size,] [ecp,] [flg,] [menu,] [multi,] [rev,] "content"
```

| Parameter | Description |
|---|---|
| x, y | Start position (dots) |
| rotate | 0, 90, 180, 270 degrees |
| size | Module size 1-20, default 6 |
| ecp | Error control: 0 = default, 1-99 = min error %, 101-104 = compact layers, 201-232 = full-range layers, 300 = Aztec Rune |
| flg | 0 = straight bytes, 1 = uses escape sequences |
| menu | Menu symbol: 0 = no, 1 = yes |
| multi | Number of symbols 1-26, default 6 |
| rev | Reversed output: 0 = no, 1 = yes |

*(Firmware v6.60EZ+)*

### MAXICODE

```
MAXICODE x, y, mode, [class, country, post, Lm,] "message"
```

| Mode | Syntax |
|---|---|
| 2 (USA) | `MAXICODE x, y, 2, class, country, postal_code, "message"` |
| 3 (Int'l) | `MAXICODE x, y, 3, class, country, postal_code, "message"` |
| 4, 5 | `MAXICODE x, y, mode, [Lm], "message"` |

For mode 2: postal code in 99999,9999 format. For other countries: up to 6 alphanumeric characters.

### RSS -- GS1 DataBar (RSS)

```
RSS x, y, "sym", rotate, pixMult, sepHt, "content"
RSS x, y, "RSSEXP", rotate, pixMult, sepHt, segWidth, "content"
RSS x, y, "UCC128CCA", rotate, pixMult, sepHt, linHeight, "content"
RSS x, y, "UCC128CCC", rotate, pixMult, sepHt, linHeight, "content"
```

**RSS Symbology Types:** RSS14, RSS14T (Truncated), RSS14S (Stacked), RSS14SO (Stacked Omnidirectional), RSSLIM (Limited), RSSEXP (Expanded), UPCA, UPCE, EAN13, EAN8, UCC128CCA, UCC128CCC.

| Parameter | Description |
|---|---|
| pixMult | Pixels per X: 1-10 |
| sepHt | Separator row height: 1-2 |
| segWidth | Segment width for RSS Expanded: even 2-22 |
| linHeight | UCC/EAN-128 height in X: 1-500 |

---

## Status Polling Commands (RS-232)

These commands query the printer status via the serial (RS-232) interface.

### ESC !? -- Get Printer Status (Immediate)

```
<ESC>!?
```

Returns one byte with printer status bits. Returns immediately even during errors.

| Bit | Status |
|---|---|
| 0 | Head opened |
| 1 | Paper jam |
| 2 | Out of paper |
| 3 | Out of ribbon |
| 4 | Pause |
| 5 | Printing |
| 6 | Cover opened (optional) |

| Hex Value | Meaning |
|---|---|
| 00 | Normal / ready |
| 01 | Head opened |
| 02 | Paper jam |
| 04 | Out of paper |
| 08 | Out of ribbon |
| 10 | Pause |
| 20 | Printing |
| 80 | Other error |

### ESC !R -- Reset Printer

```
<ESC>!R
```

Resets the printer. Downloaded files in memory are deleted. Cannot be sent in dump mode.

### ~!@ -- Query Mileage

```
~!@
```

Returns total print mileage (integer part) as ASCII, terminated by 0x0D. Only returns status when printer is ready.

### ~!A -- Query Free Memory

```
~!A
```

Returns free memory in bytes as decimal ASCII, terminated by 0x0D.

### ~!C -- Query RTC Presence

```
~!C
```

Returns 0 (no RTC) or 1 (RTC installed). For firmware before V6.xx only.

### ~!D -- Enter Dump Mode

```
~!D
```

Enters DUMP mode where the printer outputs received data directly without interpretation.

### ~!F -- Query Stored Files

```
~!F
```

Returns filenames stored in printer memory (ASCII). Each filename ends with 0x0D, final entry ends with 0x1A.

### ~!I -- Query Code Page and Country

```
~!I
```

Returns current code page and country setting (e.g., `437, 001`).

### ~!T -- Query Printer Model

```
~!T
```

Returns the printer model name as an ASCII string.

---

## File Management Commands

### DOWNLOAD -- Save Files to Printer Memory

**Program files:**
```
DOWNLOAD [n,] "FILENAME.BAS"
... program content ...
EOP
```

**Data files (images, fonts, text):**
```
DOWNLOAD [n,] "FILENAME", DATA SIZE, DATA CONTENT...
```

| Parameter | Description |
|---|---|
| n | Memory location: omitted = DRAM (volatile), F = Flash, E = Expansion module |
| FILENAME.BAS | Program filename (case-sensitive, 8.3 format, must end in .BAS) |
| DATA SIZE | Size of data content in bytes |

**Storage limits:** 50 files in DRAM; 50 (TSPL) or 256 (TSPL2) files in Flash.

If a file named `AUTO.BAS` exists in printer memory, it executes automatically on printer startup.

### EOP -- End of Program

```
EOP
```

Marks the end of a downloaded program file. Must be paired with DOWNLOAD.

### FILES -- List Stored Files

```
FILES
```

Prints a label listing all files stored in printer memory.

### KILL -- Delete File

```
KILL "FILENAME"
```

Deletes a specified file from printer memory (case-sensitive).

### MOVE -- Copy DRAM to Flash

```
MOVE
```

Copies all files from volatile DRAM to non-volatile Flash memory.

### RUN -- Execute Program

```
RUN "FILENAME.BAS"
```

Executes a previously downloaded BASIC program file.

---

## BASIC Commands and Functions

TSPL/TSPL2 includes a built-in BASIC-like scripting language for downloaded programs (.BAS files).

### Control Flow

| Command | Description |
|---|---|
| `FOR var = start TO end ... NEXT` | For-Next loop |
| `IF ... THEN ... ELSE ... ENDIF` | Conditional branching |
| `GOSUB label ... RETURN` | Subroutine call |
| `GOTO label` | Unconditional jump |
| `END` | Terminate program |
| `REM` | Comment line |

### String Functions

| Function | Description |
|---|---|
| `LEFT$(string, n)` | First n characters |
| `RIGHT$(string, n)` | Last n characters |
| `MID$(string, start, length)` | Substring extraction |
| `LEN(string)` | String length |
| `STR$(number)` | Number to string |
| `VAL(string)` | String to number |
| `CHR$(n)` | ASCII code to character |
| `ASC(string)` | Character to ASCII code |
| `TRIM$(string)` | Remove leading/trailing spaces |
| `LTRIM$(string)` | Remove leading spaces |
| `RTRIM$(string)` | Remove trailing spaces |
| `STRCOMP(s1, s2)` | Compare two strings (0=equal) |
| `INSTR(start, s1, s2)` | Find substring position |
| `FORMAT$(datetime, format)` | Format date/time string |
| `NOW$()` | Current date/time string |

### Numeric Functions

| Function | Description |
|---|---|
| `ABS(n)` | Absolute value |
| `INT(n)` | Integer part (truncate) |

### I/O Functions

| Command/Function | Description |
|---|---|
| `OPEN "filename" FOR mode AS #n` | Open file for INPUT/OUTPUT/APPEND |
| `WRITE #n, data` | Write to file |
| `READ #n, var` | Read from file |
| `SEEK #n, position` | Set file pointer position |
| `LOF(#n)` | Length of file |
| `EOF(#n)` | End of file check |
| `FREAD$(#n, length)` | Read specified bytes from file |
| `INPUT "prompt", var` | Read input from keyboard/host |
| `INP$(port, length, timeout)` | Read from communication port |
| `OUT "data"` | Send data to communication port |
| `GETKEY()` | Read keypad button press |
| `BEEP` | Sound the beeper |

---

## Device Reconfiguration Commands

These SET commands configure printer hardware behavior. Settings are saved in printer memory (persist across power cycles) unless noted otherwise.

### SET COUNTER -- Define Counter Variable

```
SET COUNTER @n step
@n = "expression"
```

| Parameter | Description |
|---|---|
| @n | Counter number (0-50, i.e. @0 through @50) |
| step | Increment per print. -999999999 to 999999999. Use 0 for fixed variables |
| expression | Initial value string (max 101 bytes). Supports digit (0-9), lowercase (a-z), uppercase (A-Z) cycling |

### SET CUTTER -- Cutter Control

```
SET CUTTER OFF/BATCH/pieces
```

| Parameter | Description |
|---|---|
| OFF | Disable cutter |
| BATCH | Cut at end of print job |
| pieces | Cut every N labels (0-65535) |

### SET PARTIAL_CUTTER -- Partial Cut (No Backfeed)

```
SET PARTIAL_CUTTER OFF/BATCH/pieces
```

Same parameters as SET CUTTER but prevents label backfeed after cutting.

### SET BACK -- Backfeed After Cut

```
SET BACK OFF/ON
```

Controls whether the printer backfeeds after cutting.

### SET PEEL -- Self-Peeling Function

```
SET PEEL ON/OFF
```

When ON, the printer pauses after each label and waits for the label to be removed before printing the next one.

### SET TEAR / SET STRIPER -- Tear-Off Position

```
SET TEAR ON/OFF              (TSPL2 printers)
SET STRIPER ON/OFF           (TSPL printers)
```

When ON, the label gap is positioned at the tear-off bar after printing.

### SET RIBBON -- Thermal Mode

```
SET RIBBON ON/OFF
```

| Parameter | Description |
|---|---|
| ON | Thermal transfer printing (uses ribbon) |
| OFF | Direct thermal printing (no ribbon) |

This setting is NOT saved in printer memory.

### SET HEAD -- Head Open Sensor

```
SET HEAD ON/OFF
```

Enables/disables the print head open detection sensor.

### SET GAP -- Gap Sensor Sensitivity

```
SET GAP n/AUTO/OFF/0,/REVERSE/OBVERSE
```

| Parameter | Description |
|---|---|
| n | Sensor sensitivity value (range varies by model, e.g. 0-255) |
| AUTO | Auto-calibrate by feeding 2-3 labels |
| OFF | Disable auto gap detection |
| 0, | Auto-calibrate gap size |
| REVERSE | Detect gap using inverted sensor logic (for front-side black marks) |
| OBVERSE | Disable REVERSE mode |

### SET COM1 -- Serial Port Configuration

```
SET COM1 baud, parity, data, stop
```

| Parameter | Values |
|---|---|
| baud | 24 (2400), 48 (4800), 96 (9600), 19 (19200), 38 (38400), 57 (57600), 115 (115200) |
| parity | N (none), E (even), O (odd) |
| data | 7 or 8 bits |
| stop | 1 or 2 stop bits |

**Example:** `SET COM1 96,N,8,1` (9600 baud, no parity, 8 data bits, 1 stop bit)

### SET PRINTKEY -- FEED Button Printing

```
SET PRINTKEY OFF/ON/AUTO/num
```

| Parameter | Description |
|---|---|
| OFF | Disable |
| ON / AUTO | Print one label per FEED key press with counter increment |
| num | Print N labels per FEED key press |

### SET REPRINT -- Reprint After Error

```
SET REPRINT ON/OFF
```

Enables/disables automatic reprint of the last label after "no paper", "no ribbon", or "carriage open" errors.

### SET KEY1 / KEY2 / KEY3 -- Button Control

```
SET KEY1 ON/OFF
SET KEY2 ON/OFF
SET KEY3 ON/OFF
```

Enable/disable physical button functions (KEY1=MENU, KEY2=PAUSE, KEY3=FEED).

### SET LED1 / LED2 / LED3 -- LED Control

```
SET LED1 ON/OFF
SET LED2 ON/OFF
SET LED3 ON/OFF
```

Enable/disable default LED functions. When OFF, LEDs can be controlled programmatically via `LEDn = 0/1`.

### LED1 / LED2 / LED3 -- Direct LED Control

```
LEDm = n
```

Set LED state directly (write-only). m = 1/2/3, n = 0 (off) or 1 (on). Must disable default LED functions first with SET LEDn OFF.

### KEY1 / KEY2 / KEY3 -- Read Button State

```
KEYm
```

Read-only variable returning button press state. Used in BASIC programs for interactive logic.

### PEEL -- Read Peel Sensor

```
PEEL
```

Read-only. Returns 0 (no paper on sensor) or 1 (paper present on peel sensor).

---

## Printer Global Variables

Date/time variables are available when the optional RTC (Real Time Clock) is installed.

| Variable | Description | Format |
|---|---|---|
| `@LABEL` | Current label count | Integer |
| `YEAR` | Year (legacy, 2-digit) | 00-99 |
| `MONTH` | Month (legacy) | 01-12 |
| `DATE` | Date (legacy) | 01-31 |
| `WEEK` | Day of week (legacy) | 0-6 (Sun-Sat) |
| `HOUR` | Hour (legacy) | 00-23 |
| `MINUTE` | Minute (legacy) | 00-59 |
| `SECOND` | Second (legacy) | 00-59 |
| `@YEAR` | Year (4-digit) | e.g. "2009" |
| `@MONTH` | Month | "01"-"12" |
| `@DATE` | Date | "01"-"31" |
| `@DAY` | Day of week | "01"-"07" |
| `@HOUR` | Hour | "00"-"23" |
| `@MINUTE` | Minute | "00"-"59" |
| `@SECOND` | Second | "00"-"59" |

The `@`-prefixed date/time variables are string variables usable in TEXT and BARCODE commands.

---

## Windows Driver Commands

These low-level commands are used by TSC Windows printer drivers:

| Command | Syntax | Description |
|---|---|---|
| `!B` | `!Bnnn` | Store nnn bytes of bitmap image data |
| `!J` | `!Jnnnn` | Print bitmap at y-position nnnn |
| `!N` | `!Nnnn` | Print nnn copies of label |

---

## Message Translation Protocol

```
~#Prompt~&[@0]
~#Prompt~&[@1]
```

Sends prompt messages to the KP-200 portable LCD keyboard. `@0` displays on LCD line 1, `@1` displays on LCD line 2.

---

## Quick Reference: Common Label Printing Sequence

A typical TSPL/TSPL2 label program follows this pattern:

```
SIZE 4,2.5                          ; Label size (inches)
GAP 0.12,0                         ; Gap between labels
SPEED 4                            ; Print speed (IPS)
DENSITY 8                          ; Darkness level
DIRECTION 0                        ; Print direction
REFERENCE 0,0                      ; Origin point
OFFSET 0                           ; Feed offset
SET CUTTER OFF                     ; Cutter control
SET PEEL OFF                       ; Peel mode
SET TEAR ON                        ; Tear-off positioning
CLS                                ; Clear image buffer
TEXT 50,50,"3",0,1,1,"Hello"       ; Add text
BARCODE 50,100,"128",96,1,0,2,2,"12345"  ; Add barcode
QRCODE 400,50,M,4,A,0,"DATA"      ; Add QR code
BOX 10,10,780,380,2                ; Add border
PRINT 1,1                          ; Print 1 set, 1 copy
```

---

## Supported Barcode Symbologies Summary

| Category | Symbologies |
|---|---|
| **1D Linear** | Code 128, Code 128M, EAN-128, Code 39, Code 39C, Code 39S, Code 93, Code 11, Codabar, MSI, MSI+Check, Plessey, Interleaved 2 of 5, I2of5+Check, ITF-14, EAN-14 |
| **1D Retail** | EAN-13 (+2/+5), EAN-8 (+2/+5), UPC-A (+2/+5), UPC-E (+2/+5), China Post |
| **1D Postal** | Postnet |
| **2D Matrix** | QR Code (M1/M2), DataMatrix (ECC200), PDF417, Aztec, MaxiCode |
| **2D Composite** | GS1 DataBar (RSS14, RSS14T, RSS14S, RSS14SO, RSSLIM, RSSEXP), UCC/EAN-128 with CC-A/B/C |
