# Next.js Security Hardening Guide

> Comprehensive security patterns for Next.js App Router applications

## Table of Contents
1. [Security Headers](#1-security-headers)
2. [Content Security Policy Deep Dive](#2-content-security-policy-deep-dive)
3. [Authentication](#3-authentication)
4. [Authorization](#4-authorization)
5. [Server Actions Security](#5-server-actions-security)
6. [API Route Security](#6-api-route-security)
7. [Input Validation](#7-input-validation)
8. [Data Exposure Prevention](#8-data-exposure-prevention)
9. [Environment Variables](#9-environment-variables)
10. [Cookie Security](#10-cookie-security)
11. [Middleware Security](#11-middleware-security)
12. [Error Handling](#12-error-handling)
13. [Dependency Security](#13-dependency-security)
14. [Vercel Security](#14-vercel-security)
15. [OWASP Top 10 for Next.js](#15-owasp-top-10-for-nextjs)
16. [Security Audit Checklist](#16-security-audit-checklist)

---

## 1. Security Headers

Security headers are your first line of defense. Configure them in both `next.config.ts` and middleware for comprehensive coverage.

### next.config.ts Headers Configuration

```typescript
// next.config.ts
import type { NextConfig } from 'next'

const securityHeaders = [
  {
    key: 'Strict-Transport-Security',
    value: 'max-age=63072000; includeSubDomains; preload'
  },
  {
    key: 'X-Content-Type-Options',
    value: 'nosniff'
  },
  {
    key: 'X-Frame-Options',
    value: 'DENY'
  },
  {
    key: 'X-XSS-Protection',
    value: '1; mode=block'
  },
  {
    key: 'Referrer-Policy',
    value: 'strict-origin-when-cross-origin'
  },
  {
    key: 'Permissions-Policy',
    value: 'camera=(), microphone=(), geolocation=(), browsing-topics=()'
  }
]

const config: NextConfig = {
  async headers() {
    return [
      {
        // Apply to all routes
        source: '/:path*',
        headers: securityHeaders
      }
    ]
  }
}

export default config
```

### Middleware Pattern for Dynamic Headers (CSP with Nonce)

```typescript
// middleware.ts
import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'

export function middleware(request: NextRequest) {
  // Generate a unique nonce for each request
  const nonce = Buffer.from(crypto.randomUUID()).toString('base64')

  // Build CSP header with nonce
  const cspHeader = `
    default-src 'self';
    script-src 'self' 'nonce-${nonce}' 'strict-dynamic';
    style-src 'self' 'nonce-${nonce}';
    img-src 'self' blob: data:;
    font-src 'self';
    object-src 'none';
    base-uri 'self';
    form-action 'self';
    frame-ancestors 'none';
    upgrade-insecure-requests;
  `.replace(/\s{2,}/g, ' ').trim()

  const requestHeaders = new Headers(request.headers)
  requestHeaders.set('x-nonce', nonce)

  const response = NextResponse.next({
    request: {
      headers: requestHeaders
    }
  })

  response.headers.set('Content-Security-Policy', cspHeader)
  response.headers.set('Strict-Transport-Security', 'max-age=63072000; includeSubDomains; preload')
  response.headers.set('X-Content-Type-Options', 'nosniff')
  response.headers.set('X-Frame-Options', 'DENY')
  response.headers.set('Referrer-Policy', 'strict-origin-when-cross-origin')
  response.headers.set('Permissions-Policy', 'camera=(), microphone=(), geolocation=()')

  return response
}

export const config = {
  matcher: [
    // Match all paths except static files and api routes that don't need CSP
    '/((?!_next/static|_next/image|favicon.ico).*)'
  ]
}
```

### Header Reference Table

| Header | Value | Purpose |
|--------|-------|---------|
| `Strict-Transport-Security` | `max-age=63072000; includeSubDomains; preload` | Force HTTPS for 2 years |
| `X-Content-Type-Options` | `nosniff` | Prevent MIME type sniffing |
| `X-Frame-Options` | `DENY` | Prevent clickjacking |
| `Referrer-Policy` | `strict-origin-when-cross-origin` | Control referrer information |
| `Permissions-Policy` | `camera=(), microphone=()` | Disable browser features |
| `Content-Security-Policy` | Complex policy with nonces | Control resource loading |

---

## 2. Content Security Policy Deep Dive

CSP is critical for preventing XSS attacks. Next.js App Router requires special handling for nonces.

### Complete CSP Middleware with Nonce Propagation

```typescript
// middleware.ts
import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'

function generateNonce(): string {
  return Buffer.from(crypto.randomUUID()).toString('base64')
}

function buildCSP(nonce: string, isDev: boolean): string {
  const directives: Record<string, string[]> = {
    'default-src': ["'self'"],
    'script-src': [
      "'self'",
      `'nonce-${nonce}'`,
      "'strict-dynamic'",
      // Allow eval in development for hot reload
      ...(isDev ? ["'unsafe-eval'"] : [])
    ],
    'style-src': [
      "'self'",
      `'nonce-${nonce}'`,
      // Required for Tailwind inline styles in some cases
      "'unsafe-inline'"
    ],
    'img-src': ["'self'", 'blob:', 'data:', 'https:'],
    'font-src': ["'self'", 'https://fonts.gstatic.com'],
    'connect-src': [
      "'self'",
      // Add your API domains
      'https://api.example.com',
      // Vercel analytics
      'https://vitals.vercel-insights.com',
      ...(isDev ? ['ws://localhost:3000'] : [])
    ],
    'frame-src': ["'self'"],
    'object-src': ["'none'"],
    'base-uri': ["'self'"],
    'form-action': ["'self'"],
    'frame-ancestors': ["'none'"],
    'upgrade-insecure-requests': []
  }

  // Add CSP reporting in production
  if (!isDev) {
    directives['report-uri'] = ['/api/csp-report']
    directives['report-to'] = ['csp-endpoint']
  }

  return Object.entries(directives)
    .map(([key, values]) =>
      values.length ? `${key} ${values.join(' ')}` : key
    )
    .join('; ')
}

export function middleware(request: NextRequest) {
  const nonce = generateNonce()
  const isDev = process.env.NODE_ENV === 'development'

  const csp = buildCSP(nonce, isDev)

  // Pass nonce to server components via header
  const requestHeaders = new Headers(request.headers)
  requestHeaders.set('x-nonce', nonce)

  const response = NextResponse.next({
    request: { headers: requestHeaders }
  })

  // Set CSP header
  response.headers.set('Content-Security-Policy', csp)

  // Report-To header for CSP reporting
  if (!isDev) {
    response.headers.set('Report-To', JSON.stringify({
      group: 'csp-endpoint',
      max_age: 10886400,
      endpoints: [{ url: '/api/csp-report' }]
    }))
  }

  return response
}
```

### Accessing Nonce in Server Components

```typescript
// app/layout.tsx
import { headers } from 'next/headers'

export default async function RootLayout({
  children
}: {
  children: React.ReactNode
}) {
  const headersList = await headers()
  const nonce = headersList.get('x-nonce') ?? ''

  return (
    <html lang="en">
      <head>
        {/* Pass nonce to script tags */}
        <Script nonce={nonce} id="inline-script">
          {`window.__NONCE__ = "${nonce}";`}
        </Script>
      </head>
      <body>
        {/* Pass nonce to providers that need it */}
        <NonceProvider nonce={nonce}>
          {children}
        </NonceProvider>
      </body>
    </html>
  )
}
```

### Nonce Provider for Client Components

```typescript
// lib/nonce-context.tsx
'use client'

import { createContext, useContext } from 'react'

const NonceContext = createContext<string>('')

export function NonceProvider({
  nonce,
  children
}: {
  nonce: string
  children: React.ReactNode
}) {
  return (
    <NonceContext.Provider value={nonce}>
      {children}
    </NonceContext.Provider>
  )
}

export function useNonce() {
  return useContext(NonceContext)
}
```

### Handling Tailwind CSS with CSP

Tailwind can generate inline styles that violate CSP. Here are solutions:

```typescript
// Option 1: Use 'unsafe-inline' for styles (less secure but simpler)
// style-src 'self' 'unsafe-inline'

// Option 2: Use Tailwind's safelist and avoid arbitrary values
// tailwind.config.ts
import type { Config } from 'tailwindcss'

const config: Config = {
  // Safelist classes you need, avoid arbitrary values like `w-[123px]`
  safelist: [
    'bg-red-500',
    'text-3xl',
    // Pattern-based safelisting
    {
      pattern: /bg-(red|green|blue)-(100|200|300)/
    }
  ]
}

export default config
```

### CSP Reporting Endpoint

```typescript
// app/api/csp-report/route.ts
import { NextRequest, NextResponse } from 'next/server'

interface CSPViolationReport {
  'csp-report': {
    'document-uri': string
    'referrer': string
    'violated-directive': string
    'effective-directive': string
    'original-policy': string
    'blocked-uri': string
    'status-code': number
  }
}

export async function POST(request: NextRequest) {
  try {
    const report: CSPViolationReport = await request.json()

    // Log to your monitoring service
    console.error('CSP Violation:', {
      documentUri: report['csp-report']['document-uri'],
      violatedDirective: report['csp-report']['violated-directive'],
      blockedUri: report['csp-report']['blocked-uri'],
      timestamp: new Date().toISOString()
    })

    // Send to external monitoring (Sentry, etc.)
    // await logToSentry(report)

    return NextResponse.json({ received: true })
  } catch {
    return NextResponse.json({ error: 'Invalid report' }, { status: 400 })
  }
}
```

### JSON-LD with CSP Nonce

When using JSON-LD structured data, you must sanitize the content to prevent XSS:

```typescript
// components/json-ld.tsx
import { headers } from 'next/headers'

interface JsonLdProps {
  data: Record<string, unknown>
}

export async function JsonLd({ data }: JsonLdProps) {
  const headersList = await headers()
  const nonce = headersList.get('x-nonce') ?? ''

  // IMPORTANT: Replace < to prevent script injection via JSON-LD
  // This is the standard Next.js pattern for JSON-LD security.
  // Without this sanitization, an attacker could inject </script><script>malicious()
  // into your JSON-LD data and execute arbitrary JavaScript.
  const sanitizedJson = JSON.stringify(data).replace(/</g, '\\u003c')

  return (
    <script
      type="application/ld+json"
      nonce={nonce}
      // Using a pre-sanitized string here - the .replace(/</g, '\\u003c')
      // escapes < as a Unicode sequence, preventing HTML tag injection
      suppressHydrationWarning
    >
      {sanitizedJson}
    </script>
  )
}

// Usage in a page
export default function ProductPage() {
  const jsonLd = {
    '@context': 'https://schema.org',
    '@type': 'Product',
    name: 'Example Product',
    description: 'Product description'
  }

  return (
    <>
      <JsonLd data={jsonLd} />
      <main>{/* Page content */}</main>
    </>
  )
}
```

> **Note**: The `.replace(/</g, '\\u003c')` sanitization is critical. Without it, an attacker could inject `</script><script>malicious()` into your JSON-LD data and execute arbitrary JavaScript. This pattern escapes the `<` character as a Unicode escape sequence, which is valid JSON but prevents the browser from interpreting it as an HTML tag.

---

## 3. Authentication

Auth.js v5 (NextAuth.js) provides secure authentication with minimal configuration.

### Auth.js v5 Setup

```typescript
// auth.ts
import NextAuth from 'next-auth'
import GitHub from 'next-auth/providers/github'
import Google from 'next-auth/providers/google'
import Credentials from 'next-auth/providers/credentials'
import { PrismaAdapter } from '@auth/prisma-adapter'
import { prisma } from '@/lib/prisma'
import bcrypt from 'bcryptjs'
import { z } from 'zod'

const loginSchema = z.object({
  email: z.string().email(),
  password: z.string().min(8)
})

export const { handlers, auth, signIn, signOut } = NextAuth({
  adapter: PrismaAdapter(prisma),

  // Session strategy: 'jwt' for stateless, 'database' for server-side sessions
  session: {
    strategy: 'database', // More secure - sessions stored server-side
    maxAge: 30 * 24 * 60 * 60, // 30 days
    updateAge: 24 * 60 * 60 // Extend session if active within 24 hours
  },

  // Secure cookie configuration
  cookies: {
    sessionToken: {
      name: process.env.NODE_ENV === 'production'
        ? '__Secure-authjs.session-token'
        : 'authjs.session-token',
      options: {
        httpOnly: true,
        sameSite: 'lax',
        path: '/',
        secure: process.env.NODE_ENV === 'production'
      }
    },
    csrfToken: {
      name: process.env.NODE_ENV === 'production'
        ? '__Host-authjs.csrf-token'
        : 'authjs.csrf-token',
      options: {
        httpOnly: true,
        sameSite: 'lax',
        path: '/',
        secure: process.env.NODE_ENV === 'production'
      }
    }
  },

  providers: [
    GitHub({
      clientId: process.env.GITHUB_ID!,
      clientSecret: process.env.GITHUB_SECRET!
    }),
    Google({
      clientId: process.env.GOOGLE_ID!,
      clientSecret: process.env.GOOGLE_SECRET!
    }),
    Credentials({
      name: 'credentials',
      credentials: {
        email: { label: 'Email', type: 'email' },
        password: { label: 'Password', type: 'password' }
      },
      async authorize(credentials) {
        // Validate input
        const result = loginSchema.safeParse(credentials)
        if (!result.success) return null

        const { email, password } = result.data

        // Find user
        const user = await prisma.user.findUnique({
          where: { email }
        })
        if (!user?.hashedPassword) return null

        // Verify password
        const isValid = await bcrypt.compare(password, user.hashedPassword)
        if (!isValid) return null

        return {
          id: user.id,
          email: user.email,
          name: user.name,
          role: user.role
        }
      }
    })
  ],

  callbacks: {
    // Add custom claims to session
    async session({ session, user }) {
      if (session.user) {
        session.user.id = user.id
        session.user.role = user.role
      }
      return session
    },

    // Control page access
    authorized({ auth, request: { nextUrl } }) {
      const isLoggedIn = !!auth?.user
      const isProtected = nextUrl.pathname.startsWith('/dashboard')

      if (isProtected && !isLoggedIn) {
        return Response.redirect(new URL('/login', nextUrl))
      }

      return true
    }
  },

  pages: {
    signIn: '/login',
    error: '/auth/error'
  },

  // Enable CSRF protection
  trustHost: true,

  // Debug in development only
  debug: process.env.NODE_ENV === 'development'
})
```

### Route Handlers Setup

```typescript
// app/api/auth/[...nextauth]/route.ts
import { handlers } from '@/auth'

export const { GET, POST } = handlers
```

### Middleware Integration

```typescript
// middleware.ts
import { auth } from '@/auth'
import { NextResponse } from 'next/server'

export default auth((request) => {
  const { auth: session, nextUrl } = request

  // Redirect authenticated users away from auth pages
  if (session && nextUrl.pathname.startsWith('/login')) {
    return NextResponse.redirect(new URL('/dashboard', nextUrl))
  }

  // Add security headers
  const response = NextResponse.next()
  response.headers.set('X-Frame-Options', 'DENY')

  return response
})

export const config = {
  matcher: ['/((?!api|_next/static|_next/image|favicon.ico).*)']
}
```

### Session vs JWT Strategy Comparison

| Aspect | Database Sessions | JWT Sessions |
|--------|-------------------|--------------|
| Security | Higher - can revoke instantly | Lower - valid until expiry |
| Scalability | Requires DB lookup | Stateless, no DB needed |
| Session Data | Unlimited, stored in DB | Limited by cookie size |
| Revocation | Instant | Must wait for expiry |
| Use Case | High-security apps | Stateless APIs |

### Protected Server Component

```typescript
// app/dashboard/page.tsx
import { auth } from '@/auth'
import { redirect } from 'next/navigation'

export default async function DashboardPage() {
  const session = await auth()

  if (!session?.user) {
    redirect('/login')
  }

  return (
    <div>
      <h1>Welcome, {session.user.name}</h1>
    </div>
  )
}
```

---

## 4. Authorization

Authorization should be centralized in a Data Access Layer (DAL) for consistency and security.

### Data Access Layer (DAL) Pattern

```typescript
// lib/dal.ts
import 'server-only'
import { cache } from 'react'
import { auth } from '@/auth'
import { prisma } from '@/lib/prisma'
import { redirect } from 'next/navigation'

// Cached and deduplicated auth check
export const getCurrentUser = cache(async () => {
  const session = await auth()
  if (!session?.user?.id) return null

  const user = await prisma.user.findUnique({
    where: { id: session.user.id },
    select: {
      id: true,
      email: true,
      name: true,
      role: true,
      permissions: true
    }
  })

  return user
})

// Require authentication - throws redirect if not authenticated
export async function requireAuth() {
  const user = await getCurrentUser()
  if (!user) {
    redirect('/login')
  }
  return user
}

// Require specific role
export async function requireRole(roles: string[]) {
  const user = await requireAuth()
  if (!roles.includes(user.role)) {
    redirect('/unauthorized')
  }
  return user
}

// Require specific permission
export async function requirePermission(permission: string) {
  const user = await requireAuth()
  if (!user.permissions.includes(permission)) {
    redirect('/unauthorized')
  }
  return user
}

// Resource-level authorization
export async function canAccessProject(projectId: string) {
  const user = await getCurrentUser()
  if (!user) return false

  // Admin can access all
  if (user.role === 'admin') return true

  // Check project membership
  const membership = await prisma.projectMember.findUnique({
    where: {
      projectId_userId: {
        projectId,
        userId: user.id
      }
    }
  })

  return !!membership
}

// Data fetching with authorization
export async function getProject(projectId: string) {
  const canAccess = await canAccessProject(projectId)
  if (!canAccess) {
    return null
  }

  return prisma.project.findUnique({
    where: { id: projectId },
    include: {
      members: true,
      tasks: true
    }
  })
}

// Get user's projects (automatically scoped)
export async function getUserProjects() {
  const user = await requireAuth()

  if (user.role === 'admin') {
    return prisma.project.findMany({
      orderBy: { updatedAt: 'desc' }
    })
  }

  return prisma.project.findMany({
    where: {
      members: {
        some: { userId: user.id }
      }
    },
    orderBy: { updatedAt: 'desc' }
  })
}
```

### Using DAL in Server Components

```typescript
// app/projects/[id]/page.tsx
import { getProject } from '@/lib/dal'
import { notFound } from 'next/navigation'

interface Props {
  params: Promise<{ id: string }>
}

export default async function ProjectPage({ params }: Props) {
  const { id } = await params
  const project = await getProject(id)

  if (!project) {
    notFound()
  }

  return (
    <div>
      <h1>{project.name}</h1>
      {/* Project content */}
    </div>
  )
}
```

### Role-Based Access Control (RBAC)

```typescript
// lib/rbac.ts
import 'server-only'

export type Role = 'admin' | 'manager' | 'member' | 'viewer'
export type Permission =
  | 'projects:read'
  | 'projects:write'
  | 'projects:delete'
  | 'users:read'
  | 'users:write'
  | 'billing:read'
  | 'billing:write'

const rolePermissions: Record<Role, Permission[]> = {
  admin: [
    'projects:read', 'projects:write', 'projects:delete',
    'users:read', 'users:write',
    'billing:read', 'billing:write'
  ],
  manager: [
    'projects:read', 'projects:write',
    'users:read',
    'billing:read'
  ],
  member: [
    'projects:read', 'projects:write'
  ],
  viewer: [
    'projects:read'
  ]
}

export function hasPermission(role: Role, permission: Permission): boolean {
  return rolePermissions[role]?.includes(permission) ?? false
}

export function hasAnyPermission(role: Role, permissions: Permission[]): boolean {
  return permissions.some(p => hasPermission(role, p))
}

export function hasAllPermissions(role: Role, permissions: Permission[]): boolean {
  return permissions.every(p => hasPermission(role, p))
}
```

### Server Action Authorization

```typescript
// app/actions/project.ts
'use server'

import { requireAuth, requirePermission, canAccessProject } from '@/lib/dal'
import { hasPermission } from '@/lib/rbac'
import { prisma } from '@/lib/prisma'
import { revalidatePath } from 'next/cache'
import { z } from 'zod'

const updateProjectSchema = z.object({
  projectId: z.string().uuid(),
  name: z.string().min(1).max(100),
  description: z.string().max(1000).optional()
})

export async function updateProject(formData: FormData) {
  // 1. Authenticate
  const user = await requireAuth()

  // 2. Validate input
  const result = updateProjectSchema.safeParse({
    projectId: formData.get('projectId'),
    name: formData.get('name'),
    description: formData.get('description')
  })

  if (!result.success) {
    return { error: 'Invalid input' }
  }

  const { projectId, name, description } = result.data

  // 3. Authorize - check permission
  if (!hasPermission(user.role, 'projects:write')) {
    return { error: 'Insufficient permissions' }
  }

  // 4. Authorize - check resource access
  const canAccess = await canAccessProject(projectId)
  if (!canAccess) {
    return { error: 'Project not found' }
  }

  // 5. Perform action
  await prisma.project.update({
    where: { id: projectId },
    data: { name, description }
  })

  revalidatePath(`/projects/${projectId}`)
  return { success: true }
}
```

### Middleware Route Protection

```typescript
// middleware.ts
import { auth } from '@/auth'
import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'

// Define protected routes and required roles
const protectedRoutes: Record<string, string[]> = {
  '/admin': ['admin'],
  '/dashboard': ['admin', 'manager', 'member', 'viewer'],
  '/settings': ['admin', 'manager'],
  '/billing': ['admin']
}

export default auth((request) => {
  const { auth: session, nextUrl } = request

  // Check if route is protected
  const matchedRoute = Object.keys(protectedRoutes).find(
    route => nextUrl.pathname.startsWith(route)
  )

  if (matchedRoute) {
    // Must be authenticated
    if (!session?.user) {
      const loginUrl = new URL('/login', nextUrl)
      loginUrl.searchParams.set('callbackUrl', nextUrl.pathname)
      return NextResponse.redirect(loginUrl)
    }

    // Must have required role
    const requiredRoles = protectedRoutes[matchedRoute]
    if (!requiredRoles.includes(session.user.role)) {
      return NextResponse.redirect(new URL('/unauthorized', nextUrl))
    }
  }

  return NextResponse.next()
})
```

---

## 5. Server Actions Security

Server Actions have built-in security features but require careful implementation.

### CSRF Protection

Server Actions automatically include CSRF protection through a secure token. No additional configuration needed:

```typescript
// Server Actions automatically validate CSRF tokens
// This is handled by Next.js internally
'use server'

export async function submitForm(formData: FormData) {
  // CSRF token is automatically validated before this runs
  // If the token is invalid, the action never executes
}
```

### Input Validation with Zod

```typescript
// app/actions/user.ts
'use server'

import { z } from 'zod'
import { requireAuth } from '@/lib/dal'
import { prisma } from '@/lib/prisma'
import { revalidatePath } from 'next/cache'

// Define strict schemas
const createUserSchema = z.object({
  email: z.string().email().toLowerCase().trim(),
  name: z.string().min(2).max(50).trim(),
  role: z.enum(['member', 'viewer']), // Never allow 'admin' from client
  teamId: z.string().uuid()
})

const updateProfileSchema = z.object({
  name: z.string().min(2).max(50).trim().optional(),
  bio: z.string().max(500).trim().optional(),
  avatar: z.string().url().optional()
})

type ActionResult<T = void> =
  | { success: true; data?: T }
  | { success: false; error: string; fieldErrors?: Record<string, string[]> }

export async function createUser(
  prevState: ActionResult,
  formData: FormData
): Promise<ActionResult<{ id: string }>> {
  // Authenticate
  const currentUser = await requireAuth()

  // Validate input
  const result = createUserSchema.safeParse({
    email: formData.get('email'),
    name: formData.get('name'),
    role: formData.get('role'),
    teamId: formData.get('teamId')
  })

  if (!result.success) {
    return {
      success: false,
      error: 'Validation failed',
      fieldErrors: result.error.flatten().fieldErrors
    }
  }

  const { email, name, role, teamId } = result.data

  // Authorization check
  const team = await prisma.team.findFirst({
    where: {
      id: teamId,
      members: {
        some: {
          userId: currentUser.id,
          role: { in: ['admin', 'owner'] }
        }
      }
    }
  })

  if (!team) {
    return { success: false, error: 'Team not found or insufficient permissions' }
  }

  // Check for existing user
  const existingUser = await prisma.user.findUnique({
    where: { email }
  })

  if (existingUser) {
    return {
      success: false,
      error: 'Validation failed',
      fieldErrors: { email: ['Email already registered'] }
    }
  }

  // Create user
  const user = await prisma.user.create({
    data: { email, name, role }
  })

  revalidatePath('/users')
  return { success: true, data: { id: user.id } }
}
```

### Rate Limiting Server Actions

```typescript
// lib/rate-limit.ts
import { Ratelimit } from '@upstash/ratelimit'
import { Redis } from '@upstash/redis'
import { headers } from 'next/headers'

const redis = new Redis({
  url: process.env.UPSTASH_REDIS_URL!,
  token: process.env.UPSTASH_REDIS_TOKEN!
})

const ratelimit = new Ratelimit({
  redis,
  limiter: Ratelimit.slidingWindow(10, '60 s'), // 10 requests per minute
  analytics: true
})

export async function checkRateLimit(identifier?: string) {
  const headersList = await headers()
  const ip = headersList.get('x-forwarded-for')?.split(',')[0] ?? 'anonymous'
  const key = identifier ?? ip

  const { success, limit, reset, remaining } = await ratelimit.limit(key)

  if (!success) {
    const retryAfter = Math.ceil((reset - Date.now()) / 1000)
    throw new RateLimitError(`Rate limit exceeded. Try again in ${retryAfter} seconds.`)
  }

  return { limit, remaining }
}

export class RateLimitError extends Error {
  constructor(message: string) {
    super(message)
    this.name = 'RateLimitError'
  }
}
```

```typescript
// app/actions/contact.ts
'use server'

import { z } from 'zod'
import { checkRateLimit, RateLimitError } from '@/lib/rate-limit'
import { sendEmail } from '@/lib/email'

const contactSchema = z.object({
  email: z.string().email(),
  message: z.string().min(10).max(5000)
})

export async function submitContactForm(formData: FormData) {
  try {
    // Rate limit before any processing
    await checkRateLimit()
  } catch (error) {
    if (error instanceof RateLimitError) {
      return { error: error.message }
    }
    throw error
  }

  const result = contactSchema.safeParse({
    email: formData.get('email'),
    message: formData.get('message')
  })

  if (!result.success) {
    return { error: 'Invalid input' }
  }

  await sendEmail(result.data)
  return { success: true }
}
```

### Closure Security

Variables captured in closures are encrypted when passed to the client:

```typescript
// app/projects/[id]/components/delete-button.tsx
import { deleteProject } from '@/app/actions'

interface Props {
  projectId: string  // This is captured in the closure
  projectName: string
}

export function DeleteButton({ projectId, projectName }: Props) {
  // The projectId is encrypted when the action is serialized
  // It cannot be modified by the client
  async function handleDelete() {
    'use server'
    // projectId here is secure - it was captured at render time
    // and encrypted before being sent to the client
    await deleteProject(projectId)
  }

  return (
    <form action={handleDelete}>
      <button type="submit">Delete {projectName}</button>
    </form>
  )
}
```

However, always validate ownership even with closures:

```typescript
// app/actions/project.ts
'use server'

import { requireAuth, canAccessProject } from '@/lib/dal'
import { prisma } from '@/lib/prisma'

export async function deleteProject(projectId: string) {
  const user = await requireAuth()

  // ALWAYS verify authorization, even though projectId came from closure
  // Defense in depth: don't rely solely on closure encryption
  const canDelete = await canAccessProject(projectId)
  if (!canDelete) {
    throw new Error('Unauthorized')
  }

  await prisma.project.delete({
    where: { id: projectId }
  })
}
```

### Preventing Sensitive Actions

```typescript
// app/actions/dangerous.ts
'use server'

import { requireRole, requireAuth } from '@/lib/dal'
import { prisma } from '@/lib/prisma'
import { z } from 'zod'
import bcrypt from 'bcryptjs'

// Extremely sensitive action - delete all user data
export async function deleteUserAccount() {
  // Require highest privilege level
  const user = await requireRole(['admin'])

  // Additional confirmation required
  // This should be validated against a recently-sent email token
  // to prevent CSRF even with admin role

  await prisma.$transaction([
    prisma.session.deleteMany({ where: { userId: user.id } }),
    prisma.account.deleteMany({ where: { userId: user.id } }),
    prisma.user.delete({ where: { id: user.id } })
  ])
}

// Better: Require re-authentication for sensitive actions
const deleteAccountSchema = z.object({
  password: z.string(),
  confirmText: z.literal('DELETE MY ACCOUNT')
})

export async function deleteUserAccountSecure(formData: FormData) {
  const user = await requireAuth()

  const result = deleteAccountSchema.safeParse({
    password: formData.get('password'),
    confirmText: formData.get('confirmText')
  })

  if (!result.success) {
    return { error: 'Invalid confirmation' }
  }

  // Verify password
  const dbUser = await prisma.user.findUnique({
    where: { id: user.id },
    select: { hashedPassword: true }
  })

  const isValid = await bcrypt.compare(result.data.password, dbUser!.hashedPassword!)
  if (!isValid) {
    return { error: 'Invalid password' }
  }

  // Proceed with deletion
  await prisma.user.delete({ where: { id: user.id } })

  return { success: true }
}
```

---

## 6. API Route Security

### Authenticated API Route

```typescript
// app/api/projects/route.ts
import { NextRequest, NextResponse } from 'next/server'
import { auth } from '@/auth'
import { prisma } from '@/lib/prisma'
import { z } from 'zod'

// Schema for request validation
const createProjectSchema = z.object({
  name: z.string().min(1).max(100),
  description: z.string().max(1000).optional()
})

export async function GET(request: NextRequest) {
  // Authenticate
  const session = await auth()
  if (!session?.user) {
    return NextResponse.json(
      { error: 'Unauthorized' },
      { status: 401 }
    )
  }

  try {
    const projects = await prisma.project.findMany({
      where: {
        members: {
          some: { userId: session.user.id }
        }
      },
      select: {
        id: true,
        name: true,
        createdAt: true
      }
    })

    return NextResponse.json({ projects })
  } catch (error) {
    console.error('Failed to fetch projects:', error)
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    )
  }
}

export async function POST(request: NextRequest) {
  const session = await auth()
  if (!session?.user) {
    return NextResponse.json(
      { error: 'Unauthorized' },
      { status: 401 }
    )
  }

  try {
    const body = await request.json()

    // Validate input
    const result = createProjectSchema.safeParse(body)
    if (!result.success) {
      return NextResponse.json(
        { error: 'Invalid input', details: result.error.flatten() },
        { status: 400 }
      )
    }

    const project = await prisma.project.create({
      data: {
        ...result.data,
        members: {
          create: {
            userId: session.user.id,
            role: 'owner'
          }
        }
      }
    })

    return NextResponse.json({ project }, { status: 201 })
  } catch (error) {
    console.error('Failed to create project:', error)
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    )
  }
}
```

### Rate Limiting with Upstash

```typescript
// lib/rate-limit.ts
import { Ratelimit } from '@upstash/ratelimit'
import { Redis } from '@upstash/redis'

const redis = new Redis({
  url: process.env.UPSTASH_REDIS_URL!,
  token: process.env.UPSTASH_REDIS_TOKEN!
})

// Different rate limits for different endpoints
export const rateLimits = {
  api: new Ratelimit({
    redis,
    limiter: Ratelimit.slidingWindow(100, '60 s'),
    prefix: 'ratelimit:api'
  }),
  auth: new Ratelimit({
    redis,
    limiter: Ratelimit.slidingWindow(5, '60 s'),
    prefix: 'ratelimit:auth'
  }),
  upload: new Ratelimit({
    redis,
    limiter: Ratelimit.slidingWindow(10, '3600 s'),
    prefix: 'ratelimit:upload'
  })
}
```

```typescript
// app/api/protected/route.ts
import { NextRequest, NextResponse } from 'next/server'
import { rateLimits } from '@/lib/rate-limit'

export async function POST(request: NextRequest) {
  // Get identifier for rate limiting
  const ip = request.headers.get('x-forwarded-for')?.split(',')[0] ??
             request.headers.get('x-real-ip') ??
             'anonymous'

  // Check rate limit
  const { success, limit, remaining, reset } = await rateLimits.api.limit(ip)

  // Always include rate limit headers
  const headers = {
    'X-RateLimit-Limit': limit.toString(),
    'X-RateLimit-Remaining': remaining.toString(),
    'X-RateLimit-Reset': reset.toString()
  }

  if (!success) {
    return NextResponse.json(
      { error: 'Too many requests' },
      { status: 429, headers }
    )
  }

  // Process request
  return NextResponse.json({ success: true }, { headers })
}
```

### CORS Configuration in Middleware

```typescript
// middleware.ts
import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'

const allowedOrigins = [
  'https://example.com',
  'https://app.example.com',
  ...(process.env.NODE_ENV === 'development' ? ['http://localhost:3000'] : [])
]

function getCorsHeaders(origin: string | null) {
  const headers: Record<string, string> = {
    'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type, Authorization, X-Requested-With',
    'Access-Control-Max-Age': '86400' // 24 hours
  }

  // Only set origin if it's in allowed list
  if (origin && allowedOrigins.includes(origin)) {
    headers['Access-Control-Allow-Origin'] = origin
    headers['Access-Control-Allow-Credentials'] = 'true'
  }

  return headers
}

export function middleware(request: NextRequest) {
  const origin = request.headers.get('origin')
  const isApiRoute = request.nextUrl.pathname.startsWith('/api')

  // Handle preflight requests
  if (request.method === 'OPTIONS' && isApiRoute) {
    return new NextResponse(null, {
      status: 204,
      headers: getCorsHeaders(origin)
    })
  }

  const response = NextResponse.next()

  // Add CORS headers to API responses
  if (isApiRoute) {
    const corsHeaders = getCorsHeaders(origin)
    Object.entries(corsHeaders).forEach(([key, value]) => {
      response.headers.set(key, value)
    })
  }

  return response
}
```

### Safe Error Responses

```typescript
// lib/api-response.ts
import { NextResponse } from 'next/server'
import { ZodError } from 'zod'
import { logger } from '@/lib/logger'

// Standard error types (safe to expose to client)
type ApiErrorType =
  | 'VALIDATION_ERROR'
  | 'UNAUTHORIZED'
  | 'FORBIDDEN'
  | 'NOT_FOUND'
  | 'RATE_LIMITED'
  | 'INTERNAL_ERROR'

interface ApiError {
  type: ApiErrorType
  message: string
  details?: unknown
}

const errorStatusMap: Record<ApiErrorType, number> = {
  VALIDATION_ERROR: 400,
  UNAUTHORIZED: 401,
  FORBIDDEN: 403,
  NOT_FOUND: 404,
  RATE_LIMITED: 429,
  INTERNAL_ERROR: 500
}

export function apiError(
  type: ApiErrorType,
  message: string,
  details?: unknown
): NextResponse<ApiError> {
  return NextResponse.json(
    { type, message, details },
    { status: errorStatusMap[type] }
  )
}

export function handleApiError(error: unknown): NextResponse<ApiError> {
  // Log full error internally
  logger.error('API Error', { error })

  // Validation errors - safe to expose details
  if (error instanceof ZodError) {
    return apiError(
      'VALIDATION_ERROR',
      'Invalid request data',
      error.flatten()
    )
  }

  // Known error types
  if (error instanceof Error) {
    // Check for specific error types
    if (error.message.includes('Unauthorized')) {
      return apiError('UNAUTHORIZED', 'Authentication required')
    }
    if (error.message.includes('Forbidden')) {
      return apiError('FORBIDDEN', 'Insufficient permissions')
    }
    if (error.message.includes('not found')) {
      return apiError('NOT_FOUND', 'Resource not found')
    }
  }

  // Default - never expose internal error details
  return apiError('INTERNAL_ERROR', 'An unexpected error occurred')
}
```

### API Key Authentication

```typescript
// lib/api-key.ts
import { prisma } from '@/lib/prisma'
import crypto from 'crypto'
import { NextRequest } from 'next/server'

export async function validateApiKey(request: NextRequest) {
  const authHeader = request.headers.get('authorization')

  if (!authHeader?.startsWith('Bearer ')) {
    return null
  }

  const apiKey = authHeader.slice(7)

  // Hash the key to compare with stored hash
  const keyHash = crypto
    .createHash('sha256')
    .update(apiKey)
    .digest('hex')

  const key = await prisma.apiKey.findUnique({
    where: { hash: keyHash },
    include: { user: true }
  })

  if (!key || key.expiresAt < new Date()) {
    return null
  }

  // Update last used timestamp
  await prisma.apiKey.update({
    where: { id: key.id },
    data: { lastUsedAt: new Date() }
  })

  return key.user
}
```

---

## 7. Input Validation

### Zod Schemas for APIs and Server Actions

```typescript
// lib/validations/user.ts
import { z } from 'zod'

// Base schemas
export const emailSchema = z
  .string()
  .email('Invalid email address')
  .toLowerCase()
  .trim()
  .max(255)

export const passwordSchema = z
  .string()
  .min(8, 'Password must be at least 8 characters')
  .max(100)
  .regex(
    /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)/,
    'Password must contain uppercase, lowercase, and number'
  )

export const usernameSchema = z
  .string()
  .min(3, 'Username must be at least 3 characters')
  .max(30)
  .regex(
    /^[a-zA-Z0-9_-]+$/,
    'Username can only contain letters, numbers, underscores, and hyphens'
  )
  .trim()

// Composite schemas
export const registerSchema = z.object({
  email: emailSchema,
  password: passwordSchema,
  confirmPassword: z.string(),
  username: usernameSchema
}).refine(data => data.password === data.confirmPassword, {
  message: 'Passwords do not match',
  path: ['confirmPassword']
})

export const loginSchema = z.object({
  email: emailSchema,
  password: z.string().min(1, 'Password is required')
})

export const updateProfileSchema = z.object({
  name: z.string().min(1).max(100).trim().optional(),
  bio: z.string().max(500).trim().optional(),
  website: z.string().url().optional().or(z.literal('')),
  avatar: z.string().url().optional()
})

// Type exports
export type RegisterInput = z.infer<typeof registerSchema>
export type LoginInput = z.infer<typeof loginSchema>
export type UpdateProfileInput = z.infer<typeof updateProfileSchema>
```

### XSS Prevention

```typescript
// lib/sanitize.ts
import DOMPurify from 'isomorphic-dompurify'

// Configure DOMPurify for safe HTML rendering
const purifyConfig = {
  ALLOWED_TAGS: ['b', 'i', 'em', 'strong', 'a', 'p', 'br', 'ul', 'ol', 'li'],
  ALLOWED_ATTR: ['href', 'target', 'rel'],
  ALLOW_DATA_ATTR: false
}

export function sanitizeHtml(dirty: string): string {
  return DOMPurify.sanitize(dirty, purifyConfig)
}

// Strict sanitization - remove all HTML
export function sanitizeText(input: string): string {
  return DOMPurify.sanitize(input, { ALLOWED_TAGS: [] })
}

// Sanitize for use in attributes
export function sanitizeAttribute(input: string): string {
  return input
    .replace(/&/g, '&amp;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#x27;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
}
```

```typescript
// components/user-content.tsx
import { sanitizeHtml } from '@/lib/sanitize'

interface Props {
  content: string
}

// Server Component - sanitize on server before rendering
// This is safe because we sanitize with DOMPurify first
export function UserContent({ content }: Props) {
  // IMPORTANT: Always sanitize user content before rendering
  const sanitized = sanitizeHtml(content)

  return (
    <div
      className="prose"
      // Safe: content has been sanitized with DOMPurify
      // which removes all dangerous HTML and scripts
      suppressHydrationWarning
    >
      {/* Render sanitized HTML */}
      <div dangerouslySetInnerHTML={{ __html: sanitized }} />
    </div>
  )
}
```

### SQL Injection Prevention with ORMs

```typescript
// Always use parameterized queries
import { prisma } from '@/lib/prisma'

// GOOD - Parameterized query
async function searchUsers(query: string) {
  return prisma.user.findMany({
    where: {
      OR: [
        { name: { contains: query, mode: 'insensitive' } },
        { email: { contains: query, mode: 'insensitive' } }
      ]
    }
  })
}

// GOOD - Raw query with parameters (using tagged template)
async function searchUsersRaw(query: string) {
  return prisma.$queryRaw`
    SELECT id, name, email
    FROM users
    WHERE name ILIKE ${'%' + query + '%'}
    OR email ILIKE ${'%' + query + '%'}
  `
}

// BAD - Never do this! Vulnerable to SQL injection
// async function searchUsersUnsafe(query: string) {
//   return prisma.$queryRawUnsafe(
//     `SELECT * FROM users WHERE name LIKE '%${query}%'`
//   )
// }
```

### File Upload Validation

```typescript
// lib/upload.ts
import { z } from 'zod'

// Allowed file types with magic bytes
const FILE_SIGNATURES: Record<string, number[][]> = {
  'image/jpeg': [[0xFF, 0xD8, 0xFF]],
  'image/png': [[0x89, 0x50, 0x4E, 0x47]],
  'image/gif': [[0x47, 0x49, 0x46, 0x38]],
  'image/webp': [[0x52, 0x49, 0x46, 0x46]],
  'application/pdf': [[0x25, 0x50, 0x44, 0x46]]
}

const MAX_FILE_SIZE = 5 * 1024 * 1024 // 5MB

export const uploadSchema = z.object({
  file: z.instanceof(File)
    .refine(file => file.size <= MAX_FILE_SIZE, {
      message: `File size must be less than ${MAX_FILE_SIZE / 1024 / 1024}MB`
    })
    .refine(file => Object.keys(FILE_SIGNATURES).includes(file.type), {
      message: 'Invalid file type'
    })
})

export async function validateFileContent(file: File): Promise<boolean> {
  const buffer = await file.arrayBuffer()
  const bytes = new Uint8Array(buffer)

  const expectedSignatures = FILE_SIGNATURES[file.type]
  if (!expectedSignatures) return false

  // Check magic bytes
  return expectedSignatures.some(signature =>
    signature.every((byte, index) => bytes[index] === byte)
  )
}

// Complete upload handler
export async function handleFileUpload(formData: FormData) {
  const file = formData.get('file')

  if (!(file instanceof File)) {
    return { error: 'No file provided' }
  }

  // Schema validation
  const result = uploadSchema.safeParse({ file })
  if (!result.success) {
    return { error: result.error.flatten().fieldErrors.file?.[0] }
  }

  // Magic bytes validation
  const isValidContent = await validateFileContent(file)
  if (!isValidContent) {
    return { error: 'File content does not match declared type' }
  }

  // Generate safe filename
  const extension = file.name.split('.').pop()?.toLowerCase()
  const safeFilename = `${crypto.randomUUID()}.${extension}`

  // Upload to storage...

  return { success: true, filename: safeFilename }
}
```

```typescript
// app/api/upload/route.ts
import { NextRequest, NextResponse } from 'next/server'
import { auth } from '@/auth'
import { handleFileUpload } from '@/lib/upload'
import { rateLimits } from '@/lib/rate-limit'

export async function POST(request: NextRequest) {
  // Auth check
  const session = await auth()
  if (!session?.user) {
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })
  }

  // Rate limit for uploads
  const { success } = await rateLimits.upload.limit(session.user.id)
  if (!success) {
    return NextResponse.json({ error: 'Upload limit exceeded' }, { status: 429 })
  }

  const formData = await request.formData()
  const result = await handleFileUpload(formData)

  if ('error' in result) {
    return NextResponse.json({ error: result.error }, { status: 400 })
  }

  return NextResponse.json(result)
}
```

---

## 8. Data Exposure Prevention

### server-only Package

```typescript
// lib/dal.ts
import 'server-only'  // This import prevents this module from being used in client components

import { prisma } from '@/lib/prisma'

// These functions can never be imported in client code
export async function getUserWithSecrets(id: string) {
  return prisma.user.findUnique({
    where: { id },
    include: {
      apiKeys: true,
      sessions: true
    }
  })
}
```

### Experimental Taint API

```typescript
// lib/taint.ts
import 'server-only'
import { experimental_taintObjectReference, experimental_taintUniqueValue } from 'react'

// Taint sensitive objects
export function taintUserSecrets<T extends object>(obj: T): T {
  experimental_taintObjectReference(
    'Do not pass user secrets to Client Components',
    obj
  )
  return obj
}

// Taint unique values like tokens
export function taintToken(token: string): string {
  experimental_taintUniqueValue(
    'Do not pass tokens to Client Components',
    token,
    token
  )
  return token
}
```

```typescript
// lib/dal.ts
import 'server-only'
import { taintUserSecrets, taintToken } from './taint'
import { prisma } from '@/lib/prisma'

export async function getUser(id: string) {
  const user = await prisma.user.findUnique({
    where: { id },
    select: {
      id: true,
      email: true,
      name: true,
      role: true,
      apiKey: true,  // Sensitive!
      refreshToken: true  // Sensitive!
    }
  })

  if (!user) return null

  // Taint sensitive fields
  if (user.apiKey) {
    taintToken(user.apiKey)
  }
  if (user.refreshToken) {
    taintToken(user.refreshToken)
  }

  // Taint the entire object
  return taintUserSecrets(user)
}
```

### Data Transfer Objects (DTOs)

```typescript
// lib/dto/user.ts
import 'server-only'
import type { User } from '@prisma/client'

// Public DTO - safe to pass to client
export interface UserDTO {
  id: string
  name: string | null
  avatar: string | null
}

// Full DTO - only for server use
export interface UserFullDTO extends UserDTO {
  email: string
  role: string
  createdAt: Date
}

// Transform functions
export function toUserDTO(user: User): UserDTO {
  return {
    id: user.id,
    name: user.name,
    avatar: user.avatar
  }
}

export function toUserFullDTO(user: User): UserFullDTO {
  return {
    ...toUserDTO(user),
    email: user.email,
    role: user.role,
    createdAt: user.createdAt
  }
}
```

```typescript
// app/users/[id]/page.tsx
import { getUser } from '@/lib/dal'
import { toUserDTO } from '@/lib/dto/user'
import { UserProfile } from './user-profile'
import { notFound } from 'next/navigation'

export default async function UserPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params
  const user = await getUser(id)

  if (!user) {
    notFound()
  }

  // Only pass safe DTO to client component
  const userDTO = toUserDTO(user)

  return <UserProfile user={userDTO} />
}
```

### Minimizing Client Component Props

```typescript
// WRONG - Passing too much data
// app/projects/page.tsx
import { getProjects } from '@/lib/dal'
import { ProjectList } from './project-list'

export default async function ProjectsPageWrong() {
  const projects = await getProjects()

  // This sends ALL project data to the client!
  return <ProjectList projects={projects} />
}

// CORRECT - Pass only what's needed
// app/projects/page.tsx
import { getProjects } from '@/lib/dal'
import { ProjectCard } from './project-card'

export default async function ProjectsPage() {
  const projects = await getProjects()

  return (
    <div className="grid gap-4">
      {projects.map(project => (
        // Render data in Server Component, pass minimal props
        <ProjectCard
          key={project.id}
          id={project.id}
          name={project.name}
          description={project.description?.slice(0, 100)}
        />
      ))}
    </div>
  )
}
```

---

## 9. Environment Variables

### NEXT_PUBLIC_ Exposure Risks

```typescript
// DANGEROUS - Never put secrets in NEXT_PUBLIC_ variables
// These are embedded in the client bundle!

// .env.local (WRONG examples - DO NOT DO THIS)
// NEXT_PUBLIC_API_KEY=sk_secret_key  // WRONG - exposed to client!
// NEXT_PUBLIC_DATABASE_URL=postgres://...  // WRONG - exposed!

// CORRECT - Keep secrets server-side only
// DATABASE_URL=postgres://...
// STRIPE_SECRET_KEY=sk_...
// API_SECRET=...

// Only public, non-sensitive values
// NEXT_PUBLIC_API_URL=https://api.example.com
// NEXT_PUBLIC_ANALYTICS_ID=UA-123456
```

### Runtime Validation with Zod

```typescript
// lib/env.ts
import { z } from 'zod'

// Server-side environment schema
const serverEnvSchema = z.object({
  // Database
  DATABASE_URL: z.string().url(),

  // Auth
  AUTH_SECRET: z.string().min(32),
  AUTH_URL: z.string().url(),

  // OAuth
  GITHUB_ID: z.string(),
  GITHUB_SECRET: z.string(),

  // API Keys
  STRIPE_SECRET_KEY: z.string().startsWith('sk_'),
  OPENAI_API_KEY: z.string().startsWith('sk-'),

  // Services
  REDIS_URL: z.string().url(),

  // Optional
  SENTRY_DSN: z.string().url().optional()
})

// Client-side environment schema
const clientEnvSchema = z.object({
  NEXT_PUBLIC_API_URL: z.string().url(),
  NEXT_PUBLIC_SITE_URL: z.string().url(),
  NEXT_PUBLIC_ANALYTICS_ID: z.string().optional()
})

// Validate at startup
function validateEnv() {
  const serverResult = serverEnvSchema.safeParse(process.env)
  const clientResult = clientEnvSchema.safeParse(process.env)

  if (!serverResult.success) {
    console.error('Invalid server environment variables:')
    console.error(serverResult.error.flatten().fieldErrors)
    throw new Error('Invalid server environment configuration')
  }

  if (!clientResult.success) {
    console.error('Invalid client environment variables:')
    console.error(clientResult.error.flatten().fieldErrors)
    throw new Error('Invalid client environment configuration')
  }

  return {
    server: serverResult.data,
    client: clientResult.data
  }
}

// Export validated env
export const env = validateEnv()

// Type-safe access
export const serverEnv = env.server
export const clientEnv = env.client
```

```typescript
// Usage
import { serverEnv, clientEnv } from '@/lib/env'
import Stripe from 'stripe'

// Server-side
const stripe = new Stripe(serverEnv.STRIPE_SECRET_KEY)

// Client-side (in client component or shared code)
const apiUrl = clientEnv.NEXT_PUBLIC_API_URL
```

### Secrets Access Pattern

```typescript
// lib/secrets.ts
import 'server-only'

// Centralized secrets access - only importable on server
class Secrets {
  private static instance: Secrets

  private constructor() {}

  static getInstance(): Secrets {
    if (!Secrets.instance) {
      Secrets.instance = new Secrets()
    }
    return Secrets.instance
  }

  get databaseUrl(): string {
    const url = process.env.DATABASE_URL
    if (!url) throw new Error('DATABASE_URL not configured')
    return url
  }

  get stripeSecretKey(): string {
    const key = process.env.STRIPE_SECRET_KEY
    if (!key) throw new Error('STRIPE_SECRET_KEY not configured')
    return key
  }

  get openaiApiKey(): string {
    const key = process.env.OPENAI_API_KEY
    if (!key) throw new Error('OPENAI_API_KEY not configured')
    return key
  }
}

export const secrets = Secrets.getInstance()
```

---

## 10. Cookie Security

### Secure Cookie Configuration

```typescript
// lib/cookies.ts
import { cookies } from 'next/headers'
import { ResponseCookie } from 'next/dist/compiled/@edge-runtime/cookies'

type CookieOptions = Partial<ResponseCookie>

// Secure defaults
const SECURE_DEFAULTS: CookieOptions = {
  httpOnly: true,
  secure: process.env.NODE_ENV === 'production',
  sameSite: 'lax',
  path: '/'
}

// Cookie configurations for different purposes
export const cookieConfigs = {
  // Session cookie - most secure
  session: {
    ...SECURE_DEFAULTS,
    sameSite: 'lax' as const,
    maxAge: 30 * 24 * 60 * 60 // 30 days
  },

  // CSRF token - stricter same-site
  csrf: {
    ...SECURE_DEFAULTS,
    sameSite: 'strict' as const,
    maxAge: 60 * 60 // 1 hour
  },

  // Remember me - longer lived
  remember: {
    ...SECURE_DEFAULTS,
    maxAge: 365 * 24 * 60 * 60 // 1 year
  },

  // Preference cookie - can be read by JS
  preference: {
    ...SECURE_DEFAULTS,
    httpOnly: false, // Accessible to JS
    maxAge: 365 * 24 * 60 * 60
  }
} as const

// Cookie name with __Host- prefix for maximum security
// __Host- prefix requirements:
// - Must be set with Secure flag
// - Must be set from a secure origin (HTTPS)
// - Must not include a Domain attribute
// - Must have Path set to /
export function getSecureCookieName(name: string): string {
  return process.env.NODE_ENV === 'production'
    ? `__Host-${name}`
    : name
}

// Helper to set secure cookies
export async function setSecureCookie(
  name: string,
  value: string,
  config: keyof typeof cookieConfigs = 'session'
) {
  const cookieStore = await cookies()
  const secureName = getSecureCookieName(name)

  cookieStore.set(secureName, value, cookieConfigs[config])
}

// Helper to get secure cookies
export async function getSecureCookie(name: string): Promise<string | undefined> {
  const cookieStore = await cookies()
  const secureName = getSecureCookieName(name)

  return cookieStore.get(secureName)?.value
}

// Helper to delete secure cookies
export async function deleteSecureCookie(name: string) {
  const cookieStore = await cookies()
  const secureName = getSecureCookieName(name)

  cookieStore.delete(secureName)
}
```

### Cookie Encryption

```typescript
// lib/cookie-crypto.ts
import 'server-only'
import { createCipheriv, createDecipheriv, randomBytes } from 'crypto'

const ALGORITHM = 'aes-256-gcm'
const KEY = Buffer.from(process.env.COOKIE_SECRET!, 'hex') // 32 bytes

export function encryptCookie(data: string): string {
  const iv = randomBytes(12)
  const cipher = createCipheriv(ALGORITHM, KEY, iv)

  let encrypted = cipher.update(data, 'utf8', 'hex')
  encrypted += cipher.final('hex')

  const authTag = cipher.getAuthTag()

  // Combine iv + authTag + encrypted
  return iv.toString('hex') + authTag.toString('hex') + encrypted
}

export function decryptCookie(encrypted: string): string | null {
  try {
    const iv = Buffer.from(encrypted.slice(0, 24), 'hex')
    const authTag = Buffer.from(encrypted.slice(24, 56), 'hex')
    const data = encrypted.slice(56)

    const decipher = createDecipheriv(ALGORITHM, KEY, iv)
    decipher.setAuthTag(authTag)

    let decrypted = decipher.update(data, 'hex', 'utf8')
    decrypted += decipher.final('utf8')

    return decrypted
  } catch {
    return null
  }
}
```

---

## 11. Middleware Security

### Comprehensive Security Middleware

```typescript
// middleware.ts
import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'
import { Ratelimit } from '@upstash/ratelimit'
import { Redis } from '@upstash/redis'

// Initialize rate limiter
const redis = new Redis({
  url: process.env.UPSTASH_REDIS_URL!,
  token: process.env.UPSTASH_REDIS_TOKEN!
})

const ratelimit = new Ratelimit({
  redis,
  limiter: Ratelimit.slidingWindow(100, '60 s')
})

// Blocked countries (ISO codes)
const BLOCKED_COUNTRIES = new Set(['XX', 'YY'])

// Known malicious patterns
const MALICIOUS_PATTERNS = [
  /\.\./,  // Path traversal
  /<script/i,  // XSS attempt
  /union\s+select/i,  // SQL injection
  /javascript:/i,  // JS protocol
  /on\w+\s*=/i  // Event handlers
]

// Bot detection patterns
const BOT_PATTERNS = [
  /curl/i,
  /wget/i,
  /python-requests/i,
  /scrapy/i
]

// Security headers
function addSecurityHeaders(response: NextResponse, nonce: string) {
  const csp = `
    default-src 'self';
    script-src 'self' 'nonce-${nonce}' 'strict-dynamic';
    style-src 'self' 'unsafe-inline';
    img-src 'self' blob: data: https:;
    font-src 'self';
    connect-src 'self' https://api.example.com;
    frame-ancestors 'none';
    base-uri 'self';
    form-action 'self';
  `.replace(/\s{2,}/g, ' ').trim()

  response.headers.set('Content-Security-Policy', csp)
  response.headers.set('X-Content-Type-Options', 'nosniff')
  response.headers.set('X-Frame-Options', 'DENY')
  response.headers.set('X-XSS-Protection', '1; mode=block')
  response.headers.set('Referrer-Policy', 'strict-origin-when-cross-origin')
  response.headers.set('Permissions-Policy', 'camera=(), microphone=(), geolocation=()')
  response.headers.set('Strict-Transport-Security', 'max-age=63072000; includeSubDomains; preload')
}

export async function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl
  const ip = request.headers.get('x-forwarded-for')?.split(',')[0] ??
             request.headers.get('x-real-ip') ??
             'anonymous'
  const userAgent = request.headers.get('user-agent') ?? ''
  const country = request.headers.get('x-vercel-ip-country') ?? ''

  // 1. Geo-blocking
  if (BLOCKED_COUNTRIES.has(country)) {
    return new NextResponse('Access denied', { status: 403 })
  }

  // 2. Bot detection (allow for API endpoints that expect programmatic access)
  if (!pathname.startsWith('/api/public') && BOT_PATTERNS.some(p => p.test(userAgent))) {
    // Log suspicious activity
    console.warn('Potential bot detected', { ip, userAgent, pathname })
    // Optionally block or add challenge
  }

  // 3. Malicious pattern detection
  const fullUrl = request.url
  if (MALICIOUS_PATTERNS.some(p => p.test(fullUrl))) {
    console.error('Malicious request blocked', { ip, url: fullUrl })
    return new NextResponse('Bad Request', { status: 400 })
  }

  // 4. Rate limiting (skip for static files)
  if (!pathname.startsWith('/_next') && !pathname.includes('.')) {
    const { success, limit, remaining, reset } = await ratelimit.limit(ip)

    if (!success) {
      return new NextResponse('Too Many Requests', {
        status: 429,
        headers: {
          'X-RateLimit-Limit': limit.toString(),
          'X-RateLimit-Remaining': remaining.toString(),
          'X-RateLimit-Reset': reset.toString(),
          'Retry-After': Math.ceil((reset - Date.now()) / 1000).toString()
        }
      })
    }
  }

  // 5. Generate nonce for CSP
  const nonce = Buffer.from(crypto.randomUUID()).toString('base64')

  // 6. Create response with modified headers
  const requestHeaders = new Headers(request.headers)
  requestHeaders.set('x-nonce', nonce)
  requestHeaders.set('x-request-id', crypto.randomUUID())

  const response = NextResponse.next({
    request: { headers: requestHeaders }
  })

  // 7. Add security headers
  addSecurityHeaders(response, nonce)

  // 8. Remove sensitive headers
  response.headers.delete('X-Powered-By')
  response.headers.delete('Server')

  return response
}

export const config = {
  matcher: [
    // Match all paths except static files
    '/((?!_next/static|_next/image|favicon.ico|.*\\.(?:svg|png|jpg|jpeg|gif|webp)$).*)'
  ]
}
```

### IP Allowlist for Admin Routes

```typescript
// middleware.ts (additional section)

const ADMIN_IPS = new Set([
  '192.168.1.1',
  '10.0.0.1'
])

function checkAdminAccess(ip: string): boolean {
  // In production, check IP allowlist
  if (process.env.NODE_ENV === 'production') {
    return ADMIN_IPS.has(ip)
  }
  return true // Allow in development
}

// In middleware function, add:
// if (pathname.startsWith('/admin')) {
//   if (!checkAdminAccess(ip)) {
//     return new NextResponse('Forbidden', { status: 403 })
//   }
// }
```

---

## 12. Error Handling

### Secure error.tsx

```typescript
// app/error.tsx
'use client'

import { useEffect } from 'react'
import { Button } from '@/components/ui/button'

interface Props {
  error: Error & { digest?: string }
  reset: () => void
}

export default function Error({ error, reset }: Props) {
  useEffect(() => {
    // Log to error reporting service
    // NEVER log full error to console in production
    if (process.env.NODE_ENV === 'development') {
      console.error(error)
    }

    // Send to monitoring (Sentry, etc.)
    // Only send digest, not full stack trace to client-side logging
    reportError(error.digest)
  }, [error])

  return (
    <div className="flex flex-col items-center justify-center min-h-screen p-4">
      <h2 className="text-xl font-semibold mb-4">Something went wrong</h2>
      {/* Never show error.message to users - it might contain sensitive info */}
      <p className="text-muted-foreground mb-4">
        An unexpected error occurred. Please try again.
      </p>
      {error.digest && (
        <p className="text-sm text-muted-foreground mb-4">
          Error ID: {error.digest}
        </p>
      )}
      <Button onClick={reset}>Try again</Button>
    </div>
  )
}

async function reportError(digest?: string) {
  if (!digest) return

  try {
    await fetch('/api/error-report', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ digest, timestamp: Date.now() })
    })
  } catch {
    // Silently fail - don't cause additional errors
  }
}
```

### Global Error Handler

```typescript
// app/global-error.tsx
'use client'

import { useEffect } from 'react'

interface Props {
  error: Error & { digest?: string }
  reset: () => void
}

export default function GlobalError({ error, reset }: Props) {
  useEffect(() => {
    // Log critical error
    console.error('Global error:', error.digest)
  }, [error])

  return (
    <html>
      <body>
        <div className="flex flex-col items-center justify-center min-h-screen p-4">
          <h2 className="text-xl font-semibold mb-4">
            Something went wrong
          </h2>
          <p className="text-gray-600 mb-4">
            We are having trouble loading this page.
          </p>
          {error.digest && (
            <p className="text-sm text-gray-500 mb-4">
              Reference: {error.digest}
            </p>
          )}
          <button
            onClick={reset}
            className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
          >
            Try again
          </button>
        </div>
      </body>
    </html>
  )
}
```

### API Error Responses

```typescript
// lib/api-errors.ts
import { NextResponse } from 'next/server'

// Error codes for client consumption
type ErrorCode =
  | 'VALIDATION_ERROR'
  | 'AUTHENTICATION_REQUIRED'
  | 'PERMISSION_DENIED'
  | 'RESOURCE_NOT_FOUND'
  | 'RATE_LIMIT_EXCEEDED'
  | 'SERVICE_UNAVAILABLE'
  | 'INTERNAL_ERROR'

interface ApiErrorResponse {
  error: {
    code: ErrorCode
    message: string
    requestId?: string
  }
}

// Status codes for each error type
const ERROR_STATUS: Record<ErrorCode, number> = {
  VALIDATION_ERROR: 400,
  AUTHENTICATION_REQUIRED: 401,
  PERMISSION_DENIED: 403,
  RESOURCE_NOT_FOUND: 404,
  RATE_LIMIT_EXCEEDED: 429,
  SERVICE_UNAVAILABLE: 503,
  INTERNAL_ERROR: 500
}

// User-friendly messages (never expose internal details)
const ERROR_MESSAGES: Record<ErrorCode, string> = {
  VALIDATION_ERROR: 'The provided data is invalid',
  AUTHENTICATION_REQUIRED: 'Authentication is required',
  PERMISSION_DENIED: 'You do not have permission to perform this action',
  RESOURCE_NOT_FOUND: 'The requested resource was not found',
  RATE_LIMIT_EXCEEDED: 'Too many requests. Please try again later',
  SERVICE_UNAVAILABLE: 'Service temporarily unavailable',
  INTERNAL_ERROR: 'An unexpected error occurred'
}

export function apiError(
  code: ErrorCode,
  requestId?: string
): NextResponse<ApiErrorResponse> {
  return NextResponse.json(
    {
      error: {
        code,
        message: ERROR_MESSAGES[code],
        requestId
      }
    },
    { status: ERROR_STATUS[code] }
  )
}
```

### Structured Logging with Pino

```typescript
// lib/logger.ts
import pino from 'pino'

// Fields to redact from logs
const REDACT_PATHS = [
  'password',
  'token',
  'authorization',
  'cookie',
  'apiKey',
  'secret',
  'creditCard',
  'ssn',
  '*.password',
  '*.token',
  'req.headers.authorization',
  'req.headers.cookie'
]

export const logger = pino({
  level: process.env.LOG_LEVEL ?? 'info',

  // Redact sensitive fields
  redact: {
    paths: REDACT_PATHS,
    censor: '[REDACTED]'
  },

  // Format based on environment
  transport: process.env.NODE_ENV === 'development'
    ? {
        target: 'pino-pretty',
        options: {
          colorize: true,
          ignore: 'pid,hostname'
        }
      }
    : undefined,

  // Base fields for all logs
  base: {
    env: process.env.NODE_ENV,
    service: 'my-app'
  },

  // Custom serializers
  serializers: {
    err: pino.stdSerializers.err,
    req: (req) => ({
      method: req.method,
      url: req.url,
      // Only include safe headers
      headers: {
        'user-agent': req.headers['user-agent'],
        'content-type': req.headers['content-type']
      }
    }),
    res: (res) => ({
      statusCode: res.statusCode
    })
  }
})

// Child logger for specific contexts
export function createLogger(context: string) {
  return logger.child({ context })
}
```

```typescript
// Usage example
import { createLogger } from '@/lib/logger'

const log = createLogger('auth')

async function login(email: string, password: string) {
  log.info({ email }, 'Login attempt')

  try {
    const user = await authenticate(email, password)
    log.info({ userId: user.id }, 'Login successful')
    return user
  } catch (error) {
    // password will be redacted automatically
    log.error({ email, password, error }, 'Login failed')
    throw error
  }
}
```

---

## 13. Dependency Security

### npm Audit Configuration

```json
{
  "scripts": {
    "audit": "npm audit --audit-level=moderate",
    "audit:fix": "npm audit fix",
    "audit:ci": "npm audit --audit-level=high --production"
  }
}
```

### Dependabot Configuration

```yaml
# .github/dependabot.yml
version: 2
updates:
  # npm dependencies
  - package-ecosystem: "npm"
    directory: "/"
    schedule:
      interval: "weekly"
      day: "monday"
      time: "09:00"
      timezone: "America/Los_Angeles"
    open-pull-requests-limit: 10

    # Group minor and patch updates
    groups:
      production-dependencies:
        dependency-type: "production"
        update-types:
          - "minor"
          - "patch"
      development-dependencies:
        dependency-type: "development"
        update-types:
          - "minor"
          - "patch"

    # Ignore major updates for certain packages (review manually)
    ignore:
      - dependency-name: "next"
        update-types: ["version-update:semver-major"]
      - dependency-name: "react"
        update-types: ["version-update:semver-major"]

    # Labels for PRs
    labels:
      - "dependencies"
      - "security"

    # Reviewers
    reviewers:
      - "security-team"

  # GitHub Actions
  - package-ecosystem: "github-actions"
    directory: "/"
    schedule:
      interval: "weekly"
    labels:
      - "ci"
      - "dependencies"
```

### GitHub Actions Security Workflow

```yaml
# .github/workflows/security.yml
name: Security Checks

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]
  schedule:
    # Run daily at midnight
    - cron: '0 0 * * *'

permissions:
  contents: read
  security-events: write

jobs:
  dependency-audit:
    name: Dependency Audit
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'pnpm'

      - name: Install dependencies
        run: pnpm install --frozen-lockfile

      - name: Run npm audit
        run: pnpm audit --audit-level=high
        continue-on-error: true

      - name: Run Snyk security scan
        uses: snyk/actions/node@master
        env:
          SNYK_TOKEN: ${{ secrets.SNYK_TOKEN }}
        with:
          args: --severity-threshold=high

  codeql:
    name: CodeQL Analysis
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Initialize CodeQL
        uses: github/codeql-action/init@v3
        with:
          languages: javascript-typescript
          queries: security-extended

      - name: Perform CodeQL Analysis
        uses: github/codeql-action/analyze@v3

  secrets-scan:
    name: Secrets Scanning
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: TruffleHog Secret Scan
        uses: trufflesecurity/trufflehog@main
        with:
          extra_args: --only-verified

  lockfile-check:
    name: Lockfile Integrity
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-node@v4
        with:
          node-version: '20'

      - name: Verify lockfile integrity
        run: |
          pnpm install --frozen-lockfile
          git diff --exit-code pnpm-lock.yaml
```

### Supply Chain Best Practices

```typescript
// scripts/check-dependencies.ts
import fs from 'fs'
import path from 'path'
import { spawnSync } from 'child_process'

// List of approved packages (example)
const APPROVED_PACKAGES = new Set([
  'next',
  'react',
  'react-dom',
  '@prisma/client',
  'zod',
  // ... add all approved packages
])

// Check for new dependencies
function checkNewDependencies() {
  const pkg = JSON.parse(
    fs.readFileSync(path.join(process.cwd(), 'package.json'), 'utf-8')
  )

  const allDeps = {
    ...pkg.dependencies,
    ...pkg.devDependencies
  }

  const unapproved: string[] = []

  for (const dep of Object.keys(allDeps)) {
    if (!APPROVED_PACKAGES.has(dep)) {
      unapproved.push(dep)
    }
  }

  if (unapproved.length > 0) {
    console.warn('Unapproved dependencies detected:')
    unapproved.forEach(dep => console.warn(`  - ${dep}`))
    console.warn('\nPlease review and add to approved list if safe.')
    process.exit(1)
  }
}

// Check for known vulnerable packages
function checkVulnerabilities() {
  const result = spawnSync('pnpm', ['audit', '--audit-level=high'], {
    stdio: 'inherit'
  })

  if (result.status !== 0) {
    console.error('Security vulnerabilities detected!')
    process.exit(1)
  }
}

checkNewDependencies()
checkVulnerabilities()
```

---

## 14. Vercel Security

### Vercel Firewall Configuration

```json
{
  "firewall": {
    "rules": [
      {
        "name": "Block known bad IPs",
        "condition": {
          "ip": ["1.2.3.4", "5.6.7.8/24"]
        },
        "action": "deny"
      },
      {
        "name": "Rate limit API",
        "condition": {
          "path": "/api/*"
        },
        "action": "rate_limit",
        "rateLimit": {
          "requests": 100,
          "window": "1m"
        }
      },
      {
        "name": "Challenge suspicious traffic",
        "condition": {
          "ja3": ["malicious-fingerprint"]
        },
        "action": "challenge"
      }
    ]
  }
}
```

### Edge Config for Dynamic Security Rules

```typescript
// lib/edge-config.ts
import { get } from '@vercel/edge-config'

interface SecurityConfig {
  blockedIPs: string[]
  blockedCountries: string[]
  maintenanceMode: boolean
  allowedOrigins: string[]
}

export async function getSecurityConfig(): Promise<SecurityConfig> {
  const config = await get<SecurityConfig>('securityConfig')

  return config ?? {
    blockedIPs: [],
    blockedCountries: [],
    maintenanceMode: false,
    allowedOrigins: []
  }
}
```

```typescript
// middleware.ts
import { getSecurityConfig } from '@/lib/edge-config'
import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'

export async function middleware(request: NextRequest) {
  const config = await getSecurityConfig()
  const ip = request.headers.get('x-forwarded-for')?.split(',')[0]
  const country = request.headers.get('x-vercel-ip-country')

  // Check IP blocklist
  if (ip && config.blockedIPs.includes(ip)) {
    return new NextResponse('Forbidden', { status: 403 })
  }

  // Check country blocklist
  if (country && config.blockedCountries.includes(country)) {
    return new NextResponse('Access not available in your region', { status: 403 })
  }

  // Maintenance mode
  if (config.maintenanceMode && !request.nextUrl.pathname.startsWith('/maintenance')) {
    return NextResponse.redirect(new URL('/maintenance', request.url))
  }

  return NextResponse.next()
}
```

### Deployment Protection

```json
{
  "git": {
    "deploymentEnabled": {
      "main": true,
      "staging": true
    }
  },
  "passwordProtection": {
    "enabled": true,
    "password": "preview-password"
  },
  "trustedIps": [
    {
      "value": "192.168.1.0/24",
      "note": "Office network"
    }
  ]
}
```

### Secure Headers in vercel.json

```json
{
  "headers": [
    {
      "source": "/(.*)",
      "headers": [
        {
          "key": "X-DNS-Prefetch-Control",
          "value": "on"
        },
        {
          "key": "Strict-Transport-Security",
          "value": "max-age=63072000; includeSubDomains; preload"
        },
        {
          "key": "X-Content-Type-Options",
          "value": "nosniff"
        },
        {
          "key": "X-Frame-Options",
          "value": "DENY"
        },
        {
          "key": "X-XSS-Protection",
          "value": "1; mode=block"
        },
        {
          "key": "Referrer-Policy",
          "value": "strict-origin-when-cross-origin"
        },
        {
          "key": "Permissions-Policy",
          "value": "camera=(), microphone=(), geolocation=()"
        }
      ]
    }
  ]
}
```

---

## 15. OWASP Top 10 for Next.js

| # | OWASP Risk | Next.js Mitigation | Priority |
|---|------------|-------------------|----------|
| 1 | Broken Access Control | DAL pattern, Server Action auth, middleware route protection | Critical |
| 2 | Cryptographic Failures | HTTPS (automatic on Vercel), secure cookies, encrypted env vars | Critical |
| 3 | Injection | Zod validation, Prisma ORM, DOMPurify | Critical |
| 4 | Insecure Design | Authorization at data layer, principle of least privilege | High |
| 5 | Security Misconfiguration | Security headers, env validation, CSP | High |
| 6 | Vulnerable Components | Dependabot, npm audit, lockfile integrity | High |
| 7 | Auth Failures | Auth.js with secure config, rate limiting, MFA | Critical |
| 8 | Data Integrity Failures | server-only, taint API, signed cookies | Medium |
| 9 | Logging Failures | Pino with redaction, audit logging | Medium |
| 10 | SSRF | URL validation, allowlists, request validation | High |

### Broken Access Control Prevention

```typescript
// lib/dal.ts - Comprehensive access control
import 'server-only'
import { cache } from 'react'
import { auth } from '@/auth'
import { prisma } from '@/lib/prisma'
import { redirect } from 'next/navigation'

// Always check ownership/membership at data layer
export const getDocument = cache(async (documentId: string) => {
  const session = await auth()
  if (!session?.user) {
    redirect('/login')
  }

  // CRITICAL: Filter by user access, not just document ID
  const document = await prisma.document.findFirst({
    where: {
      id: documentId,
      OR: [
        { ownerId: session.user.id },
        {
          team: {
            members: {
              some: { userId: session.user.id }
            }
          }
        },
        { isPublic: true }
      ]
    }
  })

  // Return null, not a generic error that might leak existence
  return document
})

// Server Action with authorization
export async function deleteDocument(documentId: string) {
  'use server'

  const session = await auth()
  if (!session?.user) {
    throw new Error('Unauthorized')
  }

  // Check ownership (only owner can delete)
  const document = await prisma.document.findFirst({
    where: {
      id: documentId,
      ownerId: session.user.id
    }
  })

  if (!document) {
    // Same error for "not found" and "not authorized"
    // Prevents enumeration attacks
    throw new Error('Document not found')
  }

  await prisma.document.delete({
    where: { id: documentId }
  })
}
```

### SSRF Prevention

```typescript
// lib/url-validator.ts
import 'server-only'

// Allowlist of safe domains
const ALLOWED_DOMAINS = new Set([
  'api.example.com',
  'cdn.example.com',
  'storage.googleapis.com'
])

// Blocked IP ranges (private networks, localhost, etc.)
const BLOCKED_IP_RANGES = [
  /^127\./,
  /^10\./,
  /^172\.(1[6-9]|2[0-9]|3[0-1])\./,
  /^192\.168\./,
  /^0\./,
  /^169\.254\./,  // Link-local
  /^::1$/,
  /^fc00:/,
  /^fe80:/
]

export function validateUrl(urlString: string): URL | null {
  try {
    const url = new URL(urlString)

    // Only allow HTTPS
    if (url.protocol !== 'https:') {
      return null
    }

    // Check against allowlist
    if (!ALLOWED_DOMAINS.has(url.hostname)) {
      return null
    }

    // Block IP addresses entirely
    const ipPattern = /^(\d{1,3}\.){3}\d{1,3}$/
    if (ipPattern.test(url.hostname)) {
      return null
    }

    return url
  } catch {
    return null
  }
}

// Safe fetch wrapper
export async function safeFetch(
  urlString: string,
  options?: RequestInit
): Promise<Response> {
  const url = validateUrl(urlString)

  if (!url) {
    throw new Error('Invalid or disallowed URL')
  }

  // Additional headers to prevent SSRF via redirects
  const response = await fetch(url, {
    ...options,
    redirect: 'error',  // Don't follow redirects
    headers: {
      ...options?.headers,
      'User-Agent': 'MyApp/1.0'
    }
  })

  return response
}
```

```typescript
// app/api/fetch-metadata/route.ts
import { NextRequest, NextResponse } from 'next/server'
import { safeFetch, validateUrl } from '@/lib/url-validator'
import { z } from 'zod'

const schema = z.object({
  url: z.string().url()
})

export async function POST(request: NextRequest) {
  const body = await request.json()
  const result = schema.safeParse(body)

  if (!result.success) {
    return NextResponse.json({ error: 'Invalid URL' }, { status: 400 })
  }

  // Validate URL before fetching
  const validatedUrl = validateUrl(result.data.url)
  if (!validatedUrl) {
    return NextResponse.json(
      { error: 'URL not allowed' },
      { status: 400 }
    )
  }

  try {
    const response = await safeFetch(validatedUrl.toString())
    const data = await response.json()

    return NextResponse.json({ data })
  } catch (error) {
    return NextResponse.json(
      { error: 'Failed to fetch URL' },
      { status: 500 }
    )
  }
}
```

---

## 16. Security Audit Checklist

Use this checklist before deploying to production:

### Authentication
- [ ] Auth.js configured with secure session strategy
- [ ] Passwords hashed with bcrypt (cost factor >= 10)
- [ ] Session cookies are httpOnly, secure, sameSite
- [ ] CSRF protection enabled
- [ ] Rate limiting on login endpoints
- [ ] Account lockout after failed attempts
- [ ] Password reset tokens are single-use and time-limited
- [ ] OAuth state parameter validated

### Authorization
- [ ] DAL pattern implemented for all data access
- [ ] Authorization checks in every Server Action
- [ ] Middleware protects sensitive routes
- [ ] Role-based access control implemented
- [ ] Resource ownership verified before access
- [ ] Same error returned for "not found" and "not authorized"

### Input Validation
- [ ] Zod schemas for all API routes
- [ ] Zod schemas for all Server Actions
- [ ] File uploads validate type, size, and magic bytes
- [ ] SQL injection prevented (ORM/parameterized queries)
- [ ] XSS prevented (DOMPurify, React auto-escaping)
- [ ] Path traversal prevented (no user input in file paths)

### Security Headers
- [ ] CSP implemented with nonces
- [ ] HSTS enabled with preload
- [ ] X-Content-Type-Options: nosniff
- [ ] X-Frame-Options: DENY
- [ ] Referrer-Policy configured
- [ ] Permissions-Policy restricts unused APIs

### Data Protection
- [ ] Sensitive data marked with server-only
- [ ] DTOs used to minimize client data
- [ ] Environment variables validated at startup
- [ ] No secrets in NEXT_PUBLIC_ variables
- [ ] Encryption at rest for sensitive data
- [ ] Cookies encrypted for sensitive values

### API Security
- [ ] Authentication required for protected endpoints
- [ ] Rate limiting implemented
- [ ] CORS properly configured
- [ ] Error responses don't leak internal details
- [ ] Request size limits configured
- [ ] API versioning implemented

### Server Actions
- [ ] CSRF protection (automatic)
- [ ] Input validation with Zod
- [ ] Authorization checks
- [ ] Rate limiting
- [ ] Closure values treated as untrusted

### Dependencies
- [ ] npm audit shows no high/critical vulnerabilities
- [ ] Dependabot or similar enabled
- [ ] Lockfile committed and verified
- [ ] No dependencies from untrusted sources
- [ ] CodeQL or similar scanning enabled

### Error Handling
- [ ] Production errors don't expose stack traces
- [ ] Structured logging with sensitive field redaction
- [ ] Error IDs returned to users for support
- [ ] Global error boundaries implemented

### Deployment
- [ ] HTTPS enforced
- [ ] Preview deployments password protected
- [ ] Production environment variables secured
- [ ] Firewall rules configured
- [ ] Monitoring and alerting enabled
- [ ] Incident response plan documented

---

## Quick Reference Commands

```bash
# Security audit
pnpm audit

# Update vulnerable packages
pnpm audit fix

# Check for secrets in code
npx trufflehog git file://. --only-verified

# Test CSP headers
curl -I https://your-site.com | grep -i content-security

# Check security headers
npx is-website-vulnerable https://your-site.com
```

---

## Resources

- [Next.js Security Documentation](https://nextjs.org/docs/app/building-your-application/authentication)
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [Auth.js Documentation](https://authjs.dev/)
- [Vercel Security](https://vercel.com/docs/security)
- [MDN Web Security](https://developer.mozilla.org/en-US/docs/Web/Security)
