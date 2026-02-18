# Headless CMS Integration Guide for Next.js

This guide provides comprehensive patterns for integrating headless CMS platforms with Next.js applications using the App Router.

---

## 1. CMS Comparison

### Feature Comparison Table

| CMS | Pricing | Query Language | Hosting Model | Next.js Integration | Visual Editing | TypeScript Support | Best For |
|-----|---------|---------------|---------------|---------------------|----------------|-------------------|----------|
| **Sanity** | Free tier + pay-as-you-go | GROQ (custom) | Hosted API, self-host Studio | Excellent (official SDK) | Yes (Presentation) | Excellent (TypeGen) | Complex content, real-time collab |
| **Contentful** | Free tier, then expensive | GraphQL & REST | Fully hosted | Excellent (official SDK) | Yes (Live Preview) | Good (codegen) | Enterprise, established workflows |
| **Payload CMS** | Open source (free) | Local API/REST/GraphQL | Self-hosted (same Next.js app) | Native (same app) | Yes (built-in) | Excellent (native TS) | Full control, Next.js monorepo |
| **Strapi** | Open source (free) | REST & GraphQL | Self-hosted or Strapi Cloud | Good (community) | Limited | Good | Customizable, SQL databases |
| **Storyblok** | Free tier available | REST & GraphQL | Fully hosted | Excellent (official SDK) | Excellent (Visual Editor) | Good | Marketing sites, visual editing |
| **Hygraph** | Free tier available | GraphQL only | Fully hosted | Good | Yes (Preview) | Good (codegen) | GraphQL-first, content federation |
| **DatoCMS** | Free tier available | GraphQL only | Fully hosted | Excellent (official SDK) | Yes (Real-time Preview) | Excellent (codegen) | Images, localization |
| **Keystatic** | Open source (free) | Local API | Git-based (files) | Native (same app) | Yes (Admin UI) | Excellent (native TS) | Markdown/MDX, developer content |
| **Tina CMS** | Free tier available | GraphQL | Git-based + hosted API | Excellent (official) | Excellent (Visual) | Good | Git-based, visual editing |

### Decision Flowchart

```
START: Choosing a Headless CMS
│
├─► Do you need visual/inline editing?
│   ├─► Yes, heavily → Storyblok or Tina CMS
│   └─► Nice to have → Continue
│
├─► Is budget a major constraint?
│   ├─► Yes, self-hosting OK → Payload CMS or Strapi
│   ├─► Yes, git-based OK → Keystatic or Tina CMS
│   └─► No → Continue
│
├─► Do you need enterprise features (SSO, audit logs)?
│   ├─► Yes → Contentful or Sanity
│   └─► No → Continue
│
├─► Do you prefer GraphQL exclusively?
│   ├─► Yes → Hygraph or DatoCMS
│   └─► No → Continue
│
├─► Do you want CMS in the same Next.js app?
│   ├─► Yes → Payload CMS or Keystatic
│   └─► No → Continue
│
├─► Do you need real-time collaboration?
│   ├─► Yes → Sanity
│   └─► No → Continue
│
├─► Primary use case?
│   ├─► Developer blog/docs → Keystatic or Tina
│   ├─► Marketing site → Storyblok or Contentful
│   ├─► Complex application → Sanity or Payload
│   └─► API-first/federation → Hygraph
│
└─► Default recommendation: Sanity (flexibility + DX)
```

---

## 2. Architecture Patterns

### Content-as-Data vs Content-as-Code

**Content-as-Data (API-based CMS)**
- Content stored in external database/service
- Fetched at build or runtime via API
- Non-developers can edit without deployments
- Examples: Sanity, Contentful, Strapi

```typescript
// Content-as-Data: Fetch from external CMS
async function getPost(slug: string) {
  const post = await sanityClient.fetch(
    `*[_type == "post" && slug.current == $slug][0]`,
    { slug }
  )
  return post
}
```

**Content-as-Code (Git-based CMS)**
- Content stored as files in repository (MDX, JSON, YAML)
- Changes require commits and deployments
- Version control built-in
- Examples: Keystatic, Tina CMS, Contentlayer

```typescript
// Content-as-Code: Import from local files
import { allPosts } from 'contentlayer/generated'

function getPost(slug: string) {
  return allPosts.find((post) => post.slug === slug)
}
```

### When to Use Each Pattern

| Pattern | Use When |
|---------|----------|
| API-based | Non-technical editors, frequent updates, real-time preview |
| Git-based | Developer-focused content, version control critical, simple needs |
| Hybrid | Marketing pages (API) + docs (Git), migration period |

### Structured Content Modeling

**Principle: Separate content from presentation**

```typescript
// Bad: Presentation mixed with content
{
  title: "My Post",
  headerColor: "#ff0000",
  titleFontSize: "24px"
}

// Good: Structured, presentation-agnostic
{
  title: "My Post",
  category: "tutorial",
  difficulty: "beginner",
  body: [/* portable text */]
}
```

**Content Type Hierarchy**

```
├── Documents (top-level, independently addressable)
│   ├── Page
│   ├── Post
│   └── Product
│
├── Objects (nested, reusable within documents)
│   ├── SEO
│   ├── Author Reference
│   └── Call to Action
│
└── Components (flexible content blocks)
    ├── Hero Section
    ├── Feature Grid
    └── Testimonial Carousel
```

---

## 3. Sanity Deep Dive

### Client Setup

```typescript
// lib/sanity/client.ts
import { createClient } from '@sanity/client'
import imageUrlBuilder from '@sanity/image-url'

export const sanityClient = createClient({
  projectId: process.env.NEXT_PUBLIC_SANITY_PROJECT_ID!,
  dataset: process.env.NEXT_PUBLIC_SANITY_DATASET!,
  apiVersion: '2024-01-01',
  useCdn: process.env.NODE_ENV === 'production',
  // For authenticated requests (mutations, drafts)
  token: process.env.SANITY_API_TOKEN,
})

// Preview client for draft content
export const previewClient = createClient({
  projectId: process.env.NEXT_PUBLIC_SANITY_PROJECT_ID!,
  dataset: process.env.NEXT_PUBLIC_SANITY_DATASET!,
  apiVersion: '2024-01-01',
  useCdn: false,
  token: process.env.SANITY_API_TOKEN,
  perspective: 'previewDrafts',
})

// Image URL builder
const builder = imageUrlBuilder(sanityClient)

export function urlFor(source: any) {
  return builder.image(source)
}
```

### GROQ Queries

```typescript
// lib/sanity/queries.ts

// Basic document fetch
export const postBySlugQuery = `
  *[_type == "post" && slug.current == $slug][0] {
    _id,
    title,
    slug,
    publishedAt,
    excerpt,
    body,
    "author": author->{
      name,
      image,
      bio
    },
    "categories": categories[]->{
      title,
      slug
    },
    mainImage {
      asset->{
        _id,
        url,
        metadata {
          dimensions,
          lqip
        }
      },
      alt
    }
  }
`

// List with pagination
export const postsQuery = `
  *[_type == "post"] | order(publishedAt desc) [$start...$end] {
    _id,
    title,
    slug,
    publishedAt,
    excerpt,
    "author": author->name,
    mainImage
  }
`

// Count for pagination
export const postCountQuery = `count(*[_type == "post"])`

// Related content
export const relatedPostsQuery = `
  *[_type == "post" && _id != $currentId && count(categories[@._ref in $categoryIds]) > 0] | order(publishedAt desc) [0...3] {
    _id,
    title,
    slug,
    mainImage
  }
`
```

### Type-Safe Queries with Sanity TypeGen

```bash
# Generate types from schema
npx sanity schema extract --path=./sanity/extract.json
npx sanity typegen generate
```

