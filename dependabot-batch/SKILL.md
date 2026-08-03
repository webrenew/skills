---
name: dependabot-batch
description: Use when a repo has several open Dependabot PRs and you want them collapsed into ONE branch and ONE PR instead of merging them one at a time — "batch the dependabot PRs", "combine all dependency updates", "fix all dependabot suggestions in one branch", "too many dependabot PRs", "our CI/preview deploys are burning money on dependabot". Also use when asked to clear open Dependabot security alerts, or when a dependency-update PR needs verifying before merge. Covers any ecosystem Dependabot supports (npm/pnpm/yarn/bun, pip, cargo, go, bundler, maven, github-actions, docker), and handles the case where some suggested bumps are breaking and must be held back.
---

# Batching Dependabot PRs

## Why this exists

Dependabot opens one PR per update. Each one triggers a full CI run and, on
platforms like Vercel or Netlify, a preview deployment. Ten open PRs means ten
builds for changes that will all end up in the same lockfile anyway — and they
serialize badly, because every merge invalidates the others' lockfiles and
forces a rebase.

Collapsing them into a single branch turns N build cycles into one, and gives
you a single place to verify the combined dependency graph — which is what
actually ships. Bumps that pass in isolation can still conflict with each other;
batching surfaces that before merge rather than after.

## The shape of the work

Gather → apply manifest edits by hand → regenerate the lock → run every gate →
drop only what's genuinely broken → one PR that documents what was held back.

The one thing to internalize: **do not merge or cherry-pick the Dependabot
branches.** They each rewrote the lockfile against a different base, so combining
them produces conflicts that are tedious and easy to resolve wrongly. Take only
the *manifest* version numbers from them and let the package manager rebuild the
lock once, from a clean state. The lockfile is derived output — regenerate it,
never hand-merge it.

## 1. Gather everything

```bash
gh pr list --state open --author "app/dependabot" \
  --json number,title,headRefName,createdAt --limit 100
gh api repos/{owner}/{repo}/dependabot/alerts \
  --jq '.[] | select(.state=="open") | {num:.number, pkg:.dependency.package.name,
        sev:.security_advisory.severity,
        vuln:.security_vulnerability.vulnerable_version_range,
        patched:.security_vulnerability.first_patched_version.identifier}'
```

Pull alerts too, not just PRs. Alerts on transitive dependencies often have no PR
at all — they're fixed by an override/resolution/constraint, and folding them in
here costs nothing extra.

Then read each PR's manifest change (ignore the lockfile half of the diff):

```bash
gh pr diff <N> -- package.json      # or Cargo.toml, go.mod, requirements.txt…
```

**Multi-account `gh` gotcha.** If `gh` errors with `Could not resolve to a
Repository`, the active account can't see this repo. Don't switch the global
account — that's shared state you'd be mutating out from under the user. Scope a
token to the command instead:

```bash
export GH_TOKEN=$(gh auth token -u <account-that-can-see-it>)
```

## 2. Branch off the *remote* default branch

```bash
git fetch origin --prune
git checkout -b chore/dependabot-batch-<date> origin/main
```

`origin/main`, not local `main`. Dependabot builds its PRs against the current
remote head, so a stale local checkout will silently give you versions older than
what the PRs assumed — and the resulting lockfile won't match anything.

## 3. Apply the manifest edits, then regenerate the lock

Edit the version specifiers by hand to match what each PR proposed, add any
override/resolution needed for the alerts (see below), then rebuild the lock with
the project's own package manager — the one its lockfile implies. Never mix
managers, never hand-edit a lockfile.

