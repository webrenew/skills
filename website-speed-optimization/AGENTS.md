# Website Speed Optimization — Full Guide

## Overview

Systematic Next.js performance optimization covering server, network, rendering, and runtime layers. Every recommendation maps to measurable Core Web Vital or Lighthouse metric improvements.

---

## 1. Audit Checklist

Run this checklist before making changes to establish a baseline:

### Server & TTFB
- [ ] Check `next.config.ts` for misconfigurations (missing `output`, unnecessary rewrites)
- [ ] Verify data fetching uses parallel `Promise.all()` not sequential awaits
- [ ] Check for blocking `getServerSideProps` — prefer `getStaticProps` + ISR where possible
- [ ] Review middleware — each middleware adds latency to every matched request
- [ ] Check database queries in server components for N+1 patterns
- [ ] Verify CDN/edge caching headers (`Cache-Control`, `s-maxage`, `stale-while-revalidate`)

### Bundle Size
- [ ] Run `npx @next/bundle-analyzer` or `ANALYZE=true next build`
- [ ] Check for barrel file imports (e.g., `import { x } from 'library'` vs direct path)
- [ ] Verify `optimizePackageImports` in `next.config.ts` for large libraries
- [ ] Check for client-side-only libraries loaded in server components
- [ ] Look for duplicate dependencies (`pnpm why <package>`)
- [ ] Verify tree-shaking works — no side-effect imports

### Images
- [ ] All images use `next/image` component
- [ ] LCP image has `priority` prop set
- [ ] Images have explicit `width`/`height` or use `fill` with `sizes` prop
- [ ] Verify `sizes` prop matches actual rendered size (not just `100vw`)
- [ ] Check for unoptimized images (`unoptimized` prop or missing from config)
- [ ] Review image formats — prefer AVIF/WebP via Next.js automatic optimization

### Fonts
- [ ] Using `next/font` for all fonts (Google or local)
- [ ] Font `display: swap` or `display: optional` set appropriately
- [ ] Subset fonts to needed character ranges
- [ ] No external font CSS loaded via `<link>` tags
- [ ] Preload critical fonts

### Scripts & Third-Party
- [ ] Third-party scripts use `next/script` with appropriate `strategy`
- [ ] Analytics/tracking deferred with `afterInteractive` or `lazyOnload`
- [ ] No render-blocking scripts in `<head>`
- [ ] Review third-party impact with Lighthouse "Reduce JavaScript execution time"
- [ ] Consider Partytown for heavy third-party scripts

### CSS
- [ ] No unused CSS — check with coverage tools
- [ ] Critical CSS is inlined (Tailwind handles this well)
- [ ] No large CSS-in-JS runtime (styled-components/emotion add ~15-30KB)
- [ ] Avoid `@import` chains in CSS files

### Rendering & Hydration
- [ ] Maximize Server Components — minimize `'use client'` boundary
- [ ] Client components pushed to leaf nodes of component tree
- [ ] No unnecessary `useEffect` on mount that could be server-rendered
- [ ] Check for hydration mismatches (console warnings)
- [ ] Large lists use virtualization (`react-window`, `@tanstack/react-virtual`)

---

## 2. Core Web Vitals — Diagnosis & Fixes

### LCP (Largest Contentful Paint) — Target: < 2.5s

**Common causes and fixes:**

| Cause | Fix |
|-------|-----|
| Hero image not prioritized | Add `priority` to `next/image` |
| Slow server response | Enable ISR/SSG, add `stale-while-revalidate` |
| Render-blocking resources | Defer non-critical CSS/JS |
| Client-side data fetching for above-fold content | Move to server component |
| Large JavaScript bundle delays hydration | Code-split with `dynamic()` |
| Font loading delays text render | Use `next/font` with `display: swap` |

```typescript
// LCP image — always set priority for above-fold hero
import Image from 'next/image'

export function Hero() {
  return (
    <Image
      src="/hero.webp"
      alt="Hero"
      width={1200}
      height={600}
      priority
      sizes="100vw"
    />
  )
}
```

### CLS (Cumulative Layout Shift) — Target: < 0.1

**Common causes and fixes:**