```typescript
// lib/sanity/queries.ts (with types)
import { defineQuery } from 'next-sanity'

export const postBySlugQuery = defineQuery(`
  *[_type == "post" && slug.current == $slug][0] {
    _id,
    title,
    slug,
    body
  }
`)

// Usage with automatic type inference
import { sanityFetch } from './fetch'
import { postBySlugQuery } from './queries'

const post = await sanityFetch({
  query: postBySlugQuery,
  params: { slug: 'my-post' }
})
// post is fully typed based on query
```

### Sanity Studio Embedded in Next.js

```typescript
// app/(sanity)/studio/[[...tool]]/page.tsx
import { NextStudio } from 'next-sanity/studio'
import config from '@/sanity.config'

export const dynamic = 'force-static'

export { metadata, viewport } from 'next-sanity/studio'

export default function StudioPage() {
  return <NextStudio config={config} />
}
```

```typescript
// sanity.config.ts
import { defineConfig } from 'sanity'
import { structureTool } from 'sanity/structure'
import { visionTool } from '@sanity/vision'
import { presentationTool } from 'sanity/presentation'
import { schemaTypes } from './sanity/schemas'

export default defineConfig({
  name: 'default',
  title: 'My CMS',
  projectId: process.env.NEXT_PUBLIC_SANITY_PROJECT_ID!,
  dataset: process.env.NEXT_PUBLIC_SANITY_DATASET!,
  basePath: '/studio',
  plugins: [
    structureTool(),
    visionTool(),
    presentationTool({
      previewUrl: {
        draftMode: {
          enable: '/api/draft',
        },
      },
    }),
  ],
  schema: {
    types: schemaTypes,
  },
})
```

### Portable Text Rendering

```typescript
// components/portable-text.tsx
import { PortableText, PortableTextComponents } from '@portabletext/react'
import Image from 'next/image'
import Link from 'next/link'
import { urlFor } from '@/lib/sanity/client'

const components: PortableTextComponents = {
  types: {
    image: ({ value }) => {
      if (!value?.asset?._ref) return null
      return (
        <figure className="my-8">
          <Image
            src={urlFor(value).width(800).url()}
            alt={value.alt || ''}
            width={800}
            height={400}
            className="rounded-lg"
          />
          {value.caption && (
            <figcaption className="text-center text-sm text-gray-500 mt-2">
              {value.caption}
            </figcaption>
          )}
        </figure>
      )
    },
    code: ({ value }) => (
      <pre className="bg-gray-900 text-gray-100 p-4 rounded-lg overflow-x-auto">
        <code className={`language-${value.language}`}>
          {value.code}
        </code>
      </pre>
    ),
    callout: ({ value }) => (
      <aside className={`p-4 rounded-lg border-l-4 ${
        value.type === 'warning' ? 'bg-yellow-50 border-yellow-500' :
        value.type === 'error' ? 'bg-red-50 border-red-500' :
        'bg-blue-50 border-blue-500'
      }`}>
        {value.text}
      </aside>
    ),
  },
  marks: {
    link: ({ children, value }) => {
      const href = value?.href || ''
      const isInternal = href.startsWith('/')

      if (isInternal) {
        return <Link href={href} className="text-blue-600 hover:underline">{children}</Link>
      }

      return (
        <a
          href={href}
          target="_blank"
          rel="noopener noreferrer"
          className="text-blue-600 hover:underline"
        >
          {children}
        </a>
      )
    },
    internalLink: ({ children, value }) => (
      <Link href={`/${value?.slug?.current}`} className="text-blue-600 hover:underline">
        {children}
      </Link>
    ),
    highlight: ({ children }) => (
      <mark className="bg-yellow-200 px-1">{children}</mark>
    ),
  },
  block: {
    h2: ({ children }) => (
      <h2 className="text-2xl font-bold mt-8 mb-4">{children}</h2>
    ),
    h3: ({ children }) => (
      <h3 className="text-xl font-semibold mt-6 mb-3">{children}</h3>
    ),
    blockquote: ({ children }) => (
      <blockquote className="border-l-4 border-gray-300 pl-4 italic my-4">
        {children}
      </blockquote>
    ),
  },
  list: {
    bullet: ({ children }) => (
      <ul className="list-disc pl-6 my-4 space-y-2">{children}</ul>
    ),
    number: ({ children }) => (
      <ol className="list-decimal pl-6 my-4 space-y-2">{children}</ol>
    ),
  },
}

interface PortableTextContentProps {
  value: any
}

export function PortableTextContent({ value }: PortableTextContentProps) {
  return <PortableText value={value} components={components} />
}
```

### Visual Editing Setup

```typescript
// app/api/draft/route.ts
import { draftMode } from 'next/headers'
import { redirect } from 'next/navigation'
import { validatePreviewUrl } from '@sanity/preview-url-secret'
import { sanityClient } from '@/lib/sanity/client'

export async function GET(request: Request) {
  const { isValid, redirectTo = '/' } = await validatePreviewUrl(
    sanityClient.withConfig({ token: process.env.SANITY_API_TOKEN }),
    request.url
  )

  if (!isValid) {
    return new Response('Invalid secret', { status: 401 })
  }

  ;(await draftMode()).enable()
  redirect(redirectTo)
}
```

```typescript
// app/api/disable-draft/route.ts
import { draftMode } from 'next/headers'
import { redirect } from 'next/navigation'

export async function GET(request: Request) {
  const { searchParams } = new URL(request.url)
  ;(await draftMode()).disable()
  redirect(searchParams.get('redirect') || '/')
}
```

```typescript
// components/visual-editing.tsx
'use client'

import { enableVisualEditing } from '@sanity/visual-editing'
import { useEffect } from 'react'

export function VisualEditing() {
  useEffect(() => {
    enableVisualEditing()
  }, [])

  return null
}

// In layout.tsx
import { draftMode } from 'next/headers'
import { VisualEditing } from '@/components/visual-editing'

export default async function RootLayout({ children }) {
  const { isEnabled } = await draftMode()

  return (
    <html>
      <body>
        {children}
        {isEnabled && <VisualEditing />}
      </body>
    </html>
  )
}
```

### Real-Time Preview with Sanity Live

```typescript
// lib/sanity/fetch.ts
import { sanityClient, previewClient } from './client'
import { draftMode } from 'next/headers'

interface SanityFetchOptions<T> {
  query: string
  params?: Record<string, any>
  tags?: string[]
}

export async function sanityFetch<T>({
  query,
  params = {},
  tags = [],
}: SanityFetchOptions<T>): Promise<T> {
  const { isEnabled: isDraftMode } = await draftMode()

  const client = isDraftMode ? previewClient : sanityClient

  return client.fetch<T>(query, params, {
    next: {
      revalidate: isDraftMode ? 0 : 3600,
      tags,
    },
  })
}
```

```typescript
// For real-time updates in preview
// components/live-query.tsx
'use client'

import { useLiveQuery } from 'next-sanity/preview'

interface LiveQueryProps<T> {
  query: string
  params?: Record<string, any>
  initialData: T
  children: (data: T) => React.ReactNode
}

export function LiveQuery<T>({
  query,
  params,
  initialData,
  children,
}: LiveQueryProps<T>) {
  const [data] = useLiveQuery(initialData, query, params)
  return <>{children(data)}</>
}
```

---

## 4. Contentful Deep Dive

### Client Setup

```typescript
// lib/contentful/client.ts
import { createClient } from 'contentful'

// Content Delivery API (published content)
export const contentfulClient = createClient({
  space: process.env.CONTENTFUL_SPACE_ID!,
  accessToken: process.env.CONTENTFUL_ACCESS_TOKEN!,
})

// Preview API (draft content)
export const contentfulPreviewClient = createClient({
  space: process.env.CONTENTFUL_SPACE_ID!,
  accessToken: process.env.CONTENTFUL_PREVIEW_ACCESS_TOKEN!,
  host: 'preview.contentful.com',
})

// Get appropriate client based on draft mode
export function getClient(isDraftMode: boolean) {
  return isDraftMode ? contentfulPreviewClient : contentfulClient
}
```

