# WCAG 2.2 Accessibility Guide for Next.js Applications

A comprehensive reference for AI agents auditing or implementing web accessibility in Next.js applications. This guide covers WCAG 2.2 Level AA compliance with practical, copy-paste ready patterns.

---

## Table of Contents

1. [Semantic HTML](#1-semantic-html)
2. [ARIA Patterns](#2-aria-patterns)
3. [Keyboard Navigation](#3-keyboard-navigation)
4. [Color & Contrast](#4-color--contrast)
5. [Accessible Forms](#5-accessible-forms)
6. [Images & Media](#6-images--media)
7. [Dynamic Content](#7-dynamic-content)
8. [Next.js Specific](#8-nextjs-specific)
9. [Testing Tools & Workflow](#9-testing-tools--workflow)
10. [Component Library Patterns](#10-component-library-patterns)
11. [Legal Compliance](#11-legal-compliance)
12. [Common Mistakes](#12-common-mistakes)
13. [Audit Checklist](#13-audit-checklist)

---

## 1. Semantic HTML

Semantic HTML provides built-in accessibility without additional ARIA. Always prefer semantic elements over ARIA-enhanced divs.

### Heading Hierarchy

Headings must follow a logical hierarchy without skipping levels. Each page should have exactly one `<h1>`.

```tsx
// app/products/[id]/page.tsx

export default function ProductPage({ params }: { params: { id: string } }) {
  return (
    <main>
      {/* Only one h1 per page */}
      <h1>Product Name</h1>

      <section aria-labelledby="description-heading">
        <h2 id="description-heading">Description</h2>
        <p>Product description text...</p>

        {/* h3 correctly follows h2 */}
        <h3>Features</h3>
        <ul>
          <li>Feature one</li>
          <li>Feature two</li>
        </ul>

        <h3>Specifications</h3>
        <dl>
          <dt>Weight</dt>
          <dd>2.5 kg</dd>
        </dl>
      </section>

      <section aria-labelledby="reviews-heading">
        <h2 id="reviews-heading">Customer Reviews</h2>
        {/* Content */}
      </section>
    </main>
  )
}
```

### Landmark Regions

Landmarks help screen reader users navigate the page structure.

```tsx
// components/layout/page-layout.tsx

interface PageLayoutProps {
  children: React.ReactNode
}

export function PageLayout({ children }: PageLayoutProps) {
  return (
    <>
      {/* Skip link - first focusable element */}
      <a
        href="#main-content"
        className="sr-only focus:not-sr-only focus:absolute focus:top-4 focus:left-4 focus:z-50 focus:px-4 focus:py-2 focus:bg-white focus:text-black focus:rounded"
      >
        Skip to main content
      </a>

      <header role="banner">
        <nav aria-label="Main navigation">
          <ul>
            <li><a href="/">Home</a></li>
            <li><a href="/products">Products</a></li>
            <li><a href="/about">About</a></li>
          </ul>
        </nav>
      </header>

      <main id="main-content" role="main" tabIndex={-1}>
        {children}
      </main>

      <aside aria-label="Related content">
        {/* Complementary content */}
      </aside>

      <footer role="contentinfo">
        <nav aria-label="Footer navigation">
          {/* Footer links */}
        </nav>
        <p>&copy; 2024 Company Name</p>
      </footer>
    </>
  )
}
```

### When to Use Semantic Elements vs Divs

| Use Case | Element | NOT |
|----------|---------|-----|
| Page sections | `<section>`, `<article>` | `<div>` |
| Navigation | `<nav>` | `<div class="nav">` |
| Lists | `<ul>`, `<ol>`, `<dl>` | Divs with bullets |
| Buttons | `<button>` | `<div onClick>` |
| Links | `<a href>` | `<span onClick>` |
| Emphasis | `<strong>`, `<em>` | `<span class="bold">` |
| Time | `<time datetime>` | `<span>` |
| Quotes | `<blockquote>`, `<q>` | `<div>` with quotes |
| Code | `<code>`, `<pre>` | `<div class="code">` |
| Tables | `<table>`, `<th>`, `<td>` | Divs in grid layout |

### Sectioning Content

```tsx
// components/blog/article-card.tsx

interface ArticleCardProps {
  title: string
  author: string
  date: string
  excerpt: string
  href: string
}

export function ArticleCard({ title, author, date, excerpt, href }: ArticleCardProps) {
  return (
    // <article> is appropriate for self-contained, independently distributable content
    <article className="border rounded-lg p-4">
      <header>
        <h2>
          <a href={href}>{title}</a>
        </h2>
        <p className="text-sm text-gray-600">
          By <address className="inline not-italic">{author}</address>
          {' on '}
          <time dateTime={date}>
            {new Date(date).toLocaleDateString('en-US', {
              year: 'numeric',
              month: 'long',
              day: 'numeric'
            })}
          </time>
        </p>
      </header>
      <p>{excerpt}</p>
    </article>
  )
}
```

---

## 2. ARIA Patterns

ARIA (Accessible Rich Internet Applications) should only be used when semantic HTML is insufficient. Follow the rules of ARIA:

1. **Don't use ARIA if you can use semantic HTML**
2. **Don't change native semantics** unless absolutely necessary
3. **All interactive ARIA controls must be keyboard accessible**
4. **Don't use `role="presentation"` or `aria-hidden="true"` on focusable elements**
5. **All interactive elements must have an accessible name**

### Dialog Pattern with shadcn/ui

```tsx
// components/ui/accessible-dialog.tsx

import * as React from 'react'
import * as DialogPrimitive from '@radix-ui/react-dialog'
import { X } from 'lucide-react'
import { cn } from '@/lib/utils'

const Dialog = DialogPrimitive.Root
const DialogTrigger = DialogPrimitive.Trigger
const DialogPortal = DialogPrimitive.Portal
const DialogClose = DialogPrimitive.Close

const DialogOverlay = React.forwardRef<
  React.ElementRef<typeof DialogPrimitive.Overlay>,
  React.ComponentPropsWithoutRef<typeof DialogPrimitive.Overlay>
>(({ className, ...props }, ref) => (
  <DialogPrimitive.Overlay
    ref={ref}
    className={cn(
      'fixed inset-0 z-50 bg-black/80 data-[state=open]:animate-in data-[state=closed]:animate-out',
      className
    )}
    {...props}
  />
))
DialogOverlay.displayName = DialogPrimitive.Overlay.displayName

const DialogContent = React.forwardRef<
  React.ElementRef<typeof DialogPrimitive.Content>,
  React.ComponentPropsWithoutRef<typeof DialogPrimitive.Content>
>(({ className, children, ...props }, ref) => (
  <DialogPortal>
    <DialogOverlay />
    <DialogPrimitive.Content
      ref={ref}
      className={cn(
        'fixed left-[50%] top-[50%] z-50 translate-x-[-50%] translate-y-[-50%]',
        'w-full max-w-lg rounded-lg bg-white p-6 shadow-lg',
        'focus:outline-none',
        className
      )}
      // Trap focus within dialog
      onOpenAutoFocus={(e) => {
        // Focus the close button by default, or first focusable element
        e.preventDefault()
        const closeButton = e.currentTarget.querySelector('[data-dialog-close]')
        if (closeButton instanceof HTMLElement) {
          closeButton.focus()
        }
      }}
      {...props}
    >
      {children}
      <DialogPrimitive.Close
        data-dialog-close
        className="absolute right-4 top-4 rounded-sm opacity-70 hover:opacity-100 focus:outline-none focus:ring-2 focus:ring-offset-2"
        aria-label="Close dialog"
      >
        <X className="h-4 w-4" aria-hidden="true" />
      </DialogPrimitive.Close>
    </DialogPrimitive.Content>
  </DialogPortal>
))
DialogContent.displayName = DialogPrimitive.Content.displayName

// REQUIRED: DialogTitle provides accessible name
const DialogTitle = React.forwardRef<
  React.ElementRef<typeof DialogPrimitive.Title>,
  React.ComponentPropsWithoutRef<typeof DialogPrimitive.Title>
>(({ className, ...props }, ref) => (
  <DialogPrimitive.Title
    ref={ref}
    className={cn('text-lg font-semibold', className)}
    {...props}
  />
))
DialogTitle.displayName = DialogPrimitive.Title.displayName

// REQUIRED: DialogDescription provides accessible description
const DialogDescription = React.forwardRef<
  React.ElementRef<typeof DialogPrimitive.Description>,
  React.ComponentPropsWithoutRef<typeof DialogPrimitive.Description>
>(({ className, ...props }, ref) => (
  <DialogPrimitive.Description
    ref={ref}
    className={cn('text-sm text-gray-600', className)}
    {...props}
  />
))
DialogDescription.displayName = DialogPrimitive.Description.displayName

export {
  Dialog,
  DialogPortal,
  DialogOverlay,
  DialogClose,
  DialogTrigger,
  DialogContent,
  DialogTitle,
  DialogDescription,
}

// Usage Example
export function ConfirmDeleteDialog() {
  return (
    <Dialog>
      <DialogTrigger asChild>
        <button className="px-4 py-2 bg-red-600 text-white rounded">
          Delete Item
        </button>
      </DialogTrigger>
      <DialogContent>
        {/* DialogTitle is REQUIRED for accessibility */}
        <DialogTitle>Confirm Deletion</DialogTitle>
        {/* DialogDescription is REQUIRED for accessibility */}
        <DialogDescription>
          Are you sure you want to delete this item? This action cannot be undone.
        </DialogDescription>
        <div className="mt-4 flex justify-end gap-2">
          <DialogClose asChild>
            <button className="px-4 py-2 border rounded">Cancel</button>
          </DialogClose>
          <button
            className="px-4 py-2 bg-red-600 text-white rounded"
            onClick={() => {/* handle delete */}}
          >
            Delete
          </button>
        </div>
      </DialogContent>
    </Dialog>
  )
}
```

### Tabs Pattern

```tsx
// components/ui/accessible-tabs.tsx

import * as React from 'react'
import * as TabsPrimitive from '@radix-ui/react-tabs'
import { cn } from '@/lib/utils'

const Tabs = TabsPrimitive.Root

const TabsList = React.forwardRef<
  React.ElementRef<typeof TabsPrimitive.List>,
  React.ComponentPropsWithoutRef<typeof TabsPrimitive.List>
>(({ className, ...props }, ref) => (
  <TabsPrimitive.List
    ref={ref}
    className={cn(
      'inline-flex items-center justify-center rounded-lg bg-gray-100 p-1',
      className
    )}
    // aria-label should be provided when using this component
    {...props}
  />
))
TabsList.displayName = TabsPrimitive.List.displayName

const TabsTrigger = React.forwardRef<
  React.ElementRef<typeof TabsPrimitive.Trigger>,
  React.ComponentPropsWithoutRef<typeof TabsPrimitive.Trigger>
>(({ className, ...props }, ref) => (
  <TabsPrimitive.Trigger
    ref={ref}
    className={cn(
      'inline-flex items-center justify-center px-3 py-1.5 text-sm font-medium',
      'rounded-md transition-all',
      'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-offset-2',
      'disabled:pointer-events-none disabled:opacity-50',
      'data-[state=active]:bg-white data-[state=active]:shadow',
      className
    )}
    {...props}
  />
))
TabsTrigger.displayName = TabsPrimitive.Trigger.displayName

const TabsContent = React.forwardRef<
  React.ElementRef<typeof TabsPrimitive.Content>,
  React.ComponentPropsWithoutRef<typeof TabsPrimitive.Content>
>(({ className, ...props }, ref) => (
  <TabsPrimitive.Content
    ref={ref}
    className={cn(
      'mt-2 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-offset-2',
      className
    )}
    // tabIndex={0} allows the panel to receive focus for keyboard users
    tabIndex={0}
    {...props}
  />
))
TabsContent.displayName = TabsPrimitive.Content.displayName

export { Tabs, TabsList, TabsTrigger, TabsContent }

// Usage Example
export function ProductTabs() {
  return (
    <Tabs defaultValue="description">
      <TabsList aria-label="Product information">
        <TabsTrigger value="description">Description</TabsTrigger>
        <TabsTrigger value="specifications">Specifications</TabsTrigger>
        <TabsTrigger value="reviews">Reviews</TabsTrigger>
      </TabsList>
      <TabsContent value="description">
        <h3>Product Description</h3>
        <p>Detailed product description...</p>
      </TabsContent>
      <TabsContent value="specifications">
        <h3>Technical Specifications</h3>
        <dl>
          <dt>Dimensions</dt>
          <dd>10 x 5 x 3 inches</dd>
        </dl>
      </TabsContent>
      <TabsContent value="reviews">
        <h3>Customer Reviews</h3>
        <p>Reviews content...</p>
      </TabsContent>
    </Tabs>
  )
}
```

### Accordion Pattern

```tsx
// components/ui/accessible-accordion.tsx

import * as React from 'react'
import * as AccordionPrimitive from '@radix-ui/react-accordion'
import { ChevronDown } from 'lucide-react'
import { cn } from '@/lib/utils'

const Accordion = AccordionPrimitive.Root

const AccordionItem = React.forwardRef<
  React.ElementRef<typeof AccordionPrimitive.Item>,
  React.ComponentPropsWithoutRef<typeof AccordionPrimitive.Item>
>(({ className, ...props }, ref) => (
  <AccordionPrimitive.Item
    ref={ref}
    className={cn('border-b', className)}
    {...props}
  />
))
AccordionItem.displayName = 'AccordionItem'

const AccordionTrigger = React.forwardRef<
  React.ElementRef<typeof AccordionPrimitive.Trigger>,
  React.ComponentPropsWithoutRef<typeof AccordionPrimitive.Trigger>
>(({ className, children, ...props }, ref) => (
  <AccordionPrimitive.Header className="flex">
    <AccordionPrimitive.Trigger
      ref={ref}
      className={cn(
        'flex flex-1 items-center justify-between py-4 font-medium',
        'transition-all hover:underline',
        'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-offset-2',
        '[&[data-state=open]>svg]:rotate-180',
        className
      )}
      {...props}
    >
      {children}
      <ChevronDown
        className="h-4 w-4 shrink-0 transition-transform duration-200"
        aria-hidden="true"
      />
    </AccordionPrimitive.Trigger>
  </AccordionPrimitive.Header>
))
AccordionTrigger.displayName = AccordionPrimitive.Trigger.displayName

const AccordionContent = React.forwardRef<
  React.ElementRef<typeof AccordionPrimitive.Content>,
  React.ComponentPropsWithoutRef<typeof AccordionPrimitive.Content>
>(({ className, children, ...props }, ref) => (
  <AccordionPrimitive.Content
    ref={ref}
    className="overflow-hidden text-sm transition-all data-[state=closed]:animate-accordion-up data-[state=open]:animate-accordion-down"
    {...props}
  >
    <div className={cn('pb-4 pt-0', className)}>{children}</div>
  </AccordionPrimitive.Content>
))
AccordionContent.displayName = AccordionPrimitive.Content.displayName

export { Accordion, AccordionItem, AccordionTrigger, AccordionContent }

// Usage Example
export function FAQAccordion() {
  return (
    <Accordion type="single" collapsible>
      <AccordionItem value="item-1">
        <AccordionTrigger>What is your return policy?</AccordionTrigger>
        <AccordionContent>
          We offer a 30-day return policy for all unused items in original packaging.
        </AccordionContent>
      </AccordionItem>
      <AccordionItem value="item-2">
        <AccordionTrigger>How long does shipping take?</AccordionTrigger>
        <AccordionContent>
          Standard shipping takes 5-7 business days. Express shipping is available.
        </AccordionContent>
      </AccordionItem>
    </Accordion>
  )
}
```

### Menu Pattern

```tsx
// components/ui/accessible-dropdown-menu.tsx

import * as React from 'react'
import * as DropdownMenuPrimitive from '@radix-ui/react-dropdown-menu'
import { Check, ChevronRight } from 'lucide-react'
import { cn } from '@/lib/utils'

const DropdownMenu = DropdownMenuPrimitive.Root
const DropdownMenuTrigger = DropdownMenuPrimitive.Trigger
const DropdownMenuGroup = DropdownMenuPrimitive.Group
const DropdownMenuSub = DropdownMenuPrimitive.Sub
const DropdownMenuRadioGroup = DropdownMenuPrimitive.RadioGroup

const DropdownMenuContent = React.forwardRef<
  React.ElementRef<typeof DropdownMenuPrimitive.Content>,
  React.ComponentPropsWithoutRef<typeof DropdownMenuPrimitive.Content>
>(({ className, sideOffset = 4, ...props }, ref) => (
  <DropdownMenuPrimitive.Portal>
    <DropdownMenuPrimitive.Content
      ref={ref}
      sideOffset={sideOffset}
      className={cn(
        'z-50 min-w-[8rem] overflow-hidden rounded-md border bg-white p-1 shadow-md',
        'data-[state=open]:animate-in data-[state=closed]:animate-out',
        className
      )}
      {...props}
    />
  </DropdownMenuPrimitive.Portal>
))
DropdownMenuContent.displayName = DropdownMenuPrimitive.Content.displayName

const DropdownMenuItem = React.forwardRef<
  React.ElementRef<typeof DropdownMenuPrimitive.Item>,
  React.ComponentPropsWithoutRef<typeof DropdownMenuPrimitive.Item> & {
    inset?: boolean
  }
>(({ className, inset, ...props }, ref) => (
  <DropdownMenuPrimitive.Item
    ref={ref}
    className={cn(
      'relative flex cursor-default select-none items-center rounded-sm px-2 py-1.5 text-sm outline-none',
      'focus:bg-gray-100 focus:text-gray-900',
      'data-[disabled]:pointer-events-none data-[disabled]:opacity-50',
      inset && 'pl-8',
      className
    )}
    {...props}
  />
))
DropdownMenuItem.displayName = DropdownMenuPrimitive.Item.displayName

const DropdownMenuCheckboxItem = React.forwardRef<
  React.ElementRef<typeof DropdownMenuPrimitive.CheckboxItem>,
  React.ComponentPropsWithoutRef<typeof DropdownMenuPrimitive.CheckboxItem>
>(({ className, children, checked, ...props }, ref) => (
  <DropdownMenuPrimitive.CheckboxItem
    ref={ref}
    className={cn(
      'relative flex cursor-default select-none items-center rounded-sm py-1.5 pl-8 pr-2 text-sm outline-none',
      'focus:bg-gray-100 focus:text-gray-900',
      'data-[disabled]:pointer-events-none data-[disabled]:opacity-50',
      className
    )}
    checked={checked}
    {...props}
  >
    <span className="absolute left-2 flex h-3.5 w-3.5 items-center justify-center">
      <DropdownMenuPrimitive.ItemIndicator>
        <Check className="h-4 w-4" aria-hidden="true" />
      </DropdownMenuPrimitive.ItemIndicator>
    </span>
    {children}
  </DropdownMenuPrimitive.CheckboxItem>
))
DropdownMenuCheckboxItem.displayName = DropdownMenuPrimitive.CheckboxItem.displayName

const DropdownMenuLabel = React.forwardRef<
  React.ElementRef<typeof DropdownMenuPrimitive.Label>,
  React.ComponentPropsWithoutRef<typeof DropdownMenuPrimitive.Label> & {
    inset?: boolean
  }
>(({ className, inset, ...props }, ref) => (
  <DropdownMenuPrimitive.Label
    ref={ref}
    className={cn(
      'px-2 py-1.5 text-sm font-semibold',
      inset && 'pl-8',
      className
    )}
    {...props}
  />
))
DropdownMenuLabel.displayName = DropdownMenuPrimitive.Label.displayName

const DropdownMenuSeparator = React.forwardRef<
  React.ElementRef<typeof DropdownMenuPrimitive.Separator>,
  React.ComponentPropsWithoutRef<typeof DropdownMenuPrimitive.Separator>
>(({ className, ...props }, ref) => (
  <DropdownMenuPrimitive.Separator
    ref={ref}
    className={cn('-mx-1 my-1 h-px bg-gray-200', className)}
    {...props}
  />
))
DropdownMenuSeparator.displayName = DropdownMenuPrimitive.Separator.displayName

export {
  DropdownMenu,
  DropdownMenuTrigger,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuCheckboxItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuGroup,
  DropdownMenuSub,
  DropdownMenuRadioGroup,
}

// Usage Example
export function UserMenu() {
  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <button
          className="flex items-center gap-2 rounded-full p-2 hover:bg-gray-100"
          aria-label="User menu"
        >
          <span className="sr-only">Open user menu</span>
          <img
            src="/avatar.jpg"
            alt=""
            className="h-8 w-8 rounded-full"
            aria-hidden="true"
          />
        </button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end">
        <DropdownMenuLabel>My Account</DropdownMenuLabel>
        <DropdownMenuSeparator />
        <DropdownMenuItem>Profile</DropdownMenuItem>
        <DropdownMenuItem>Settings</DropdownMenuItem>
        <DropdownMenuItem>Billing</DropdownMenuItem>
        <DropdownMenuSeparator />
        <DropdownMenuItem>Log out</DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>
  )
}
```

### Combobox Pattern (Autocomplete)

```tsx
// components/ui/accessible-combobox.tsx

'use client'

import * as React from 'react'
import { useCombobox } from 'downshift'
import { cn } from '@/lib/utils'

interface ComboboxOption {
  value: string
  label: string
}

interface ComboboxProps {
  options: ComboboxOption[]
  placeholder?: string
  label: string
  onChange?: (value: string | null) => void
}

export function Combobox({ options, placeholder, label, onChange }: ComboboxProps) {
  const [inputItems, setInputItems] = React.useState(options)

  const {
    isOpen,
    getToggleButtonProps,
    getLabelProps,
    getMenuProps,
    getInputProps,
    highlightedIndex,
    getItemProps,
    selectedItem,
  } = useCombobox({
    items: inputItems,
    itemToString: (item) => item?.label ?? '',
    onInputValueChange: ({ inputValue }) => {
      setInputItems(
        options.filter((item) =>
          item.label.toLowerCase().includes(inputValue?.toLowerCase() ?? '')
        )
      )
    },
    onSelectedItemChange: ({ selectedItem }) => {
      onChange?.(selectedItem?.value ?? null)
    },
  })

  return (
    <div className="relative">
      <label {...getLabelProps()} className="block text-sm font-medium mb-1">
        {label}
      </label>
      <div className="relative">
        <input
          {...getInputProps()}
          placeholder={placeholder}
          className={cn(
            'w-full rounded-md border border-gray-300 px-3 py-2 pr-10',
            'focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500'
          )}
        />
        <button
          {...getToggleButtonProps()}
          aria-label="toggle menu"
          className="absolute right-2 top-1/2 -translate-y-1/2"
          type="button"
        >
          <svg
            className="h-5 w-5 text-gray-400"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
            aria-hidden="true"
          >
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
          </svg>
        </button>
      </div>
      <ul
        {...getMenuProps()}
        className={cn(
          'absolute z-10 mt-1 max-h-60 w-full overflow-auto rounded-md bg-white shadow-lg',
          'border border-gray-200',
          !isOpen && 'hidden'
        )}
      >
        {isOpen &&
          inputItems.map((item, index) => (
            <li
              key={item.value}
              {...getItemProps({ item, index })}
              className={cn(
                'cursor-pointer px-3 py-2',
                highlightedIndex === index && 'bg-blue-100',
                selectedItem?.value === item.value && 'font-semibold'
              )}
            >
              {item.label}
            </li>
          ))}
        {isOpen && inputItems.length === 0 && (
          <li className="px-3 py-2 text-gray-500">No results found</li>
        )}
      </ul>
    </div>
  )
}
```

### Live Regions

Live regions announce dynamic content changes to screen readers.

```tsx
// components/ui/live-region.tsx

'use client'

import * as React from 'react'

interface LiveRegionProps {
  /** 'polite' waits for user to finish, 'assertive' interrupts immediately */
  politeness?: 'polite' | 'assertive'
  /** Content to announce */
  children: React.ReactNode
  /** Optional: clear announcement after delay */
  clearAfter?: number
}

export function LiveRegion({
  politeness = 'polite',
  children,
  clearAfter
}: LiveRegionProps) {
  const [announcement, setAnnouncement] = React.useState(children)

  React.useEffect(() => {
    setAnnouncement(children)

    if (clearAfter) {
      const timer = setTimeout(() => setAnnouncement(''), clearAfter)
      return () => clearTimeout(timer)
    }
  }, [children, clearAfter])

  return (
    <div
      role="status"
      aria-live={politeness}
      aria-atomic="true"
      className="sr-only"
    >
      {announcement}
    </div>
  )
}

// Usage Example
export function SearchResults({ count, query }: { count: number; query: string }) {
  return (
    <>
      <LiveRegion politeness="polite">
        {count} results found for "{query}"
      </LiveRegion>
      {/* Visual results display */}
    </>
  )
}

// Assertive announcement for errors
export function ErrorAnnouncement({ error }: { error: string | null }) {
  return (
    <div
      role="alert"
      aria-live="assertive"
      className="sr-only"
    >
      {error}
    </div>
  )
}
```

---

## 3. Keyboard Navigation

All interactive elements must be keyboard accessible. Users should be able to navigate using Tab, Shift+Tab, Enter, Space, and arrow keys.

### Focus Management

```tsx
// hooks/use-focus-management.ts

'use client'

import * as React from 'react'

/**
 * Returns focus to the trigger element when a component closes
 */
export function useFocusReturn(isOpen: boolean) {
  const triggerRef = React.useRef<HTMLElement | null>(null)

  React.useEffect(() => {
    if (isOpen) {
      // Store the currently focused element
      triggerRef.current = document.activeElement as HTMLElement
    } else if (triggerRef.current) {
      // Return focus when closed
      triggerRef.current.focus()
      triggerRef.current = null
    }
  }, [isOpen])
}

/**
 * Traps focus within a container element
 */
export function useFocusTrap(containerRef: React.RefObject<HTMLElement>, isActive: boolean) {
  React.useEffect(() => {
    if (!isActive || !containerRef.current) return

    const container = containerRef.current
    const focusableElements = container.querySelectorAll<HTMLElement>(
      'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
    )
    const firstElement = focusableElements[0]
    const lastElement = focusableElements[focusableElements.length - 1]

    function handleKeyDown(e: KeyboardEvent) {
      if (e.key !== 'Tab') return

      if (e.shiftKey) {
        if (document.activeElement === firstElement) {
          e.preventDefault()
          lastElement?.focus()
        }
      } else {
        if (document.activeElement === lastElement) {
          e.preventDefault()
          firstElement?.focus()
        }
      }
    }

    // Focus first element when trap activates
    firstElement?.focus()

    container.addEventListener('keydown', handleKeyDown)
    return () => container.removeEventListener('keydown', handleKeyDown)
  }, [containerRef, isActive])
}
```

### Skip Links

```tsx
// components/layout/skip-links.tsx

export function SkipLinks() {
  return (
    <div className="skip-links">
      <a
        href="#main-content"
        className="sr-only focus:not-sr-only focus:absolute focus:top-4 focus:left-4 focus:z-[100] focus:px-4 focus:py-2 focus:bg-white focus:text-black focus:rounded focus:shadow-lg focus:ring-2 focus:ring-blue-500"
      >
        Skip to main content
      </a>
      <a
        href="#main-navigation"
        className="sr-only focus:not-sr-only focus:absolute focus:top-4 focus:left-48 focus:z-[100] focus:px-4 focus:py-2 focus:bg-white focus:text-black focus:rounded focus:shadow-lg focus:ring-2 focus:ring-blue-500"
      >
        Skip to navigation
      </a>
    </div>
  )
}

// In layout.tsx
export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <SkipLinks />
        <nav id="main-navigation" aria-label="Main">
          {/* Navigation content */}
        </nav>
        <main id="main-content" tabIndex={-1}>
          {children}
        </main>
      </body>
    </html>
  )
}
```

### Roving Tabindex Pattern

For composite widgets like toolbars, tab lists, and menus, use roving tabindex so only one element is in the tab order at a time.

```tsx
// components/ui/toolbar.tsx

'use client'

import * as React from 'react'

interface ToolbarProps {
  children: React.ReactNode
  'aria-label': string
}

export function Toolbar({ children, 'aria-label': ariaLabel }: ToolbarProps) {
  const toolbarRef = React.useRef<HTMLDivElement>(null)
  const [focusedIndex, setFocusedIndex] = React.useState(0)

  const handleKeyDown = (e: React.KeyboardEvent) => {
    const items = toolbarRef.current?.querySelectorAll<HTMLElement>(
      'button:not([disabled]), [role="button"]:not([disabled])'
    )
    if (!items) return

    const itemCount = items.length
    let newIndex = focusedIndex

    switch (e.key) {
      case 'ArrowRight':
      case 'ArrowDown':
        e.preventDefault()
        newIndex = (focusedIndex + 1) % itemCount
        break
      case 'ArrowLeft':
      case 'ArrowUp':
        e.preventDefault()
        newIndex = (focusedIndex - 1 + itemCount) % itemCount
        break
      case 'Home':
        e.preventDefault()
        newIndex = 0
        break
      case 'End':
        e.preventDefault()
        newIndex = itemCount - 1
        break
      default:
        return
    }

    setFocusedIndex(newIndex)
    items[newIndex]?.focus()
  }

  return (
    <div
      ref={toolbarRef}
      role="toolbar"
      aria-label={ariaLabel}
      onKeyDown={handleKeyDown}
      className="flex items-center gap-1 p-1 border rounded"
    >
      {React.Children.map(children, (child, index) => {
        if (React.isValidElement(child)) {
          return React.cloneElement(child as React.ReactElement<any>, {
            tabIndex: index === focusedIndex ? 0 : -1,
          })
        }
        return child
      })}
    </div>
  )
}

// Usage
export function TextFormattingToolbar() {
  return (
    <Toolbar aria-label="Text formatting">
      <button aria-label="Bold" aria-pressed="false">
        <strong>B</strong>
      </button>
      <button aria-label="Italic" aria-pressed="false">
        <em>I</em>
      </button>
      <button aria-label="Underline" aria-pressed="false">
        <u>U</u>
      </button>
    </Toolbar>
  )
}
```

### Focus Visible Styles

```css
/* globals.css */

/* Remove default outline and add custom focus styles */
*:focus {
  outline: none;
}

/* Only show focus ring for keyboard navigation */
*:focus-visible {
  outline: 2px solid #2563eb;
  outline-offset: 2px;
}

/* High contrast focus for dark backgrounds */
.dark *:focus-visible {
  outline-color: #60a5fa;
}

/* Skip link styles */
.sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border-width: 0;
}

.focus\:not-sr-only:focus {
  position: absolute;
  width: auto;
  height: auto;
  padding: 0;
  margin: 0;
  overflow: visible;
  clip: auto;
  white-space: normal;
}
```

---

## 4. Color & Contrast

WCAG 2.2 requires sufficient color contrast and color-independent information conveyance.

### Contrast Ratios

| Element Type | Minimum Ratio | WCAG Level |
|--------------|---------------|------------|
| Normal text (< 18pt or < 14pt bold) | 4.5:1 | AA |
| Large text (≥ 18pt or ≥ 14pt bold) | 3:1 | AA |
| UI components & graphics | 3:1 | AA |
| Enhanced contrast (normal text) | 7:1 | AAA |
| Enhanced contrast (large text) | 4.5:1 | AAA |

### Color Palette with Accessible Combinations

```tsx
// lib/colors.ts

/**
 * Accessible color combinations verified for WCAG AA compliance
 * All combinations meet 4.5:1 contrast ratio for normal text
 */
export const accessibleColors = {
  // Primary colors with accessible text colors
  primary: {
    background: '#2563eb', // Blue 600
    foreground: '#ffffff', // White - 8.59:1 contrast
  },
  secondary: {
    background: '#64748b', // Slate 500
    foreground: '#ffffff', // White - 4.54:1 contrast
  },
  success: {
    background: '#16a34a', // Green 600
    foreground: '#ffffff', // White - 4.52:1 contrast
  },
  warning: {
    background: '#ca8a04', // Yellow 600
    foreground: '#000000', // Black - 5.74:1 contrast (white fails!)
  },
  error: {
    background: '#dc2626', // Red 600
    foreground: '#ffffff', // White - 4.53:1 contrast
  },

  // Text colors
  text: {
    primary: '#111827',   // Gray 900 on white: 16.10:1
    secondary: '#4b5563', // Gray 600 on white: 5.91:1
    muted: '#6b7280',     // Gray 500 on white: 4.54:1 (minimum!)
    disabled: '#9ca3af',  // Gray 400 on white: 2.85:1 (fails - use for decorative only)
  },

  // Dark mode
  dark: {
    background: '#111827', // Gray 900
    foreground: '#f9fafb', // Gray 50 - 15.98:1 contrast
    muted: '#9ca3af',      // Gray 400 on Gray 900: 7.25:1
  },
} as const
```

### Color-Independent Indicators

Never use color alone to convey information.

```tsx
// components/form/form-field-status.tsx

interface FormFieldStatusProps {
  status: 'default' | 'success' | 'error' | 'warning'
  message?: string
}

export function FormFieldStatus({ status, message }: FormFieldStatusProps) {
  if (!message) return null

  const statusConfig = {
    default: {
      icon: null,
      className: 'text-gray-600',
      prefix: '',
    },
    success: {
      // Icon AND color - don't rely on color alone
      icon: (
        <svg className="h-4 w-4" fill="currentColor" viewBox="0 0 20 20" aria-hidden="true">
          <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
        </svg>
      ),
      className: 'text-green-700',
      prefix: 'Success: ',
    },
    error: {
      icon: (
        <svg className="h-4 w-4" fill="currentColor" viewBox="0 0 20 20" aria-hidden="true">
          <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
        </svg>
      ),
      className: 'text-red-700',
      prefix: 'Error: ',
    },
    warning: {
      icon: (
        <svg className="h-4 w-4" fill="currentColor" viewBox="0 0 20 20" aria-hidden="true">
          <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
        </svg>
      ),
      className: 'text-yellow-700',
      prefix: 'Warning: ',
    },
  }

  const config = statusConfig[status]

  return (
    <p className={`mt-1 flex items-center gap-1 text-sm ${config.className}`}>
      {config.icon}
      {/* Screen reader gets prefix for context without color */}
      <span className="sr-only">{config.prefix}</span>
      {message}
    </p>
  )
}
```

### Reduced Motion

Respect user preferences for reduced motion.

```tsx
// hooks/use-reduced-motion.ts

'use client'

import * as React from 'react'

export function useReducedMotion(): boolean {
  const [prefersReducedMotion, setPrefersReducedMotion] = React.useState(false)

  React.useEffect(() => {
    const mediaQuery = window.matchMedia('(prefers-reduced-motion: reduce)')
    setPrefersReducedMotion(mediaQuery.matches)

    const listener = (event: MediaQueryListEvent) => {
      setPrefersReducedMotion(event.matches)
    }

    mediaQuery.addEventListener('change', listener)
    return () => mediaQuery.removeEventListener('change', listener)
  }, [])

  return prefersReducedMotion
}
```

```css
/* globals.css */

/* Disable animations for users who prefer reduced motion */
@media (prefers-reduced-motion: reduce) {
  *,
  *::before,
  *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
    scroll-behavior: auto !important;
  }
}

/* Provide alternative for important status changes */
@media (prefers-reduced-motion: reduce) {
  .loading-spinner {
    animation: none;
  }

  .loading-spinner::after {
    content: 'Loading...';
  }
}
```

### Dark Mode Support

```tsx
// components/theme-provider.tsx

'use client'

import * as React from 'react'

type Theme = 'light' | 'dark' | 'system'

interface ThemeProviderProps {
  children: React.ReactNode
  defaultTheme?: Theme
}

const ThemeContext = React.createContext<{
  theme: Theme
  setTheme: (theme: Theme) => void
}>({
  theme: 'system',
  setTheme: () => {},
})

export function ThemeProvider({ children, defaultTheme = 'system' }: ThemeProviderProps) {
  const [theme, setTheme] = React.useState<Theme>(defaultTheme)

  React.useEffect(() => {
    const root = document.documentElement

    if (theme === 'system') {
      const systemTheme = window.matchMedia('(prefers-color-scheme: dark)').matches
        ? 'dark'
        : 'light'
      root.classList.toggle('dark', systemTheme === 'dark')
    } else {
      root.classList.toggle('dark', theme === 'dark')
    }
  }, [theme])

  return (
    <ThemeContext.Provider value={{ theme, setTheme }}>
      {children}
    </ThemeContext.Provider>
  )
}

export function useTheme() {
  return React.useContext(ThemeContext)
}

// Accessible theme toggle
export function ThemeToggle() {
  const { theme, setTheme } = useTheme()
  const isDark = theme === 'dark' ||
    (theme === 'system' && typeof window !== 'undefined' &&
     window.matchMedia('(prefers-color-scheme: dark)').matches)

  return (
    <button
      onClick={() => setTheme(isDark ? 'light' : 'dark')}
      aria-label={`Switch to ${isDark ? 'light' : 'dark'} mode`}
      className="p-2 rounded-md hover:bg-gray-100 dark:hover:bg-gray-800"
    >
      {isDark ? (
        <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z" />
        </svg>
      ) : (
        <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z" />
        </svg>
      )}
    </button>
  )
}
```

---

## 5. Accessible Forms

Forms are critical for accessibility. Every input must have a label, errors must be clearly communicated, and validation must be accessible.

### Label Associations

```tsx
// components/form/text-input.tsx

'use client'

import * as React from 'react'
import { useId } from 'react'
import { cn } from '@/lib/utils'

interface TextInputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label: string
  error?: string
  hint?: string
}

export function TextInput({
  label,
  error,
  hint,
  className,
  required,
  ...props
}: TextInputProps) {
  // useId ensures unique IDs for SSR and hydration
  const id = useId()
  const errorId = `${id}-error`
  const hintId = `${id}-hint`

  // Build aria-describedby from available descriptions
  const describedBy = [
    hint && hintId,
    error && errorId,
  ].filter(Boolean).join(' ') || undefined

  return (
    <div className="space-y-1">
      <label htmlFor={id} className="block text-sm font-medium text-gray-700">
        {label}
        {required && (
          <span className="text-red-600 ml-1" aria-hidden="true">*</span>
        )}
        {required && <span className="sr-only"> (required)</span>}
      </label>

      {hint && (
        <p id={hintId} className="text-sm text-gray-500">
          {hint}
        </p>
      )}

      <input
        id={id}
        aria-describedby={describedBy}
        aria-invalid={error ? 'true' : undefined}
        aria-required={required}
        required={required}
        className={cn(
          'block w-full rounded-md border px-3 py-2 text-sm',
          'focus:outline-none focus:ring-2 focus:ring-offset-0',
          error
            ? 'border-red-500 focus:border-red-500 focus:ring-red-500'
            : 'border-gray-300 focus:border-blue-500 focus:ring-blue-500',
          className
        )}
        {...props}
      />

      {error && (
        <p id={errorId} className="text-sm text-red-600 flex items-center gap-1" role="alert">
          <svg className="h-4 w-4" fill="currentColor" viewBox="0 0 20 20" aria-hidden="true">
            <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
          </svg>
          {error}
        </p>
      )}
    </div>
  )
}
```

### Fieldset and Legend for Related Fields

```tsx
// components/form/radio-group.tsx

'use client'

import * as React from 'react'
import { useId } from 'react'

interface RadioOption {
  value: string
  label: string
  description?: string
}

interface RadioGroupProps {
  legend: string
  name: string
  options: RadioOption[]
  value?: string
  onChange?: (value: string) => void
  error?: string
  required?: boolean
}

export function RadioGroup({
  legend,
  name,
  options,
  value,
  onChange,
  error,
  required,
}: RadioGroupProps) {
  const groupId = useId()
  const errorId = `${groupId}-error`

  return (
    <fieldset
      aria-describedby={error ? errorId : undefined}
      aria-invalid={error ? 'true' : undefined}
    >
      <legend className="text-sm font-medium text-gray-700">
        {legend}
        {required && (
          <>
            <span className="text-red-600 ml-1" aria-hidden="true">*</span>
            <span className="sr-only"> (required)</span>
          </>
        )}
      </legend>

      <div className="mt-2 space-y-2">
        {options.map((option) => {
          const optionId = `${groupId}-${option.value}`
          const descriptionId = option.description ? `${optionId}-description` : undefined

          return (
            <div key={option.value} className="flex items-start">
              <input
                type="radio"
                id={optionId}
                name={name}
                value={option.value}
                checked={value === option.value}
                onChange={(e) => onChange?.(e.target.value)}
                aria-describedby={descriptionId}
                required={required}
                className="mt-1 h-4 w-4 border-gray-300 text-blue-600 focus:ring-blue-500"
              />
              <div className="ml-3">
                <label htmlFor={optionId} className="text-sm text-gray-700">
                  {option.label}
                </label>
                {option.description && (
                  <p id={descriptionId} className="text-sm text-gray-500">
                    {option.description}
                  </p>
                )}
              </div>
            </div>
          )
        })}
      </div>

      {error && (
        <p id={errorId} className="mt-2 text-sm text-red-600" role="alert">
          {error}
        </p>
      )}
    </fieldset>
  )
}
```

### Error Summary Pattern

For forms with multiple errors, provide an error summary at the top.

```tsx
// components/form/error-summary.tsx

'use client'

import * as React from 'react'

interface FieldError {
  field: string
  message: string
}

interface ErrorSummaryProps {
  errors: FieldError[]
  title?: string
}

export function ErrorSummary({ errors, title = 'There were errors with your submission' }: ErrorSummaryProps) {
  const summaryRef = React.useRef<HTMLDivElement>(null)

  React.useEffect(() => {
    if (errors.length > 0) {
      // Focus the error summary when errors appear
      summaryRef.current?.focus()
    }
  }, [errors])

  if (errors.length === 0) return null

  return (
    <div
      ref={summaryRef}
      role="alert"
      aria-labelledby="error-summary-title"
      tabIndex={-1}
      className="rounded-md border border-red-400 bg-red-50 p-4 mb-6"
    >
      <h2 id="error-summary-title" className="text-lg font-medium text-red-800">
        {title}
      </h2>
      <ul className="mt-2 list-disc list-inside text-sm text-red-700">
        {errors.map((error) => (
          <li key={error.field}>
            <a
              href={`#${error.field}`}
              className="underline hover:text-red-900"
              onClick={(e) => {
                e.preventDefault()
                const field = document.getElementById(error.field)
                field?.focus()
              }}
            >
              {error.message}
            </a>
          </li>
        ))}
      </ul>
    </div>
  )
}

// Usage in form
export function ContactForm() {
  const [errors, setErrors] = React.useState<FieldError[]>([])

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    // Validation logic
    const newErrors: FieldError[] = []

    // Example validation
    const form = e.target as HTMLFormElement
    const name = form.elements.namedItem('name') as HTMLInputElement
    if (!name.value) {
      newErrors.push({ field: 'name', message: 'Enter your name' })
    }

    setErrors(newErrors)

    if (newErrors.length === 0) {
      // Submit form
    }
  }

  return (
    <form onSubmit={handleSubmit}>
      <ErrorSummary errors={errors} />

      <TextInput
        id="name"
        name="name"
        label="Name"
        error={errors.find(e => e.field === 'name')?.message}
        required
      />

      {/* More fields */}

      <button type="submit">Submit</button>
    </form>
  )
}
```

### Validation Announcements

```tsx
// components/form/form-with-validation.tsx

'use client'

import * as React from 'react'
import { LiveRegion } from '../ui/live-region'

export function FormWithValidation() {
  const [validationMessage, setValidationMessage] = React.useState('')
  const [isSubmitting, setIsSubmitting] = React.useState(false)
  const [isSuccess, setIsSuccess] = React.useState(false)

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault()
    setIsSubmitting(true)
    setValidationMessage('Submitting form...')

    try {
      // API call
      await new Promise(resolve => setTimeout(resolve, 1000))
      setIsSuccess(true)
      setValidationMessage('Form submitted successfully!')
    } catch {
      setValidationMessage('Form submission failed. Please try again.')
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <form onSubmit={handleSubmit}>
      {/* Live region announces validation state changes */}
      <LiveRegion politeness="polite">
        {validationMessage}
      </LiveRegion>

      {/* Form fields */}

      <button
        type="submit"
        disabled={isSubmitting}
        aria-busy={isSubmitting}
      >
        {isSubmitting ? 'Submitting...' : 'Submit'}
      </button>
    </form>
  )
}
```

---

## 6. Images & Media

All non-decorative images must have alternative text. The appropriate alt text depends on the image's purpose.

### Alt Text Decision Tree

```
Is the image purely decorative?
├── YES → alt="" (empty alt, NOT omitted)
└── NO → Does it convey information?
    ├── YES → Is it simple information?
    │   ├── YES → Write concise alt text (< 125 chars)
    │   └── NO → Provide extended description (aria-describedby or figure/figcaption)
    └── NO → Is it functional (link/button)?
        ├── YES → Describe the action/destination
        └── NO → Is it complex (chart/diagram)?
            └── YES → Provide detailed text alternative nearby
```

### Image Component Examples

```tsx
// components/images/accessible-image.tsx

import Image from 'next/image'

// 1. Informative Image - conveys information
export function InformativeImage() {
  return (
    <Image
      src="/products/red-sneakers.jpg"
      alt="Red canvas sneakers with white rubber soles and matching laces"
      width={400}
      height={300}
    />
  )
}

// 2. Decorative Image - purely aesthetic
export function DecorativeImage() {
  return (
    <Image
      src="/decorative-pattern.svg"
      alt="" // Empty alt, not omitted!
      aria-hidden="true"
      width={100}
      height={100}
    />
  )
}

// 3. Functional Image - used as a link or button
export function FunctionalImage() {
  return (
    <a href="/home">
      <Image
        src="/logo.svg"
        alt="Acme Corp - Go to homepage" // Describes the destination
        width={150}
        height={40}
      />
    </a>
  )
}

// 4. Complex Image - charts, diagrams, infographics
export function ComplexImage() {
  return (
    <figure>
      <Image
        src="/quarterly-sales-chart.png"
        alt="Bar chart showing quarterly sales growth"
        aria-describedby="chart-description"
        width={600}
        height={400}
      />
      <figcaption id="chart-description">
        <p>
          Quarterly sales data for 2024. Q1: $1.2M, Q2: $1.5M (+25%),
          Q3: $1.8M (+20%), Q4: $2.1M (+17%). Total annual growth: 75%.
        </p>
      </figcaption>
    </figure>
  )
}

// 5. Image with adjacent text (don't repeat)
export function ImageWithAdjacentText() {
  return (
    <article>
      <Image
        src="/jane-doe.jpg"
        alt="" // Empty because name is in adjacent text
        width={200}
        height={200}
      />
      <h2>Jane Doe</h2>
      <p>Senior Software Engineer</p>
    </article>
  )
}

// 6. Background/CSS images that convey information
export function InformativeBackgroundImage() {
  return (
    <div
      className="bg-cover bg-center h-64"
      style={{ backgroundImage: "url('/hero-image.jpg')" }}
      role="img"
      aria-label="Team collaboration in modern office space"
    />
  )
}
```

### Video with Captions

```tsx
// components/media/accessible-video.tsx

interface VideoProps {
  src: string
  poster: string
  captionsSrc: string
  title: string
  transcript?: string
}

export function AccessibleVideo({ src, poster, captionsSrc, title, transcript }: VideoProps) {
  return (
    <figure>
      <video
        controls
        poster={poster}
        preload="metadata"
        aria-label={title}
      >
        <source src={src} type="video/mp4" />
        {/* Captions for deaf/hard of hearing users */}
        <track
          kind="captions"
          src={captionsSrc}
          srcLang="en"
          label="English captions"
          default
        />
        {/* Fallback for browsers that don't support video */}
        <p>
          Your browser doesn't support HTML video.
          <a href={src}>Download the video</a> instead.
        </p>
      </video>

      <figcaption className="sr-only">{title}</figcaption>

      {/* Full transcript for accessibility and SEO */}
      {transcript && (
        <details className="mt-4">
          <summary className="cursor-pointer text-blue-600 hover:underline">
            View transcript
          </summary>
          <div className="mt-2 p-4 bg-gray-50 rounded text-sm">
            {transcript}
          </div>
        </details>
      )}
    </figure>
  )
}
```

### Audio with Transcript

```tsx
// components/media/accessible-audio.tsx

interface AudioProps {
  src: string
  title: string
  transcript: string
  duration: string
}

export function AccessibleAudio({ src, title, transcript, duration }: AudioProps) {
  return (
    <figure className="border rounded-lg p-4">
      <figcaption className="font-medium mb-2">
        {title}
        <span className="text-sm text-gray-500 ml-2">({duration})</span>
      </figcaption>

      <audio controls className="w-full" aria-label={title}>
        <source src={src} type="audio/mpeg" />
        <p>
          Your browser doesn't support audio.
          <a href={src}>Download the audio file</a>.
        </p>
      </audio>

      {/* Transcript is required for audio content */}
      <details className="mt-4">
        <summary className="cursor-pointer text-blue-600 hover:underline">
          View transcript
        </summary>
        <div className="mt-2 p-4 bg-gray-50 rounded text-sm whitespace-pre-wrap">
          {transcript}
        </div>
      </details>
    </figure>
  )
}
```

---

## 7. Dynamic Content

Single Page Applications require special attention for dynamic content changes.

### Route Change Announcements

```tsx
// components/layout/route-announcer.tsx

'use client'

import * as React from 'react'
import { usePathname } from 'next/navigation'

export function RouteAnnouncer() {
  const pathname = usePathname()
  const [announcement, setAnnouncement] = React.useState('')

  React.useEffect(() => {
    // Get the page title or generate from pathname
    const pageTitle = document.title || pathname.split('/').pop() || 'page'
    setAnnouncement(`Navigated to ${pageTitle}`)

    // Clear after announcement
    const timer = setTimeout(() => setAnnouncement(''), 1000)
    return () => clearTimeout(timer)
  }, [pathname])

  return (
    <div
      role="status"
      aria-live="polite"
      aria-atomic="true"
      className="sr-only"
    >
      {announcement}
    </div>
  )
}

// Add to layout.tsx
export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <RouteAnnouncer />
        {children}
      </body>
    </html>
  )
}
```

### Loading States with aria-busy

```tsx
// components/ui/loading-container.tsx

'use client'

import * as React from 'react'

interface LoadingContainerProps {
  isLoading: boolean
  loadingLabel?: string
  children: React.ReactNode
}

export function LoadingContainer({
  isLoading,
  loadingLabel = 'Loading content',
  children
}: LoadingContainerProps) {
  const containerRef = React.useRef<HTMLDivElement>(null)

  return (
    <div
      ref={containerRef}
      aria-busy={isLoading}
      aria-live="polite"
    >
      {isLoading && (
        <div className="flex items-center justify-center p-8">
          <div
            role="status"
            aria-label={loadingLabel}
            className="animate-spin h-8 w-8 border-4 border-blue-600 border-t-transparent rounded-full"
          />
          <span className="sr-only">{loadingLabel}</span>
        </div>
      )}

      {/* Content is visually hidden but kept in DOM when loading */}
      <div className={isLoading ? 'sr-only' : undefined}>
        {children}
      </div>
    </div>
  )
}

// Usage with data fetching
export function ProductList() {
  const [products, setProducts] = React.useState([])
  const [isLoading, setIsLoading] = React.useState(true)

  React.useEffect(() => {
    fetch('/api/products')
      .then(res => res.json())
      .then(data => {
        setProducts(data)
        setIsLoading(false)
      })
  }, [])

  return (
    <LoadingContainer isLoading={isLoading} loadingLabel="Loading products">
      <ul>
        {products.map(product => (
          <li key={product.id}>{product.name}</li>
        ))}
      </ul>
    </LoadingContainer>
  )
}
```

### Toast Notifications

```tsx
// components/ui/toast.tsx

'use client'

import * as React from 'react'
import * as ToastPrimitive from '@radix-ui/react-toast'
import { X } from 'lucide-react'
import { cn } from '@/lib/utils'

const ToastProvider = ToastPrimitive.Provider

const ToastViewport = React.forwardRef<
  React.ElementRef<typeof ToastPrimitive.Viewport>,
  React.ComponentPropsWithoutRef<typeof ToastPrimitive.Viewport>
>(({ className, ...props }, ref) => (
  <ToastPrimitive.Viewport
    ref={ref}
    className={cn(
      'fixed bottom-0 right-0 z-[100] flex max-h-screen w-full flex-col-reverse p-4 sm:max-w-[420px]',
      className
    )}
    {...props}
  />
))
ToastViewport.displayName = ToastPrimitive.Viewport.displayName

interface ToastProps extends React.ComponentPropsWithoutRef<typeof ToastPrimitive.Root> {
  variant?: 'default' | 'success' | 'error' | 'warning'
}

const Toast = React.forwardRef<
  React.ElementRef<typeof ToastPrimitive.Root>,
  ToastProps
>(({ className, variant = 'default', ...props }, ref) => {
  const variantStyles = {
    default: 'bg-white border-gray-200',
    success: 'bg-green-50 border-green-200',
    error: 'bg-red-50 border-red-200',
    warning: 'bg-yellow-50 border-yellow-200',
  }

  return (
    <ToastPrimitive.Root
      ref={ref}
      className={cn(
        'group pointer-events-auto relative flex w-full items-center justify-between space-x-4 overflow-hidden rounded-md border p-6 pr-8 shadow-lg transition-all',
        variantStyles[variant],
        className
      )}
      // Role is automatically handled by Radix based on type
      {...props}
    />
  )
})
Toast.displayName = ToastPrimitive.Root.displayName

const ToastAction = React.forwardRef<
  React.ElementRef<typeof ToastPrimitive.Action>,
  React.ComponentPropsWithoutRef<typeof ToastPrimitive.Action>
>(({ className, ...props }, ref) => (
  <ToastPrimitive.Action
    ref={ref}
    className={cn(
      'inline-flex h-8 shrink-0 items-center justify-center rounded-md border bg-transparent px-3 text-sm font-medium',
      'hover:bg-gray-100 focus:outline-none focus:ring-2 focus:ring-offset-2',
      'disabled:pointer-events-none disabled:opacity-50',
      className
    )}
    {...props}
  />
))
ToastAction.displayName = ToastPrimitive.Action.displayName

const ToastClose = React.forwardRef<
  React.ElementRef<typeof ToastPrimitive.Close>,
  React.ComponentPropsWithoutRef<typeof ToastPrimitive.Close>
>(({ className, ...props }, ref) => (
  <ToastPrimitive.Close
    ref={ref}
    className={cn(
      'absolute right-2 top-2 rounded-md p-1 opacity-0 transition-opacity',
      'hover:opacity-100 focus:opacity-100 focus:outline-none focus:ring-2',
      'group-hover:opacity-100',
      className
    )}
    toast-close=""
    aria-label="Close notification"
    {...props}
  >
    <X className="h-4 w-4" aria-hidden="true" />
  </ToastPrimitive.Close>
))
ToastClose.displayName = ToastPrimitive.Close.displayName

const ToastTitle = React.forwardRef<
  React.ElementRef<typeof ToastPrimitive.Title>,
  React.ComponentPropsWithoutRef<typeof ToastPrimitive.Title>
>(({ className, ...props }, ref) => (
  <ToastPrimitive.Title
    ref={ref}
    className={cn('text-sm font-semibold', className)}
    {...props}
  />
))
ToastTitle.displayName = ToastPrimitive.Title.displayName

const ToastDescription = React.forwardRef<
  React.ElementRef<typeof ToastPrimitive.Description>,
  React.ComponentPropsWithoutRef<typeof ToastPrimitive.Description>
>(({ className, ...props }, ref) => (
  <ToastPrimitive.Description
    ref={ref}
    className={cn('text-sm opacity-90', className)}
    {...props}
  />
))
ToastDescription.displayName = ToastPrimitive.Description.displayName

export {
  ToastProvider,
  ToastViewport,
  Toast,
  ToastAction,
  ToastClose,
  ToastTitle,
  ToastDescription,
}

// Toast hook and context
type ToastVariant = 'default' | 'success' | 'error' | 'warning'

interface ToastData {
  id: string
  title: string
  description?: string
  variant?: ToastVariant
  action?: React.ReactNode
}

interface ToastContextValue {
  toasts: ToastData[]
  addToast: (toast: Omit<ToastData, 'id'>) => void
  removeToast: (id: string) => void
}

const ToastContext = React.createContext<ToastContextValue | null>(null)

export function useToast() {
  const context = React.useContext(ToastContext)
  if (!context) throw new Error('useToast must be used within ToastProvider')
  return context
}

// Usage
export function SaveButton() {
  const { addToast } = useToast()

  const handleSave = async () => {
    try {
      await saveData()
      addToast({
        title: 'Changes saved',
        description: 'Your changes have been saved successfully.',
        variant: 'success',
      })
    } catch {
      addToast({
        title: 'Error saving changes',
        description: 'Please try again.',
        variant: 'error',
      })
    }
  }

  return <button onClick={handleSave}>Save</button>
}
```

---

## 8. Next.js Specific

Next.js has specific accessibility considerations for App Router, Server Components, and built-in components.

### next/image Alt Text

```tsx
// Always provide alt text for next/image
import Image from 'next/image'

// Required: alt must be provided
<Image
  src="/hero.jpg"
  alt="Team meeting in a bright office space with laptops and whiteboards"
  width={1200}
  height={600}
  priority // Above-the-fold images should use priority
/>

// Decorative images: use empty alt
<Image
  src="/decorative-wave.svg"
  alt=""
  aria-hidden="true"
  width={100}
  height={20}
/>
```

### next/link Accessibility

```tsx
import Link from 'next/link'

// Good: Descriptive link text
<Link href="/products/shoes">
  View all shoes
</Link>

// Bad: Non-descriptive link text
<Link href="/products/shoes">
  Click here
</Link>

// When link wraps an image, ensure accessible name
<Link href="/products/shoes" aria-label="View all shoes">
  <Image src="/shoes.jpg" alt="" width={200} height={200} />
</Link>

// Opening in new tab - warn users
<Link
  href="https://external.com"
  target="_blank"
  rel="noopener noreferrer"
>
  External Resource
  <span className="sr-only"> (opens in new tab)</span>
  <svg aria-hidden="true" className="inline h-4 w-4 ml-1">
    {/* External link icon */}
  </svg>
</Link>
```

### useId for Labels

```tsx
// app/components/search-form.tsx
'use client'

import { useId } from 'react'

export function SearchForm() {
  // useId generates stable IDs that work with SSR
  const searchId = useId()
  const resultsId = useId()

  return (
    <form role="search">
      <label htmlFor={searchId}>Search products</label>
      <input
        id={searchId}
        type="search"
        aria-describedby={resultsId}
      />
      <div id={resultsId} aria-live="polite">
        {/* Search results count */}
      </div>
    </form>
  )
}
```

### Server Component Considerations

```tsx
// app/products/page.tsx

// Server Components don't have access to browser APIs
// Ensure accessibility attributes are properly set

export default async function ProductsPage() {
  const products = await getProducts()

  return (
    <main>
      <h1>Products</h1>

      {/* Static content can be fully accessible in Server Components */}
      <section aria-labelledby="featured-heading">
        <h2 id="featured-heading">Featured Products</h2>
        <ul role="list">
          {products.map((product) => (
            <li key={product.id}>
              <article>
                <h3>{product.name}</h3>
                <p>{product.description}</p>
              </article>
            </li>
          ))}
        </ul>
      </section>

      {/* Interactive elements need Client Components */}
      <ProductFilters /> {/* 'use client' component */}
    </main>
  )
}

// components/product-filters.tsx
'use client'

export function ProductFilters() {
  // Client Component for interactive filtering
  return (
    <form role="search" aria-label="Filter products">
      {/* Interactive form elements */}
    </form>
  )
}
```

### Custom Route Announcer

Next.js 13+ removed the built-in route announcer. Implement your own:

```tsx
// components/route-announcer.tsx
'use client'

import * as React from 'react'
import { usePathname, useSearchParams } from 'next/navigation'

export function RouteAnnouncer() {
  const pathname = usePathname()
  const searchParams = useSearchParams()
  const [announcement, setAnnouncement] = React.useState('')

  React.useEffect(() => {
    // Announce navigation
    const title = document.title || 'Page'
    setAnnouncement(`Navigated to ${title}`)
  }, [pathname, searchParams])

  return (
    <div
      role="status"
      aria-live="assertive"
      aria-atomic="true"
      className="sr-only"
    >
      {announcement}
    </div>
  )
}

// app/layout.tsx
import { RouteAnnouncer } from '@/components/route-announcer'

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <RouteAnnouncer />
        {children}
      </body>
    </html>
  )
}
```

### Metadata for Accessibility

```tsx
// app/layout.tsx
import { Metadata } from 'next'

export const metadata: Metadata = {
  title: {
    template: '%s | Acme Corp',
    default: 'Acme Corp',
  },
  description: 'Accessible e-commerce platform',
}

// app/products/page.tsx
export const metadata: Metadata = {
  title: 'Products', // Results in "Products | Acme Corp"
  description: 'Browse our collection of products',
}

export default function ProductsPage() {
  return (
    <main>
      {/* Page content */}
    </main>
  )
}
```

---

## 9. Testing Tools & Workflow

### ESLint Plugin jsx-a11y Configuration

```json
// .eslintrc.json
{
  "extends": [
    "next/core-web-vitals",
    "plugin:jsx-a11y/recommended"
  ],
  "plugins": ["jsx-a11y"],
  "rules": {
    // Enforce alt text
    "jsx-a11y/alt-text": ["error", {
      "elements": ["img", "object", "area", "input[type=\"image\"]"],
      "img": ["Image"]
    }],

    // Ensure anchors have content
    "jsx-a11y/anchor-has-content": "error",

    // Ensure anchors are valid
    "jsx-a11y/anchor-is-valid": ["error", {
      "components": ["Link"],
      "specialLink": ["hrefLeft", "hrefRight"],
      "aspects": ["invalidHref", "preferButton"]
    }],

    // Ensure interactive elements are focusable
    "jsx-a11y/interactive-supports-focus": "error",

    // Ensure form elements have labels
    "jsx-a11y/label-has-associated-control": ["error", {
      "labelComponents": ["Label"],
      "labelAttributes": ["label"],
      "controlComponents": ["Input", "Select", "Textarea"],
      "depth": 3
    }],

    // No autofocus (disorienting for screen readers)
    "jsx-a11y/no-autofocus": ["error", {
      "ignoreNonDOM": true
    }],

    // No redundant roles
    "jsx-a11y/no-redundant-roles": "error",

    // Require onClick for onKeyDown
    "jsx-a11y/click-events-have-key-events": "error",
    "jsx-a11y/no-static-element-interactions": "error"
  }
}
```

### Playwright + axe-core Integration Tests

```typescript
// tests/accessibility.spec.ts

import { test, expect } from '@playwright/test'
import AxeBuilder from '@axe-core/playwright'

test.describe('Accessibility', () => {
  test('homepage should have no accessibility violations', async ({ page }) => {
    await page.goto('/')

    const accessibilityScanResults = await new AxeBuilder({ page })
      .withTags(['wcag2a', 'wcag2aa', 'wcag21a', 'wcag21aa', 'wcag22aa'])
      .analyze()

    expect(accessibilityScanResults.violations).toEqual([])
  })

  test('product page should have no accessibility violations', async ({ page }) => {
    await page.goto('/products/example-product')

    const accessibilityScanResults = await new AxeBuilder({ page })
      .withTags(['wcag2a', 'wcag2aa', 'wcag21a', 'wcag21aa', 'wcag22aa'])
      .exclude('.third-party-widget') // Exclude elements you can't control
      .analyze()

    expect(accessibilityScanResults.violations).toEqual([])
  })

  test('form validation errors are accessible', async ({ page }) => {
    await page.goto('/contact')

    // Submit empty form
    await page.getByRole('button', { name: 'Submit' }).click()

    // Check error summary is announced
    const errorSummary = page.getByRole('alert')
    await expect(errorSummary).toBeVisible()
    await expect(errorSummary).toBeFocused()

    // Check individual field errors
    const nameInput = page.getByLabel('Name')
    await expect(nameInput).toHaveAttribute('aria-invalid', 'true')

    // Run axe on error state
    const accessibilityScanResults = await new AxeBuilder({ page })
      .withTags(['wcag2a', 'wcag2aa'])
      .analyze()

    expect(accessibilityScanResults.violations).toEqual([])
  })

  test('modal dialog traps focus', async ({ page }) => {
    await page.goto('/products/example')

    // Open modal
    await page.getByRole('button', { name: 'Quick view' }).click()

    const dialog = page.getByRole('dialog')
    await expect(dialog).toBeVisible()

    // First focusable element should be focused
    const closeButton = dialog.getByRole('button', { name: 'Close' })
    await expect(closeButton).toBeFocused()

    // Tab through all focusable elements
    await page.keyboard.press('Tab')
    await page.keyboard.press('Tab')
    await page.keyboard.press('Tab')

    // Focus should wrap back to first element
    await expect(closeButton).toBeFocused()

    // Escape closes modal
    await page.keyboard.press('Escape')
    await expect(dialog).not.toBeVisible()

    // Focus returns to trigger
    await expect(page.getByRole('button', { name: 'Quick view' })).toBeFocused()
  })

  test('keyboard navigation works correctly', async ({ page }) => {
    await page.goto('/')

    // Tab to skip link
    await page.keyboard.press('Tab')
    const skipLink = page.getByRole('link', { name: 'Skip to main content' })
    await expect(skipLink).toBeFocused()

    // Activate skip link
    await page.keyboard.press('Enter')
    const main = page.locator('main')
    await expect(main).toBeFocused()
  })
})
```

### Manual Testing Checklist

```markdown
## VoiceOver Testing (macOS)

### Setup
- [ ] Enable VoiceOver: Cmd + F5
- [ ] Enable trackpad commander: VoiceOver Utility > Commanders

### Page Load
- [ ] Page title is announced
- [ ] Landmarks are navigable (VO + U, then arrows)
- [ ] Heading structure is logical (VO + Cmd + H)

### Navigation
- [ ] Skip link is first focusable element
- [ ] Tab order is logical
- [ ] All interactive elements are reachable
- [ ] Focus is visible

### Forms
- [ ] Labels are announced with inputs
- [ ] Required fields are announced
- [ ] Error messages are announced immediately
- [ ] Error summary is announced and focused

### Images
- [ ] Informative images have descriptive alt text
- [ ] Decorative images are ignored (not announced)

### Dynamic Content
- [ ] Route changes are announced
- [ ] Loading states are announced
- [ ] Toasts/notifications are announced

## NVDA Testing (Windows)

### Setup
- [ ] Download from nvaccess.org
- [ ] Use Browse mode for reading (default)
- [ ] Use Focus mode for forms (NVDA + Space to toggle)

### Key Commands
- [ ] H - Next heading
- [ ] D - Next landmark
- [ ] Tab - Next focusable element
- [ ] Enter - Activate link/button
- [ ] Space - Toggle checkbox/expand

### Testing Steps
(Same as VoiceOver checklist above)
```

### Tool Comparison Table

| Tool | Type | Coverage | Best For |
|------|------|----------|----------|
| eslint-plugin-jsx-a11y | Linter | Static analysis | Development-time errors |
| axe-core | Automated | ~50-60% of issues | CI/CD integration |
| Lighthouse | Automated | ~30% of issues | Quick audits |
| WAVE | Browser extension | ~40% of issues | Visual debugging |
| VoiceOver | Screen reader | Manual | macOS testing |
| NVDA | Screen reader | Manual | Windows testing |
| Keyboard only | Manual | Navigation | Focus management |

---

## 10. Component Library Patterns

### Accessible shadcn/ui Dialog

```tsx
// components/ui/dialog.tsx

import * as React from 'react'
import * as DialogPrimitive from '@radix-ui/react-dialog'
import { X } from 'lucide-react'
import { cn } from '@/lib/utils'

const Dialog = DialogPrimitive.Root
const DialogTrigger = DialogPrimitive.Trigger
const DialogPortal = DialogPrimitive.Portal
const DialogClose = DialogPrimitive.Close

const DialogOverlay = React.forwardRef<
  React.ElementRef<typeof DialogPrimitive.Overlay>,
  React.ComponentPropsWithoutRef<typeof DialogPrimitive.Overlay>
>(({ className, ...props }, ref) => (
  <DialogPrimitive.Overlay
    ref={ref}
    className={cn(
      'fixed inset-0 z-50 bg-black/80',
      'data-[state=open]:animate-in data-[state=closed]:animate-out',
      'data-[state=closed]:fade-out-0 data-[state=open]:fade-in-0',
      className
    )}
    {...props}
  />
))
DialogOverlay.displayName = DialogPrimitive.Overlay.displayName

const DialogContent = React.forwardRef<
  React.ElementRef<typeof DialogPrimitive.Content>,
  React.ComponentPropsWithoutRef<typeof DialogPrimitive.Content>
>(({ className, children, ...props }, ref) => (
  <DialogPortal>
    <DialogOverlay />
    <DialogPrimitive.Content
      ref={ref}
      className={cn(
        'fixed left-[50%] top-[50%] z-50 grid w-full max-w-lg translate-x-[-50%] translate-y-[-50%] gap-4 border bg-background p-6 shadow-lg duration-200',
        'data-[state=open]:animate-in data-[state=closed]:animate-out',
        'data-[state=closed]:fade-out-0 data-[state=open]:fade-in-0',
        'data-[state=closed]:zoom-out-95 data-[state=open]:zoom-in-95',
        'data-[state=closed]:slide-out-to-left-1/2 data-[state=closed]:slide-out-to-top-[48%]',
        'data-[state=open]:slide-in-from-left-1/2 data-[state=open]:slide-in-from-top-[48%]',
        'sm:rounded-lg',
        className
      )}
      {...props}
    >
      {children}
      <DialogPrimitive.Close
        className="absolute right-4 top-4 rounded-sm opacity-70 ring-offset-background transition-opacity hover:opacity-100 focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2 disabled:pointer-events-none data-[state=open]:bg-accent data-[state=open]:text-muted-foreground"
        aria-label="Close"
      >
        <X className="h-4 w-4" aria-hidden="true" />
      </DialogPrimitive.Close>
    </DialogPrimitive.Content>
  </DialogPortal>
))
DialogContent.displayName = DialogPrimitive.Content.displayName

const DialogHeader = ({
  className,
  ...props
}: React.HTMLAttributes<HTMLDivElement>) => (
  <div
    className={cn('flex flex-col space-y-1.5 text-center sm:text-left', className)}
    {...props}
  />
)
DialogHeader.displayName = 'DialogHeader'

const DialogFooter = ({
  className,
  ...props
}: React.HTMLAttributes<HTMLDivElement>) => (
  <div
    className={cn('flex flex-col-reverse sm:flex-row sm:justify-end sm:space-x-2', className)}
    {...props}
  />
)
DialogFooter.displayName = 'DialogFooter'

// CRITICAL: DialogTitle is REQUIRED for accessibility
const DialogTitle = React.forwardRef<
  React.ElementRef<typeof DialogPrimitive.Title>,
  React.ComponentPropsWithoutRef<typeof DialogPrimitive.Title>
>(({ className, ...props }, ref) => (
  <DialogPrimitive.Title
    ref={ref}
    className={cn('text-lg font-semibold leading-none tracking-tight', className)}
    {...props}
  />
))
DialogTitle.displayName = DialogPrimitive.Title.displayName

// CRITICAL: DialogDescription is REQUIRED for accessibility
const DialogDescription = React.forwardRef<
  React.ElementRef<typeof DialogPrimitive.Description>,
  React.ComponentPropsWithoutRef<typeof DialogPrimitive.Description>
>(({ className, ...props }, ref) => (
  <DialogPrimitive.Description
    ref={ref}
    className={cn('text-sm text-muted-foreground', className)}
    {...props}
  />
))
DialogDescription.displayName = DialogPrimitive.Description.displayName

export {
  Dialog,
  DialogPortal,
  DialogOverlay,
  DialogClose,
  DialogTrigger,
  DialogContent,
  DialogHeader,
  DialogFooter,
  DialogTitle,
  DialogDescription,
}

// USAGE - Always include DialogTitle and DialogDescription
export function ExampleDialog() {
  return (
    <Dialog>
      <DialogTrigger asChild>
        <button className="px-4 py-2 bg-blue-600 text-white rounded">
          Open Dialog
        </button>
      </DialogTrigger>
      <DialogContent>
        <DialogHeader>
          {/* REQUIRED: Provides accessible name for the dialog */}
          <DialogTitle>Edit Profile</DialogTitle>
          {/* REQUIRED: Provides accessible description */}
          <DialogDescription>
            Make changes to your profile here. Click save when done.
          </DialogDescription>
        </DialogHeader>

        <form>
          {/* Form fields */}
        </form>

        <DialogFooter>
          <DialogClose asChild>
            <button type="button">Cancel</button>
          </DialogClose>
          <button type="submit">Save changes</button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}
```

### Custom Disclosure Component

```tsx
// components/ui/disclosure.tsx

'use client'

import * as React from 'react'
import { ChevronDown } from 'lucide-react'
import { cn } from '@/lib/utils'

interface DisclosureContextValue {
  isOpen: boolean
  toggle: () => void
  triggerId: string
  contentId: string
}

const DisclosureContext = React.createContext<DisclosureContextValue | null>(null)

function useDisclosure() {
  const context = React.useContext(DisclosureContext)
  if (!context) {
    throw new Error('Disclosure components must be used within a Disclosure')
  }
  return context
}

interface DisclosureProps {
  children: React.ReactNode
  defaultOpen?: boolean
}

export function Disclosure({ children, defaultOpen = false }: DisclosureProps) {
  const [isOpen, setIsOpen] = React.useState(defaultOpen)
  const id = React.useId()
  const triggerId = `${id}-trigger`
  const contentId = `${id}-content`

  const toggle = React.useCallback(() => setIsOpen((prev) => !prev), [])

  return (
    <DisclosureContext.Provider value={{ isOpen, toggle, triggerId, contentId }}>
      <div className="border rounded-lg">{children}</div>
    </DisclosureContext.Provider>
  )
}

interface DisclosureTriggerProps {
  children: React.ReactNode
  className?: string
}

export function DisclosureTrigger({ children, className }: DisclosureTriggerProps) {
  const { isOpen, toggle, triggerId, contentId } = useDisclosure()

  return (
    <button
      id={triggerId}
      type="button"
      onClick={toggle}
      aria-expanded={isOpen}
      aria-controls={contentId}
      className={cn(
        'flex w-full items-center justify-between p-4 text-left font-medium',
        'hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-inset focus:ring-blue-500',
        className
      )}
    >
      {children}
      <ChevronDown
        className={cn(
          'h-5 w-5 transition-transform duration-200',
          isOpen && 'rotate-180'
        )}
        aria-hidden="true"
      />
    </button>
  )
}

interface DisclosureContentProps {
  children: React.ReactNode
  className?: string
}

export function DisclosureContent({ children, className }: DisclosureContentProps) {
  const { isOpen, triggerId, contentId } = useDisclosure()

  return (
    <div
      id={contentId}
      role="region"
      aria-labelledby={triggerId}
      hidden={!isOpen}
      className={cn(
        'overflow-hidden transition-all duration-200',
        isOpen ? 'max-h-96' : 'max-h-0',
        className
      )}
    >
      <div className="p-4 pt-0">{children}</div>
    </div>
  )
}

// Usage
export function FAQItem() {
  return (
    <Disclosure>
      <DisclosureTrigger>
        What is your return policy?
      </DisclosureTrigger>
      <DisclosureContent>
        We offer a 30-day return policy for all items in original condition.
        Simply contact our support team to initiate a return.
      </DisclosureContent>
    </Disclosure>
  )
}
```

### Accessible Select/Dropdown

```tsx
// components/ui/select.tsx

'use client'

import * as React from 'react'
import * as SelectPrimitive from '@radix-ui/react-select'
import { Check, ChevronDown, ChevronUp } from 'lucide-react'
import { cn } from '@/lib/utils'

const Select = SelectPrimitive.Root
const SelectGroup = SelectPrimitive.Group
const SelectValue = SelectPrimitive.Value

const SelectTrigger = React.forwardRef<
  React.ElementRef<typeof SelectPrimitive.Trigger>,
  React.ComponentPropsWithoutRef<typeof SelectPrimitive.Trigger>
>(({ className, children, ...props }, ref) => (
  <SelectPrimitive.Trigger
    ref={ref}
    className={cn(
      'flex h-10 w-full items-center justify-between rounded-md border border-input bg-background px-3 py-2 text-sm',
      'ring-offset-background placeholder:text-muted-foreground',
      'focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2',
      'disabled:cursor-not-allowed disabled:opacity-50',
      '[&>span]:line-clamp-1',
      className
    )}
    {...props}
  >
    {children}
    <SelectPrimitive.Icon asChild>
      <ChevronDown className="h-4 w-4 opacity-50" aria-hidden="true" />
    </SelectPrimitive.Icon>
  </SelectPrimitive.Trigger>
))
SelectTrigger.displayName = SelectPrimitive.Trigger.displayName

const SelectContent = React.forwardRef<
  React.ElementRef<typeof SelectPrimitive.Content>,
  React.ComponentPropsWithoutRef<typeof SelectPrimitive.Content>
>(({ className, children, position = 'popper', ...props }, ref) => (
  <SelectPrimitive.Portal>
    <SelectPrimitive.Content
      ref={ref}
      className={cn(
        'relative z-50 max-h-96 min-w-[8rem] overflow-hidden rounded-md border bg-popover text-popover-foreground shadow-md',
        'data-[state=open]:animate-in data-[state=closed]:animate-out',
        'data-[state=closed]:fade-out-0 data-[state=open]:fade-in-0',
        'data-[state=closed]:zoom-out-95 data-[state=open]:zoom-in-95',
        'data-[side=bottom]:slide-in-from-top-2 data-[side=left]:slide-in-from-right-2',
        'data-[side=right]:slide-in-from-left-2 data-[side=top]:slide-in-from-bottom-2',
        position === 'popper' &&
          'data-[side=bottom]:translate-y-1 data-[side=left]:-translate-x-1 data-[side=right]:translate-x-1 data-[side=top]:-translate-y-1',
        className
      )}
      position={position}
      {...props}
    >
      <SelectScrollUpButton />
      <SelectPrimitive.Viewport
        className={cn(
          'p-1',
          position === 'popper' &&
            'h-[var(--radix-select-trigger-height)] w-full min-w-[var(--radix-select-trigger-width)]'
        )}
      >
        {children}
      </SelectPrimitive.Viewport>
      <SelectScrollDownButton />
    </SelectPrimitive.Content>
  </SelectPrimitive.Portal>
))
SelectContent.displayName = SelectPrimitive.Content.displayName

const SelectLabel = React.forwardRef<
  React.ElementRef<typeof SelectPrimitive.Label>,
  React.ComponentPropsWithoutRef<typeof SelectPrimitive.Label>
>(({ className, ...props }, ref) => (
  <SelectPrimitive.Label
    ref={ref}
    className={cn('py-1.5 pl-8 pr-2 text-sm font-semibold', className)}
    {...props}
  />
))
SelectLabel.displayName = SelectPrimitive.Label.displayName

const SelectItem = React.forwardRef<
  React.ElementRef<typeof SelectPrimitive.Item>,
  React.ComponentPropsWithoutRef<typeof SelectPrimitive.Item>
>(({ className, children, ...props }, ref) => (
  <SelectPrimitive.Item
    ref={ref}
    className={cn(
      'relative flex w-full cursor-default select-none items-center rounded-sm py-1.5 pl-8 pr-2 text-sm outline-none',
      'focus:bg-accent focus:text-accent-foreground',
      'data-[disabled]:pointer-events-none data-[disabled]:opacity-50',
      className
    )}
    {...props}
  >
    <span className="absolute left-2 flex h-3.5 w-3.5 items-center justify-center">
      <SelectPrimitive.ItemIndicator>
        <Check className="h-4 w-4" aria-hidden="true" />
      </SelectPrimitive.ItemIndicator>
    </span>
    <SelectPrimitive.ItemText>{children}</SelectPrimitive.ItemText>
  </SelectPrimitive.Item>
))
SelectItem.displayName = SelectPrimitive.Item.displayName

const SelectSeparator = React.forwardRef<
  React.ElementRef<typeof SelectPrimitive.Separator>,
  React.ComponentPropsWithoutRef<typeof SelectPrimitive.Separator>
>(({ className, ...props }, ref) => (
  <SelectPrimitive.Separator
    ref={ref}
    className={cn('-mx-1 my-1 h-px bg-muted', className)}
    {...props}
  />
))
SelectSeparator.displayName = SelectPrimitive.Separator.displayName

const SelectScrollUpButton = React.forwardRef<
  React.ElementRef<typeof SelectPrimitive.ScrollUpButton>,
  React.ComponentPropsWithoutRef<typeof SelectPrimitive.ScrollUpButton>
>(({ className, ...props }, ref) => (
  <SelectPrimitive.ScrollUpButton
    ref={ref}
    className={cn('flex cursor-default items-center justify-center py-1', className)}
    {...props}
  >
    <ChevronUp className="h-4 w-4" aria-hidden="true" />
  </SelectPrimitive.ScrollUpButton>
))
SelectScrollUpButton.displayName = SelectPrimitive.ScrollUpButton.displayName

const SelectScrollDownButton = React.forwardRef<
  React.ElementRef<typeof SelectPrimitive.ScrollDownButton>,
  React.ComponentPropsWithoutRef<typeof SelectPrimitive.ScrollDownButton>
>(({ className, ...props }, ref) => (
  <SelectPrimitive.ScrollDownButton
    ref={ref}
    className={cn('flex cursor-default items-center justify-center py-1', className)}
    {...props}
  >
    <ChevronDown className="h-4 w-4" aria-hidden="true" />
  </SelectPrimitive.ScrollDownButton>
))
SelectScrollDownButton.displayName = SelectPrimitive.ScrollDownButton.displayName

export {
  Select,
  SelectGroup,
  SelectValue,
  SelectTrigger,
  SelectContent,
  SelectLabel,
  SelectItem,
  SelectSeparator,
  SelectScrollUpButton,
  SelectScrollDownButton,
}

// Usage with proper labeling
export function CountrySelect() {
  const id = React.useId()

  return (
    <div>
      <label id={`${id}-label`} className="block text-sm font-medium mb-1">
        Country
      </label>
      <Select>
        <SelectTrigger aria-labelledby={`${id}-label`}>
          <SelectValue placeholder="Select a country" />
        </SelectTrigger>
        <SelectContent>
          <SelectGroup>
            <SelectLabel>North America</SelectLabel>
            <SelectItem value="us">United States</SelectItem>
            <SelectItem value="ca">Canada</SelectItem>
            <SelectItem value="mx">Mexico</SelectItem>
          </SelectGroup>
          <SelectSeparator />
          <SelectGroup>
            <SelectLabel>Europe</SelectLabel>
            <SelectItem value="uk">United Kingdom</SelectItem>
            <SelectItem value="de">Germany</SelectItem>
            <SelectItem value="fr">France</SelectItem>
          </SelectGroup>
        </SelectContent>
      </Select>
    </div>
  )
}
```

---

## 11. Legal Compliance

### Compliance Standards Overview

| Standard | Region | Level | Key Requirements |
|----------|--------|-------|------------------|
| ADA (Americans with Disabilities Act) | USA | N/A | Web accessibility for public accommodations |
| Section 508 | USA | WCAG 2.0 AA | Federal agency websites and contractors |
| EN 301 549 | EU | WCAG 2.1 AA | Public sector websites (EAA extends to private) |
| AODA (Accessibility for Ontarians) | Ontario, CA | WCAG 2.0 AA | Public and private organizations |
| ACA (Accessible Canada Act) | Canada | WCAG 2.1 AA | Federally regulated organizations |

### Compliance Deadlines

| Regulation | Effective Date | Applies To |
|------------|---------------|------------|
| EAA (European Accessibility Act) | June 28, 2025 | Products and services in EU market |
| WCAG 2.2 (W3C Recommendation) | October 5, 2023 | Voluntary, becoming standard |
| Section 508 Refresh | January 18, 2018 | US Federal agencies |
| AODA Final Compliance | January 1, 2021 | Organizations with 50+ employees |

### VPAT/ACR Documentation

When creating accessibility conformance reports:

```markdown
# Voluntary Product Accessibility Template (VPAT)

## Product Information
- Product Name: [Your Product]
- Version: [Version]
- Report Date: [Date]
- Contact: [accessibility@yourcompany.com]

## Evaluation Methods
- Automated testing with axe-core
- Manual testing with VoiceOver and NVDA
- Keyboard-only navigation testing

## WCAG 2.2 Level AA Conformance

### Perceivable

| Criterion | Level | Conformance | Remarks |
|-----------|-------|-------------|---------|
| 1.1.1 Non-text Content | A | Supports | All images have alt text |
| 1.2.1 Audio-only/Video-only | A | Supports | Transcripts provided |
| 1.3.1 Info and Relationships | A | Supports | Semantic HTML used |
| 1.4.1 Use of Color | A | Supports | Icons accompany color |
| 1.4.3 Contrast (Minimum) | AA | Supports | 4.5:1 ratio verified |
| 1.4.11 Non-text Contrast | AA | Supports | 3:1 for UI components |

### Operable

| Criterion | Level | Conformance | Remarks |
|-----------|-------|-------------|---------|
| 2.1.1 Keyboard | A | Supports | All functionality keyboard accessible |
| 2.1.2 No Keyboard Trap | A | Supports | Focus can always move |
| 2.4.1 Bypass Blocks | A | Supports | Skip links provided |
| 2.4.4 Link Purpose (In Context) | A | Supports | Descriptive link text |
| 2.4.7 Focus Visible | AA | Supports | Custom focus styles |

### Understandable

| Criterion | Level | Conformance | Remarks |
|-----------|-------|-------------|---------|
| 3.1.1 Language of Page | A | Supports | lang attribute set |
| 3.2.1 On Focus | A | Supports | No unexpected changes |
| 3.3.1 Error Identification | A | Supports | Errors announced |
| 3.3.2 Labels or Instructions | A | Supports | All inputs labeled |

### Robust

| Criterion | Level | Conformance | Remarks |
|-----------|-------|-------------|---------|
| 4.1.1 Parsing | A | N/A | Obsolete in WCAG 2.2 |
| 4.1.2 Name, Role, Value | A | Supports | ARIA correctly applied |
```

---

## 12. Common Mistakes

### 1. Click Handlers on Non-Interactive Elements

```tsx
// BAD: div is not keyboard accessible
<div onClick={handleClick}>
  Click me
</div>

// GOOD: Use a button
<button onClick={handleClick}>
  Click me
</button>

// GOOD: If you must use a div (rare), add keyboard support
<div
  role="button"
  tabIndex={0}
  onClick={handleClick}
  onKeyDown={(e) => {
    if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault()
      handleClick()
    }
  }}
>
  Click me
</div>
```

### 2. Missing Form Labels

```tsx
// BAD: No label association
<input type="text" placeholder="Email" />

// GOOD: Explicit label
<label htmlFor="email">Email</label>
<input id="email" type="text" />

// GOOD: Implicit label
<label>
  Email
  <input type="text" />
</label>

// GOOD: aria-label for icon buttons
<button aria-label="Search">
  <SearchIcon aria-hidden="true" />
</button>
```

### 3. Focus Loss on Route Changes

```tsx
// BAD: Focus is lost when content changes
function ProductList({ products }) {
  return (
    <div>
      {products.map(p => <ProductCard key={p.id} {...p} />)}
    </div>
  )
}

// GOOD: Manage focus when content changes
function ProductList({ products }) {
  const headingRef = useRef<HTMLHeadingElement>(null)

  useEffect(() => {
    // Move focus to heading when products change
    headingRef.current?.focus()
  }, [products])

  return (
    <div>
      <h2 ref={headingRef} tabIndex={-1}>
        {products.length} products found
      </h2>
      {products.map(p => <ProductCard key={p.id} {...p} />)}
    </div>
  )
}
```

### 4. Missing Skip Navigation

```tsx
// BAD: No way to skip repetitive navigation
<header>
  <nav>{/* 20 navigation links */}</nav>
</header>
<main>{/* Content */}</main>

// GOOD: Skip link as first focusable element
<a href="#main-content" className="sr-only focus:not-sr-only">
  Skip to main content
</a>
<header>
  <nav>{/* Navigation */}</nav>
</header>
<main id="main-content" tabIndex={-1}>
  {/* Content */}
</main>
```

### 5. Div Soup (Missing Semantic HTML)

```tsx
// BAD: No semantic meaning
<div class="header">
  <div class="nav">
    <div class="nav-item">Home</div>
  </div>
</div>
<div class="main">
  <div class="section">
    <div class="heading">Welcome</div>
  </div>
</div>

// GOOD: Semantic HTML
<header>
  <nav aria-label="Main">
    <ul>
      <li><a href="/">Home</a></li>
    </ul>
  </nav>
</header>
<main>
  <section aria-labelledby="welcome-heading">
    <h1 id="welcome-heading">Welcome</h1>
  </section>
</main>
```

### 6. Inaccessible Custom Controls

```tsx
// BAD: Custom checkbox with no accessibility
<div
  className={`checkbox ${checked ? 'checked' : ''}`}
  onClick={() => setChecked(!checked)}
>
  {checked && <CheckIcon />}
</div>

// GOOD: Accessible custom checkbox
<label className="flex items-center gap-2 cursor-pointer">
  <input
    type="checkbox"
    checked={checked}
    onChange={(e) => setChecked(e.target.checked)}
    className="sr-only peer"
  />
  <div className="w-5 h-5 border-2 rounded peer-checked:bg-blue-600 peer-checked:border-blue-600 peer-focus:ring-2 peer-focus:ring-offset-2 peer-focus:ring-blue-500">
    {checked && <CheckIcon className="text-white" aria-hidden="true" />}
  </div>
  <span>Accept terms</span>
</label>
```

### 7. Color-Only Indicators

```tsx
// BAD: Status indicated only by color
<span className={status === 'error' ? 'text-red-500' : 'text-green-500'}>
  {status}
</span>

// GOOD: Color AND icon/text
<span className={status === 'error' ? 'text-red-700' : 'text-green-700'}>
  {status === 'error' ? (
    <>
      <XCircleIcon aria-hidden="true" />
      <span>Error: </span>
    </>
  ) : (
    <>
      <CheckCircleIcon aria-hidden="true" />
      <span>Success: </span>
    </>
  )}
  {message}
</span>
```

### 8. Images Without Alt Text

```tsx
// BAD: Missing alt
<img src="/product.jpg" />

// BAD: Meaningless alt
<img src="/product.jpg" alt="image" />
<img src="/product.jpg" alt="photo" />

// GOOD: Descriptive alt
<img src="/product.jpg" alt="Blue running shoes with white soles" />

// GOOD: Decorative image
<img src="/decorative.svg" alt="" aria-hidden="true" />
```

### 9. Auto-Playing Media

```tsx
// BAD: Auto-playing video with sound
<video autoPlay src="/promo.mp4" />

// GOOD: Muted autoplay with controls
<video autoPlay muted controls src="/promo.mp4">
  <track kind="captions" src="/captions.vtt" label="English" />
</video>

// BETTER: No autoplay, let user control
<video controls src="/promo.mp4">
  <track kind="captions" src="/captions.vtt" label="English" default />
</video>
```

### 10. Timeout Without Warning

```tsx
// BAD: Session expires without warning
useEffect(() => {
  const timeout = setTimeout(logout, 30 * 60 * 1000)
  return () => clearTimeout(timeout)
}, [])

// GOOD: Warn user before timeout
function SessionTimeout() {
  const [showWarning, setShowWarning] = useState(false)
  const [timeLeft, setTimeLeft] = useState(0)

  useEffect(() => {
    // Warn 2 minutes before timeout
    const warningTimer = setTimeout(() => {
      setShowWarning(true)
      setTimeLeft(120)
    }, 28 * 60 * 1000)

    return () => clearTimeout(warningTimer)
  }, [])

  if (!showWarning) return null

  return (
    <Dialog open={showWarning}>
      <DialogContent role="alertdialog">
        <DialogTitle>Session Expiring</DialogTitle>
        <DialogDescription>
          Your session will expire in {timeLeft} seconds.
          Would you like to continue?
        </DialogDescription>
        <button onClick={extendSession}>Continue Session</button>
        <button onClick={logout}>Log Out</button>
      </DialogContent>
    </Dialog>
  )
}
```

---

## 13. Audit Checklist

Use this checklist when auditing a Next.js application for WCAG 2.2 AA compliance.

### Document Structure

- [ ] `<html>` has a valid `lang` attribute
- [ ] Page has exactly one `<h1>`
- [ ] Heading hierarchy is logical (no skipped levels)
- [ ] Page title is descriptive and unique
- [ ] Document structure uses semantic HTML

### Landmarks

- [ ] Page has `<main>` landmark
- [ ] Page has `<header>` with navigation
- [ ] Page has `<footer>`
- [ ] Navigation has `<nav>` with `aria-label` if multiple
- [ ] Complementary content uses `<aside>`
- [ ] All content is within landmarks

### Images

- [ ] All `<img>` elements have `alt` attribute
- [ ] Informative images have descriptive alt text
- [ ] Decorative images have `alt=""`
- [ ] Complex images have extended descriptions
- [ ] Background images conveying info have text alternatives

### Links

- [ ] All links have accessible names
- [ ] Link text describes destination
- [ ] No "click here" or "read more" links without context
- [ ] Links opening new windows warn users
- [ ] Skip link is first focusable element

### Forms

- [ ] All inputs have associated labels
- [ ] Required fields are indicated (not just with color)
- [ ] Error messages are associated with fields (`aria-describedby`)
- [ ] Error summary appears and receives focus on submission
- [ ] Form instructions are provided where needed
- [ ] Related fields are grouped with `<fieldset>` and `<legend>`

### Color and Contrast

- [ ] Text contrast is at least 4.5:1 (3:1 for large text)
- [ ] UI component contrast is at least 3:1
- [ ] Information is not conveyed by color alone
- [ ] Focus indicators are visible
- [ ] Links are distinguishable from text

### Keyboard

- [ ] All functionality is keyboard accessible
- [ ] Focus order is logical
- [ ] Focus is visible at all times
- [ ] No keyboard traps
- [ ] Modal dialogs trap focus correctly
- [ ] Focus returns to trigger when dialogs close
- [ ] Skip links work correctly

### Dynamic Content

- [ ] Route changes are announced
- [ ] Loading states are announced
- [ ] Error messages are announced immediately
- [ ] Toasts/notifications use live regions
- [ ] Content updates don't cause unexpected focus changes

### Media

- [ ] Videos have captions
- [ ] Audio has transcripts
- [ ] No auto-playing audio
- [ ] Media controls are keyboard accessible
- [ ] Time-based media can be paused

### Interactive Components

- [ ] Dialogs have accessible name (DialogTitle)
- [ ] Dialogs have accessible description (DialogDescription)
- [ ] Tabs announce selected state
- [ ] Accordions announce expanded/collapsed state
- [ ] Menus are keyboard navigable
- [ ] Custom controls have correct ARIA roles

### Testing Verification

- [ ] Passes automated axe-core tests
- [ ] Passes eslint-plugin-jsx-a11y
- [ ] Tested with VoiceOver (macOS)
- [ ] Tested with NVDA (Windows)
- [ ] Tested with keyboard only
- [ ] Tested at 200% zoom
- [ ] Tested with reduced motion preference

---

## Quick Reference

### Essential ARIA Attributes

| Attribute | Purpose | Example |
|-----------|---------|---------|
| `aria-label` | Accessible name when no visible text | `<button aria-label="Close">X</button>` |
| `aria-labelledby` | Reference to element providing name | `<section aria-labelledby="heading-id">` |
| `aria-describedby` | Reference to element providing description | `<input aria-describedby="hint-id">` |
| `aria-expanded` | Expanded/collapsed state | `<button aria-expanded="false">` |
| `aria-controls` | Element this one controls | `<button aria-controls="menu-id">` |
| `aria-hidden` | Hide from assistive technology | `<span aria-hidden="true">` |
| `aria-live` | Announce dynamic changes | `<div aria-live="polite">` |
| `aria-busy` | Content is loading | `<div aria-busy="true">` |
| `aria-invalid` | Input validation state | `<input aria-invalid="true">` |
| `aria-required` | Field is required | `<input aria-required="true">` |
| `role` | Override element semantics | `<div role="button">` |

### Keyboard Interaction Patterns

| Component | Keys |
|-----------|------|
| Button | Enter, Space |
| Link | Enter |
| Checkbox | Space |
| Radio Group | Arrow keys |
| Tabs | Arrow keys, Home, End |
| Menu | Arrow keys, Enter, Escape |
| Dialog | Tab (trapped), Escape to close |
| Combobox | Arrow keys, Enter, Escape |

### Screen Reader Commands

| Action | VoiceOver (macOS) | NVDA (Windows) |
|--------|-------------------|----------------|
| Start/Stop | Cmd + F5 | Ctrl + Alt + N |
| Next heading | VO + Cmd + H | H |
| Next landmark | VO + Cmd + U | D |
| Next link | VO + Cmd + L | K |
| Next form field | VO + Cmd + J | F |
| Read all | VO + A | NVDA + Down |
| Stop reading | Ctrl | Ctrl |

---

## Resources

- [WCAG 2.2 Guidelines](https://www.w3.org/TR/WCAG22/)
- [WAI-ARIA 1.2 Specification](https://www.w3.org/TR/wai-aria-1.2/)
- [ARIA Authoring Practices Guide](https://www.w3.org/WAI/ARIA/apg/)
- [axe-core Rules](https://dequeuniversity.com/rules/axe/)
- [Radix UI Primitives](https://www.radix-ui.com/)
- [shadcn/ui Components](https://ui.shadcn.com/)
