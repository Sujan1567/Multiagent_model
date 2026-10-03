# 1. Handoffs

## What happens underneath

When you write this:

    triage_agent = Agent(
        name="Triage agent",
        instructions="...",
        handoffs=[booking_agent, complaint_agent, general_agent],
    )

the framework shows those three agents to the model **as tools**. The model
chooses one the same way it chooses any tool — by reading its name and its
description. When it chooses, control moves across, and that agent finishes
the job.

---

## What the model sees

| What it reads | Where it comes from |
|---|---|
| The specialist's name | `name="Booking agent"` |
| When to use it | `handoff_description="..."` |

**That is all.** It does not see the specialist's instructions, its tools, or
its code.

If you leave `handoff_description` empty, the model has only the name to go
on — and `"Agent 2"` tells it nothing.

---

## Writing a good handoff_description

The same two halves as any tool description:

    handoff_description=(
        "Handles new bookings, changing dates, checking availability and "
        "cancellations. Use this for anything about rooms or dates. "
        "Do NOT use this for complaints about a stay that already happened."
    )

**Say when to use it. Say when not to.** The second half is what stops two
similar specialists becoming indistinguishable.

---

## The triage pattern

| Part | Its job |
|---|---|
| Triage agent | Reads the request. Chooses a specialist. Hands over. **Nothing else** |
| Specialists | Each knows one area, and carries only the tools for that area |

### Why this is useful, not just tidy

- Each specialist has a short focused instruction instead of one enormous one
- Each carries only its own tools — Day 13 showed accuracy falls past 15–20
- You can give different specialists different models
- You can change one specialist without touching the others

### The instruction that matters

    "Do NOT answer the guest's question yourself, even if you know the
     answer. Always hand off."

Without this line, a triage agent will often answer the question itself,
because answering looks more helpful than routing.

---

## When a handoff is worth it

| Situation | Handoff? | Why |
|---|---|---|
| Different jobs needing different tools | Yes | Each agent stays small |
| The instruction is filling up with "if the user asks about X" | Yes | That is a routing problem |
| One part needs a cheap model, another an expensive one | Yes | Model is set per agent |
| The steps are the same every time | No | That is a workflow |
| It sounds more advanced | No | Day 5, still |

The cost of a handoff is real: another model call, more latency, and one more
place for the wrong choice. **Default to one agent. Split when you can name
what it fixes.**