### GraphQL vs REST

**REST API (default)**

```typescript
// lib/contentful/api.ts
import { getClient } from './client'
import type { Entry, EntryCollection } from 'contentful'

export async function getPost(slug: string, isDraftMode = false) {
  const client = getClient(isDraftMode)

  const entries = await client.getEntries({
    content_type: 'blogPost',
    'fields.slug': slug,
    include: 2, // Resolve up to 2 levels of linked entries
  })

  return entries.items[0] || null
}

export async function getPosts(limit = 10, skip = 0, isDraftMode = false) {
  const client = getClient(isDraftMode)

  const entries = await client.getEntries({
    content_type: 'blogPost',
    order: ['-fields.publishDate'],
    limit,
    skip,
    include: 1,
  })

  return {
    posts: entries.items,
    total: entries.total,
  }
}
```

**GraphQL API**

```typescript
// lib/contentful/graphql.ts
const CONTENTFUL_GRAPHQL_ENDPOINT = `https://graphql.contentful.com/content/v1/spaces/${process.env.CONTENTFUL_SPACE_ID}`

interface GraphQLOptions {
  query: string
  variables?: Record<string, any>
  preview?: boolean
  tags?: string[]
}

export async function contentfulGraphQL<T>({
  query,
  variables = {},
  preview = false,
  tags = [],
}: GraphQLOptions): Promise<T> {
  const response = await fetch(CONTENTFUL_GRAPHQL_ENDPOINT, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${
        preview
          ? process.env.CONTENTFUL_PREVIEW_ACCESS_TOKEN
          : process.env.CONTENTFUL_ACCESS_TOKEN
      }`,
    },
    body: JSON.stringify({ query, variables }),
    next: {
      revalidate: preview ? 0 : 3600,
      tags,
    },
  })

  const json = await response.json()

  if (json.errors) {
    console.error('Contentful GraphQL Error:', json.errors)
    throw new Error('Failed to fetch from Contentful')
  }

  return json.data
}

// Example query
const POST_QUERY = `
  query GetPost($slug: String!, $preview: Boolean!) {
    blogPostCollection(where: { slug: $slug }, preview: $preview, limit: 1) {
      items {
        sys {
          id
          publishedAt
        }
        title
        slug
        excerpt
        content {
          json
          links {
            assets {
              block {
                sys { id }
                url
                title
                width
                height
              }
            }
          }
        }
        author {
          name
          avatar {
            url
          }
        }
      }
    }
  }
`

export async function getPost(slug: string, preview = false) {
  const data = await contentfulGraphQL<{
    blogPostCollection: { items: any[] }
  }>({
    query: POST_QUERY,
    variables: { slug, preview },
    preview,
    tags: ['posts'],
  })

  return data.blogPostCollection.items[0] || null
}
```

### Rich Text Rendering

```typescript
// components/contentful-rich-text.tsx
import {
  documentToReactComponents,
  Options,
} from '@contentful/rich-text-react-renderer'
import { BLOCKS, INLINES, MARKS, Document } from '@contentful/rich-text-types'
import Image from 'next/image'
import Link from 'next/link'

interface RichTextProps {
  content: Document
  links?: {
    assets?: { block?: any[] }
    entries?: { block?: any[]; inline?: any[] }
  }
}

export function ContentfulRichText({ content, links }: RichTextProps) {
  // Create asset map for embedded assets
  const assetMap = new Map()
  links?.assets?.block?.forEach((asset) => {
    assetMap.set(asset.sys.id, asset)
  })

  // Create entry map for embedded entries
  const entryMap = new Map()
  links?.entries?.block?.forEach((entry) => {
    entryMap.set(entry.sys.id, entry)
  })
  links?.entries?.inline?.forEach((entry) => {
    entryMap.set(entry.sys.id, entry)
  })

  const options: Options = {
    renderMark: {
      [MARKS.BOLD]: (text) => <strong className="font-bold">{text}</strong>,
      [MARKS.ITALIC]: (text) => <em className="italic">{text}</em>,
      [MARKS.CODE]: (text) => (
        <code className="bg-gray-100 px-1 py-0.5 rounded font-mono text-sm">
          {text}
        </code>
      ),
    },
    renderNode: {
      [BLOCKS.PARAGRAPH]: (node, children) => (
        <p className="my-4 leading-relaxed">{children}</p>
      ),
      [BLOCKS.HEADING_2]: (node, children) => (
        <h2 className="text-2xl font-bold mt-8 mb-4">{children}</h2>
      ),
      [BLOCKS.HEADING_3]: (node, children) => (
        <h3 className="text-xl font-semibold mt-6 mb-3">{children}</h3>
      ),
      [BLOCKS.UL_LIST]: (node, children) => (
        <ul className="list-disc pl-6 my-4 space-y-2">{children}</ul>
      ),
      [BLOCKS.OL_LIST]: (node, children) => (
        <ol className="list-decimal pl-6 my-4 space-y-2">{children}</ol>
      ),
      [BLOCKS.QUOTE]: (node, children) => (
        <blockquote className="border-l-4 border-gray-300 pl-4 italic my-4">
          {children}
        </blockquote>
      ),
      [BLOCKS.EMBEDDED_ASSET]: (node) => {
        const asset = assetMap.get(node.data.target.sys.id)
        if (!asset) return null

        return (
          <figure className="my-8">
            <Image
              src={`https:${asset.url}`}
              alt={asset.title || ''}
              width={asset.width || 800}
              height={asset.height || 400}
              className="rounded-lg"
            />
            {asset.description && (
              <figcaption className="text-center text-sm text-gray-500 mt-2">
                {asset.description}
              </figcaption>
            )}
          </figure>
        )
      },
      [BLOCKS.EMBEDDED_ENTRY]: (node) => {
        const entry = entryMap.get(node.data.target.sys.id)
        if (!entry) return null

        // Handle different entry types
        switch (entry.__typename) {
          case 'CodeBlock':
            return (
              <pre className="bg-gray-900 text-gray-100 p-4 rounded-lg overflow-x-auto my-4">
                <code>{entry.code}</code>
              </pre>
            )
          case 'CallToAction':
            return (
              <div className="bg-blue-50 p-6 rounded-lg my-6 text-center">
                <h4 className="font-bold text-lg">{entry.title}</h4>
                <p className="my-2">{entry.description}</p>
                <Link
                  href={entry.link}
                  className="inline-block bg-blue-600 text-white px-4 py-2 rounded"
                >
                  {entry.buttonText}
                </Link>
              </div>
            )
          default:
            return null
        }
      },
      [INLINES.HYPERLINK]: (node, children) => (
        <a
          href={node.data.uri}
          target="_blank"
          rel="noopener noreferrer"
          className="text-blue-600 hover:underline"
        >
          {children}
        </a>
      ),
      [INLINES.ENTRY_HYPERLINK]: (node, children) => {
        const entry = entryMap.get(node.data.target.sys.id)
        if (!entry) return <>{children}</>

        return (
          <Link href={`/${entry.slug}`} className="text-blue-600 hover:underline">
            {children}
          </Link>
        )
      },
    },
  }

  return <>{documentToReactComponents(content, options)}</>
}
```

### Image API

```typescript
// lib/contentful/image.ts

interface ImageOptions {
  width?: number
  height?: number
  quality?: number
  format?: 'jpg' | 'png' | 'webp' | 'avif'
  fit?: 'pad' | 'fill' | 'scale' | 'crop' | 'thumb'
  focus?: 'center' | 'top' | 'bottom' | 'left' | 'right' | 'face' | 'faces'
}

export function contentfulImageUrl(
  url: string,
  options: ImageOptions = {}
): string {
  const params = new URLSearchParams()

  if (options.width) params.set('w', options.width.toString())
  if (options.height) params.set('h', options.height.toString())
  if (options.quality) params.set('q', options.quality.toString())
  if (options.format) params.set('fm', options.format)
  if (options.fit) params.set('fit', options.fit)
  if (options.focus) params.set('f', options.focus)

  const queryString = params.toString()
  return queryString ? `${url}?${queryString}` : url
}

// Usage
const imageUrl = contentfulImageUrl(asset.url, {
  width: 800,
  format: 'webp',
  quality: 80,
})
```

### Live Preview

```typescript
// lib/contentful/preview.ts
'use client'

import { ContentfulLivePreviewProvider } from '@contentful/live-preview/react'

export function ContentfulPreviewProvider({
  children,
  isEnabled,
}: {
  children: React.ReactNode
  isEnabled: boolean
}) {
  return (
    <ContentfulLivePreviewProvider
      locale="en-US"
      enableInspectorMode={isEnabled}
      enableLiveUpdates={isEnabled}
    >
      {children}
    </ContentfulLivePreviewProvider>
  )
}
```

```typescript
// components/preview-post.tsx
'use client'

import { useContentfulLiveUpdates } from '@contentful/live-preview/react'

interface PreviewPostProps {
  initialPost: any
}

export function PreviewPost({ initialPost }: PreviewPostProps) {
  // This will automatically update when content changes in Contentful
  const post = useContentfulLiveUpdates(initialPost)

  return (
    <article>
      <h1>{post.fields.title}</h1>
      {/* Render content */}
    </article>
  )
}
```

---

## 5. Payload CMS Deep Dive

Payload CMS runs in the same Next.js application, providing a local API for zero-latency data access.

### Project Setup

```bash
npx create-payload-app@latest my-project
# Select: Next.js (App Router)
# Select: MongoDB or Postgres
```

### Collection Configuration

```typescript
// collections/Posts.ts
import type { CollectionConfig } from 'payload'

export const Posts: CollectionConfig = {
  slug: 'posts',
  admin: {
    useAsTitle: 'title',
    defaultColumns: ['title', 'status', 'publishedAt'],
  },
  access: {
    read: () => true, // Public read
    create: ({ req: { user } }) => !!user,
    update: ({ req: { user } }) => !!user,
    delete: ({ req: { user } }) => !!user,
  },
  hooks: {
    beforeChange: [
      ({ data, operation }) => {
        if (operation === 'create' && !data.slug) {
          data.slug = data.title
            .toLowerCase()
            .replace(/[^a-z0-9]+/g, '-')
            .replace(/(^-|-$)/g, '')
        }
        return data
      },
    ],
    afterChange: [
      async ({ doc, operation }) => {
        // Revalidate on change
        if (operation === 'update' || operation === 'create') {
          await fetch(`${process.env.NEXT_PUBLIC_SITE_URL}/api/revalidate`, {
            method: 'POST',
            body: JSON.stringify({ tag: 'posts' }),
          })
        }
      },
    ],
  },
  fields: [
    {
      name: 'title',
      type: 'text',
      required: true,
    },
    {
      name: 'slug',
      type: 'text',
      unique: true,
      admin: {
        position: 'sidebar',
      },
    },
    {
      name: 'status',
      type: 'select',
      options: [
        { label: 'Draft', value: 'draft' },
        { label: 'Published', value: 'published' },
      ],
      defaultValue: 'draft',
      admin: {
        position: 'sidebar',
      },
    },
    {
      name: 'publishedAt',
      type: 'date',
      admin: {
        position: 'sidebar',
        date: {
          pickerAppearance: 'dayAndTime',
        },
      },
    },
    {
      name: 'author',
      type: 'relationship',
      relationTo: 'users',
      required: true,
    },
    {
      name: 'categories',
      type: 'relationship',
      relationTo: 'categories',
      hasMany: true,
    },
    {
      name: 'featuredImage',
      type: 'upload',
      relationTo: 'media',
    },
    {
      name: 'excerpt',
      type: 'textarea',
    },
    {
      name: 'content',
      type: 'richText',
    },
    {
      name: 'seo',
      type: 'group',
      fields: [
        { name: 'title', type: 'text' },
        { name: 'description', type: 'textarea' },
        { name: 'image', type: 'upload', relationTo: 'media' },
      ],
    },
  ],
}
```

### Globals Configuration

```typescript
// globals/SiteSettings.ts
import type { GlobalConfig } from 'payload'

export const SiteSettings: GlobalConfig = {
  slug: 'site-settings',
  access: {
    read: () => true,
  },
  fields: [
    {
      name: 'siteName',
      type: 'text',
      required: true,
    },
    {
      name: 'siteDescription',
      type: 'textarea',
    },
    {
      name: 'logo',
      type: 'upload',
      relationTo: 'media',
    },
    {
      name: 'socialLinks',
      type: 'array',
      fields: [
        {
          name: 'platform',
          type: 'select',
          options: ['twitter', 'linkedin', 'github', 'instagram'],
        },
        { name: 'url', type: 'text' },
      ],
    },
    {
      name: 'navigation',
      type: 'array',
      fields: [
        { name: 'label', type: 'text', required: true },
        { name: 'link', type: 'text', required: true },
      ],
    },
  ],
}
```

### Local API Usage

```typescript
// lib/payload.ts
import { getPayloadHMR } from '@payloadcms/next/utilities'
import configPromise from '@payload-config'

export async function getPayload() {
  return getPayloadHMR({ config: configPromise })
}
```

```typescript
// app/blog/[slug]/page.tsx
import { getPayload } from '@/lib/payload'
import { notFound } from 'next/navigation'
import { draftMode } from 'next/headers'

interface PageProps {
  params: Promise<{ slug: string }>
}

export default async function BlogPost({ params }: PageProps) {
  const { slug } = await params
  const { isEnabled: isDraft } = await draftMode()
  const payload = await getPayload()

  const { docs } = await payload.find({
    collection: 'posts',
    where: {
      slug: { equals: slug },
      ...(isDraft ? {} : { status: { equals: 'published' } }),
    },
    depth: 2, // Resolve relationships 2 levels deep
    draft: isDraft,
  })

  const post = docs[0]

  if (!post) {
    notFound()
  }

  return (
    <article>
      <h1>{post.title}</h1>
      {/* Render post content */}
    </article>
  )
}

export async function generateStaticParams() {
  const payload = await getPayload()

  const { docs } = await payload.find({
    collection: 'posts',
    where: { status: { equals: 'published' } },
    limit: 1000,
  })

  return docs.map((post) => ({
    slug: post.slug,
  }))
}

export async function generateMetadata({ params }: PageProps) {
  const { slug } = await params
  const payload = await getPayload()

  const { docs } = await payload.find({
    collection: 'posts',
    where: { slug: { equals: slug } },
  })

  const post = docs[0]

  return {
    title: post?.seo?.title || post?.title,
    description: post?.seo?.description || post?.excerpt,
  }
}
```

### Access Control Patterns

```typescript
// access/isAdmin.ts
import type { Access } from 'payload'

export const isAdmin: Access = ({ req: { user } }) => {
  return user?.role === 'admin'
}

export const isAdminOrSelf: Access = ({ req: { user } }) => {
  if (!user) return false
  if (user.role === 'admin') return true

  return {
    id: { equals: user.id },
  }
}

export const isPublishedOrAdmin: Access = ({ req: { user } }) => {
  if (user?.role === 'admin') return true

  return {
    status: { equals: 'published' },
  }
}
```

### Deployment on Vercel

```typescript
// payload.config.ts
import { buildConfig } from 'payload'
import { mongooseAdapter } from '@payloadcms/db-mongodb'
// OR for Postgres:
// import { postgresAdapter } from '@payloadcms/db-postgres'
import { vercelBlobStorage } from '@payloadcms/storage-vercel-blob'

export default buildConfig({
  collections: [Posts, Media, Users, Categories],
  globals: [SiteSettings],
  db: mongooseAdapter({
    url: process.env.MONGODB_URI!,
  }),
  // OR for Postgres:
  // db: postgresAdapter({
  //   pool: { connectionString: process.env.POSTGRES_URL },
  // }),
  plugins: [
    vercelBlobStorage({
      collections: {
        media: true,
      },
      token: process.env.BLOB_READ_WRITE_TOKEN!,
    }),
  ],
  secret: process.env.PAYLOAD_SECRET!,
  typescript: {
    outputFile: 'payload-types.ts',
  },
})
```

---

## 6. Draft Mode

### Basic Setup

```typescript
// app/api/draft/route.ts
import { draftMode } from 'next/headers'
import { redirect } from 'next/navigation'

export async function GET(request: Request) {
  const { searchParams } = new URL(request.url)
  const secret = searchParams.get('secret')
  const slug = searchParams.get('slug')
  const type = searchParams.get('type') || 'page'

  // Validate secret token
  if (secret !== process.env.DRAFT_MODE_SECRET) {
    return new Response('Invalid token', { status: 401 })
  }

  // Enable draft mode
  const draft = await draftMode()
  draft.enable()

  // Redirect to the path being previewed
  const path = type === 'post' ? `/blog/${slug}` : `/${slug || ''}`
  redirect(path)
}
```

```typescript
// app/api/draft/disable/route.ts
import { draftMode } from 'next/headers'
import { redirect } from 'next/navigation'

export async function GET(request: Request) {
  const { searchParams } = new URL(request.url)
  const draft = await draftMode()
  draft.disable()
  redirect(searchParams.get('redirect') || '/')
}
```

### Conditional Data Fetching

```typescript
// lib/data.ts
import { draftMode } from 'next/headers'

export async function getPageData(slug: string) {
  const { isEnabled: isDraft } = await draftMode()

  // Sanity
  const client = isDraft ? previewClient : sanityClient
  const query = isDraft
    ? `*[_type == "page" && slug.current == $slug][0]`
    : `*[_type == "page" && slug.current == $slug && !(_id in path("drafts.**"))][0]`

  return client.fetch(query, { slug }, {
    next: { revalidate: isDraft ? 0 : 3600 },
  })
}
```

### Draft Mode Indicator

```typescript
// components/draft-mode-banner.tsx
import { draftMode } from 'next/headers'
import Link from 'next/link'

export async function DraftModeBanner() {
  const { isEnabled } = await draftMode()

  if (!isEnabled) return null

  return (
    <div className="fixed bottom-4 right-4 bg-yellow-500 text-black px-4 py-2 rounded-lg shadow-lg z-50 flex items-center gap-4">
      <span className="font-medium">Draft Mode Enabled</span>
      <Link
        href="/api/draft/disable"
        className="bg-black text-white px-3 py-1 rounded text-sm hover:bg-gray-800"
      >
        Exit Preview
      </Link>
    </div>
  )
}
```

### Per-CMS Implementation

**Sanity**

```typescript
// Sanity uses validatePreviewUrl for secure preview
import { validatePreviewUrl } from '@sanity/preview-url-secret'

export async function GET(request: Request) {
  const { isValid, redirectTo = '/' } = await validatePreviewUrl(
    sanityClient.withConfig({ token: process.env.SANITY_API_TOKEN }),
    request.url
  )

  if (!isValid) {
    return new Response('Invalid secret', { status: 401 })
  }

  ;(await draftMode()).enable()
  redirect(redirectTo)
}
```

**Contentful**

```typescript
// Contentful uses a simple secret comparison
export async function GET(request: Request) {
  const { searchParams } = new URL(request.url)
  const secret = searchParams.get('secret')
  const slug = searchParams.get('slug')

  if (secret !== process.env.CONTENTFUL_PREVIEW_SECRET) {
    return new Response('Invalid token', { status: 401 })
  }

  // Verify the content exists in Contentful
  const entries = await contentfulPreviewClient.getEntries({
    content_type: 'page',
    'fields.slug': slug,
    limit: 1,
  })

  if (!entries.items.length) {
    return new Response('Content not found', { status: 404 })
  }

  ;(await draftMode()).enable()
  redirect(`/${slug}`)
}
```

**Payload CMS**

```typescript
// Payload has built-in preview handling
// Configure in collection
{
  slug: 'pages',
  admin: {
    livePreview: {
      url: ({ data }) => `${process.env.NEXT_PUBLIC_SITE_URL}/${data.slug}`,
    },
  },
  versions: {
    drafts: {
      autosave: true,
    },
  },
}
```

---

## 7. ISR & Webhook Revalidation

### Time-Based Revalidation

```typescript
// In any Server Component or data fetching function
async function getData() {
  const response = await fetch('https://api.example.com/data', {
    next: {
      revalidate: 3600, // Revalidate every hour
    },
  })
  return response.json()
}
```

### Tag-Based Caching

```typescript
// lib/sanity/fetch.ts
export async function sanityFetch<T>({
  query,
  params = {},
  tags = [],
}: {
  query: string
  params?: Record<string, any>
  tags?: string[]
}): Promise<T> {
  return sanityClient.fetch<T>(query, params, {
    next: {
      revalidate: 3600,
      tags: ['sanity', ...tags], // e.g., ['sanity', 'posts', 'post-my-slug']
    },
  })
}

// Usage
const post = await sanityFetch({
  query: postQuery,
  params: { slug },
  tags: ['posts', `post-${slug}`],
})
```

### On-Demand Revalidation Webhook

```typescript
// app/api/revalidate/route.ts
import { revalidatePath, revalidateTag } from 'next/cache'
import { NextRequest, NextResponse } from 'next/server'
import crypto from 'crypto'

// Verify webhook signature (Sanity example)
function verifySignature(body: string, signature: string): boolean {
  const expectedSignature = crypto
    .createHmac('sha256', process.env.SANITY_WEBHOOK_SECRET!)
    .update(body)
    .digest('hex')

  return crypto.timingSafeEqual(
    Buffer.from(signature),
    Buffer.from(expectedSignature)
  )
}

export async function POST(request: NextRequest) {
  try {
    const body = await request.text()
    const signature = request.headers.get('sanity-webhook-signature')

    // Verify webhook authenticity
    if (!signature || !verifySignature(body, signature)) {
      return NextResponse.json(
        { error: 'Invalid signature' },
        { status: 401 }
      )
    }

    const payload = JSON.parse(body)
    const { _type, slug, _id } = payload

    // Revalidate based on content type
    switch (_type) {
      case 'post':
        revalidateTag('posts')
        if (slug?.current) {
          revalidateTag(`post-${slug.current}`)
          revalidatePath(`/blog/${slug.current}`)
        }
        revalidatePath('/blog')
        break

      case 'page':
        revalidateTag('pages')
        if (slug?.current) {
          revalidatePath(`/${slug.current}`)
        }
        break

      case 'siteSettings':
        revalidateTag('settings')
        revalidatePath('/', 'layout') // Revalidate entire site
        break

      default:
        // Generic revalidation
        revalidateTag(_type)
    }

    return NextResponse.json({
      revalidated: true,
      type: _type,
      slug: slug?.current,
    })
  } catch (error) {
    console.error('Revalidation error:', error)
    return NextResponse.json(
      { error: 'Revalidation failed' },
      { status: 500 }
    )
  }
}
```

### Contentful Webhook Handler

```typescript
// app/api/revalidate/contentful/route.ts
import { revalidatePath, revalidateTag } from 'next/cache'
import { NextRequest, NextResponse } from 'next/server'

export async function POST(request: NextRequest) {
  const secret = request.headers.get('x-contentful-webhook-secret')

  if (secret !== process.env.CONTENTFUL_WEBHOOK_SECRET) {
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })
  }

  const payload = await request.json()
  const contentType = payload.sys.contentType?.sys.id
  const slug = payload.fields?.slug?.['en-US']

  // Contentful sends different payloads for different events
  switch (contentType) {
    case 'blogPost':
      revalidateTag('posts')
      if (slug) {
        revalidatePath(`/blog/${slug}`)
      }
      break
    case 'page':
      revalidateTag('pages')
      if (slug) {
        revalidatePath(`/${slug}`)
      }
      break
  }

  return NextResponse.json({ revalidated: true })
}
```

### Caching Strategy Reference

| Content Type | Cache Strategy | Tags | Revalidate |
|-------------|----------------|------|------------|
| Blog posts | Tag + Time | `['posts', 'post-{slug}']` | 1 hour |
| Pages | Tag + Time | `['pages', 'page-{slug}']` | 1 hour |
| Navigation | Tag only | `['navigation']` | On change |
| Site settings | Tag only | `['settings']` | On change |
| User-specific | No cache | - | 0 |

---

## 8. TypeScript Integration

### Sanity TypeGen

```bash
# Install dependencies
pnpm add -D @sanity/codegen

# Extract schema
npx sanity schema extract --path=./sanity/extract.json

# Generate types
npx sanity typegen generate
```

```typescript
// sanity.types.ts (generated)
export type Post = {
  _id: string
  _type: 'post'
  title: string
  slug: { current: string }
  body: PortableTextBlock[]
  author: Reference
  // ...
}
```

```typescript
// Usage with defineQuery
import { defineQuery } from 'next-sanity'
import type { Post } from './sanity.types'

export const postQuery = defineQuery(`
  *[_type == "post" && slug.current == $slug][0]
`)

// Type is inferred from query
const post = await sanityFetch({ query: postQuery, params: { slug } })
```

### Contentful TypeScript SDK

```bash
# Generate types from Contentful space
npx contentful-typescript-codegen --output src/types/contentful.d.ts
```

```typescript
// contentful.d.ts (generated)
export interface IBlogPostFields {
  title: string
  slug: string
  content: Document
  author: Entry<IAuthorFields>
  publishDate: string
}

export interface IBlogPost extends Entry<IBlogPostFields> {}
```

### GraphQL Codegen

```bash
pnpm add -D @graphql-codegen/cli @graphql-codegen/typescript @graphql-codegen/typescript-operations
```

```yaml
# codegen.yml
schema:
  - https://graphql.contentful.com/content/v1/spaces/${CONTENTFUL_SPACE_ID}:
      headers:
        Authorization: Bearer ${CONTENTFUL_ACCESS_TOKEN}

documents: 'src/**/*.graphql'

generates:
  src/types/graphql.ts:
    plugins:
      - typescript
      - typescript-operations
```

```graphql
# queries/posts.graphql
query GetPost($slug: String!) {
  blogPostCollection(where: { slug: $slug }, limit: 1) {
    items {
      title
      slug
      content {
        json
      }
    }
  }
}
```

```typescript
// Generated types
export type GetPostQuery = {
  blogPostCollection: {
    items: Array<{
      title: string
      slug: string
      content: { json: Document }
    }>
  }
}

export type GetPostQueryVariables = {
  slug: string
}
```

### Type-Safe Query Wrapper

```typescript
// lib/sanity/typed-fetch.ts
import { sanityClient } from './client'
import type { QueryParams } from 'next-sanity'

type QueryResult<T extends string> = T extends `*[_type == "post"${string}]`
  ? Post
  : T extends `*[_type == "page"${string}]`
  ? Page
  : unknown

export async function typedFetch<Q extends string>(
  query: Q,
  params?: QueryParams
): Promise<QueryResult<Q>> {
  return sanityClient.fetch(query, params)
}
```

---

## 9. Content Modeling Best Practices

### Portable/Rich Text Structure

```typescript
// Sanity schema for flexible rich text
export const richText = {
  name: 'content',
  type: 'array',
  of: [
    {
      type: 'block',
      styles: [
        { title: 'Normal', value: 'normal' },
        { title: 'H2', value: 'h2' },
        { title: 'H3', value: 'h3' },
        { title: 'Quote', value: 'blockquote' },
      ],
      marks: {
        decorators: [
          { title: 'Bold', value: 'strong' },
          { title: 'Italic', value: 'em' },
          { title: 'Code', value: 'code' },
          { title: 'Highlight', value: 'highlight' },
        ],
        annotations: [
          {
            name: 'link',
            type: 'object',
            title: 'External Link',
            fields: [
              { name: 'href', type: 'url', title: 'URL' },
              { name: 'blank', type: 'boolean', title: 'Open in new tab' },
            ],
          },
          {
            name: 'internalLink',
            type: 'object',
            title: 'Internal Link',
            fields: [
              {
                name: 'reference',
                type: 'reference',
                to: [{ type: 'page' }, { type: 'post' }],
              },
            ],
          },
        ],
      },
    },
    // Embedded content types
    { type: 'image' },
    { type: 'codeBlock' },
    { type: 'callout' },
    { type: 'videoEmbed' },
    { type: 'table' },
  ],
}
```

### Image Assets Pattern

```typescript
// Sanity image schema with metadata
export const imageWithMetadata = {
  name: 'mainImage',
  type: 'image',
  options: {
    hotspot: true, // Enable hotspot for smart cropping
  },
  fields: [
    {
      name: 'alt',
      type: 'string',
      title: 'Alternative Text',
      description: 'Important for SEO and accessibility',
      validation: (Rule: any) => Rule.required(),
    },
    {
      name: 'caption',
      type: 'string',
      title: 'Caption',
    },
  ],
}

// Responsive image component
function ResponsiveImage({ image }: { image: any }) {
  const src = urlFor(image).width(1200).url()
  const srcSet = [400, 800, 1200]
    .map((w) => `${urlFor(image).width(w).url()} ${w}w`)
    .join(', ')

  return (
    <Image
      src={src}
      srcSet={srcSet}
      sizes="(max-width: 768px) 100vw, (max-width: 1200px) 50vw, 800px"
      alt={image.alt || ''}
      width={1200}
      height={800}
      placeholder="blur"
      blurDataURL={image.asset.metadata.lqip}
    />
  )
}
```

### References and Relations

```typescript
// Author reference with population
export const authorReference = {
  name: 'author',
  type: 'reference',
  to: [{ type: 'author' }],
  validation: (Rule: any) => Rule.required(),
}

// Query with reference expansion
const postWithAuthor = `
  *[_type == "post" && slug.current == $slug][0] {
    title,
    "author": author->{
      name,
      bio,
      "avatar": image.asset->url
    }
  }
`

// Many-to-many relationship
export const categoriesReference = {
  name: 'categories',
  type: 'array',
  of: [
    {
      type: 'reference',
      to: [{ type: 'category' }],
    },
  ],
}
```

### Localized Content

```typescript
// Sanity localization with document-level translation
export const localizedPost = {
  name: 'post',
  type: 'document',
  fields: [
    {
      name: 'language',
      type: 'string',
      options: {
        list: [
          { title: 'English', value: 'en' },
          { title: 'Spanish', value: 'es' },
          { title: 'French', value: 'fr' },
        ],
      },
    },
    {
      name: 'translationOf',
      type: 'reference',
      to: [{ type: 'post' }],
      description: 'Link to the original post this is a translation of',
    },
    // ... other fields
  ],
}

// Query localized content
const localizedPostQuery = `
  *[_type == "post" && slug.current == $slug && language == $lang][0] {
    ...,
    "translations": *[_type == "post" && translationOf._ref == ^._id] {
      language,
      slug
    }
  }
`
```

### Reusable Components (Page Builder)

```typescript
// Sanity page builder schema
export const page = {
  name: 'page',
  type: 'document',
  fields: [
    { name: 'title', type: 'string' },
    { name: 'slug', type: 'slug' },
    {
      name: 'sections',
      type: 'array',
      of: [
        { type: 'hero' },
        { type: 'featureGrid' },
        { type: 'testimonials' },
        { type: 'callToAction' },
        { type: 'faq' },
        { type: 'richTextSection' },
      ],
    },
  ],
}

// Component types
export const hero = {
  name: 'hero',
  type: 'object',
  fields: [
    { name: 'headline', type: 'string' },
    { name: 'subheadline', type: 'text' },
    { name: 'backgroundImage', type: 'image' },
    { name: 'cta', type: 'cta' },
  ],
  preview: {
    select: { title: 'headline' },
    prepare: ({ title }) => ({ title, subtitle: 'Hero Section' }),
  },
}

// Render page sections
function PageSections({ sections }: { sections: any[] }) {
  return (
    <>
      {sections.map((section, index) => {
        switch (section._type) {
          case 'hero':
            return <Hero key={index} {...section} />
          case 'featureGrid':
            return <FeatureGrid key={index} {...section} />
          case 'testimonials':
            return <Testimonials key={index} {...section} />
          case 'callToAction':
            return <CallToAction key={index} {...section} />
          default:
            return null
        }
      })}
    </>
  )
}
```

---

## 10. Performance & Caching

### Fetch-Level Caching

```typescript
// lib/cms/fetch.ts
interface FetchOptions {
  tags?: string[]
  revalidate?: number | false
  cache?: RequestCache
}

export async function cachedFetch<T>(
  url: string,
  options: FetchOptions = {}
): Promise<T> {
  const { tags = [], revalidate = 3600, cache } = options

  const response = await fetch(url, {
    next: {
      tags,
      revalidate,
    },
    cache,
  })

  if (!response.ok) {
    throw new Error(`Fetch failed: ${response.statusText}`)
  }

  return response.json()
}

// Sanity with caching
export async function sanityFetch<T>({
  query,
  params = {},
  tags = [],
  revalidate = 3600,
}: {
  query: string
  params?: Record<string, any>
  tags?: string[]
  revalidate?: number | false
}): Promise<T> {
  const { isEnabled: isDraft } = await draftMode()

  return sanityClient.fetch<T>(query, params, {
    next: {
      revalidate: isDraft ? 0 : revalidate,
      tags: isDraft ? [] : ['sanity', ...tags],
    },
  })
}
```

### CDN Strategies

```typescript
// next.config.js - Image optimization with CMS
module.exports = {
  images: {
    remotePatterns: [
      {
        protocol: 'https',
        hostname: 'cdn.sanity.io',
      },
      {
        protocol: 'https',
        hostname: 'images.ctfassets.net',
      },
    ],
    // Use Vercel's image optimization
    loader: 'default',
    // Or use CMS's built-in optimization
    // loader: 'custom',
    // loaderFile: './lib/image-loader.js',
  },
}
```

```typescript
// Custom image loader for Sanity
export default function sanityLoader({
  src,
  width,
  quality,
}: {
  src: string
  width: number
  quality?: number
}) {
  const url = new URL(src)
  url.searchParams.set('w', width.toString())
  url.searchParams.set('q', (quality || 75).toString())
  url.searchParams.set('auto', 'format')
  return url.toString()
}
```

### Avoiding N+1 Queries

```typescript
// Bad: N+1 query pattern
async function getPostsWithAuthors() {
  const posts = await sanityClient.fetch(`*[_type == "post"]`)

  // N additional queries!
  const postsWithAuthors = await Promise.all(
    posts.map(async (post) => ({
      ...post,
      author: await sanityClient.fetch(
        `*[_type == "author" && _id == $id][0]`,
        { id: post.author._ref }
      ),
    }))
  )

  return postsWithAuthors
}

// Good: Single query with reference expansion
async function getPostsWithAuthors() {
  return sanityClient.fetch(`
    *[_type == "post"] {
      ...,
      "author": author->{
        name,
        image,
        bio
      }
    }
  `)
}

// Good: Batch fetch with references
async function getPostsWithAuthors() {
  const posts = await sanityClient.fetch(`*[_type == "post"]`)

  // Get all unique author IDs
  const authorIds = [...new Set(posts.map((p) => p.author._ref))]

  // Single query for all authors
  const authors = await sanityClient.fetch(
    `*[_type == "author" && _id in $ids]`,
    { ids: authorIds }
  )

  // Create lookup map
  const authorMap = new Map(authors.map((a) => [a._id, a]))

  // Merge
  return posts.map((post) => ({
    ...post,
    author: authorMap.get(post.author._ref),
  }))
}
```

### Parallel Data Fetching

```typescript
// app/blog/[slug]/page.tsx
export default async function BlogPost({ params }) {
  const { slug } = await params

  // Parallel fetch - don't await sequentially
  const [post, relatedPosts, siteSettings] = await Promise.all([
    getPost(slug),
    getRelatedPosts(slug),
    getSiteSettings(),
  ])

  if (!post) notFound()

  return (
    <article>
      <h1>{post.title}</h1>
      <Content post={post} />
      <RelatedPosts posts={relatedPosts} />
    </article>
  )
}
```

---

## 11. Migration Strategies

### WordPress to Headless Migration

**Phase 1: Content Export**

```typescript
// scripts/export-wordpress.ts
import { JSDOM } from 'jsdom'
import TurndownService from 'turndown'

const WP_API = 'https://your-wordpress-site.com/wp-json/wp/v2'

interface WPPost {
  id: number
  slug: string
  title: { rendered: string }
  content: { rendered: string }
  excerpt: { rendered: string }
  date: string
  featured_media: number
  categories: number[]
  tags: number[]
  _embedded?: {
    'wp:featuredmedia'?: [{ source_url: string }]
    'wp:term'?: [{ name: string; slug: string }[]]
  }
}

async function fetchAllPosts(): Promise<WPPost[]> {
  const posts: WPPost[] = []
  let page = 1
  let hasMore = true

  while (hasMore) {
    const response = await fetch(
      `${WP_API}/posts?per_page=100&page=${page}&_embed`
    )

    if (!response.ok) break

    const data = await response.json()
    posts.push(...data)

    hasMore = data.length === 100
    page++
  }

  return posts
}

function convertHtmlToPortableText(html: string) {
  const turndown = new TurndownService({
    headingStyle: 'atx',
    codeBlockStyle: 'fenced',
  })

  // Convert to markdown first
  const markdown = turndown.turndown(html)

  // Then to Portable Text (simplified - use a proper converter)
  return [
    {
      _type: 'block',
      children: [{ _type: 'span', text: markdown }],
    },
  ]
}

async function exportToSanity(posts: WPPost[]) {
  const sanityDocuments = posts.map((post) => ({
    _type: 'post',
    _id: `wordpress-import-${post.id}`,
    title: post.title.rendered,
    slug: { current: post.slug },
    publishedAt: post.date,
    excerpt: new JSDOM(post.excerpt.rendered).window.document.body.textContent,
    body: convertHtmlToPortableText(post.content.rendered),
    // Map categories and tags
    categories: post._embedded?.['wp:term']?.[0]?.map((cat) => ({
      _type: 'reference',
      _ref: `category-${cat.slug}`,
    })),
  }))

  // Write to NDJSON for import
  const fs = await import('fs/promises')
  await fs.writeFile(
    'sanity-import.ndjson',
    sanityDocuments.map((doc) => JSON.stringify(doc)).join('\n')
  )
}

// Run export
const posts = await fetchAllPosts()
await exportToSanity(posts)
```

**Phase 2: URL Redirect Mapping**

```typescript
// scripts/generate-redirects.ts
interface Redirect {
  source: string
  destination: string
  permanent: boolean
}

async function generateRedirects(wpPosts: WPPost[]): Promise<Redirect[]> {
  return wpPosts.map((post) => ({
    // WordPress often uses /YYYY/MM/DD/slug or /slug format
    source: `/${post.slug}`,
    destination: `/blog/${post.slug}`,
    permanent: true,
  }))
}

// next.config.js
module.exports = {
  async redirects() {
    // Import generated redirects
    const redirects = require('./redirects.json')
    return redirects
  },
}
```

**Phase 3: Phased Migration**

```typescript
// middleware.ts - Route traffic during migration
import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'

const MIGRATED_PATHS = new Set(['/blog', '/about', '/contact'])

export function middleware(request: NextRequest) {
  const path = request.nextUrl.pathname

  // Check if this path has been migrated
  const isMigrated = MIGRATED_PATHS.has(path) ||
    Array.from(MIGRATED_PATHS).some((p) => path.startsWith(`${p}/`))

  if (!isMigrated) {
    // Proxy to old WordPress site
    return NextResponse.rewrite(
      new URL(path, 'https://old-wordpress-site.com')
    )
  }

  return NextResponse.next()
}

export const config = {
  matcher: ['/((?!api|_next/static|_next/image|favicon.ico).*)'],
}
```

**Phase 4: SEO Preservation**

```typescript
// app/blog/[slug]/page.tsx
import { Metadata } from 'next'

export async function generateMetadata({ params }): Promise<Metadata> {
  const post = await getPost(params.slug)

  return {
    title: post.seo?.title || post.title,
    description: post.seo?.description || post.excerpt,
    openGraph: {
      title: post.seo?.title || post.title,
      description: post.seo?.description || post.excerpt,
      type: 'article',
      publishedTime: post.publishedAt,
      authors: [post.author?.name],
      images: post.mainImage
        ? [
            {
              url: urlFor(post.mainImage).width(1200).height(630).url(),
              width: 1200,
              height: 630,
            },
          ]
        : [],
    },
    alternates: {
      canonical: `https://your-site.com/blog/${post.slug.current}`,
    },
  }
}
```

---

## 12. Common Mistakes

### 1. Over-Fetching Content

```typescript
// Bad: Fetching entire documents
const posts = await sanityClient.fetch(`*[_type == "post"]`)

