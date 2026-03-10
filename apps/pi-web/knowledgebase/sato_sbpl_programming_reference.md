# SATO SBPL Programming Reference

> Extracted from: **SBPL Programming Guide Basic Command** (Ver 01.20.01, 94 pages) and **CL4NX Plus / CL6NX Plus Programming Reference** (619 pages).

## Overview

**SBPL (SATO Barcode Printer Language)** is a high-level printer control language used to define label formats and control label printing on all SATO barcode printers.

### Supported Printers

SBPL is the shared programming language across all SATO printer families:

| Family | Models |
| --- | --- |
| CL4NX Plus / CL6NX Plus | Industrial 4" and 6" printers (203/305/609 dpi) |
| CT4-LX | Compact desktop printer |
| WS2 | Desktop printer |
| WT4 | Portable printer |
| CL4e / CL6e series | CL408e, CL412e, CL608e, CL612e |
| CT series | CT400DT/TT, CT410DT/TT |
| M-8400RVe | Industrial printer |

### How SBPL Works

- Commands are sent as **escape sequences**: ESC character (0x1B) followed by command code
- In documentation, `<A>` means `ESC + A` (i.e., `0x1B 0x41`)
- Every label print job is wrapped between `<A>` (start) and `<Z>` (end)
- Positions are specified in **dots** (1 dot = 0.125mm at 203dpi, 0.083mm at 305dpi, 0.042mm at 609dpi)
- Commands between `<A>` and `<Z>` are reset to defaults when `<Z>` is issued, except system commands

### Basic Label Structure

```
<A>                          Start data block
<A1>08000640                 Label size: 800 dots high x 640 dots wide
<CS>4                        Print speed: 4 inch/s
<#F>5A                       Print darkness: level 5
<V>100<H>50<L>0404<XB>1SATO  Print "SATO" with XB font, 4x enlarged, smoothed
<V>350<H>100<B>104250*12345* Print CODE39 barcode
<Q>1                         Print 1 label
<Z>                          End data block
```

---

## Control Commands

| Command | ESC Code | Function | Format |
| --- | --- | --- | --- |
| `<A>` | ESC+A | Start data block | `<A>` |
| `<Z>` | ESC+Z | End data block (resets most settings) | `<Z>` |
| `<Q>` | ESC+Q | Print quantity (1-999999) | `<Q>aaaaaa` |
| `<ID>` | ESC+ID | Job ID number for status return (00-99) | `<ID>aa` |
| `<WK>` | ESC+WK | Job name for status return (max 16 ASCII / 8 Kanji) | `<WK>a-a` |
| `<CR>` | ESC+CR | Status 5 reply check setting | `<CR>` |

### Start/Stop Code Notes

- `<A>` must always be paired with `<Z>` -- printing does not start without both
- All command settings (except system commands) reset to defaults when `<Z>` is issued
- `<Q>` specifies how many labels to print from this `<A>`...`<Z>` block

---

## Print Position Commands

| Command | ESC Code | Function | Format |
| --- | --- | --- | --- |
| `<H>` | ESC+H | Horizontal print position (dots from start point) | `<H>aaaa` |
| `<V>` | ESC+V | Vertical print position (dots from start point) | `<V>aaaa` |

### Print Area Limits (dots)

| Model | Head DPI | H Max | V Max |
| --- | --- | --- | --- |
| CL4NX Plus (203 dpi) | 203 | 832 | 20000 |
| CL4NX Plus (305 dpi) | 305 | 1248 | 18000 |
| CL4NX Plus (609 dpi) | 609 | 2496 | 9600 |
| CL408e / M-8400RVe | 203 | 832 | 1424 |
| CL412e | 305 | 1248 | 2136 |
| CL608e | 203 | 1216 | 1424 |
| CL612e | 305 | 1984 | 2136 |
| CT400DT/TT | 203 | 832 | 3200 |
| CT410DT/TT | 305 | 1248 | 4800 |

---

## Modification Commands

