# Technical SEO — Full Guide

## Overview

Comprehensive Next.js App Router SEO implementation covering metadata, structured data, sitemaps, social sharing, rendering strategies, and common mistakes. Every pattern uses the latest Next.js conventions.

---

## 1. Metadata API

### Static Metadata

Use the `metadata` export for pages with fixed metadata:

```typescript
// app/about/page.tsx
import type { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'About Us',
  description: 'Learn more about our company and mission.',
  keywords: ['about', 'company', 'mission'],
  authors: [{ name: 'John Doe', url: 'https://example.com' }],
  robots: {
    index: true,
    follow: true,
  },
}
```

### Dynamic Metadata

Use `generateMetadata` when metadata depends on dynamic data:

```typescript
// app/products/[id]/page.tsx
import type { Metadata, ResolvingMetadata } from 'next'

type Props = {
  params: Promise<{ id: string }>
}

export async function generateMetadata(
  { params }: Props,
  parent: ResolvingMetadata
): Promise<Metadata> {
  const { id } = await params
  const product = await getProduct(id)
  const previousImages = (await parent).openGraph?.images || []

  return {
    title: product.name,
    description: product.description,
    openGraph: {
      title: product.name,
      description: product.description,
      images: [product.image, ...previousImages],
    },
  }
}
```

### Title Templates

```typescript
// app/layout.tsx — sets template for all child pages
export const metadata: Metadata = {
  title: {
    template: '%s | Acme Inc',
    default: 'Acme Inc - Building the Future',
  },
  description: 'Acme Inc is a technology company...',
}

// app/blog/page.tsx — outputs "Blog | Acme Inc"
export const metadata: Metadata = {
  title: 'Blog',
}

// app/legal/privacy/page.tsx — ignores template
export const metadata: Metadata = {
  title: {
    absolute: 'Privacy Policy',
  },
}
```

### Metadata Base URL

Set once in root layout — all relative URLs resolve against this:

```typescript
// app/layout.tsx
export const metadata: Metadata = {
  metadataBase: new URL('https://acme.com'),
  alternates: {
    canonical: '/',
    languages: {
      'en-US': '/en-US',
      'de-DE': '/de-DE',
    },
  },
  openGraph: {
    images: '/og-image.png', // Becomes https://acme.com/og-image.png
  },
}
```

### Metadata Best Practices

- [ ] Keep titles under 60 characters
- [ ] Keep descriptions between 150-160 characters
- [ ] Use unique metadata for every page
- [ ] Set `metadataBase` in root layout
- [ ] Use static `metadata` for static pages, `generateMetadata` only when dynamic data is needed
- [ ] Never export both `metadata` and `generateMetadata` from the same file

### Complete Metadata Reference

```typescript
export const metadata: Metadata = {
  // Basic
  title: 'Page Title',
  description: 'Page description',
  keywords: ['keyword1', 'keyword2'],
  authors: [{ name: 'Author', url: 'https://...' }],
  creator: 'Creator Name',
  publisher: 'Publisher Name',

  // URLs
  metadataBase: new URL('https://acme.com'),
  alternates: {
    canonical: '/page',
    languages: { 'en-US': '/en-US/page' },
  },

  // Robots
  robots: {
    index: true,
    follow: true,
    googleBot: {
      index: true,
      follow: true,
      'max-image-preview': 'large',
    },
  },

  // Open Graph
  openGraph: {
    title: 'OG Title',
    description: 'OG Description',
    url: 'https://acme.com/page',
    siteName: 'Acme',
    images: [{ url: '/og.png', width: 1200, height: 630 }],
    locale: 'en_US',
    type: 'website',
  },

  // Twitter
  twitter: {
    card: 'summary_large_image',
    title: 'Twitter Title',
    description: 'Twitter Description',
    images: ['/twitter.png'],
    creator: '@username',
  },

  // Verification
  verification: {
    google: 'google-verification-code',
    yandex: 'yandex-verification-code',
  },

  // Icons
  icons: {
    icon: '/icon.png',
    apple: '/apple-icon.png',
  },

  // Manifest
  manifest: '/manifest.webmanifest',
}
```

---

## 2. Structured Data / JSON-LD

### Implementation Pattern