// Good: Project only needed fields
const posts = await sanityClient.fetch(`
  *[_type == "post"] {
    _id,
    title,
    slug,
    excerpt,
    "authorName": author->name,
    mainImage
  }
`)
```

### 2. Not Using ISR

```typescript
// Bad: No caching, fetches on every request
export const dynamic = 'force-dynamic'

async function Page() {
  const data = await fetch(API_URL) // No caching
}

// Good: ISR with appropriate revalidation
async function Page() {
  const data = await fetch(API_URL, {
    next: { revalidate: 3600, tags: ['content'] },
  })
}
```

### 3. N+1 Query Problems

```typescript
// Bad: Separate query for each author
const posts = await getPosts()
for (const post of posts) {
  post.author = await getAuthor(post.authorId) // N additional queries!
}

// Good: Single query with joins/references
const posts = await sanityClient.fetch(`
  *[_type == "post"] {
    ...,
    "author": author->{ name, image }
  }
`)
```

### 4. Missing Image Optimization

```typescript
// Bad: Using CMS URLs directly
<img src={post.image.url} />

// Good: Using Next.js Image with optimization
<Image
  src={urlFor(post.image).width(800).url()}
  width={800}
  height={450}
  alt={post.image.alt}
  placeholder="blur"
  blurDataURL={post.image.asset.metadata.lqip}
