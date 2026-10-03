# 3. Reading the handoff

## The habit, again

Day 19's rule has not changed:

> Reading the trace is the difference between someone who can debug agents
> and someone who guesses.

What is new today is **what** you are looking for. Not "which tool did it
call" but **"which specialist did it choose, and did it choose well?"**

---

## Watching it live

Every run now prints a **live trace** as it happens, through `live_trace.py`.
You don't need to add anything. Just run:

    python guesthouse_router.py "Do you have a room free from Friday for two nights?"

You will see:

    🛡  GUARDRAIL passed: It asks about a room booking.

    🤖  AGENT WORKING: Triage agent
    MODEL CALL 1  —  sending to the model:
      [user]  Do you have a room free from Friday for two nights?
      → the model asks for:  transfer_to_booking_agent  {}

      ↪  HANDOFF:  Triage agent  →  Booking agent

    🤖  AGENT WORKING: Booking agent
    MODEL CALL 2  —  sending to the model:
      ...
      → the model answers:   Just to confirm: Friday and Saturday night...

    ✔  Answered by: Booking agent

Three lines matter most today:

- **`transfer_to_booking_agent`** — this is how the handoff looks to the model:
  an ordinary tool call. The SDK names one such tool for each specialist.
- **`↪ HANDOFF`** — the exact moment the work moves to another agent.
- **`✔ Answered by`** — which specialist actually gave the answer. It comes
  from `result.last_agent`.

The trace prints *during* the run, so if anything fails, every step up to the
failure is already on screen.

For a tidier screen on the projector, use `LiveTrace(show_full_output=False)`
in `guesthouse_router.py`.

---

## What to check, in order

| Step | Question |
|---|---|
| 1 | Did the guardrail let it through, or stop it? |
| 2 | Which specialist did the triage agent choose? |
| 3 | Do you agree with that choice? |
| 4 | Did the triage agent answer it itself instead of handing off? |
| 5 | Did the specialist stay inside its own job? |

Step 4 is a real failure, and it is easy to miss because the answer often
looks fine. Check the `✔ Answered by` line — if it is still the triage agent, no
handoff happened.

---

## The ambiguous case

Test 4 is written to be genuinely ambiguous:

> *"I booked last week but the room was dirty, can I move to another one?"*

There is no correct answer. Both specialists are defensible.

What matters is that **you** decide which one you want, and then make the
system agree with you — by editing one `handoff_description`, not by editing
the message.

Keep both traces. Being able to show "before my change it went here, after my
change it goes there" is the evidence that you understand the mechanism.