| Command | ESC Code | Function | Format |
| --- | --- | --- | --- |
| `<P>` | ESC+P | Character pitch in dots (default 02, range 0-99) | `<P>aa` |
| `<L>` | ESC+L | Enlargement ratio, H and V (01-12 each) | `<L>aabb` |
| `<E>` | ESC+E | Automatic line feed pitch (0-999 dots) | `<E>aaa` |
| `<%>` | ESC+% | Rotation (0=0deg, 1=90deg, 2=180deg, 3=270deg) | `<%>a` |
| `<PS>` | ESC+PS | Enable proportional pitch (XU-XL fonts) | `<PS>` |
| `<PR>` | ESC+PR | Cancel proportional pitch (return to fixed) | `<PR>` |
| `<F>` | ESC+F | Sequential number printing | `<F>aaaabcccc,dd,ee,f` |
| `<FW>` | ESC+FW | Ruled line / grid / frame print | see below |
| `<FC>` | ESC+FC | Print circle | `<FC>` |
| `<FT>` | ESC+FT | Print triangle | `<FT>` |
| `<(>` | ESC+( | Reverse color (black/white inversion) print | `<(>aaaa,bbbb` |
| `<0>` | ESC+0 | Partial edit (modify previous print data) | `<0>` |
| `<WD>` | ESC+WD | Partial copy within a label | `<WD>VaaaaHbbbbYccccXdddd` |
| `<J>` | ESC+J | Journal print mode | `<J>` |
| `<RM>` | ESC+RM | Mirror image print | `<RM>` |
| `<AL>` | ESC+AL | Field alignment | `<AL>` |

### Enlargement `<L>`

```
<L>aabb
  aa = horizontal enlargement ratio (01-12)
  bb = vertical enlargement ratio (01-12)
```

Example: `<L>0304` = 3x horizontal, 4x vertical. Also enlarges character pitch. Invalid for barcodes. Valid for fonts, graphics, PCX/BMP.

### Rotation `<%>`

```
<%>a
  0 = 0 degrees (Parallel 1 - forward feed)
  1 = 90 degrees (Serial 1)
  2 = 180 degrees (Parallel 2 - reverse)
  3 = 270 degrees (Serial 2)
```

Setting persists until changed or `<Z>` resets it. When rotating barcodes at 90/270 degrees, increase narrow bar width to 3+ dots to avoid blurring.

### Sequential Number `<F>`

```
<F>aaaabcccc,dd,ee,f
  aaaa = repeat count for identical print (1-9999)
  b    = +/- (increment or decrement)
  cccc = step value (1-9999)
  dd   = effective digit count (1-99, default 8)
  ee   = low-level invalid digit (0-99, default 0)
  f    = 0: decimal, 1: hexadecimal
```

Example: `<F>100+1,5,0<XS>10000` -- prints "10000", increments by 1, prints 100 copies of each.

### Ruled Line / Frame `<FW>`

**Ruled line:**
```
<FW>aabcccc
  aa = line width (02-999 dots)
  b  = H (horizontal) or V (vertical)
  cccc = line length
```

**Frame (rectangle):**
```
<FW>aabbVccccHdddd
  aa = vertical line width (02-99 dots)
  bb = horizontal line width (02-99 dots)
  cccc = vertical line length
  dddd = horizontal line length
```

### Reverse Color `<(>`

```
<(>aaaa,bbbb
  aaaa = inversion area horizontal (8 to H Max dots)
  bbbb = inversion area vertical (8 to V Max dots)
```

Print area of black fill should not exceed 30% of total label area.

---

## Font Commands

### Bitmap Fonts

| Command | ESC Code | Basic Size (WxH dots) | Pitch | Smoothing |
| --- | --- | --- | --- | --- |
| `<XU>` | ESC+XU | 5 x 9 | Fixed only | No |
| `<XS>` | ESC+XS | 17 x 17 | Fixed/Proportional | No |
| `<XM>` | ESC+XM | 24 x 24 | Fixed/Proportional | No |
| `<XB>` | ESC+XB | 48 x 48 | Fixed/Proportional | Optional |
| `<XL>` | ESC+XL | 48 x 48 | Fixed/Proportional | Optional |
| `<U>` | ESC+U | 5 x 9 | Fixed only | No |
| `<S>` | ESC+S | 8 x 15 | Fixed only | No |
| `<M>` | ESC+M | 13 x 20 | Fixed only | No |
| `<WB>` | ESC+WB | 18 x 30 | Fixed only | Optional |
| `<WL>` | ESC+WL | 28 x 52 | Fixed only | Optional |
| `<OA>` | ESC+OA | OCR-A (15x22 @203dpi, 22x33 @305dpi) | Fixed | No |
| `<OB>` | ESC+OB | OCR-B (20x24 @203dpi, 30x36 @305dpi) | Fixed | No |

**CL4NX Plus additional bitmap fonts:**

| Command | ESC Code | Basic Size (WxH dots) |
| --- | --- | --- |
| `<X20>` | ESC+X20 | 5 x 9 |
| `<X21>` | ESC+X21 | 17 x 17 |
| `<X22>` | ESC+X22 | 24 x 24 |
| `<X23>` | ESC+X23 | 48 x 48 |
| `<X24>` | ESC+X24 | 48 x 48 |

### Smoothing Parameter

For fonts that support smoothing (`<XB>`, `<XL>`, `<WB>`, `<WL>`):
```
<XB>an-n
  a = 0: smoothing off, 1: smoothing on (effective 3x-12x enlargement)
  n = print data
```

### Outline Font `<$>` / `<$=>`

```
<$>a,bbb,ccc,d
  a = font type: A (Helvetica Bold proportional), B (Helvetica Bold fixed)
  bbb = font width (50-999 dots)
  ccc = font height (50-999 dots)
  d = style:
      0: Standard (black)
      1: Inversion (enclosed)
      2: Gray pattern 1
      3: Gray pattern 2
      4: Gray pattern 3
      5: Shadow
      6: Inversion with shadow
      7: Mirror
      8: Standard italic (15-degree slant)
      9: Inversion with shadow italic

<$=>n-n     (print data follows)
```

Example: `<$>A,100,100,1<$=>SATO` -- Helvetica Bold proportional, 100x100 dots, inverted.

### CG Font `<RD>`

```
<RD>abb,ccc,ddd,n-n
  a  = font type: A (CG Times), B (CG Triumvirate)
  bb = font style: 00 (Normal), 01 (Bold)
  ccc = horizontal size: 16-999 (dots) or P08-P72 (points)
  ddd = vertical size: 16-999 (dots) or P08-P72 (points)
  n  = print data
```

### Scalable Font `<RH>` (CL4NX Plus)

Supports TrueType fonts with variable sizing.

### Multiple Language `<RG>` (CL4NX Plus)

Supports printing in multiple languages/character sets.

---

## 1D Barcode Commands

### Barcode Ratio Commands

| Command | ESC Code | Narrow:Wide Ratio | Format |
| --- | --- | --- | --- |
| `<B>` | ESC+B | 1:3 | `<B>abbcccn-n` |
| `<D>` | ESC+D | 1:2 | `<D>abbcccn-n` |
| `<BD>` | ESC+BD | 2:5 | `<BD>abbcccn-n` |
| `<BT>` | ESC+BT | Custom ratio registration | `<BT>abbccddee` |
| `<BW>` | ESC+BW | Print with registered ratio | `<BW>aabbn-n` |

### Common Barcode Parameters (`<B>`, `<D>`, `<BD>`)

```
<B>abbcccn-n
  a   = barcode type (see table below)
  bb  = narrow bar width (01-36 dots)
  ccc = barcode height (001-999 dots)
  n   = print data
```

### Barcode Type Codes

| Code | Barcode Type | `<B>` (1:3) | `<D>` (1:2) | `<BD>` (2:5) | Notes |
| --- | --- | --- | --- | --- | --- |
| 0 | CODABAR (NW-7) | Yes | Yes | Yes | Include start/stop chars (A,B,C,D) |
| 1 | CODE39 | Yes | Yes | Yes | Include start/stop chars (*) |
| 2 | ITF (Interleaved 2 of 5) | Yes | Yes | Yes | Even-digit data required |
| 3 | JAN/EAN-13 | No HRI/guard | Guard bar | HRI + guard | 12-13 digit data |
| 4 | JAN/EAN-8 | No HRI/guard | Guard bar | HRI + guard | 7-8 digit data |
| 5 | Industrial 2 of 5 | Yes | Yes | Yes | Character pitch enabled |
| 6 | Matrix 2 of 5 | Yes | Yes | Yes | Character pitch enabled |
| A | MSI | Yes | -- | -- | Max 13 digits |
| C | CODE93 | Yes | -- | -- | Use `<BC>` for detailed control |
| E | UPC-E | Yes | -- | -- | 6-digit data only |
| F | Bookland (UPC Add-on) | Yes | -- | -- | Use `<BF>` for detailed control |
| G | CODE128 | Yes | -- | -- | Use `<BG>` for detailed control |
| H | UPC-A | No HRI/guard | Guard bar | HRI + guard | 11-digit data |
| I | GS1-128 (UCC/EAN-128) | Yes | -- | -- | Use `<BI>` for detailed control |
| P | POSTNET | Yes | -- | -- | Use `<BP>` for detailed control |
| S | USPS Barcode | Yes | -- | -- | Use `<BS>` for detailed control |

### HRI and Guard Bar Behavior by Command

| Barcode | `<B>` | `<D>` | `<BD>` |
| --- | --- | --- | --- |
| JAN/EAN-13 | No HRI, No guard | No HRI, Guard bar | HRI + Guard bar |
| JAN/EAN-8 | No HRI, No guard | No HRI, Guard bar | HRI + Guard bar |
| UPC-A | No HRI, No guard | No HRI, Guard bar | HRI + Guard bar |

### Barcode with HRI `<D>~<d>`

```
<D>abbcccn-n<d>n-n
  (first part = barcode)
  d = character type for HRI: XU, XS, XM, XB, XL, OA, OB, U, S, M, WB, WL, X20-X24
  n = HRI data
```

### Specialized 1D Barcode Commands

#### CODE93 `<BC>`
```
<BC>aabbbccn-n
  aa  = narrow bar width (01-12)
  bbb = barcode height (001-600 dots)
  cc  = data digit count (01-99)
  n   = print data
```
C/D automatically generated. Max 99 digits.

#### CODE128 `<BG>`
```
<BG>aabbbn-n
  aa  = narrow bar width (01-12)
  bbb = barcode height (001-600 dots)
  n   = print data (use <A>, <B>, <C> for start character switching)
```
C/D automatically generated. Start Character C requires even number of digits.

Example with code set switching: `<BG>031600<B>1<C>23456789012345`

#### GS1-128 (UCC/EAN-128) `<BI>`
```
<BI>aabbbcn-n
  aa  = narrow bar width (01-12)
  bbb = barcode height (001-600 dots)
  c   = HRI: 0=none, 1=top, 2=bottom
  n   = print data (17 digits, C/D auto-added for 18 total)
```

#### UPC Add-on / Bookland `<BF>`
```
<BF>bbccn-n
  bb = narrow bar width (01-03)
  cc = bar height (001-600 dots)
  n  = print data (2-5 digits)
```

#### POSTNET `<BP>`
```
<BP>n-n
  n = address data: 5, 6, 9, or 11 digits
```

#### USPS Barcode `<BS>`
```
<BS>n-n
```

#### UPC-A `<BL>` / `<BM>`
```
<BL>abbcccn-n      UPC-A without HRI (with guard bar)
<BM>abbcccn-n      UPC-A with HRI and guard bar
```

#### Composite Symbol `<EU>`
```
<EU>...             Composite barcode (CC-A, CC-B, CC-C)
```

### Custom Barcode Ratio `<BT>` / `<BW>`

```
<BT>abbccddee      Register custom ratio
  a  = barcode type (0:NW-7, 1:CODE39, 2:ITF, 5:Industrial 2of5, 6:Matrix 2of5)
  bb = narrow space width (01-99)
  cc = wide space width (01-99)
  dd = narrow bar width (01-99)
  ee = wide bar width (01-99)

<BW>aabbn-n         Print with registered ratio
  aa = narrow bar width (01-12)
  bb = barcode height (001-600)
  n  = print data
```

### Inter-character Gap

For NW-7, CODE39, Industrial 2of5, and Matrix 2of5: set `<P>` immediately before the barcode command. Gap = `<P>` value x narrow bar width.

### Narrow Bar Width Recommendations

| Head Density | Minimum Narrow Bar |
| --- | --- |
| 203 dpi (8 dots/mm) | 2 dots (parallel), 3 dots (serial/rotated) |
| 305 dpi (12 dots/mm) | 2 dots (parallel), 3 dots (serial/rotated) |
| 609 dpi (24 dots/mm) | 4 dots (parallel), 6 dots (serial/rotated) |

### Check Digit Auto-Generation

| Barcode | Method | Input Digits |
| --- | --- | --- |
| JAN/EAN-13 | Modulus 10 | 12 digits (C/D added), 13 digits (no check) |
| JAN/EAN-8 | Modulus 10 | 7 digits (C/D added), 8 digits (no check) |
| UPC-A | Modulus 10 | 11 digits (C/D added) |
| UPC-E | Modulus 10 | 6 digits |
| CODE93 | Modulus 47 | Auto |
| CODE128 | Modulus 103 | Auto |
| GS1-128 | Modulus 10 + Modulus 103 | 17 digits |

---

## 2D Barcode Commands

### 2D Code Command Summary

| Command | ESC Code | 2D Code Type |
| --- | --- | --- |
| `<2D10>` | ESC+2D10 | PDF417 |
| `<2D12>` | ESC+2D12 | Micro PDF417 |
| `<2D20>` | ESC+2D20 | MaxiCode |
| `<2D30>` | ESC+2D30 | QR Code (Model 2) |
| `<2D31>` | ESC+2D31 | QR Code (Model 1) |
| `<2D32>` | ESC+2D32 | Micro QR Code |
| `<2D34>` | ESC+2D34 | GS1 QR Code (Model 2) |
| `<2D50>` | ESC+2D50 | DataMatrix (ECC200) |
| `<2D51>` | ESC+2D51 | GS1 DataMatrix |
| `<2D70>` | ESC+2D70 | Aztec Code |
| `<BQ>` | ESC+BQ | QR Code (compatible/legacy) |
| `<BV>` | ESC+BV | MaxiCode (compatible/legacy) |
| `<BK>` | ESC+BK | PDF417 (compatible/legacy) |
| `<BX>` | ESC+BX | DataMatrix ECC200 (compatible/legacy) |
| `<DC>` | ESC+DC | DataMatrix data specify (compatible) |
| `<FX>` | ESC+FX | DataMatrix sequential number (compatible) |
| `<QV>` | ESC+QV | QR code version setting |

### PDF417 `<2D10>`

```
Setup:  <2D10>,aa,bb,c,dd,ee(,f)
Data:   <DN>mmmm,n...n

  aa = minimum module width (01-27 dots)
  bb = minimum module height (01-72 dots)
  c  = security level (0-8)
  dd = data code words per line (01-30, 00=auto)
  ee = number of lines per symbol (03-90, 00=auto)
  f  = code type: 0=normal (default), 1=truncated

  mmmm = number of data bytes (1-2681)
  n    = print data
```

Example:
```
<A>
<V>100<H>200<2D10>,03,09,3,03,18
<DN>0010,0123456789
<Q>2
<Z>
```

### Micro PDF417 `<2D12>`

Similar to PDF417 but produces smaller symbols. 34 predefined symbol sizes.

### MaxiCode `<2D20>`

Fixed-size 2D code used primarily by UPS for package sorting.

### QR Code (Model 2) `<2D30>`

```
Setup:  <2D30>,a,bb,c,d(,ee,ff,gg)
Data:   <DN>mmmm,n...n   (automatic mode)
   or:  <DS>k,n...n      (manual mode)

  a  = error correction: L(7%), M(15%), Q(25%), H(30%)
  bb = cell size (01-99 dots, recommend 04+)
  c  = data mode: 0=manual, 1=automatic
  d  = concatenation: 0=normal, 1=concatenation mode
  ee = number of partitions (01-16, concat only)
  ff = partition sequence (01-16, concat only)
  gg = parity data (00-FF hex, concat only)

Manual mode input modes (k):
  1 = Numeric
  2 = Alphanumeric
  3 = Kanji (Shift JIS)

  mmmm = data byte count (1-2953)
```

Example (automatic mode):
```
<A>
<V>100<H>200<2D30>,M,04,1,0
<DN>0013,Hello World!!
<Q>1
<Z>
```

### QR Code Version `<QV>`

```
<QV>pp
  pp = version 00-40 (00 or omitted = auto)
```

Use to fix QR symbol size. Place before the QR data command.

### Micro QR Code `<2D32>`

Smaller QR code variant for limited space applications.

### GS1 QR Code `<2D34>`

QR Code with GS1 Application Identifier encoding.

### DataMatrix (ECC200) `<2D50>`

```
Setup:  <2D50>,aa,bb,ccc,ddd
Data:   <DN>mmmm,n...n

  aa  = horizontal cell size (01-99 dots)
  bb  = vertical cell size (01-99 dots)
  ccc = cells per line (010-144, 000=auto)
  ddd = number of cell lines (008-144, 000=auto)

  mmmm = data byte count (1-3116)
```

Example:
```
<A>
<V>100<H>200<2D50>,03,03,000,000
<DN>0010,0123456789
<Z>
```

**DataMatrix capacity (auto/square, max symbol):**

| Data Format | Max Characters |
| --- | --- |
| Numeric | 3116 |
| Alphanumeric | 2335 |
| Binary (00-FF) | 1556 |

**DataMatrix symbol sizes:** 30 standard sizes from 10x10 to 144x144 cells (square) plus rectangular variants.

When data contains 0x7E, specify it as "7E 7E" (doubled).

### GS1 DataMatrix `<2D51>`

DataMatrix with GS1 Application Identifier encoding.

### Aztec Code `<2D70>`

2D matrix code with built-in bulls-eye finder pattern.

---

## Graphic Commands

| Command | ESC Code | Function | Format |
| --- | --- | --- | --- |
| `<G>` | ESC+G | Raw graphic data print | `<G>abbbcccn-n` |
| `<GM>` | ESC+GM | BMP file print | `<GM>aaaaa,n-n` |
| `<GP>` | ESC+GP | PCX file print | `<GP>aaaaa,n-n` |

### Raw Graphic `<G>`

```
<G>abbbcccn-n
  a   = data format: H (hex), B (binary)
  bbb = graphic width in bytes (H direction)
  ccc = graphic height in bytes (V direction)
  n   = graphic data
```

Rotation `<%>` and enlargement `<L>` can be applied to graphics.

### BMP/PCX File Print

```
<GM>aaaaa,n-n       BMP file (black/white mode only)
<GP>aaaaa,n-n       PCX file (black/white mode only)
  aaaaa = total byte count of file
  n     = file data (binary)
```

Both support rotation and enlargement. Color mode files cause command errors.

---

## System Commands

### Label/Media Configuration

| Command | ESC Code | Function | Format |
| --- | --- | --- | --- |
| `<A1>` | ESC+A1 | Media/label size | `<A1>aaaabbbb` or `<A1>VaaaaaHbbbb` |
| `<A3>` | ESC+A3 | Base reference point (start point correction) | `<A3>VabbbbbHcdddd` |
| `<EP>` | ESC+EP | Print end position (sensor ignored mode) | `<EP>[,aaaaa]` |
| `<PO>` | ESC+PO | Offset specification | `<PO>` |
| `<TG>` | ESC+TG | Gap/space between labels | `<TG>` |
| `<YE>` | ESC+YE | Paper type specification | `<YE>` |
| `<AX>` | ESC+AX | Print area enlargement | `<AX>` |
| `<AR>` | ESC+AR | Print area standard (reset enlargement) | `<AR>` |

#### Media Size `<A1>`

```
<A1>aaaabbbb          Fixed 4-digit format (label size < 9999 dots)
<A1>VaaaaaHbbbb       Variable format

  aaaa/aaaaa = label height in dots
  bbbb       = label width in dots
```

CL4NX Plus valid ranges:

| DPI | Width (dots) | Height (dots) |
| --- | --- | --- |
| 203 | 1 to 832 | 1 to 20000 |
| 305 | 1 to 1248 | 1 to 18000 |
| 609 | 1 to 2496 | 1 to 9600 |

#### Base Reference Point `<A3>`

```
<A3>VabbbbbHcdddd
  a = vertical sign (+/-)
  bbbbb = vertical correction (dots)
  c = horizontal sign (+/-)
  dddd = horizontal correction (dots)
```

With sign (+/-): not saved after power off. Without sign: saved to EEPROM (legacy format).

### Print Control

| Command | ESC Code | Function | Format |
| --- | --- | --- | --- |
| `<CS>` | ESC+CS | Print speed | `<CS>aa` |
| `<#F>` | ESC+#F | Print darkness (1-10 level, A-F type) | `<#F>ab` or `<#F>aab` |
| `<#E>` | ESC+#E | Print darkness (compatible, 1-5 levels) | `<#E>ab` |
| `<PH>` | ESC+PH | Print method (thermal/direct thermal) | `<PH>` |
| `<PM>` | ESC+PM | Operation mode | `<PM>` |
| `<IG>` | ESC+IG | Sensor type | `<IG>` |
| `<C>` | ESC+C | Reprint last label | `<C>` |
| `<VB>` | ESC+VB | Barcode checker/verifier | `<VB>` |

#### Print Speed `<CS>`

```
<CS>aa
  CL4NX Plus (203/305 dpi): 2-14 (inch/s), default 6
  CL4NX Plus (609 dpi): 2-6 (inch/s), default 4
```

| Parameter | Speed |
| --- | --- |
| 2 | 2 inch/s (50.8 mm/s) |
| 3 | 3 inch/s (76.2 mm/s) |
| 4 | 4 inch/s (101.6 mm/s) |
| 5 | 5 inch/s (127.0 mm/s) |
| 6 | 6 inch/s (152.4 mm/s) |
| 7 | 7 inch/s (177.8 mm/s) |
| 8 | 8 inch/s (203.2 mm/s) |
| 9 | 9 inch/s (228.6 mm/s) |
| 10 | 10 inch/s (254.0 mm/s) |
| 11 | 11 inch/s (279.4 mm/s) |
| 12 | 12 inch/s (304.8 mm/s) |
| 13 | 13 inch/s (330.2 mm/s) |
| 14 | 14 inch/s (355.6 mm/s) |

In linerless cutter mode, max speed is 6 inch/s.

#### Print Darkness `<#F>` (CL4NX Plus)

```
<#F>ab    or    <#F>aab
  a/aa = darkness level: 1 (lightest) to 10 (darkest), default 5
  b    = darkness type: A (default), B-F reserved
```

#### Print Darkness `<#E>` (Compatible)

```
<#E>ab
  a = darkness level: 1-5 (compatible with older models)
  b = type: A-F
```

Note: `<#E>` is the legacy command. The display/DC2+PB value shows 2x the `<#E>` value.

#### Sensor Type `<IG>`

```
<IG>a
  1 = Reflection sensor (eye mark) -- default
  2 = Transparent sensor (gap/space)
  3 = Sensor ignored (continuous media)
```

#### Operation Mode `<PM>`

```
<PM>a
  0 = Continuous operation
  1 = Tear-off operation
  2 = Cutter (head position)
  3 = Cutter (cutter position)
  4 = Cutter (without backfeed)
  5 = Linerless (cutter position)
  6 = Linerless (without backfeed)
  7 = Dispenser (head position)
  8 = Dispenser (dispenser position)
```

### Cut Commands

| Command | ESC Code | Function | Format |
| --- | --- | --- | --- |
| `<~>` / `<NUL>` | ESC+~ | Multiple cut (N labels per cut) | `<~>aaaa` or `<NUL>aaaa` |
| `<CT>` | ESC+CT | Cut number unit | `<CT>aaaa` |
| `<NC>` | ESC+NC | Eject and cut (single cut) | `<NC>` |
| `<~A>` | ESC+~A | Cut number unit (alternative) | `<~A>aaaa` |
| `<~B>` | ESC+~B | Eject and cut (alternative) | `<~B>` |

#### Multiple Cut `<~>` / `<NUL>`

```
<~>aaaa     or     <NUL>aaaa
  aaaa = number of labels before cutting (0-9999, 0=no cut)
```

Place after `<Q>`. `<Q>` x `<~>` value must not exceed 999999.

#### Cut Number Unit `<CT>` / `<~A>`

```
<CT>aaaa    or    <~A>aaaa
  aaaa = labels between each cut (0-9999, 0=no cut)
```

Place before `<Q>`. Cannot combine with `<~>`.

### Memory/State Commands

| Command | ESC Code | Function | Format |
| --- | --- | --- | --- |
| `<*>` | ESC+* | Memory clear | `<*>a` |
| `<@>` | ESC+@ | Set printer offline | `<@>` |
| `<C>` | ESC+C | Reprint previous label | `<C>` |
| `<RF>` | ESC+RF | Recall registered font/logo list | `<RF>` |
| `<FC>` | ESC+FC | Font delete (SBPL guide) | `<FC>` |
| `<PG>` | ESC+PG | Save printer settings to EEPROM | `<PG>abcde...` |

#### Memory Clear `<*>`

```
<*>         Clear receive and edit buffers (reprint not possible)
<*>T        Clear user-defined characters
<*>&        Clear form overlay
<*>X        All clear (buffers + user chars + overlay, not current job)
```

Wait 100ms+ after `<*>` before sending next data.

### Character Set Commands

| Command | ESC Code | Function |
| --- | --- | --- |
| `<KC>` | ESC+KC | Kanji code selection (JIS/Shift-JIS) |
| `<KS>` | ESC+KS | Kanji set selection |
| `<KM>` | ESC+KM | Mincho Kanji typeface |
| `<KG>` | ESC+KG | Gothic Kanji typeface |
| `<CE>` | ESC+CE | European code page selection |
| `<CL>` | ESC+CL | Delete CR/LF from data stream |
| `<TK>` | ESC+TK | Forced tear off |
| `<TW>` | ESC+TW | Option waiting time |

---

## Form Overlay Commands

| Command | ESC Code | Function |
| --- | --- | --- |
| `<&>` | ESC+& | Register form overlay (RAM, lost on power off) |
| `</>` | ESC+/ | Recall form overlay |
| `<&S>` | ESC+&S | Register form overlay to memory card |
| `<&R>` | ESC+&R | Recall form overlay from memory card |
| `<YS>` | ESC+YS | Format registration (memory card) |
| `<YR>` | ESC+YR | Format call (memory card) |
| `</N>` | ESC+/N | Field registration |
| `</D>` | ESC+/D | Field print |

### RAM Overlay Example

```
(Register)
<A>
<V>100<H>50<FW>1010V800H750
<V>100<H>50<FW>0505V760H710
<V>150<H>100<XB>0MODEL
<&>
<Z>

(Recall and print)
<A>
</>
<V>200<H>100<P>0<$>B,100,100,6
<$=>SATOPRINTER
<V>720<H>150<B>102100*95000012345*
<Q>1
<Z>
```

---

## Calendar Commands

| Command | ESC Code | Function | Format |
| --- | --- | --- | --- |
| `<WT>` | ESC+WT | Calendar setup (set date/time) | `<WT>` |
| `<WP>` | ESC+WP | Calendar arithmetic (add days/months/years) | `<WP>` |
| `<WA>` | ESC+WA | Calendar print (real-time date/time) | `<WA>` |
| `<WU>` | ESC+WU | Expanded calendar print | `<WU>` |

Requires Calendar IC option on older models. Built-in on CL4NX Plus.

---

## Memory Card Commands (CL4NX Plus)

| Command | ESC Code | Function |
| --- | --- | --- |
| `<CC>` | ESC+CC | Select card slot |
| `<FM>` | ESC+FM | Memory card initialization |
| `<BJF>` | ESC+BJF | Memory card initialization (alt) |
| `<FP>` | ESC+FP | Memory card status print |
| `<BJS>` | ESC+BJS | Memory card status print (alt) |
| `<GI>` | ESC+GI | Register graphic to memory card |
| `<GR>` | ESC+GR | Recall graphic from memory card |
| `<GT>` | ESC+GT | Register BMP to memory card |
| `<GC>` | ESC+GC | Recall BMP from memory card |
| `<PI>` | ESC+PI | Register PCX to memory card |
| `<PY>` | ESC+PY | Recall PCX from memory card |

---

## XML Template Commands (CL4NX Plus)

| Command | ESC Code | Function |
| --- | --- | --- |
| `</Y>` | ESC+/Y | Register print template name |
| `</X>` | ESC+/X | Set XML variable name |
| `</R>` | ESC+/R | Remove print template |
| `</S>` | ESC+/S | Set print template name |
| `</G>` | ESC+/G | Get print template information |

---

## Common Device Commands (DC2 Protocol)

These commands work across all printer languages (not SBPL-specific). They use DC2 (0x12) prefix instead of ESC.

| Command | Function |
| --- | --- |
| `DC2+PA` | Printer setting command (configure all settings) |
| `DC2+PB` | Printer setting information acquisition |
| `DC2+PC` | Printer device information acquisition |
| `DC2+PD` | Sensor information acquisition |
| `DC2+PG` | Printer status information acquisition |
| `DC2+PH` | Cancel request |
| `DC2+PI` | Application (language) change |
| `DC2+PN` | Request label pitch size |
| `DC2+DB` | Initialization (factory reset) |
| `DC2+DC` | Reset |
| `DC2+DD` | Power OFF |
| `DC2+DE` | File download |
| `DC2+DF` | File name information acquisition |
| `DC2+DG` | File information acquisition |
| `DC2+DH` | File deletion |

---

## Communication / Interface

### Supported Interfaces (CL4NX Plus)

| Interface | Specification |
| --- | --- |
| USB | USB 2.0 High-Speed (Type-A and Type-B connectors) |
| LAN | 10BASE-T / 100BASE-TX, RJ-45 |
| RS-232C | DB9 pin (female) |
| IEEE1284 | ECP/Compatible mode, Amphenol 36-pin |
| Bluetooth | Ver 3.0+EDR Class 2 |
| NFC | Tag mode, Pass-through mode, Handover mode |
| Wireless LAN | 802.11 a/b/g/n (optional) |
| External Signal | Amphenol 14-pin (for dispenser, applicator, etc.) |

### Communication Protocols

| Protocol | RS-232C | IEEE1284 | USB | LAN | Bluetooth | NFC |
| --- | --- | --- | --- | --- | --- | --- |
| Multiple buffer (no bidirectional) | -- | -- | -- | -- | Yes | -- |
| READY/BUSY | Yes | Yes | -- | -- | -- | -- |
| XON/XOFF | Yes | -- | -- | -- | -- | -- |
| Status3 (bidirectional) | Yes | -- | -- | -- | -- | -- |
| Status4 (bidirectional) | Yes | Yes | Yes | Yes | -- | -- |
| Status5 (bidirectional) | Yes | Yes | Yes | Yes | Yes | Yes |

### Status Return Protocols

**Status3** -- Polled status return via ENQ/ACK handshake. Returns printer state after each label.

**Status4** -- Enhanced bidirectional. Returns detailed status including job ID, error codes.

**Status5** -- Full bidirectional with buffer control. Supports:
- Receiving buffer status
- Print completion status
- Error status with detailed codes
- Job name and ID feedback

### LAN/WLAN Communication

- **TCP/IP Socket**: Port 1024 (default) for raw data
- **LPR**: Standard Line Printer protocol
- **FTP**: File transfer for firmware/fonts
- **HTTP/HTTPS**: Web-based configuration interface
- **NTP**: Network time synchronization

Cannot use LAN and WLAN simultaneously -- must select one via LCD settings.

### Socket Communication

Default TCP port: 1024. Supports multiple simultaneous connections with TCP connection queue management.

---

## Supported Barcode Symbologies Summary

### 1D Barcodes

| Symbology | Commands | Ratios Available | Check Digit |
| --- | --- | --- | --- |
| CODABAR (NW-7) | B, D, BD, BT/BW | 1:3, 1:2, 2:5, custom | None (manual) |
| CODE39 | B, D, BD, BT/BW | 1:3, 1:2, 2:5, custom | None (manual) |
| ITF (Interleaved 2 of 5) | B, D, BD, BT/BW | 1:3, 1:2, 2:5, custom | None |
| JAN/EAN-13 | B, D, BD | Fixed module | Modulus 10 (auto) |
| JAN/EAN-8 | B, D, BD | Fixed module | Modulus 10 (auto) |
| UPC-A | B, D, BD, BL, BM | Fixed module | Modulus 10 (auto) |
| UPC-E | B | Fixed module | Modulus 10 (auto) |
| Industrial 2 of 5 | B, D, BD, BT/BW | 1:3, 1:2, 2:5, custom | None |
| Matrix 2 of 5 | B, D, BD, BT/BW | 1:3, 1:2, 2:5, custom | None |
| MSI | B | Fixed | None |
| CODE93 | BC | Fixed module | Modulus 47 (auto) |
| CODE128 (A/B/C) | BG | Fixed module | Modulus 103 (auto) |
| GS1-128 (UCC/EAN-128) | BI | Fixed module | Modulus 10+103 (auto) |
| POSTNET | BP | Fixed | Auto |
| USPS Intelligent Mail | BS | Fixed | Auto |
| UPC Add-on / Bookland | BF | Fixed | Auto |
| Composite Symbol | EU | Fixed | Auto |

### 2D Codes

| Symbology | Command | Max Data Capacity |
| --- | --- | --- |
| PDF417 | 2D10 | 2681 bytes |
| Micro PDF417 | 2D12 | 366 bytes (max symbol) |
| MaxiCode | 2D20 | 93 alphanumeric |
| QR Code Model 2 | 2D30 | 2953 bytes |
| QR Code Model 1 | 2D31 | Legacy, smaller capacity |
| Micro QR Code | 2D32 | Reduced capacity |
| GS1 QR Code | 2D34 | 2953 bytes (with AI) |
| DataMatrix ECC200 | 2D50 | 3116 numeric / 1556 binary |
| GS1 DataMatrix | 2D51 | With Application Identifiers |
| Aztec Code | 2D70 | Variable |

---

## Key Parameters Quick Reference

| Parameter | Command | Range | Default | Persistence |
| --- | --- | --- | --- | --- |
| Print quantity | `<Q>` | 1-999999 | -- | Per job |
| Horizontal position | `<H>` | 1-H Max (dots) | -- | Per field |
| Vertical position | `<V>` | 1-V Max (dots) | -- | Per field |
| Character pitch | `<P>` | 0-99 (dots) | 02 | Reset by font command or `<Z>` |
| Enlargement | `<L>` | 01-12 each axis | 0101 | Until re-specified or `<Z>` |
| Rotation | `<%>` | 0-3 | 0 | Until re-specified or `<Z>` |
| Print speed | `<CS>` | 2-14 (inch/s) | 6 | Saved (survives power off) |
| Print darkness level | `<#F>` | 1-10 | 5 | Saved |
| Print darkness type | `<#F>` | A-F | A | Saved |
| Label height | `<A1>` | 1-20000 (dots) | -- | Until changed or power off |
| Label width | `<A1>` | 1-2496 (dots) | -- | Until changed or power off |
| Sensor type | `<IG>` | 1-3 | 1 (reflection) | Until power off |
| Operation mode | `<PM>` | 0-8 | 0 (continuous) | Until power off |
| Narrow bar width | `<B>` etc. | 01-36 (dots) | -- | Per barcode |
| Barcode height | `<B>` etc. | 001-999 (dots) | -- | Per barcode |

---

## Dot-to-Millimeter Conversion

| DPI | Dots/mm | 1 dot (mm) | 1 mm (dots) |
| --- | --- | --- | --- |
| 203 | 8 | 0.125 | 8 |
| 305 | 12 | 0.083 | 12 |
| 609 | 24 | 0.042 | 24 |

**Common conversions (203 dpi):**
- 25mm = 200 dots
- 50mm = 400 dots
- 100mm = 800 dots
- 104mm (4") = 832 dots

**Point size (for CG fonts):** 1 point = 0.35mm
