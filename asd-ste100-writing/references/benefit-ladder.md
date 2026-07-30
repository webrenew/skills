# The benefit ladder

STE makes copy unambiguous. It does not make copy matter. This is the other half.

The reader does not want the capability. They want their life back. Every piece of copy climbs from what the product does to what the reader gets, and it must reach the top before the reader loses interest — which is roughly one sentence.

## The four primitives

Everything a product gives a person reduces to one of four. Name which one before writing the line.

**Freedom** — the reader stops depending on someone. No agency, no vendor, no gatekeeper, no waiting for a person to reply. Signals: you do it yourself, you own it, you leave whenever you want, no contract, no phone call.

**Peace of mind** — a bad outcome the reader was carrying is now impossible or handled. Signals: nothing breaks silently, nothing double-books, nothing is lost, you find out before the customer does, you can stop checking.

**Time back** — hours returned, in a unit the reader recognizes. Signals: minutes instead of days, one place instead of six tabs, done while you sleep, never again.

**Power** — the reader can now do something that was out of reach, or beat someone who used to beat them. Signals: compete with the big operator, see what they see, change it yourself, at any scale.

Two secondary primitives are allowed when they are literally true and specific: **money kept** (a number, not "savings") and **standing** (the reader looks competent to their own customers). Do not reach for these first — they are usually a restatement of one of the four.

## The "so what" chain

Take the feature. Ask "so what?" until a primitive appears. Three hops maximum.

```
Feature → what it does → what it removes or gives → primitive
```

If the chain runs past three hops, the feature is too deep to lead with. Put it in the docs and lead with the feature above it in the stack.

If the chain reaches no primitive at all, the feature does not go in the copy. This is the useful part of the method: it deletes things.

## Structure of a benefit line

1. **Lead sentence lands on the primitive.** Concrete, second person, present tense, under 12 words for a headline.
2. **Second sentence gives the mechanism.** This is where the technical capability finally appears, as evidence.
3. **Third sentence gives the number**, if there is one.

Never invert this. A capability first and a benefit bolted to the end ("...so you can focus on what matters") reads as an apology for the first half of the sentence.

## Worked examples

**Channel sync**
- Feature: two-way ARI sync, sub-minute propagation, 40 channels
- Chain: rates and availability match everywhere → no double bookings, no stale rates → **peace of mind**
- Copy: "You never take two bookings for the same night. Rates and availability match on all 40 channels, in less than a minute."

**DIY credit repair**
- Feature: AI letter generation against bureau dispute rules
- Chain: the letters are written for you → you do not hire a repair company → **freedom**, **money kept**
- Copy: "Fix your own credit. You do not need to pay a repair company $99 a month. The letters take ten minutes, and we know the rules the bureaus follow."

**Timeshare exit**
- Feature: state-specific rescission letter generator
- Chain: the letter is correct for your state → you send it inside the deadline → the contract ends → **freedom**
- Copy: "End the contract yourself, inside the cancellation window. The letter matches the law in your state. You send it; nobody takes a fee."

**Terminal agent orchestration**
- Feature: multiplexed agent sessions in a TUI
- Chain: many agents run at once → you watch all of them in one screen → you stop babysitting one at a time → **power**, **time back**
- Copy: "Run twelve agents and watch all of them. One screen, no tab switching. You keep the terminal you already use."

## Anti-patterns

**The bolt-on.** "Automated sync so you can focus on growing your business." The benefit is generic and could follow any feature. Delete it, or make it specific.

**The abstraction ladder taken too far.** "Freedom." alone, in 96pt type, over a photo. The primitive must be attached to the actual thing it frees the reader from, or it is decoration.

**The feature disguised as a benefit.** "Get powerful insights into your portfolio." Insights are not a primitive. So what? → you see which unit loses money → you fix it → **power**. Write that instead.

**Benefit inflation.** Claiming peace of mind for something that only half-works. The reader finds out in week two and never trusts the page again. Only claim the primitive the product actually delivers.

**Us-language.** "We built", "our platform", "we are excited to". Count the "we"s against the "you"s. The reader is not here for the company.

## Checks before shipping

- Does the first sentence of every block name a primitive, or the concrete thing it removes?
- Is every claim checkable — a number, a named outcome, a thing that stops happening?
- Could a competitor paste any line onto their site unchanged? If yes, it says nothing.
- Are there more "you"s than "we"s?
- Did any bullet fail the three-hop chain and survive anyway? Cut it.