Always escape `<` characters to prevent XSS when rendering JSON-LD:

```typescript
// components/json-ld.tsx
function JsonLd({ data }: { data: Record<string, unknown> }) {
  const sanitized = JSON.stringify(data).replace(/</g, '\\u003c')
  return (
    <script
      type="application/ld+json"
      dangerouslySetInnerHTML={{ __html: sanitized }}
    />
  )
}
```

> **Note:** `dangerouslySetInnerHTML` is the standard Next.js pattern for JSON-LD.
> The `.replace(/</g, '\\u003c')` escaping prevents script injection.
> This is documented in the [official Next.js JSON-LD guide](https://nextjs.org/docs/app/guides/json-ld).

### Type-Safe with schema-dts

```typescript
import type { Product, WithContext } from 'schema-dts'

const jsonLd: WithContext<Product> = {
  '@context': 'https://schema.org',
  '@type': 'Product',
  name: 'Widget',
  image: 'https://acme.com/widget.png',
  description: 'A great widget.',
}
```

### Organization Schema (root layout)

```typescript
const organizationSchema = {
  '@context': 'https://schema.org',
  '@type': 'Organization',
  name: 'Acme Inc',
  url: 'https://acme.com',
  logo: 'https://acme.com/logo.png',
  sameAs: [
    'https://twitter.com/acme',
    'https://linkedin.com/company/acme',
  ],
  contactPoint: {
    '@type': 'ContactPoint',
    telephone: '+1-800-555-1234',
    contactType: 'customer service',
  },
}
```

### Product Schema

```typescript
const productSchema = {
  '@context': 'https://schema.org',
  '@type': 'Product',
  name: product.name,
  image: product.images,
  description: product.description,
  sku: product.sku,
  brand: {
    '@type': 'Brand',
    name: product.brand,
  },
  offers: {
    '@type': 'Offer',
    url: `https://acme.com/products/${product.slug}`,
    priceCurrency: 'USD',
    price: product.price,
    availability: product.inStock
      ? 'https://schema.org/InStock'
      : 'https://schema.org/OutOfStock',
  },
}
```

### Article Schema (blog posts)

```typescript
const articleSchema = {
  '@context': 'https://schema.org',
  '@type': 'Article',
  headline: post.title,
  description: post.excerpt,
  image: post.featuredImage,
  datePublished: post.publishedAt,
  dateModified: post.updatedAt,
  author: {
    '@type': 'Person',
    name: post.author.name,
    url: post.author.url,
  },
  publisher: {
    '@type': 'Organization',
    name: 'Acme Inc',
    logo: {
      '@type': 'ImageObject',
      url: 'https://acme.com/logo.png',
    },
  },
}
```

### FAQ Schema

```typescript
const faqSchema = {
  '@context': 'https://schema.org',
  '@type': 'FAQPage',
  mainEntity: faqs.map((faq) => ({
    '@type': 'Question',
    name: faq.question,
    acceptedAnswer: {
      '@type': 'Answer',
      text: faq.answer,
    },
  })),
}
```

### BreadcrumbList Schema

```typescript
const breadcrumbSchema = {
  '@context': 'https://schema.org',
  '@type': 'BreadcrumbList',
  itemListElement: [
    {
      '@type': 'ListItem',
      position: 1,
      name: 'Home',
      item: 'https://acme.com',
    },
    {
      '@type': 'ListItem',
      position: 2,
      name: 'Products',
      item: 'https://acme.com/products',
    },
    {
      '@type': 'ListItem',
      position: 3,
      name: product.name,
      item: `https://acme.com/products/${product.slug}`,
    },
  ],
}
```

### LocalBusiness Schema

```typescript
const localBusinessSchema = {
  '@context': 'https://schema.org',
  '@type': 'LocalBusiness',
  name: 'Acme Coffee Shop',
  image: 'https://acme.com/storefront.jpg',
  '@id': 'https://acme.com',
  url: 'https://acme.com',
  telephone: '+1-555-123-4567',
  address: {
    '@type': 'PostalAddress',
    streetAddress: '123 Main St',
    addressLocality: 'Charleston',
    addressRegion: 'SC',
    postalCode: '29401',
    addressCountry: 'US',
  },
  geo: {
    '@type': 'GeoCoordinates',
    latitude: 32.7765,
    longitude: -79.9311,
  },
  openingHoursSpecification: [
    {
      '@type': 'OpeningHoursSpecification',
      dayOfWeek: ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'],
      opens: '08:00',
      closes: '18:00',
    },
  ],
}
```

### WebSite Schema with Search

```typescript
const websiteSchema = {
  '@context': 'https://schema.org',
  '@type': 'WebSite',
  name: 'Acme Inc',
  url: 'https://acme.com',
  potentialAction: {
    '@type': 'SearchAction',
    target: {
      '@type': 'EntryPoint',
      urlTemplate: 'https://acme.com/search?q={search_term_string}',
    },
    'query-input': 'required name=search_term_string',
  },
}
```

### Validation Tools

- [Google Rich Results Test](https://search.google.com/test/rich-results)
- [Schema Markup Validator](https://validator.schema.org/)

---

## 3. Open Graph & Social

### Open Graph for Blog Posts

```typescript
export async function generateMetadata({ params }): Promise<Metadata> {
  const { slug } = await params
  const post = await getPost(slug)

  return {
    openGraph: {
      title: post.title,
      description: post.excerpt,
      url: `https://acme.com/blog/${slug}`,
      siteName: 'Acme Blog',
      images: [
        {
          url: post.featuredImage,
          width: 1200,
          height: 630,
          alt: post.title,
        },
      ],
      locale: 'en_US',
      type: 'article',
      publishedTime: post.publishedAt,
      modifiedTime: post.updatedAt,
      authors: [post.author.name],
      section: post.category,
      tags: post.tags,
    },
    twitter: {
      card: 'summary_large_image',
      title: post.title,
      description: post.excerpt,
      creator: '@acme',
      images: [post.featuredImage],
    },
  }
}
```

### Dynamic OG Image Generation

#### Site-Wide Default

```typescript
// app/opengraph-image.tsx
import { ImageResponse } from 'next/og'

