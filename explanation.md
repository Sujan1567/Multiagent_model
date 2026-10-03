# How the guesthouse router works

This walks through `agents_setup.py` (the four agents), `guardrail.py` (the
check that runs before them) and `guesthouse_router.py` (the code that runs
one message through both), block by block.

## How each block is laid out below

For every block you will see, in this order:

1. the code itself,
2. **What this block does** — the purpose, in plain English,
3. **Line by line** — every piece of syntax,
4. sometimes **Why it is written this way** — the design reason.

---

# Part 1 — agents_setup.py

> It picks one model, builds three specialist agents — each with a
> description the router reads and instructions only the specialist reads —
> and then builds a triage agent whose only job is to hand each message to
> one of them. Nothing is sent to a model here; the file only builds objects.

---

## 1.1 The module docstring

```python
"""
The agents.
===========

Four agents: three specialists, and one triage agent that routes between them.

Read the handoff_description of each specialist. That text is what the triage
agent uses to choose. It is not documentation — it is a prompt.

    A handoff is a tool call. The tool happens to be another agent.
...
"""
```

**What this block does:** it tells you what is in the file and, more
importantly, how to read it — the `handoff_description` text below is not a
comment for humans but an input the model acts on.

**Line by line:**

- `"""` ... `"""` — a **triple-quoted string**, which can span many lines.
  When it is the very first statement in a file it becomes the **module
  docstring**: Python stores it as `agents_setup.__doc__`, and tools like
  `help()` display it.
- `===========` — just characters inside the string. Underlining a title like
  this is a plain-text convention, not syntax.
- The indented line is also just text. Indenting it makes it stand out as the
  one sentence to remember.

---

## 1.2 The import

```python
from agents import Agent, ModelSettings
```

**What this block does:** it brings in the two classes this file needs from
the OpenAI Agents SDK — one to build an agent, one to set how it samples.

**Line by line:**

- `from agents import ...` — loads the `agents` package (installed as
  `openai-agents`) and pulls two names out of it, so you can write `Agent`
  instead of `agents.Agent`.
- `Agent` — the class every agent in this project is built from.
- `ModelSettings` — a small class holding model options such as
  `temperature`.

---

## 1.3 The model constant

```python
# Every agent says exactly which model it uses, so you can see what runs
# and what it costs. The triage agent uses a very low temperature, because
# routing must be steady. The specialists use a little more, so their
# replies sound natural.
MODEL = "gpt-4o-mini"
```

**What this block does:** it names the model in one place, so all four
agents use the same one and you change it with a single edit.

**Line by line:**

- `#` — a **comment**. Python ignores everything after it on the line.
- `MODEL = "gpt-4o-mini"` — assigns a string to a variable. The name in
  `ALL_CAPS` is a **convention** meaning "this is a constant — set once,
  never reassigned". Python does not enforce it; readers rely on it.
- `"gpt-4o-mini"` — OpenAI's small, cheap model. Every model call in this
  project uses it.

**Why it is written this way:** the comment explains a decision that lives
further down — different **temperatures** per agent. Temperature controls
how much randomness the model uses when picking words: near `0` it gives
nearly the same answer every time, higher values vary more. A router should
be boring and repeatable; a reply to a guest can afford some variety.

---

## 1.4 The booking specialist

**What the three specialists are for:** each one handles one kind of guest
message, with its own short set of rules. They are built the same way, so the
booking agent is explained in full and the other two only where they differ.

### 1.4a Who it is

```python
booking_agent = Agent(
    name="Booking agent",
    model=MODEL,
    model_settings=ModelSettings(temperature=0.4),
```

**What this block does:** it creates the booking specialist and fixes its
identity — its name, its model, and how much variety its replies have.

**Line by line:**

- `booking_agent = Agent(` — calls the `Agent` class to build an object, and
  stores it in `booking_agent`. The call continues over many lines until its
  closing `)`.
- `name="Booking agent"` — a **keyword argument**: you pass a value by naming
  the parameter it goes to, so the order does not matter. The name shows up
  in the trace (`AGENT WORKING: Booking agent`) and, crucially, becomes part
  of the tool the router sees: `transfer_to_booking_agent`.
- `model=MODEL` — uses the constant from 1.3.
- `model_settings=ModelSettings(temperature=0.4)` — builds a settings object
  inline and passes it straight in. `0.4` is moderate: steady, but not
  robotic.

### 1.4b When to send it work