/>
```

### 5. Coupling Frontend to CMS Schema

```typescript
// Bad: CMS structure leaks into components
function PostCard({ post }) {
  return <h2>{post.fields.title['en-US']}</h2> // Contentful structure
}

// Good: Transform data at the boundary
function transformPost(entry: ContentfulEntry): Post {
  return {
    title: entry.fields.title['en-US'],
    slug: entry.fields.slug['en-US'],
    // ...normalized structure
  }
}

function PostCard({ post }: { post: Post }) {
  return <h2>{post.title}</h2>
}
```

### 6. Not Handling Rich Text Properly

```typescript
// Bad: Rendering HTML string directly (XSS risk, use sanitization libraries like DOMPurify instead)
// <div dangerouslySetInnerHTML={{ __html: post.content }} />

// Good: Use proper rich text renderers
// Sanity
<PortableText value={post.body} components={customComponents} />

// Contentful
{documentToReactComponents(post.content.json, renderOptions)}
```

### 7. Skipping Draft Mode

```typescript
// Bad: No preview capability
async function getPost(slug: string) {
  return sanityClient.fetch(query, { slug })
}

// Good: Draft mode support
async function getPost(slug: string) {
  const { isEnabled: isDraft } = await draftMode()
  const client = isDraft ? previewClient : sanityClient

  return client.fetch(query, { slug }, {
    next: { revalidate: isDraft ? 0 : 3600 },
  })
}
```

### 8. Hardcoding API Tokens

```typescript
// Bad: Tokens in code
const client = createClient({
  token: 'sk_abc123...',
})

