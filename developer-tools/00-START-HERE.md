# Developer Tools — Day 22

The map of this folder, and the one idea to hold while you read it.

| File | What it answers |
|---|---|
| `01-handoffs-reference.md` | How do handoffs actually work? |
| `02-guardrails-reference.md` | What are guardrails, and what are the options? |
| `03-reading-the-handoff.md` | How do I see which specialist it chose, and why? |
| `04-experiments.md` | Things to try that teach something |
| `05-troubleshooting.md` | It broke, or routed wrongly. Now what? |
| `06-limitations.md` | What this pattern cannot do |
| `07-setup-guide.md` | How do I get it running, on any platform? |
| `08-writing-handoff-descriptions.md` | How do I write the sentence that decides the route? |
| `09-comparison-with-one-agent.md` | Was splitting into four agents worth it? |

New here? Read in this order: `07` to get it running, `01` and `03` to
understand what you see, `04` to break it, `08` to fix it properly.

---

## The one sentence for today

> A handoff is a tool call. The tool happens to be another agent.

It is not a new mechanism. Everything you learned about writing tool
descriptions on Day 13 decides whether your handoffs work.

---

## The mental model

Picture a message moving through three gates:

    guest message
         │
         ▼
    1. GUARDRAIL      topic_checker: is this about the guesthouse?
         │            no  → polite refusal, nothing else runs
         ▼ yes
    2. TRIAGE         reads three tool names + descriptions, picks one
         │            transfer_to_booking_agent / complaint / general
         ▼
    3. SPECIALIST     answers, using its own instructions and rules
         │
         ▼
    reply   (and "✔ Answered by: <specialist>")

Gate 1 is code — it cannot be argued with. Gates 2 and 3 are models — they
are only as good as the text you give them. When something goes wrong, find
which gate it went wrong at first.