| Cause | Fix |
|-------|-----|
| Images without dimensions | Always set `width`/`height` or use `fill` with container |
| Dynamic content injected above fold | Reserve space with skeleton/placeholder |
| Fonts causing FOUT | Use `next/font` with `display: optional` for body text |
| Ads/embeds without reserved space | Set explicit container dimensions |
| Client-side navigation layout changes | Ensure layout components are server components |

```typescript
// Reserve space for dynamic content
function AdSlot() {
  return (
    <div className="min-h-[250px] w-full bg-muted animate-pulse">
      <Suspense fallback={<Skeleton className="h-[250px] w-full" />}>
        <Ad />
      </Suspense>
    </div>
  )
}
```

### INP (Interaction to Next Paint) — Target: < 200ms

**Common causes and fixes:**

| Cause | Fix |
|-------|-----|
| Heavy event handlers blocking main thread | Use `startTransition` for non-urgent updates |
| Large re-renders on interaction | Memoize with `useMemo`/`useCallback`, split state |
| Synchronous state updates cascade | Batch updates, use `useTransition` |
| Long task in click handler | Move to Web Worker or `requestIdleCallback` |

```typescript
'use client'
import { useTransition } from 'react'

function SearchResults({ query }: { query: string }) {
  const [isPending, startTransition] = useTransition()
  const [results, setResults] = useState([])

  function handleSearch(value: string) {
    // Urgent: update input immediately
    setQuery(value)
    // Non-urgent: update results without blocking
    startTransition(() => {
      setResults(filterResults(value))
    })
  }

  return (
    <div className={isPending ? 'opacity-70' : ''}>
      {results.map(r => <ResultCard key={r.id} result={r} />)}
    </div>
  )
}
```

---

## 3. Next.js Configuration Optimizations

```typescript
// next.config.ts
import type { NextConfig } from 'next'

const config: NextConfig = {
  // Reduce bundle size for large icon/component libraries
  optimizePackageImports: [
    'lucide-react',
    '@radix-ui/react-icons',
    'date-fns',
    'lodash-es',
    '@phosphor-icons/react',
  ],

  images: {
    // Use modern formats
    formats: ['image/avif', 'image/webp'],
    // Set appropriate device sizes
    deviceSizes: [640, 750, 828, 1080, 1200, 1920],
    // Minimize image sizes generated
    imageSizes: [16, 32, 48, 64, 96, 128, 256],
    // Cache optimized images longer
    minimumCacheTTL: 60 * 60 * 24 * 30, // 30 days
  },

  // Enable compression
  compress: true,

  // Production source maps only if needed for error tracking
  productionBrowserSourceMaps: false,

  // Strict mode catches issues early
  reactStrictMode: true,

  // Headers for caching static assets
  async headers() {
    return [
      {
        source: '/fonts/:path*',
        headers: [
          {
            key: 'Cache-Control',
            value: 'public, max-age=31536000, immutable',
          },
        ],
      },
      {
        source: '/_next/static/:path*',
        headers: [
          {
            key: 'Cache-Control',
            value: 'public, max-age=31536000, immutable',
          },
        ],
      },
    ]
  },
}

export default config
```

---

## 4. Server Component Data Fetching Patterns

```typescript
// Deduplicate with React.cache
import { cache } from 'react'

export const getProduct = cache(async (id: string) => {
  return db.product.findUnique({ where: { id } })
})

// Parallel fetching in page
export default async function ProductPage({
  params,
}: {
  params: { id: string }
}) {
  const [product, reviews, related] = await Promise.all([
    getProduct(params.id),
    getReviews(params.id),
    getRelatedProducts(params.id),
  ])

  return (
    <>
      <ProductDetails product={product} />
      <Suspense fallback={<ReviewsSkeleton />}>
        <Reviews reviews={reviews} />
      </Suspense>
      <Suspense fallback={<RelatedSkeleton />}>
        <RelatedProducts products={related} />
      </Suspense>
    </>
  )
}
```

---

## 5. Dynamic Import Patterns

```typescript
import dynamic from 'next/dynamic'

// Heavy chart library — only load when visible
const Chart = dynamic(() => import('@/components/chart'), {
  loading: () => <Skeleton className="h-[400px] w-full" />,
  ssr: false,
})

// Modal — load on interaction
const SettingsModal = dynamic(() => import('@/components/settings-modal'))

// Below-fold sections
const Testimonials = dynamic(() => import('@/components/testimonials'))
const FAQ = dynamic(() => import('@/components/faq'))
```