| Manager | Regenerate |
|---|---|
| pnpm | `pnpm install --no-frozen-lockfile` |
| npm | `npm install` |
| yarn | `yarn install` |
| bun | `bun install` |
| cargo | `cargo update -p <crate> --precise <ver>` |
| go | `go get <mod>@<ver> && go mod tidy` |
| pip | `pip-compile` (or the project's lock tool) |

Installs can block on a TTY prompt, which hangs a non-interactive session. If one
stalls, re-run it non-interactively — e.g. pnpm's modules-purge confirmation
clears with `--config.confirmModulesPurge=false`; most managers respect `CI=1`.

### Security alerts: check the override actually covers the patch

The subtle failure worth slowing down for. A repo can already carry an override
for a package and *still* be vulnerable, because the override's boundary predates
the advisory's fix:

```jsonc
// override says "anything below 1.1.16 → bump to 1.1.16"
"brace-expansion@<1.1.16": ">=1.1.16 <2"
// but the advisory is only patched in 1.1.17 — so 1.1.16 resolves, and it's vulnerable
```

Compare each alert's `first_patched_version` against the existing constraint and
widen it if the constraint stops short. An override that looks like it's handling
a package is not evidence that it's handling *this* advisory.

## 4. Run every gate, and read failures carefully

Run the project's real commands — read `package.json` scripts / `Makefile` /
`justfile` rather than assuming `npm test`. Typically: typecheck, lint, tests,
production build.

Two failure classes look alike and must not be confused:

- **Environment failures** — missing secrets, absent services, no network. A
  local build dying on `Missing env var: X` is not a dependency regression. Prove
  it by re-running with placeholder values for the required vars; if it then
  completes, the dependency graph is fine. Collect the names with something like
  `grep -rho 'process\.env\.[A-Z0-9_]*' src | sort -u`, and use obviously fake
  values (`https://example.invalid`, `dummy`) — never real credentials, and never
  commit them.
- **Real regressions** — the new version genuinely broke something. Fix or hold
  back (next section).

For a **major** bump of a runtime dependency, a green typecheck is necessary but
not sufficient. Read the installed package's own types and confirm the props or
functions your call sites use still exist and still mean the same thing:

```bash
node -e "console.log(JSON.stringify(require('./node_modules/<pkg>/package.json').exports,null,1))"
grep -E "propA|propB" node_modules/<pkg>/dist/*.d.ts
```

Also check the new `engines` / MSRV / language-version floor against what CI and
production actually run.

## 5. Hold back only what's broken

When one bump fails, drop *that one* back to its previous version and keep
everything else. Abandoning the whole batch over a single incompatible package
throws away a dozen good updates, and the next Dependabot run just re-proposes
them all.

Dependabot has no view of your framework's constraints, so it will happily suggest
a version your framework rejects. A real example:

```
TypeScript 7.0.2 does not provide the compiler API required by Next.js.
```

Quote the exact error in the commit and the PR. It's the thing that saves the next
person from re-attempting the same bump in three weeks, and it tells you exactly
what has to change upstream before it's viable.

## 6. Commit, PR, and close the originals

Commit the manifest and lockfile together — they're one atomic change. Reference
the superseded PR numbers and state the held-back items with their reason.

The PR body carries the review burden, since the diff itself is mostly
unreviewable lockfile churn. Include:

- a table of superseded PRs and alerts
- what changed, grouped as dev vs production dependencies (production bumps are
  the ones that can reach users)
- what was held back, with the verbatim error
- a test plan listing the commands you ran and their actual results
- any check a human still needs to do — e.g. eyeballing a preview deploy after a
  major UI-library bump, which no automated gate covers

Then close the originals. `Closes #N` does **not** close a pull request — that
syntax only works on issues. Dependabot does eventually close its own PRs once it
sees the bumps on the default branch, but "eventually" means they keep running CI
and preview builds until then, which is the cost you were trying to avoid. Close
them explicitly with a pointer:

```bash
gh pr close <N> --comment "Superseded by #<batch-pr>, which batched every open
Dependabot suggestion into one branch."
```

Follow the repo's conventions for merging (many set `gh pr merge --auto --squash`).
If the batch contains a major bump to something user-visible and no automated gate
covers it, say so plainly rather than letting auto-merge imply it was verified.

## Verify it worked

```bash
gh pr list --state open --author "app/dependabot"                  # expect empty
gh api repos/{owner}/{repo}/dependabot/alerts \
  --jq '[.[] | select(.state=="open")] | length'                   # expect 0
```

If an alert is still open after merge, the override didn't take — re-check the
resolved version in the lockfile rather than trusting the constraint you wrote.

## Reporting back

State what merged, what was held back and why, and what still needs a human eye.
A held-back bump is a real, open loop — name it rather than letting "all
Dependabot PRs handled" imply otherwise.
