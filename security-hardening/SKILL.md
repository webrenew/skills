# Security Hardening

> Next.js security hardening, OWASP compliance, and production security checklist

## Metadata

- **Name**: security-hardening
- **Version**: 1.0.0
- **Author**: webrenew
- **Tags**: nextjs, security, owasp, csp, authentication, authorization, xss, csrf, headers

## When to Use

This skill should be used when:
- Hardening a Next.js application for production deployment
- Configuring security headers (CSP, HSTS, X-Frame-Options, Permissions-Policy)
- Implementing authentication and authorization (Auth.js, middleware, RBAC)
- Securing API routes and Server Actions (input validation, rate limiting, CORS)
- Preventing data exposure from Server Components to Client Components
- Setting up dependency security scanning (npm audit, Snyk, Dependabot)
- Reviewing OWASP Top 10 vulnerabilities specific to Next.js
- Configuring Vercel-specific security (Firewall, WAF, deployment protection)

## Summary

Comprehensive Next.js security hardening guide covering security headers and CSP with nonces, authentication patterns with Auth.js v5, authorization via Data Access Layer and middleware, Server Action security (CSRF, validation, rate limiting), API route protection, input validation with Zod, XSS and SQL injection prevention, environment variable management, data exposure prevention (server-only, taint API, DTOs), cookie security, middleware-based rate limiting and bot detection, secure error handling, dependency auditing, Vercel security features, OWASP Top 10 mapped to Next.js, and pre-deployment security checklists.