// Good: Environment variables
const client = createClient({
  token: process.env.SANITY_API_TOKEN,
})

// Better: Different tokens for different environments
const client = createClient({
  token: process.env.NODE_ENV === 'production'
    ? process.env.SANITY_READ_TOKEN
    : process.env.SANITY_PREVIEW_TOKEN,
})
```

### 9. Not Validating Webhook Signatures

```typescript
// Bad: Accepting any webhook
export async function POST(request: Request) {
  const body = await request.json()
  revalidateTag('posts') // Anyone can trigger this!
}

// Good: Verify signature
export async function POST(request: Request) {
  const body = await request.text()
  const signature = request.headers.get('x-webhook-signature')

  if (!verifySignature(body, signature, process.env.WEBHOOK_SECRET)) {
    return new Response('Unauthorized', { status: 401 })
  }

  const payload = JSON.parse(body)
  revalidateTag('posts')
}
```

### 10. Not Implementing Fallback States

```typescript
// Bad: No loading/error states for preview
async function Page({ params }) {
  const post = await getPost(params.slug)
  return <Article post={post} />
}

// Good: Handle missing content gracefully
async function Page({ params }) {
  const post = await getPost(params.slug)

  if (!post) {
    notFound()
  }

  return <Article post={post} />
}

// With Suspense for streaming
async function Page({ params }) {
  return (
    <Suspense fallback={<ArticleSkeleton />}>
      <ArticleContent slug={params.slug} />
    </Suspense>
  )
}
```

---

## Quick Reference: CMS Setup Commands

```bash
# Sanity
npx sanity@latest init --env --create-project "My Project" --dataset production

# Contentful
npm install contentful @contentful/rich-text-react-renderer

# Payload CMS
npx create-payload-app@latest

# Keystatic
npm install keystatic @keystatic/core @keystatic/next

# Tina CMS
npx @tinacms/cli@latest init
```

---

## Environment Variables Template

```env
# Sanity
NEXT_PUBLIC_SANITY_PROJECT_ID=
NEXT_PUBLIC_SANITY_DATASET=production
SANITY_API_TOKEN=
SANITY_WEBHOOK_SECRET=

# Contentful
CONTENTFUL_SPACE_ID=
CONTENTFUL_ACCESS_TOKEN=
CONTENTFUL_PREVIEW_ACCESS_TOKEN=
CONTENTFUL_WEBHOOK_SECRET=

# Payload CMS
PAYLOAD_SECRET=
MONGODB_URI=
# or POSTGRES_URL=

# Draft Mode
DRAFT_MODE_SECRET=

# Site
NEXT_PUBLIC_SITE_URL=
```
