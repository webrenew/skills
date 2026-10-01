---
name: overscroll-behavior
description: >
  Kill the macOS/desktop rubber-band overscroll bounce without breaking mobile pull-to-refresh,
  by setting `overscroll-behavior: none` on the root scroller gated behind `@media (pointer: fine)`
  (the pattern Vercel ships). Also covers `overscroll-behavior: contain` for modals, drawers,
  sidebars, and other nested scroll areas to stop scroll chaining. Triggers whenever building or
  reviewing a root layout, global CSS (globals.css, app/layout.tsx, _document, index.css), app
  shells, dashboards, full-height/fixed-viewport UIs, chat or editor layouts, scrollable panels,
  modals, sheets, or when the user mentions overscroll, rubber-band, bounce, elastic scroll,
  scroll chaining, pull-to-refresh, or "the page bounces on my trackpad".
---

# Overscroll Behavior — No Bounce on Desktop, Pull-to-Refresh on Mobile

**RULE: Disable root overscroll only for fine pointers. Never disable it for touch.**

```css
@media (pointer: fine) {
  html,
  body {
    overscroll-behavior: none;
  }
}
```

- `overscroll-behavior: none` stops the elastic rubber-band bounce when a trackpad or mouse
  scrolls past the top or bottom of the page. App-like UIs (dashboards, editors, sticky
  headers, fixed sidebars) stop showing a blank gap or a dragged-off header.
- `(pointer: fine)` means the **primary** input is a mouse or trackpad. Phones and tablets report
  `pointer: coarse`, so the rule does not apply there and **pull-to-refresh keeps working**.
- On Chrome desktop, `none` on the root also blocks the horizontal swipe back/forward gesture.
  That is usually fine for app UIs. If you want to keep it, set only the vertical axis:
  `overscroll-behavior-y: none`.

## Why the gate matters

An ungated `html { overscroll-behavior: none }` removes pull-to-refresh on Android Chrome and
iOS Safari. Mobile users lose a gesture they expect, and nothing tells them why. The media
query keeps the fix on the devices that have the problem.

## Placement

The root scroller is the viewport, which reads the value from `html`. Put the rule in global
CSS, once. Include `body` too because it is harmless and covers layouts where `body` is the
scroll container.

### Tailwind v4.1+

Use the built-in `pointer-fine` variant on the root element:

```tsx
// app/layout.tsx
<html lang="en" className="pointer-fine:overscroll-none">
  <body className="pointer-fine:overscroll-none">{children}</body>
</html>
```

Or in `globals.css`:

```css
@layer base {
  html, body {
    @variant pointer-fine {
      overscroll-behavior: none;
    }
  }
}
```

### Tailwind v3

No `pointer-fine` variant. Use an arbitrary variant or plain CSS:

```tsx
<html className="[@media(pointer:fine)]:overscroll-none">
```

## Nested scroll areas: use `contain`, not `none`

For anything that scrolls inside the page — modals, drawers, sheets, command palettes, chat
message lists, sidebars, dropdown lists — use `contain` so scrolling to the end of the panel
does not chain into the page behind it:

```css
.modal-body,
.drawer,
.sidebar-scroll {
  overflow-y: auto;
  overscroll-behavior: contain; /* Tailwind: overscroll-contain */
}
```

`contain` keeps the local bounce effect but stops scroll chaining. Do **not** gate this one
behind `(pointer: fine)` — chaining from a modal into the page is a bug on touch too, and
pull-to-refresh triggered from inside a modal is never what the user wants.

## Banned alternatives

```ts
// BANNED — non-passive wheel/touch listeners to block bounce
window.addEventListener('wheel', e => e.preventDefault(), { passive: false })
document.addEventListener('touchmove', e => e.preventDefault(), { passive: false })
```

These block the compositor, cause scroll jank, and kill native gestures everywhere. The CSS
property does the same job with zero runtime cost.

```css
/* BANNED — ungated, breaks pull-to-refresh on mobile */
html { overscroll-behavior: none; }

/* BANNED — position:fixed body hack to stop bounce */
body { position: fixed; inset: 0; overflow: hidden; }
```

## Companion detail

Set an explicit `background-color` on `html` that matches the page edges (and `theme-color`
meta for mobile). Touch devices still bounce by design, and the revealed area should match
the page, not flash white in dark mode.

## Review checklist

When you touch global CSS or a root layout:

1. Is there a root `overscroll-behavior: none`? If missing in an app-like UI, add it **gated**.
2. Is an existing root `overscroll-behavior: none` ungated? Wrap it in `@media (pointer: fine)`.
3. Do modals, drawers, and inner scroll panels use `overscroll-behavior: contain`?
4. Are there `preventDefault` wheel/touchmove listeners used to stop bounce? Replace with CSS.
5. Does `html` have a background color that matches the page in light and dark mode?

## Verify

- macOS trackpad, Safari and Chrome: scroll hard past top and bottom → no bounce, no gap.
- iOS Safari / Android Chrome (real device): pull down at the top → pull-to-refresh still works.
- DevTools device emulation switches to `pointer: coarse`, so the rule turns off there — that
  confirms the gate, but test the gesture on a real phone.
- Touchscreen laptops report `pointer: fine` (primary input is the trackpad), so the rule
  applies. That is intended; desktop browsers have no pull-to-refresh to protect.