export const runtime = 'edge'
export const alt = 'Acme Inc'
export const size = { width: 1200, height: 630 }
export const contentType = 'image/png'

export default async function Image() {
  return new ImageResponse(
    (
      <div
        style={{
          height: '100%',
          width: '100%',
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          backgroundColor: '#000',
          backgroundImage: 'linear-gradient(to bottom right, #1a1a2e, #16213e)',
        }}
      >
        <div style={{ fontSize: 72, fontWeight: 'bold', color: 'white' }}>
          Acme Inc
        </div>
        <div style={{ fontSize: 32, color: '#888', marginTop: 20 }}>
          Building the Future
        </div>
      </div>
    ),
    { ...size }
  )
}
```

#### Per-Page Dynamic OG Image

```typescript
// app/blog/[slug]/opengraph-image.tsx
import { ImageResponse } from 'next/og'
import { readFile } from 'node:fs/promises'
import { join } from 'node:path'

export const alt = 'Blog Post'
export const size = { width: 1200, height: 630 }
export const contentType = 'image/png'

export default async function Image({
  params,
}: {
  params: Promise<{ slug: string }>
}) {
  const { slug } = await params
  const post = await getPost(slug)

  const interBold = await readFile(
    join(process.cwd(), 'assets/fonts/Inter-Bold.ttf')
  )

  return new ImageResponse(
    (
      <div
        style={{
          height: '100%',
          width: '100%',
          display: 'flex',
          flexDirection: 'column',
          padding: 60,
          backgroundImage: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        }}
      >
        <div style={{ display: 'flex', flexDirection: 'column', flex: 1, justifyContent: 'center' }}>
          <div style={{ fontSize: 64, fontWeight: 'bold', color: 'white', lineHeight: 1.2, maxWidth: 900 }}>
            {post.title}
          </div>
          <div style={{ fontSize: 28, color: 'rgba(255,255,255,0.8)', marginTop: 24 }}>
            {post.author.name} · {new Date(post.publishedAt).toLocaleDateString()}
          </div>
        </div>
      </div>
    ),
    {
      ...size,
      fonts: [{ name: 'Inter', data: interBold, style: 'normal', weight: 700 }],
    }
  )
}
```

### OG Image Size Reference

| Platform | Recommended Size |
|----------|------------------|
| Open Graph (Facebook) | 1200 x 630 |
| Twitter | 1200 x 628 |
| LinkedIn | 1200 x 627 |

---

## 4. Sitemaps

### Dynamic Sitemap

```typescript
// app/sitemap.ts
import type { MetadataRoute } from 'next'