---

## 6. Caching Strategy

### Route Segment Config

```typescript
// Static page with ISR — revalidate every hour
export const revalidate = 3600

// Force dynamic for user-specific pages
export const dynamic = 'force-dynamic'

// Edge runtime for fastest TTFB
export const runtime = 'edge'
```

### API Route Caching

```typescript
// app/api/products/route.ts
import { NextResponse } from 'next/server'

export async function GET() {
  const products = await getProducts()

  return NextResponse.json(products, {
    headers: {
      'Cache-Control': 'public, s-maxage=3600, stale-while-revalidate=86400',
    },
  })
}
```

### Fetch-Level Caching

```typescript
// Cache for 1 hour, serve stale for 24 hours while revalidating
const data = await fetch('https://api.example.com/data', {
  next: { revalidate: 3600 },
})

// Tag-based revalidation
const data = await fetch('https://api.example.com/products', {
  next: { tags: ['products'] },
})

// Revalidate by tag on mutation
import { revalidateTag } from 'next/cache'
revalidateTag('products')
```

---

## 7. Font Optimization

```typescript
// app/layout.tsx
import { Inter, JetBrains_Mono } from 'next/font/google'

const inter = Inter({
  subsets: ['latin'],
  display: 'swap',
  variable: '--font-sans',
})

const mono = JetBrains_Mono({
  subsets: ['latin'],
  display: 'swap',
  variable: '--font-mono',
})

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className={`${inter.variable} ${mono.variable}`}>
      <body className="font-sans">{children}</body>
    </html>
  )
}
```

---

## 8. Script Loading Strategy

```typescript
import Script from 'next/script'

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        {children}

        {/* Analytics — load after page is interactive */}
        <Script
          src="https://www.googletagmanager.com/gtag/js?id=G-XXXXX"
          strategy="afterInteractive"
        />

        {/* Non-critical — load when browser is idle */}
        <Script
          src="https://widget.example.com/embed.js"
          strategy="lazyOnload"
        />

        {/* Critical — load before hydration (rare, use sparingly) */}
        <Script
          src="/critical-polyfill.js"
          strategy="beforeInteractive"
        />
      </body>
    </html>
  )
}
```

---

## 9. Monitoring & Measurement

### Web Vitals Reporting

```typescript
// app/layout.tsx or a client component
'use client'
import { useReportWebVitals } from 'next/web-vitals'

export function WebVitals() {
  useReportWebVitals((metric) => {
    // Send to your analytics
    const body = {
      name: metric.name,       // LCP, FID, CLS, INP, TTFB
      value: metric.value,
      rating: metric.rating,   // 'good' | 'needs-improvement' | 'poor'
      id: metric.id,
      page: window.location.pathname,
    }

    // Use sendBeacon for reliability
    if (navigator.sendBeacon) {
      navigator.sendBeacon('/api/vitals', JSON.stringify(body))
    }
  })

  return null
}
```

### Build Analysis Commands

```bash
# Bundle analyzer
ANALYZE=true pnpm build

# Check unused dependencies
pnpm dlx depcheck

# Check duplicate dependencies
pnpm dlx duplicate-package-checker-webpack-plugin

# Lighthouse CI
pnpm dlx @lhci/cli autorun
```

---

## 10. Quick Wins Checklist

High-impact changes that take < 30 minutes:

1. **Add `priority` to LCP image** — instant LCP improvement
2. **Enable `optimizePackageImports`** — reduces bundle by 10-50KB+
3. **Switch to `next/font`** — eliminates font FOUT/FOIT
4. **Add `sizes` prop to images** — prevents oversized image downloads
5. **Wrap below-fold sections in `dynamic()`** — reduces initial JS
6. **Add `loading="lazy"` to iframes** — defers offscreen content
7. **Set `Cache-Control` headers on static assets** — faster repeat visits
8. **Move data fetching to server components** — reduces client JS + waterfall
9. **Add `Suspense` boundaries around slow sections** — progressive loading
10. **Enable React Strict Mode** — catches performance anti-patterns in dev
