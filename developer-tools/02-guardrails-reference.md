# 2. Guardrails

## What a guardrail is

A check that runs alongside your agent. Two kinds.

| Kind | When it runs | What it is for |
|---|---|---|
| **Input guardrail** | Before the agent sees the message | Stopping requests you do not want to process at all |
| **Output guardrail** | Before the answer reaches the user | Catching answers that should not be sent |

---

## Why an input guardrail saves money

Picture a support system with five specialists and expensive tools. Someone
sends it a homework question.

**Without a guardrail:** triage runs, a handoff happens, a specialist thinks
hard about something irrelevant, tools get called. You pay for all of it.

**With a guardrail:** a small cheap model checks the message first, decides it
is off-topic, and the run stops. **The expensive part never starts** — but
only if the check really runs *first*. See the next section.

---

## Parallel or first? The guardrail trade-off

By default, the SDK starts the guardrail and the agent **at the same time**
(`run_in_parallel=True`). We tested what that means:

| Setting | Off-topic message | Triage agent model calls made |
|---|---|---|
| `run_in_parallel=True` (the default) | Blocked | **1** — you still paid for it |
| `run_in_parallel=False` (this project) | Blocked | **0** — the check ran first |

| | Parallel (default) | First |
|---|---|---|
| Normal messages | Faster — nobody waits for the check | A short wait while the check runs |
| Blocked messages | Still cost the agent's first model call | Cost nothing extra |
| Choose it when… | Speed matters most, and blocked messages are rare | Cost matters, or the agent's first step is expensive or risky |

This project uses `@input_guardrail(run_in_parallel=False)`.

**The lesson:** a framework's *default* is a choice someone else made for
you. Find out what it is before you rely on it.

---

## What an output guardrail catches

- An answer that leaks something it should not — a key, another customer's data
- An answer in the wrong shape, when your code expects a fixed shape
- An answer that promises something the business cannot do — a refund, a discount

---

## Tripwires

When a guardrail fires, it is called a **tripwire**. The run stops and raises
an exception, and you decide what happens next:

    try:
        result = await Runner.run(triage_agent, message)
        return result.final_output
    except InputGuardrailTripwireTriggered:
        return "Sorry — I can only help with questions about the guesthouse."

Options at that point: a polite refusal, a message to a human, a log entry,
or all three.

---

## Guardrails are not instructions

This is the idea underneath all of Lesson 8.

| | In the system prompt | As a guardrail |
|---|---|---|
| Where it lives | Inside the model's instructions | Outside the model, in your code |
| Can it be argued with? | Yes | No — it is an `if` statement |
| Does it always run? | Only if the model attends to it | Every time, without exception |
| Cost when it blocks | You have already paid | You stop before the expensive part |

> A rule you can talk a model out of is not a rule. A rule in code is.

You have met this before. It is written on the **Check and Stamp** node of
your Project 1 workflow, where the escalation rule lives in JavaScript rather
than in the prompt.

---

## Choosing the model for the checker

Look at `guardrail.py`. The `topic_checker` uses a small cheap model on
purpose.

You do not need an expensive model to answer *"is this about a hotel?"* —
and if your guardrail costs as much as the thing it is protecting, it has
failed at its main job.

This is Day 3's model-tiering advice, in a new place.