export default async function sitemap(): Promise<MetadataRoute.Sitemap> {
  const baseUrl = 'https://acme.com'

  const posts = await getAllPosts()
  const products = await getAllProducts()

  const staticPages: MetadataRoute.Sitemap = [
    { url: baseUrl, lastModified: new Date(), changeFrequency: 'monthly', priority: 1 },
    { url: `${baseUrl}/about`, lastModified: new Date(), changeFrequency: 'yearly', priority: 0.8 },
    { url: `${baseUrl}/contact`, lastModified: new Date(), changeFrequency: 'yearly', priority: 0.5 },
  ]

  const blogPages: MetadataRoute.Sitemap = posts.map((post) => ({
    url: `${baseUrl}/blog/${post.slug}`,
    lastModified: new Date(post.updatedAt),
    changeFrequency: 'weekly' as const,
    priority: 0.7,
  }))

  const productPages: MetadataRoute.Sitemap = products.map((product) => ({
    url: `${baseUrl}/products/${product.slug}`,
    lastModified: new Date(product.updatedAt),
    changeFrequency: 'daily' as const,
    priority: 0.9,
  }))

  return [...staticPages, ...blogPages, ...productPages]
}
```

### Sitemap with Images

```typescript
export default function sitemap(): MetadataRoute.Sitemap {
  return [
    {
      url: 'https://acme.com/products/widget',
      lastModified: new Date(),
      images: [
        'https://acme.com/images/widget-front.jpg',
        'https://acme.com/images/widget-side.jpg',
      ],
    },
  ]
}
```

### Localized Sitemap

```typescript
export default function sitemap(): MetadataRoute.Sitemap {
  return [
    {
      url: 'https://acme.com',
      lastModified: new Date(),
      alternates: {
        languages: {
          en: 'https://acme.com/en',
          es: 'https://acme.com/es',
          de: 'https://acme.com/de',
        },
      },
    },
  ]
}
```

### Multi-Sitemap for Large Sites (50k+ URLs)

```typescript
const URLS_PER_SITEMAP = 50000

export async function generateSitemaps() {
  const totalProducts = await getProductCount()
  const numberOfSitemaps = Math.ceil(totalProducts / URLS_PER_SITEMAP)
  return Array.from({ length: numberOfSitemaps }, (_, i) => ({ id: i }))
}

export default async function sitemap(props: {
  id: Promise<string>
}): Promise<MetadataRoute.Sitemap> {
  const id = Number(await props.id)
  const start = id * URLS_PER_SITEMAP
  const products = await getProducts({ offset: start, limit: URLS_PER_SITEMAP })

  return products.map((product) => ({
    url: `https://acme.com/products/${product.slug}`,
    lastModified: product.updatedAt,
  }))
}
```

---

## 5. Robots Configuration

### Dynamic robots.ts

```typescript
// app/robots.ts
import type { MetadataRoute } from 'next'

