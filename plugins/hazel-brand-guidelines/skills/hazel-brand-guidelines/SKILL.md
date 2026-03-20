---
name: hazel-brand-guidelines
description: Applies Hazel Health's official brand colors, typography, and layout patterns to any visual deliverable — slides, reports, dashboards, PDFs, or HTML artifacts. Use when brand colors, style guidelines, visual formatting, or company design standards apply.
---

# Hazel Health Brand Formatting

When creating slides, reports, dashboards, PDFs, or any visual deliverable, use these specs:

**Keywords**: branding, corporate identity, visual identity, styling, brand colors, typography, Hazel Health brand, visual formatting, visual design, hazel brand

## Fonts

- **Titles/Headings:** Marcellus (Google Fonts, serif)
- **Body/Labels:** Figtree (Google Fonts, sans-serif), weights 400/500/600/700
- **Google Fonts import:**
  ```css
  @import url('https://fonts.googleapis.com/css2?family=Marcellus&family=Figtree:wght@400;500;600;700&display=swap');
  ```

## Colors

- **Background:** `#FFF8F0` (warm cream)
- **Primary accent (headings, table headers, labels):** `#481B91` (deep purple)
- **Secondary accent (subtitles, lighter labels):** `#6B3FA0` (medium purple)
- **Muted text (meta lines, dates):** `#8A8494`
- **Body text:** `#2D2A33`
- **Table cell background:** `#FFFCF8`
- **Table borders:** `#E5DDD4`
- **Callout (info/neutral):** background `#F3ECF9`, left border `#481B91`
- **Callout (warning):** background `#FEF3C7`, left border `#B45309`
- **Callout (critical/risk):** background `#FFE4E6`, left border `#BE123C`
- **Status: positive/goal:** `#047857` (green)
- **Status: warning:** `#B45309` (amber)
- **Status: danger:** `#BE123C` (red)

## Layout Patterns

- **Subtitles:** uppercase, 13px, font-weight 700, letter-spacing 2px, color `#6B3FA0`
- **Section headings:** Marcellus, 18-22px, color `#481B91`
- **Table headers:** background `#481B91`, white text, uppercase, 13px, letter-spacing 1px
- **Callout boxes:** 4px left border, 6px border-radius on right side, 16px padding
- **Stat boxes:** centered number in Marcellus 32px, uppercase label below in 12px
- **Page background:** `#FFF8F0` everywhere, including print

## PDF Export

When converting HTML to PDF:

- Embed fonts as base64 (Google Fonts `@import` won't load in headless Chrome)
- Use Chrome headless with: `--headless --disable-gpu --run-all-compositor-stages-before-draw --virtual-time-budget=10000 --print-to-pdf --print-background --no-pdf-header-footer --no-margins`
- Set `@page { size: 8.5in 11in; margin: 0; }` and force `-webkit-print-color-adjust: exact` on all elements
- Scale font sizes down ~15-20% in `@media print` to fit content per page

## General Rules

- Never use generic fonts (Inter, Roboto, system defaults)
- Never use teal, navy, or blue palettes
- All executive-facing materials should feel warm and intentional, not clinical
- Confidential footer: "Hazel Health · [Month Year] · Confidential"
