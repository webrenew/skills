# ASD-STE100 rules, applied to product copy

The spec has nine sections of writing rules plus the dictionary. Below is each section condensed, with the translation to product and marketing copy. Where the spec is stricter than product copy can bear, the deviation is marked **[relaxed]** and bounded.

## Contents

1. Words
2. Noun phrases
3. Verbs
4. Sentences
5. Procedures
6. Descriptive writing
7. Warnings and cautions
8. Punctuation
9. Writing practices

---

## 1. Words

- Use only approved words, in the approved part of speech, with the approved meaning.
- One concept, one word. Never vary terminology for style. Elegant variation is the single most common cause of reader confusion.
- One word, one concept. If "run" means "execute a job", it never also means "operate the business".
- Technical names are exempt from the dictionary, but each must be defined once and then used identically.
- Do not use a technical name as a verb. "Onboard the customer" → "Do the onboarding for the customer" or "Set up the customer".
- No slang, no idiom, no metaphor that a non-native reader would have to decode. "Out of the box", "heavy lifting", "under the hood", "moving the needle", "low-hanging fruit" all fail.
- **[relaxed]** Marketing copy may use the benefit nouns in `benefit-ladder.md` and may use one metaphor per page if it is culturally neutral and explained by its context.

## 2. Noun phrases

- Maximum three nouns in a row. Break longer stacks with prepositions and articles.
  - "guest reservation cancellation policy update" → "an update to the cancellation policy for guest reservations"
- Keep articles. "Open Settings page" → "Open the Settings page."
- Do not drop "that". "Make sure the file is saved" → "Make sure that the file is saved."
- Avoid stacked possessives and long chains of "of".

## 3. Verbs

- Approved forms only: infinitive, imperative, simple present, simple past, simple future, and past participle used as an adjective.
- No `-ing` forms except inside a fixed technical name ("booking engine", "landing page").
  - "Managing your calendar is easy" → "You manage your calendar in one place."
  - "By connecting Stripe, you can..." → "Connect Stripe. You can then..."
- No perfect or continuous tenses. "We have been working" → "We work." "It will be running" → "It runs."
- Active voice everywhere. Passive hides the actor, and the actor is usually the reason the sentence exists.
  - "Payouts are processed nightly" → "We pay out every night."
- Put the verb early. Long subject phrases before the verb force the reader to hold state.
- Do not turn verbs into nouns. "Perform a calculation of" → "calculate". "Give consideration to" → "consider" → better: "think about".

## 4. Sentences

- Procedural: 20 words maximum. Descriptive and marketing: 25 words maximum. Headlines: 12.
- One idea per sentence. Every "and" that joins two thoughts is a period in disguise.
- Vary length deliberately. Twelve consecutive short sentences read like a robot and lose the reader as surely as one long one.
- Start with the topic, not with a subordinate clause. Front-load.
- Use a vertical list when there are more than three parallel items, or when the sentence would otherwise exceed the cap.
- Do not use parentheses to smuggle in a second sentence. Either it matters, or it goes.

## 5. Procedures

- One instruction per step. A step with two verbs is two steps.
- Start each step with the imperative verb. "Click Save" not "You should now click Save."
- Give the condition before the action. "If the sync fails, open the log." Not the reverse — the reader must know whether to keep reading before they act.
- Give a reason when the step is not obvious, in a separate sentence.
- Use the same step structure across the whole document.

## 6. Descriptive writing

- Six sentences maximum per paragraph. Web copy: three.
- One topic per paragraph, announced in the first sentence.
- Vary construction, but never at the cost of terminology consistency.
- Prefer the concrete to the abstract at every level: name the thing, name the number, name the person who acts.

## 7. Warnings and cautions

Product equivalents are error messages, destructive-action confirmations, and billing notices. The structure holds:

- The warning comes before the action, never after.
- State the condition first, then the command: "If the file is open in another program, the save will fail. Close the other program."
- Start with a command, not a description of the danger.
- Say what happens. "This cannot be undone" beats "Proceed with caution."
- One warning covers one hazard.

## 8. Punctuation

- Use standard punctuation only. No em-dash chains, no ellipses for tone, no exclamation marks.
- Hyphenate compound modifiers where the spec allows: "two-way sync", "read-only key".
- Avoid the slash. "and/or" is banned; pick one, or write both.
- Avoid the colon inside a sentence when a period would do.
- Serial comma always.

## 9. Writing practices

- Spell out abbreviations on first use, then use the abbreviation consistently. Do not switch back and forth.
- Write numbers as digits, including one through nine, in technical contexts. Keep "one" as a word only in idiomatic use.
- Use the international date format or spell the month. "03/04" is ambiguous across regions and STE exists precisely to remove that class of failure.
- Give units every time.
- Keep the same word order across parallel items in a list.
- Do not use footnotes for anything the reader needs.

---

## Fast self-check

Read the draft once against these six questions. Most violations fall out.

1. Does any sentence pass the word cap?
2. Does any word appear in two senses, or any concept under two words?
3. Is there an `-ing`, a passive, or a perfect tense?
4. Is there a stack of four or more nouns?
5. Could a competitor paste any sentence onto their page unchanged?
6. Does the first sentence of each block land on a human benefit?