export default function robots(): MetadataRoute.Robots {
  const baseUrl = process.env.NEXT_PUBLIC_BASE_URL || 'https://acme.com'

  return {
    rules: [
      {
        userAgent: '*',
        allow: '/',
        disallow: ['/admin/', '/api/', '/private/', '/_next/'],
      },
      {
        userAgent: 'GPTBot',
        disallow: ['/'],
      },
      {
        userAgent: 'CCBot',
        disallow: ['/'],
      },
    ],
    sitemap: `${baseUrl}/sitemap.xml`,
    host: baseUrl,
  }
}
```

### Per-Page Noindex

```typescript
export const metadata: Metadata = {
  robots: {
    index: false,
    follow: false,
    nocache: true,
    googleBot: {
      index: false,
      follow: false,
      noimageindex: true,
    },
  },
}
```

### Robots Directives Reference

| Directive | Purpose |
|-----------|---------|
| `index` / `noindex` | Allow/prevent page indexing |
| `follow` / `nofollow` | Follow/ignore links on page |
| `noarchive` | Don't show cached version |
| `noimageindex` | Don't index images on page |
| `max-snippet` | Max text snippet length |
| `max-image-preview` | Max image preview size (`none`, `standard`, `large`) |
| `max-video-preview` | Max video preview length in seconds |

---

## 6. Canonical URLs

### Setting Canonical URLs

```typescript
export async function generateMetadata({ params }): Promise<Metadata> {
  const { slug } = await params
  return {
    alternates: {
      canonical: `https://acme.com/products/${slug}`,
    },
  }
}
```

### Trailing Slash Configuration

```typescript
// next.config.ts — pick one and be consistent
const config: NextConfig = {
  trailingSlash: false, // /about (redirect /about/ -> /about)
}
```

### WWW Redirect

```typescript
// next.config.ts
const config: NextConfig = {
  async redirects() {
    return [
      {
        source: '/:path*',
        has: [{ type: 'host', value: 'www.acme.com' }],
        destination: 'https://acme.com/:path*',
        permanent: true,
      },
    ]
  },
}
```

### Self-Healing URLs

```typescript
import { redirect, notFound } from 'next/navigation'

