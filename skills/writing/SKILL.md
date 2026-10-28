---
name: writing
description: 'Writing prose for human readers. Load it before drafting, editing or reviewing any of these, however short: an email, chat message or reply the owner sends; a README or docs page; a technical explanation, plan, report or spec; or a blog post, landing page or announcement. Not for your own chat replies to the user.'
---

# Writing

One skill for prose that people read. Pick the mode by who reads the text and what they do after reading it, read that mode's file, and apply the shared rules below to every mode.

Before returning any text, check it and your chat reply around it for AI tells. In the docs and marketing modes, whose text the public reads, also read the catalogue in [`../humanizer/SKILL.md`](../humanizer/SKILL.md) (`<this skill's folder>/../humanizer/SKILL.md`) by itself and in full, with the Read tool or by loading the `humanizer` skill: never in one command with other files, never through `head` or a grep of its headings.

These five tells most often survive a rewrite:

- §1 Not X but Y: a contrast whose negative half denies something nobody claimed.
- §2 Closers: a last line or fragment that repeats the point instead of adding to it.
- §6 Triads: three items or examples where the meaning has fewer parts.
- §8 Dashes: an em or en dash outside code, where a period, comma, colon or parentheses fits.
- §19 Bold labels: list items that each open with a bold label and a colon, or bold that marks nothing. A bold full sentence that opens an item with its verdict ("**p95 fell 38%.** Batched lookups…") is a claim, not a label, and stays.

## Route

| Reader, and what the text is for | Read |
|---|---|
| Someone you write to as the owner: an email, chat message, reply or comment | [communication.md](communication.md) |
| People using or building on a product: a README, docs page, guide, reference or changelog | [docs.md](docs.md) |
| A colleague or the owner who must understand or decide: an explanation, plan, report, spec or postmortem | [technical.md](technical.md) |
| A public audience you want to win over: a blog post, landing page, announcement or launch post | [marketing.md](marketing.md) |
| An agent: an `AGENTS.md`, `CLAUDE.md`, skill, subagent brief or prompt | the `writing-for-agents` skill instead of this one |

When two rows fit (an announcement sent as an email), pick by the reader's next action. Pasted text that only needs its AI tells removed goes straight to the `humanizer` skill.

Done when you have read exactly one mode file, or handed off.

## Shared rules

1. **The point comes first.** Name the reader and what they must know or do after reading. The answer, ask or decision opens the text; supporting detail follows.
2. **Precise terms in plain sentences.** Name each thing by the term a practitioner uses for it ("counterexample", "cross-file rule", "p95 latency"), and keep that term throughout. When the reader may not know a term, define it in a clause where it first appears, then use the term itself: a paraphrase in its place is longer and less precise. Keep the plainness in the syntax: full sentences that keep the reasoning between facts, the "because" and the "so". Cut what the reader already has: background they know, restatements, and announcements of what comes next.
3. **Facts trace to a source.** Every name, number, date, quote, commitment and claim comes from the user, the repo, or something you read or ran. A gap becomes a question or a visible placeholder (`[confirm: launch date]`), never a plausible guess.
4. **Specific beats general.** Numbers with units over adjectives, the real symbol, file or command over a description of it, one concrete example over an abstraction.
5. **Match the voice that already exists.** A writing sample, the thread you are replying in, or the repo's existing docs set sentence length, punctuation and terms. Use the repo's glossary terms when it has a glossary. With none of these, write plain and direct.
6. **Finish with the AI-tell pass.** Check your draft for the five tells above, and against the whole catalogue when it applies: mark the tells strongest first, rewrite the sentences around them, then search the text and your reply again for the five tells above, and confirm the rewrite added or dropped no fact. Done when a full read of the text and the reply finds none of the five tells, and no §1 to §5 tell when you read the catalogue.
