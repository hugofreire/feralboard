# FeralBoard Design System

Design language for all FeralBoard / FeralByte products.
Grounded on the [AIO-500 product datasheet](https://feralboard.feralbyte.com).

---

## Philosophy

**Industrial clarity, developer polish.**

The FeralBoard brand sits between two worlds: industrial hardware and modern software.
The design system reflects that with technical mono-spaced labels, bold display headings,
and a muted purple palette that feels precise without being cold.

Core principles:

1. **Data-first** — content is dense and scannable; every section earns its space.
2. **Mono-as-signal** — monospace type is used for anything technical (specs, labels, ICs, signals).
   Body copy stays in a humanist sans for readability.
3. **Restrained motion** — animations exist to reveal, not to entertain.
   Fade + translate on scroll, once per element, short durations.
4. **Light default, dark hero** — most content sits on a clean white ground.
   The hero and key blocks use the dark `ink` background as contrast anchors.
5. **Purple identity** — a single vibrant purple (`hsl(263 84% 58%)`) carries the brand.
   Green marks success states and galvanic isolation. No other accent colors.

---

## Color Palette

### Brand Colors

| Token             | HSL                  | Hex       | Usage                          |
|-------------------|----------------------|-----------|--------------------------------|
| `--primary`       | `263 84% 58%`        | `#7c3aed` | Buttons, accents, active state |
| `--primary-dark`  | `263 69% 42%`        | `#5b21b6` | Hover, dark accents            |
| `--primary-light` | `258 95% 76%`        | `#a78bfa` | Subtle highlights              |

### Neutrals

| Token                  | HSL              | Usage                    |
|------------------------|------------------|--------------------------|
| `--background`         | `0 0% 100%`     | Page background          |
| `--foreground`         | `220 20% 7%`    | Primary text             |
| `--ink`                | `220 20% 7%`    | Dark blocks / hero bg    |
| `--mid`                | `220 8% 32%`    | Secondary text           |
| `--light`              | `220 5% 56%`    | Tertiary text            |
| `--muted-foreground`   | `220 7% 55%`    | Body copy, descriptions  |
| `--rule`               | `216 12% 84%`   | Borders, dividers        |
| `--tint`               | `220 8% 96%`    | Subtle section bg        |
| `--tint-accent`        | `255 100% 97%`  | Purple-tinted bg, notes  |

### Semantic

| Token              | HSL              | Usage                      |
|--------------------|------------------|----------------------------|
| `--success`        | `160 84% 30%`   | IC chips, isolation badge  |
| `--success-light`  | `152 81% 96%`   | IC chip background         |
| `--destructive`    | `0 84% 60%`     | Errors (rarely used)       |

### Hero-Specific (hardcoded)

| Value         | Usage                            |
|---------------|----------------------------------|
| `#0d0d14`     | Hero background                  |
| `#6c3dd1`     | Gradient start                   |
| `#4a1fa0`     | Gradient end                     |
| `#8b6ce0`     | Hero accent text, logo highlight |

---

## Typography

### Font Stack

| Class          | Family                      | Role                          |
|----------------|------------------------------|-------------------------------|
| `font-display` | **Outfit**, sans-serif       | Headings (h1–h6)             |
| `font-body`    | **DM Sans**, sans-serif      | Body text (default on `body`) |
| `font-mono`    | **JetBrains Mono**, monospace | Labels, specs, chips, nav     |

### Type Scale

| Element              | Font    | Size          | Weight      | Tracking          |
|----------------------|---------|---------------|-------------|--------------------|
| Page title (h1)      | Outfit  | `3xl` / `4xl` | `extrabold` | `tight`            |
| Section title (h2)   | Outfit  | `3xl`         | `bold`      | `tight`            |
| Card title (h3)      | Outfit  | `sm`          | `semibold`  | —                  |
| Section label        | Mono    | `10px`        | `normal`    | `tracking-[3px]`   |
| Subsection label     | Mono    | `xs`          | `semibold`  | `tracking-[1.5px]` |
| Chip / badge         | Mono    | `11px`        | `semibold`  | —                  |
| Isolation badge      | Mono    | `10px`        | `semibold`  | `tracking-wider`   |
| Nav item             | Mono    | `xs`          | `normal`    | `tracking-wide`    |
| Body copy            | DM Sans | `sm`          | `normal`    | —                  |

### Convention: Uppercase

All mono-set labels use `uppercase` with explicit letter-spacing.
Body text is never uppercased.

---

## Spacing & Layout

### Section Template

```
py-20 px-6                     ← vertical rhythm + horizontal safety
  max-w-6xl mx-auto            ← content cap at ~1152px, centered
    SectionHead                ← icon + label + rule + h2
    content grid / cards       ← varies per section
```

### Grid Patterns

| Layout                 | Classes                                    |
|------------------------|--------------------------------------------|
| Two-column cards       | `grid md:grid-cols-2 gap-4`                |
| Three-column features  | `grid md:grid-cols-2 lg:grid-cols-3 gap-6` |
| Sidebar + content      | `md:grid md:grid-cols-[auto_1fr] md:gap-10`|
| Highlights bar         | `grid-cols-3 sm:grid-cols-4 md:grid-cols-7`|
| Bento image grid       | `grid grid-cols-[1fr_1.4fr] grid-rows-2 gap-2` |

### Border Radius

```
--radius: 0.5rem (8px)
rounded-lg  = var(--radius)
rounded-md  = var(--radius) - 2px
rounded-sm  = var(--radius) - 4px
```

Cards use `rounded-lg`. Chips use `rounded`. Images use `rounded-xl`.

---

## Components

### SectionHead

Every content section opens with this header.

```
┌─────────────────────────────────────────┐
│ [■] SECTION LABEL ─────────────────────── │  ← icon + mono label + rule
│ Section Title                            │  ← display font, bold
└─────────────────────────────────────────┘
```

- Icon: `w-7 h-7 bg-primary rounded` with `w-3.5 h-3.5` lucide icon inside
- Label: `font-mono text-[10px] uppercase tracking-[3px] text-primary`
- Rule: `flex-1 h-px bg-rule`
- Title: `font-display text-3xl font-bold text-foreground`
- Margin below: `mb-10`

### ChipBadge Variants

| Variant      | Background       | Text          | Extra                  |
|--------------|------------------|---------------|------------------------|
| `IcChip`     | `success-light`  | `success`     | `font-mono text-[11px]`|
| `SignalChip` | `tint`           | `mid`         | `font-mono text-[11px]`|
| `IsoBadge`   | `success-light`  | `success`     | `uppercase tracking-wider text-[10px]` |

Inline markup: `<ic>PART</ic>`, `<signal>PIN</signal>`, `<b>bold</b>`
parsed by `renderChips()`.

### InterfaceCard

```
┌──────────────────────────┐
┃ ▎ INTERFACE NAME [ISO]   │  ← 3px left bar (green if isolated, purple default)
│   Label: Value           │
│   Label: Value           │
└──────────────────────────┘
```

- Border: `border border-rule rounded-lg p-4`
- Left accent: `w-[3px] h-full` — `bg-success` (isolated) or `bg-primary`
- Title: `font-mono text-xs font-semibold uppercase tracking-wider`

### SystemBlock

Dark-header card for architecture diagrams.

```
┌──────────────────────────────────┐
│ ██ TAG ██  Block Title           │  ← bg-ink header, purple tag badge
├──────────────────────────────────┤
│ • Label: Value                   │
│ • Label: Value                   │  ← two-column grid on md+
└──────────────────────────────────┘
```

- Header: `bg-ink` with white text
- Tag: `bg-primary text-primary-foreground font-mono text-[10px] uppercase tracking-wider px-2.5 py-0.5 rounded`
- Bullets: `w-1.5 h-1.5 rounded-full bg-primary`

### NoteBox

```
┃ Note: Important information here.    ← 3px left border, tinted bg
```

- Background: `bg-tint-accent`
- Border: `border-l-[3px] border-primary rounded-r-md`
- Padding: `px-5 py-4`
- Text: `text-sm text-muted-foreground leading-relaxed`

### SpecGroup

Titled list of specification items.

```
SUBSECTION TITLE
────────────────
• Spec line one
• Spec line two
```

- Title: `font-mono text-xs font-semibold uppercase tracking-[1.5px] text-primary`
- Underline: `border-b-2 border-tint-accent`
- Bullets: `w-1.5 h-1.5 bg-primary rounded-sm`
- Items: `text-sm text-muted-foreground`

---

## Motion

All animations use **framer-motion**.

### Scroll Reveal (default)

```ts
initial={{ opacity: 0, y: 12 }}
whileInView={{ opacity: 1, y: 0 }}
transition={{ delay: i * 0.08, duration: 0.4 }}
viewport={{ once: true }}
```

- `y: 12` — subtle upward shift
- `0.08s` stagger per item in lists
- `once: true` — never replays

### Hero Entrance

```ts
initial={{ opacity: 0, y: 20 }}
animate={{ opacity: 1, y: 0 }}
transition={{ duration: 0.6 }}
```

- Fires immediately on mount (no scroll trigger)
- Slightly larger y offset and longer duration

### Horizontal Slide

```ts
initial={{ opacity: 0, x: -30 }}   // or x: 40 for right
whileInView={{ opacity: 1, x: 0 }}
transition={{ duration: 0.6 }}
viewport={{ once: true }}
```

Used for images and side content.

### Scale Pop (chips/tags)

```ts
initial={{ opacity: 0, scale: 0.9 }}
whileInView={{ opacity: 1, scale: 1 }}
transition={{ delay: 0.15 + i * 0.04 }}
viewport={{ once: true }}
```

Faster stagger (`0.04s`) for small elements.

---

## Navbar

- Sticky: `sticky top-0 z-50`
- Frosted glass: `bg-background/90 backdrop-blur-sm`
- Border: `border-b border-rule`
- Active item: `bg-primary/10 text-primary font-semibold`
- Inactive: `text-muted-foreground hover:text-foreground hover:bg-tint`
- Font: `font-mono text-xs`
- Scroll-spy via IntersectionObserver (`rootMargin: "-80px 0px -60% 0px"`)

---

## Iconography

- Library: **lucide-react**
- Default stroke width: `2`
- Section header icons: `w-3.5 h-3.5` inside `w-7 h-7` container
- Nav icons: `w-3 h-3`
- Inline icons: `w-5 h-5`

---

## Responsive Strategy

Mobile-first with Tailwind breakpoints:

| Breakpoint | Width    | Behavior                            |
|------------|----------|--------------------------------------|
| Default    | < 768px  | Single column, stacked layouts       |
| `md:`      | ≥ 768px  | Two-column grids, side-by-side       |
| `lg:`      | ≥ 1024px | Three-column grids where applicable  |

Common pattern: `grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3`

---

## Image Guidelines

- Format: **WebP** (quality 80 via `cwebp -q 80`)
- Location: `public/` directory
- Naming: `feralboard-{descriptor}.webp`
- Styling: `rounded-xl`, `object-cover`, constrained with `max-w-{size}`
- Always include descriptive `alt` text

---

## Internationalization

- Framework: **react-i18next**
- Languages: English (`en.ts`), Portuguese (`pt.ts`)
- Key convention: `section.element` (e.g., `hero.title`, `overview.description`)
- All visible strings go through `t()` — no hardcoded user-facing text
- Rich text parsed via `renderChips()` for inline `<ic>`, `<signal>`, `<b>` tags

---

## Tech Stack

| Layer        | Tool                                    |
|--------------|-----------------------------------------|
| Framework    | React 18 + TypeScript                   |
| Build        | Vite                                    |
| Styling      | Tailwind CSS 3.4 + `tailwindcss-animate`|
| Motion       | Framer Motion 12                        |
| Icons        | Lucide React                            |
| i18n         | react-i18next                           |
| Primitives   | Radix UI                                |
| Fonts        | Google Fonts (Outfit, DM Sans, JetBrains Mono) |