export default async function ProductPage({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = await params
  const product = await getProductBySlug(slug)

  if (!product) notFound()
  if (product.slug !== slug) redirect(`/products/${product.slug}`)

  return <div>{product.name}</div>
}
```

---

## 7. International SEO

### Hreflang Tags

```typescript
export async function generateMetadata({ params }): Promise<Metadata> {
  const { locale } = await params
  return {
    alternates: {
      canonical: `https://acme.com/${locale}`,
      languages: {
        en: 'https://acme.com/en',
        es: 'https://acme.com/es',
        de: 'https://acme.com/de',
        'x-default': 'https://acme.com/en',
      },
    },
  }
}
```

### Localized Metadata

```typescript
const translations = {
  en: { title: 'Welcome', description: 'Welcome to our site' },
  es: { title: 'Bienvenido', description: 'Bienvenido a nuestro sitio' },
  de: { title: 'Willkommen', description: 'Willkommen auf unserer Seite' },
}

export async function generateMetadata({ params }): Promise<Metadata> {
  const { locale } = await params
  const t = translations[locale as keyof typeof translations]
  return {
    title: t.title,
    description: t.description,
    openGraph: { locale },
  }
}
```

---

## 8. Rendering Strategies & SEO Impact

| Strategy | Crawlability | Time to Index | Best For |
|----------|--------------|---------------|----------|
| **SSG** | Excellent | Immediate | Marketing pages, blog, docs |
| **ISR** | Excellent | Fast | Semi-dynamic content (products, listings) |
| **SSR** | Excellent | Fast | Personalized / real-time content |
| **CSR** | Poor | Delayed/None | Dashboards only (never for public pages) |

### ISR Configuration

```typescript
// Revalidate every hour
export const revalidate = 3600

// On-demand revalidation via webhook
import { revalidatePath, revalidateTag } from 'next/cache'

export async function POST(request: NextRequest) {
  const { path, tag, secret } = await request.json()
  if (secret !== process.env.REVALIDATION_SECRET) {
    return NextResponse.json({ error: 'Invalid secret' }, { status: 401 })
  }
  if (path) revalidatePath(path)
  if (tag) revalidateTag(tag)
  return NextResponse.json({ revalidated: true })
}
```

### generateStaticParams for SSG

```typescript
export async function generateStaticParams() {
  const posts = await getAllPosts()
  return posts.map((post) => ({ slug: post.slug }))
}

// Return 404 for unknown params (strict) or allow dynamic rendering (flexible)
export const dynamicParams = true
```

---

## 9. URL Structure Best Practices

| Practice | Good | Bad |
|----------|------|-----|
| Lowercase | `/products/widget` | `/Products/Widget` |
| Hyphens | `/product-details` | `/product_details` |
| Short & descriptive | `/blog/seo-tips` | `/blog/article/2024/tips-for-search-engine-optimization` |
| Keywords | `/services/web-development` | `/services/s12345` |
| Clean paths | `/products/bags` | `/products?category=bags` |

---

## 10. Internal Linking

### Prefetching Control

```typescript
// Default: prefetch when link enters viewport
<Link href="/products">Products</Link>

// Disable prefetch for less important links
<Link href="/about" prefetch={false}>About</Link>
```

### Accessible Link Text

```typescript
// GOOD: descriptive
<Link href="/products/leather-bag">View the Leather Messenger Bag</Link>

// BAD: generic
<Link href="/products/leather-bag">Click here</Link>
```

### Breadcrumb Navigation

```typescript
function Breadcrumb({ items }: { items: Array<{ label: string; href: string }> }) {
  return (
    <nav aria-label="Breadcrumb">
      <ol className="flex gap-2">
        {items.map((item, index) => (
          <li key={item.href} className="flex items-center gap-2">
            {index > 0 && <span>/</span>}
            {index === items.length - 1 ? (
              <span aria-current="page">{item.label}</span>
            ) : (
              <Link href={item.href}>{item.label}</Link>
            )}
          </li>
        ))}
      </ol>
    </nav>
  )
}
```

---

## 11. Common Mistakes

### Client-Side Only Rendering

```typescript
// BAD: content invisible to crawlers
'use client'
export default function ProductList() {
  const [products, setProducts] = useState([])
  useEffect(() => {
    fetch('/api/products').then((r) => r.json()).then(setProducts)
  }, [])
  return <div>{products.map(p => <div key={p.id}>{p.name}</div>)}</div>
}

// GOOD: server component — content in initial HTML
export default async function ProductList() {
  const products = await getProducts()
  return <div>{products.map(p => <div key={p.id}>{p.name}</div>)}</div>
}
```

### Soft 404 Errors

```typescript
// BAD: returns 200 with "not found" content
if (!product) return <div>Product not found</div>

// GOOD: proper 404 status
import { notFound } from 'next/navigation'
if (!product) notFound()
```

### Client-Side Redirects

```typescript
// BAD: client-side redirect — crawlers may not follow
'use client'
useEffect(() => { router.push('/new-page') }, [])

// GOOD: server-side redirect
import { redirect } from 'next/navigation'
redirect('/new-page')
```

### Redirect Chains

```typescript
// BAD: /old -> /temp -> /new (chain)
// GOOD: /old -> /new (direct)
export default {
  async redirects() {
    return [
      { source: '/old-page', destination: '/new-page', permanent: true },
    ]
  },
}
```

### Missing Alt Text

```typescript
// BAD
<Image src="/product.jpg" width={400} height={300} alt="" />

// GOOD
<Image
  src="/product.jpg"
  alt="Blue leather messenger bag with brass buckles"
  width={400}
  height={300}
/>
```

---

## 12. File-Based Metadata (App Router)

```
app/
├── favicon.ico            → /favicon.ico
├── icon.png               → /icon-<hash>.png
├── apple-icon.png         → /apple-icon.png
├── opengraph-image.tsx    → Dynamic OG image
├── twitter-image.tsx      → Dynamic Twitter image
├── robots.ts              → /robots.txt
├── sitemap.ts             → /sitemap.xml
└── manifest.ts            → /manifest.webmanifest
```

---

## 13. SEO Audit Checklist

| Category | Check |
|----------|-------|
| **Metadata** | Unique title per page (< 60 chars) |
| | Unique description per page (150-160 chars) |
| | `metadataBase` set in root layout |
| | Title template configured |
| **Structured Data** | Organization schema on homepage |
| | Product schema on product pages |
| | Article schema on blog posts |
| | FAQ schema on FAQ pages |
| | BreadcrumbList on deep pages |
| | Validated with Rich Results Test |
| **Social** | OG image (1200x630) on all pages |
| | Twitter card configured |
| | Dynamic OG images for content pages |
| **Technical** | `sitemap.xml` exists and is valid |
| | `robots.txt` properly configured |
| | Canonical URLs set on all pages |
| | No redirect chains |
| | Proper 404 handling with `notFound()` |
| | Server-side redirects (not client-side) |
| **Content** | All images have descriptive alt text |
| | No broken internal links |
| | Descriptive link text (no "click here") |
| | Clean URL structure |
| **Performance** | LCP < 2.5s |
| | INP < 200ms |
| | CLS < 0.1 |
| **i18n** | hreflang tags for multi-language |
| | x-default set |
| | Localized metadata |