```python
    handoff_description=(
        "Handles new bookings, changing dates, checking availability, room "
        "types and cancellations. Use this for anything about rooms, dates or "
        "availability. Do NOT use this for complaints about a stay that has "
        "already happened, or for refunds."
    ),
```

**What this block does:** it is the sentence the triage agent reads when it
decides whether a message belongs here. It is the most important text in
the file.

**Line by line:**

- `handoff_description=(` ... `)` — the parentheses let one value span
  several lines. They do not make a tuple, because there is no comma inside.
- `"Handles new bookings, ... room "` `"types and ..."` — **adjacent string
  literals**: Python joins strings written next to each other into one, at
  the moment it reads the file. `"room " "types"` becomes `"room types"`.
  That is why each line ends with a space inside the quotes — leave it out
  and you get `"roomtypes"`.
- The text has three jobs: what it handles ("new bookings, changing dates
  ..."), when to use it ("anything about rooms, dates or availability"), and
  when not to ("Do NOT use this for complaints ...").

Three different strings on an agent are easy to confuse, so here they are
side by side:

| Thing | What it is for | What breaks without it |
|---|---|---|
| `name` | Labels the agent in the trace and becomes the tool name `transfer_to_booking_agent` | Rename it `"Agent 1"` and the router sees `transfer_to_agent_1` — a name that says nothing |
| `handoff_description` | Read by the **triage** agent to decide whether to route here | The router has only the name to go on; booking messages land on the wrong specialist or get answered by triage itself |
| `instructions` | Read by **this** agent once it has the message | The specialist answers in its own default style — it may invent availability or skip confirming dates |

**Why it is written this way:** the SDK turns this into a tool description
that reads *"Handoff to the Booking agent agent to handle the request.
Handles new bookings..."*. The router never sees the specialist's
instructions. So the "Do NOT" sentence is what separates this agent from the
complaint agent — without it, "can I change rooms?" has two plausible
homes.

### 1.4c How it behaves

```python
    instructions=(
        "You handle room bookings for a guesthouse in Thamel, Kathmandu.\n\n"
        "Be brief and warm. Two or three sentences.\n"
        "Always confirm the dates back to the guest before anything else.\n"
        "Give all prices in NPR.\n"
        "If you do not know the availability, say so and offer to check — "
        "never invent a room as available."
    ),
)
```

**What this block does:** it is the booking agent's system prompt — the
rules it follows once a message has been handed to it.

**Line by line:**

- `\n` — an **escape sequence** for a newline. `\n\n` leaves a blank line,
  separating the opening sentence from the rules.
- `"Always confirm the dates back..."` — a concrete behaviour, easy to check
  in the reply.
- `"never invent a room as available"` — the specialist has no booking
  system to look things up in, so this line stops it making availability up.
- `)` on its own line — closes the `Agent(` call from 1.4a.

**Why it is written this way:** each rule is one short, checkable line.
"Be helpful" cannot be tested; "two or three sentences" and "prices in NPR"
can. This specialist has no tools, so honesty about what it does not know is
the only safe behaviour.

---

## 1.5 The complaint specialist

```python
complaint_agent = Agent(
    name="Complaint agent",
    ...
    handoff_description=(
        "Handles complaints about a stay, problems with a room, poor service, "
        "and requests for refunds or compensation. Use this when the guest is "
        "unhappy about something that already happened. Do NOT use this for "
        "new bookings or availability questions."
    ),
    instructions=(
        "You handle complaints for a guesthouse in Thamel, Kathmandu.\n\n"
        "Apologise once, clearly, and then move to what happens next.\n"
        "Do not apologise repeatedly — it reads as insincere.\n"
        "Never promise a refund, a discount or compensation. You are not "
        "authorised to. Say that a manager will confirm what can be done.\n"
        "Keep it under four sentences."
    ),
)
```

**What this block does:** it builds the specialist for unhappy guests, and
puts a hard business limit — no promised refunds — into its instructions.

**Line by line:**

- `...` — the `model` and `model_settings` lines are identical to 1.4a.
- `"unhappy about something that already happened"` — the **deciding
  signal**. Bookings are about the future; complaints are about the past.
  That one phrase is what separates this description from the booking one.
- `"Do NOT use this for new bookings..."` — the mirror image of the booking
  agent's "Do NOT" line. Each description excludes the other.
- `"Never promise a refund... You are not authorised to."` — gives the model
  the reason, not only the rule. Models follow a rule more reliably when
  they are told why it exists.

**Why it is written this way:** the refund rule lives in a prompt, so it is a
soft rule — a persuasive guest might still talk the model past it. That is
acceptable for tone, but it is exactly the kind of rule Part 2 moves into
code when it really matters.

---

## 1.6 The general questions specialist

```python
general_agent = Agent(
    name="General questions agent",
    ...
    handoff_description=(
        "Handles practical questions about the guesthouse: breakfast times, "
        "wifi, airport pickup, luggage storage, directions, check-in and "
        "check-out times. Use this for anything factual about the property "
        "itself. Do NOT use this for bookings or complaints."
    ),
```

**What this block does:** it builds the catch-all for factual questions, and
fences it off from the other two.

**Line by line:**

- `"breakfast times, wifi, airport pickup..."` — a list of the actual words
  guests use. The router matches on meaning, but concrete examples make the
  match far more reliable than an abstract phrase like "facility
  information".
- `"Do NOT use this for bookings or complaints."` — without this, "general"
  sounds like it could take anything, and it would start swallowing messages
  meant for the others.
- Its `instructions` (not shown) end with `"Never invent a time, a price or a
  facility."` — the same honesty rule as the booking agent.

---

## 1.7 The triage agent — routing and nothing else

```python
triage_agent = Agent(
    name="Triage agent",
    model=MODEL,
    model_settings=ModelSettings(temperature=0.1),
    instructions=(
        "You are the first point of contact for a guesthouse in Thamel, "
        "Kathmandu.\n\n"
        "Your ONLY job is to decide which specialist should answer, and hand "
        "the message to them.\n\n"
        "Do NOT answer the guest's question yourself, even if you know the "
        "answer. Always hand off.\n\n"
        "If a message could go to more than one specialist, choose the one "
        "matching what the guest most wants resolved."
    ),
```

**What this block does:** it builds the agent that receives every message
first and tells it, firmly, that its job is to choose — not to answer.

**Line by line:**

- `temperature=0.1` — lower than the specialists' `0.4`. The same message
  should go to the same specialist every time.
- No `handoff_description` — nothing hands off *to* the triage agent, so it
  does not need one.
- `"Do NOT answer the guest's question yourself..."` — the comment above the
  agent in the file explains why this is there: answering looks more helpful
  than routing, so without this line the model often just answers.
- `"choose the one matching what the guest most wants resolved"` — a
  **tie-break rule** for messages that fit two specialists, like test 4.

**Why it is written this way:** if the triage agent answers directly, every
rule the specialists carry is skipped — including "never promise a refund".
So "always hand off" is not about tidiness; it is what makes the
specialists' rules apply at all.

### 1.7b The list of specialists

```python
    handoffs=[booking_agent, complaint_agent, general_agent],
)
```

**What this block does:** it gives the triage agent the three specialists it
may hand a message to.

**Line by line:**

- `[booking_agent, complaint_agent, general_agent]` — a **list** of the three
  objects built above. They must exist before this line runs, which is why
  the triage agent is defined last.
- `handoffs=` — for each agent in the list, the SDK creates a tool named
  `transfer_to_<name>` whose description is the agent's
  `handoff_description`. Calling that tool moves the conversation to that
  agent, which then writes the final reply.

---

# Part 2 — guardrail.py

> It defines the shape of a yes-or-no answer, builds a small agent that gives
> that answer for "is this message about the guesthouse?", and wraps it in a
> guardrail function that runs before the triage agent and stops the whole
> run when the answer is no.

---

## 2.1 The module docstring

```python
"""
The guardrail.
==============

A guardrail is a check that runs alongside the agent. This one runs BEFORE
the triage agent sees the message, and stops anything that is clearly not
about the guesthouse.

Why bother? Two reasons.

    1. Cost.  ...
    2. Control.  ...

        A rule you can talk a model out of is not a rule. A rule in code is.
...
"""
```

**What this block does:** it explains why the file exists — to save money on
off-topic messages, and to enforce a rule that a prompt alone cannot.

**Line by line:**

- Same triple-quoted module docstring as 1.1.
- The "Cost" reason only holds when the check runs first. The docstring
  points ahead to `run_in_parallel` in 2.5, where that is decided.

---

## 2.2 The imports

```python
from pydantic import BaseModel

from agents import (
    Agent,
    GuardrailFunctionOutput,
    RunContextWrapper,
    Runner,
    input_guardrail,
)
```

**What this block does:** it brings in the tool for describing a structured
answer (`BaseModel`) and the five SDK pieces needed to build and run a
guardrail.

**Line by line:**

- `from pydantic import BaseModel` — **Pydantic** is a library for declaring
  the shape of data and checking that real data matches it.
- `from agents import (` ... `)` — the parentheses let one import span many
  lines, one name per line. The trailing comma after `input_guardrail` is
  allowed, and means adding a name later changes one line, not two.
- `Agent` — builds the checker agent.
- `Runner` — runs an agent. You will see `Runner.run(...)` in 2.7.
- `RunContextWrapper` — the type of the first argument the SDK passes to a
  guardrail. Used only as a **type hint** here.
- `GuardrailFunctionOutput` — the object a guardrail must return.
- `input_guardrail` — the **decorator** that turns a plain function into a
  guardrail (see 2.5).

---

## 2.3 The shape of the answer

```python
class TopicCheck(BaseModel):
    """What the checking agent must return."""

    is_about_guesthouse: bool
    reason: str
```

**What this block does:** it defines exactly what the checker agent must
return — a true/false verdict plus a reason — so your code gets a value it
can test with `if`, not a sentence it has to interpret.

**Line by line:**

- `class TopicCheck(BaseModel):` — defines a new class that **inherits** from
  `BaseModel`, which gives it Pydantic's checking and parsing.
- `"""What the checking agent must return."""` — a one-line class docstring.
- `is_about_guesthouse: bool` — a field with a **type hint**: the name, a
  colon, then the type. In a plain class this would do nothing at runtime;
  in a Pydantic class it is enforced. `bool` means only `True` or `False`.
- `reason: str` — a short explanation, which the guardrail prints so you can
  see *why* it decided.

**Why it is written this way:** if the checker returned free text — "Yes,
this seems to be about a hotel" — you would need to parse it, and parsing
prose is fragile. A `bool` field turns a model's judgement into a value
code can act on without guessing.

---

## 2.4 The checker agent

```python
topic_checker = Agent(
    name="Topic checker",
    instructions=(
        "Decide whether the message is about a guesthouse or hotel in any "
        "way — bookings, rooms, complaints, facilities, directions, prices, "
        "check-in, or anything a guest might reasonably ask.\n\n"
        "Be generous. A vague or oddly worded guest message still counts.\n"
        "Only mark it false if it is clearly about something else entirely, "
        "such as homework, coding, politics, or general trivia."
    ),
    output_type=TopicCheck,
    model="gpt-4o-mini",
)
```

**What this block does:** it builds a small, single-purpose agent that reads
the guest's message and fills in a `TopicCheck`.

**Line by line:**

- `"Be generous."` — sets the direction of error. A wrongly blocked guest is
  worse than a homework question slipping through to a polite specialist, so
  the checker is told to lean towards "yes".
- `"such as homework, coding, politics, or general trivia"` — concrete
  examples of "no", so "clearly about something else" has a meaning.
- `output_type=TopicCheck` — tells the SDK to make the model reply in that
  exact shape. `result.final_output` will then be a `TopicCheck` object, not
  a string.
- `model="gpt-4o-mini"` — the cheap model again, written out directly.

**Why it is written this way:** a check that costs as much as the thing it
protects has failed at its job. Deciding "is this about a hotel?" needs no
large model. One small flaw: the model name is typed out here rather than
reusing `MODEL` from `agents_setup.py`, so changing the model means editing
two files.

---

## 2.5 The decorator, and running first

```python
# run_in_parallel=False means: finish the check FIRST, then start the agent.
#
# By default (True), the SDK starts the check and the triage agent at the SAME
# time. ...
#
#     run_in_parallel=True   → blocked, but the triage agent made 1 model call
#     run_in_parallel=False  → blocked, and the triage agent made 0 calls
#
# Here we choose False: blocked messages cost nothing extra, and every normal
# message waits a moment for the check. Both are valid choices.
@input_guardrail(run_in_parallel=False)
```

**What this block does:** it registers the function below as an input
guardrail and makes it run to completion *before* the triage agent starts,
so a blocked message never reaches a paid triage call.

**Line by line:**

- `@input_guardrail(...)` — a **decorator**: the `@` line wraps the function
  defined directly underneath it. Here it turns a plain `async def` into an
  `InputGuardrail` object the SDK knows how to run.
- `(run_in_parallel=False)` — passes an option to the decorator. Leave the
  parentheses off entirely and you get the default, `True`.
- The comment records a measured result, not a guess: 1 triage call versus
  0. This option only exists in `openai-agents` 0.6.0 and later.

**Why it is written this way:** the SDK's default favours speed — check and
agent start together, so normal messages never wait. This project favours
cost. Neither is wrong, but the default is a choice someone else made for
you, and here it is overridden on purpose and the reason is written down.

---

## 2.6 The guardrail function — its signature

```python
async def guesthouse_topic_guardrail(
    ctx: RunContextWrapper[None],
    agent: Agent,
    user_input: str,
) -> GuardrailFunctionOutput:
    """Stop messages that are clearly not about the guesthouse.

    Returns a tripwire when the message is off-topic. When a tripwire fires,
    the run stops and raises an exception — and you decide what happens next.
    """
```

**What this block does:** it declares the function the SDK will call with
every incoming message, in the exact shape the SDK expects.

**Line by line:**

- `async def` — defines a **coroutine**: a function that can pause while it
  waits (here, for a model reply) without blocking the whole program. You
  call it with `await`, never plainly.
- `ctx: RunContextWrapper[None]` — the run's context. The square brackets
  say what kind of custom data travels with the run; `None` means this
  project carries none.
- `agent: Agent` — the agent the guardrail is protecting (the triage agent).
  This function does not use it, but the SDK always passes it, so it must
  be in the signature.
- `user_input: str` — the guest's message.
- `-> GuardrailFunctionOutput` — a **return type hint**: this function
  promises to return that type.
- The docstring introduces the word **tripwire**: the signal that stops the
  run. The stop arrives as an exception, which Part 3 catches.

---

## 2.7 Running the checker

```python
    result = await Runner.run(topic_checker, user_input, context=ctx.context)
    check = result.final_output
```

**What this block does:** it sends the guest's message to the checker agent
and takes out the `TopicCheck` it returns.

**Line by line:**

- `await Runner.run(...)` — runs an agent to completion. `await` pauses this
  coroutine until the model replies.
- `topic_checker, user_input` — which agent, and what to send it.
- `context=ctx.context` — passes the outer run's context along, so the
  inner run sees the same data. Here that is `None`, but the habit is right.
- `result.final_output` — because of `output_type=TopicCheck` in 2.4, this
  is a `TopicCheck` object, so `check.is_about_guesthouse` is a real `bool`.

**Why it is written this way:** a guardrail can be any code at all — a
keyword list, a regex, a database lookup. This one happens to use a model
because "is this about a hotel?" is hard to answer with keywords. The point
is that the *decision* lives in the next block, in Python.

---

## 2.8 Printing the verdict

```python
    # Show the decision in the terminal, at the moment it is made.
    verdict = "passed" if check.is_about_guesthouse else "BLOCKED"
    print(f"\n🛡  GUARDRAIL {verdict}: {check.reason}")
```

**What this block does:** it prints the guardrail's decision and its reason,
so you can see what happened before any agent runs.

**Line by line:**

- `"passed" if ... else "BLOCKED"` — a **conditional expression**: it gives
  the first value when the condition is true, the second otherwise. One line
  instead of a four-line `if` / `else`.
- `f"..."` — an **f-string**. Anything inside `{ }` is evaluated and
  inserted: with `verdict = "BLOCKED"` and `reason = "It asks for maths
  help"` you get `🛡  GUARDRAIL BLOCKED: It asks for maths help`.
- `\n` — starts with a blank line so the verdict stands apart in the trace.

**Why it is written this way:** the live trace in `live_trace.py` only sees
the main run, not this inner checker run, so without this line the
guardrail's decision would be invisible. One trap: on Windows, if you
redirect the output to a file or pipe, printing `🛡` raises
`UnicodeEncodeError`. Setting `PYTHONUTF8=1` avoids it.

---

## 2.9 Returning the decision

```python
    return GuardrailFunctionOutput(
        output_info=check,
        tripwire_triggered=not check.is_about_guesthouse,
    )
```

**What this block does:** it hands the verdict back to the SDK, and if the
message is off-topic, trips the wire that stops the run.

**Line by line:**

- `output_info=check` — attaches the full `TopicCheck` for anyone who wants
  to inspect it later. The SDK does not act on it.
- `tripwire_triggered=not check.is_about_guesthouse` — the field the SDK
  *does* act on. `not` flips a boolean: about the guesthouse (`True`) means
  tripwire `False`, and the run continues.

**Why it is written this way:** this one line is where the rule stops being a
suggestion. No prompt can argue with `not False`. When it is `True`, the SDK
raises `InputGuardrailTripwireTriggered` and the triage agent never runs.

---

# Part 3 — guesthouse_router.py

> It loads your API key, attaches the guardrail to the triage agent, and
> gives you `handle()` — one function that runs a message through the whole
> system and always returns text, whatever happens — plus a `main()` that
> reads a message from the command line and prints the result.

---

## 3.1 The module docstring

```python
"""
Day 22 — Guesthouse Message Router
===================================

A triage agent that reads a customer message and hands it to one of three
specialists. An input guardrail blocks anything that is not about the
guesthouse at all.

Run it:      python guesthouse_router.py
Ask it:      python guesthouse_router.py "Do you have a room on Friday?"
Test suite:  python run_tests.py

Before running, copy .env.example to .env and put your key in it.
"""
```

**What this block does:** it is the file's usage note — what it does and the
three ways to run it.

**Line by line:**

- The aligned `Run it:` / `Ask it:` / `Test suite:` lines are copy-pasteable
  commands. Putting usage in the docstring means it travels with the code.

---

## 3.2 The imports

```python
import asyncio
import os
import sys

from dotenv import load_dotenv
from agents import Runner, InputGuardrailTripwireTriggered
from agents.exceptions import MaxTurnsExceeded

from agents_setup import triage_agent
from guardrail import guesthouse_topic_guardrail
from live_trace import LiveTrace
```

**What this block does:** it brings in everything the file uses, in three
groups: Python's own modules, installed packages, and this project's files.

**Line by line:**

- `asyncio` — runs `async` code; used at the very bottom.
- `os` — used to read the environment variable `OPENAI_API_KEY`.
- `sys` — used for the command-line arguments and the exit code.
- `load_dotenv` — from `python-dotenv`; reads `.env` into the environment.
- `InputGuardrailTripwireTriggered` — the exception raised when the
  guardrail's tripwire fires (2.9).
- `MaxTurnsExceeded` — the exception raised when a run hits its step limit.
  It is imported from `agents.exceptions` rather than `agents`; both work.
- The last three lines import this project's own objects, which only works
  when you run from inside the project folder.

**Why it is written this way:** the three blank-line-separated groups —
**standard library, third-party, local** — are the PEP 8 convention. At a
glance you can see what needs `pip install` (the middle group) and what is
this project's own code (the last group).

---

## 3.3 Loading the key

```python
load_dotenv()
```

**What this block does:** it copies every line of `.env` into the process's
environment, so the SDK can find `OPENAI_API_KEY` without the key ever being
written in code.

**Line by line:**

- `load_dotenv()` — finds `.env`, reads lines like `OPENAI_API_KEY=sk-...`,
  and sets each as an environment variable. It does not overwrite a
  variable that is already set.
- It sits at the top level, so it runs at **import time** — the moment any
  file imports `guesthouse_router`, including `run_tests.py`.

**Why it is written this way:** the key lives in `.env`, which `.gitignore`
keeps out of git. The SDK reads `OPENAI_API_KEY` from the environment by
itself; nothing here passes the key around by hand.

---

## 3.4 Attaching the guardrail

```python
# Attach the guardrail to the agent that receives the message first.
triage_agent.input_guardrails = [guesthouse_topic_guardrail]
```

**What this block does:** it connects Part 2 to Part 1 — the triage agent
will now run the topic check on every message before doing anything else.

**Line by line:**

- `triage_agent.input_guardrails` — an attribute on the `Agent` object,
  holding a list of input guardrails. Assigning to it **changes the object
  in place**.
- `[guesthouse_topic_guardrail]` — a list of one. More checks could be added
  to the list.

**Why it is written this way:** input guardrails only run on the *first*
agent of a run, so the triage agent is the right place. Keeping this line
here rather than in `agents_setup.py` keeps the two files independent. The
cost is a **side effect** at import time: if some other file imports
`triage_agent` straight from `agents_setup.py` without importing this file,
it gets an unguarded agent.

---

## 3.5 The handle function

**What the whole of `handle()` is for:** it is the single entry point other
code calls. It runs one message and always returns a string — a reply, a
refusal, or a description of what went wrong — and never lets an exception
escape.

### 3.5a Its signature

```python
async def handle(message: str) -> str:
    """Run one message through the router.

    Returns either the specialist's reply, or a polite refusal if the
    guardrail stopped it.
    """
```

**What this block does:** it promises callers a simple contract — text in,
text out.

**Line by line:**

- `async def` — a coroutine, because it awaits `Runner.run`. Callers must
  `await handle(...)`, as `run_tests.py` does.
- `message: str` and `-> str` — type hints for the input and output.

### 3.5b Running the message

```python
    try:
        # max_turns=10  → course rule 3: every agent has a limit.
        # hooks=LiveTrace() → prints every step of THIS run as it happens,
        #                     including the moment of each HANDOFF.
        result = await Runner.run(triage_agent, message, max_turns=10,
                                  hooks=LiveTrace())
        print(f"\n✔  Answered by: {result.last_agent.name}")
        return result.final_output
```

**What this block does:** it runs the guest's message through the guardrail,
the triage agent and whichever specialist it picks, then reports which agent
answered and returns the reply.

**Line by line:**

- `try:` — starts a block whose errors will be caught by the `except`
  clauses below.
- `Runner.run(triage_agent, message, ...)` — always starts at the triage
  agent. The handoff to a specialist happens inside this one call.
- `max_turns=10` — a hard limit on steps. If agents kept handing off or
  calling tools in a loop, the run stops at 10 instead of spending forever.
- `hooks=LiveTrace()` — a fresh `LiveTrace` object per run, so its model-call
  counter starts at 1 every time. The SDK calls its methods at each step,
  which is what prints the live trace.
- The second line of the call is indented to line up under the first
  argument — a style choice, since anything inside `( )` can continue on the
  next line.
- `result.last_agent.name` — the agent that produced the final answer. If
  this prints `Triage agent`, no handoff happened.
- `result.final_output` — the reply text. The triage agent has no
  `output_type`, so this is a plain string.

### 3.5c When the guardrail blocks it

```python
    except InputGuardrailTripwireTriggered:
        # The guardrail fired. Because it runs first, no agent ran at all.
        return (
            "Sorry — I can only help with questions about the guesthouse. "
            "Is there anything about your stay I can help with?"
        )
```

**What this block does:** it turns the guardrail's stop signal into a polite
reply to the guest.

**Line by line:**

- `except InputGuardrailTripwireTriggered:` — runs only when that exception
  was raised inside `try`.
- `return ( ... )` — two adjacent strings joined into one, as in 1.4b.

**Why it is written this way:** the tripwire is an expected outcome, not a
failure, so it gets a designed answer rather than a stack trace. The comment
is slightly loose — the topic checker *is* an agent and it did run. What did
not run is the triage agent and every specialist.

### 3.5d When something else goes wrong

```python
    except MaxTurnsExceeded:
        return ("The agents stopped after 10 steps without finishing. "
                "Read the trace above to see what they were doing.")

    except Exception as error:
        # Any other error: the live trace above shows every step up to here.
        return f"The run failed: {type(error).__name__}: {error}"
```

**What this block does:** it catches the step limit and every other error,
and returns a message describing it instead of crashing.

**Line by line:**

- `except MaxTurnsExceeded:` — the limit from 3.5b was hit. The message
  points you at the trace, which shows what was looping.
- `except Exception as error:` — catches almost any error and binds it to
  the name `error`. It comes last because Python checks `except` clauses in
  order, and this one would otherwise catch everything first.
- `type(error).__name__` — the exception class's name, such as
  `AuthenticationError`. With a bad key you would get
  `The run failed: AuthenticationError: Error code: 401 ...`.

**Why it is written this way:** returning text instead of raising means
`run_tests.py` keeps going through all five tests even if one fails. The
cost is real: a catch-all also swallows your own bugs — a typo in an agent
file appears as a "Reply:" line rather than a crash with a line number. For
learning that is fine; in production you would log the full traceback too.

---

## 3.6 The main function

### 3.6a Choosing the message

```python
async def main() -> None:
    if len(sys.argv) > 1:
        message = " ".join(sys.argv[1:])
    else:
        message = "Do you have a room free from Friday for two nights?"
```

**What this block does:** it uses the message you typed on the command line
if there is one, and a built-in booking question if not.

**Line by line:**

- `-> None` — the function returns nothing useful; it only prints.
- `sys.argv` — the list of words on the command line. For
  `python guesthouse_router.py Is wifi free` it is
  `["guesthouse_router.py", "Is", "wifi", "free"]`.
- `len(sys.argv) > 1` — true when you typed anything after the file name.
- `sys.argv[1:]` — a **slice**: everything from index 1 onwards, which drops
  the file name.
- `" ".join([...])` — glues the words back with spaces:
  `" ".join(["Is", "wifi", "free"])` gives `"Is wifi free"`. So the quotes
  around your message are optional — though you still need them for
  characters the shell treats specially, like `?` in some shells or `'`.

### 3.6b Running it and showing the reply

```python
    print("\nGUEST SAYS")
    print(" ", message)
    print("\nRouting...\n")

    reply = await handle(message)

    print("REPLY")
    print(" ", reply)
    print()
    print("-" * 70)
    print("Read the trace above. Which specialist did it choose, and why?")
    print("See developer-tools/03-reading-the-handoff.md")
    print("-" * 70)
```

**What this block does:** it shows the message, runs it, shows the reply,
and ends by pointing you at what to look for in the trace.

**Line by line:**

- `print(" ", message)` — `print` puts a space between its arguments, so
  this indents the message by two spaces.
- `await handle(message)` — everything from 3.5 happens here, and the live
  trace prints between "Routing..." and "REPLY".
- `print()` — with no arguments, prints a blank line.
- `"-" * 70` — **string repetition**: a string times a number repeats it, so
  this is a line of 70 dashes.

---

## 3.7 The entry point and the key check

```python
if __name__ == "__main__":
    if not os.getenv("OPENAI_API_KEY"):
        print("\nNo OPENAI_API_KEY found.")
        print("Copy .env.example to .env and put your key in it.\n")
        sys.exit(1)
    asyncio.run(main())
```

**What this block does:** when you run this file directly, it checks for an
API key before doing anything else, and then starts the program.

**Line by line:**

- `if __name__ == "__main__":` — Python sets `__name__` to `"__main__"` only
  for the file you ran. When `run_tests.py` imports this file, `__name__` is
  `"guesthouse_router"`, so this block is skipped.
- `os.getenv("OPENAI_API_KEY")` — returns the value, or `None` if it is not
  set. `not None` is `True`, as is `not ""` — an empty string is **falsy**,
  meaning it counts as false in an `if`.
- `sys.exit(1)` — stops the program with **exit code** `1`. By convention
  `0` means success and anything else means failure, which scripts and CI
  can check.
- `asyncio.run(main())` — starts the event loop that runs `async` code and
  runs `main()` to completion. It is the bridge from ordinary code into
  `async`.

**Why it is written this way:** this is a **fail-fast** check — a missing key
gives one clear sentence instead of an authentication error deep inside the
SDK. Because it is inside the `__main__` guard, `run_tests.py` does not get
it: a missing key there shows up as `The run failed: ...` on each test.

---

# Part 4 — the patterns worth taking away

1. **A description the model reads is a prompt, not documentation.** The
   triage agent picks a specialist from its `name` and `handoff_description`
   alone (1.4b), so those lines decide routing as surely as any code does.

2. **Say when not to, as well as when to.** Every specialist's description
   ends with "Do NOT use this for..." (1.4b, 1.5, 1.6). That half is what
   keeps the booking and complaint agents from blurring together.

3. **Keep what the router reads separate from what the specialist reads.**
   `handoff_description` is for the triage agent; `instructions` are for the
   specialist. Each stays short because it serves one reader.

4. **Put rules that must hold in code, and style in prompts.** "Never promise
   a refund" is a prompt rule and can be argued with (1.5). The topic check
   ends in `tripwire_triggered=not check.is_about_guesthouse` (2.9), which
   cannot.

5. **Turn model judgements into typed values before you act on them.**
   `output_type=TopicCheck` (2.4) makes the checker return a real `bool`, so
   the decision is an `if`, not text parsing.

6. **Check before you spend.** `run_in_parallel=False` (2.5) means a blocked
   message costs one cheap call instead of one cheap call plus a triage
   call. Know a framework's defaults before you rely on them.

7. **Match model and temperature to the job.** The checker and all agents
   use the small model; the router runs at `0.1` for steadiness and the
   specialists at `0.4` for natural replies (1.3, 1.7).

8. **Bound every run and design every exit.** `max_turns=10` caps the steps
   (3.5b), and `handle()` turns each way of stopping — tripwire, limit, error
   — into a message the caller can show (3.5c, 3.5d).
