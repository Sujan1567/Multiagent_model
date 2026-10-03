# 8. Writing handoff descriptions

How do I write the sentence that decides where every message goes?

This is the core skill of the day. `01-handoffs-reference.md` explains the
mechanism; this file is about doing it well.

---

## What the router actually reads

For each specialist, the SDK builds one tool and shows it to the triage
model. For the booking agent it looks like this:

    name:         transfer_to_booking_agent
    description:  Handoff to the Booking agent agent to handle the request.
                  Handles new bookings, changing dates, checking
                  availability, room types and cancellations. Use this for
                  ...

The first sentence is generated from `name`. Everything after it is your
`handoff_description`. (The doubled "agent agent" is real — the SDK appends
the word "agent" to whatever name you chose.)

That is the whole input to the routing decision. Write for that reader.

---

## The four parts of a good description

Look at `complaint_agent` in `agents_setup.py`:

| Part | Example from the code | What breaks without it |
|---|---|---|
| **What it handles** — concrete nouns | "complaints about a stay, problems with a room, poor service, and requests for refunds" | The router has to guess from the name alone |
| **The deciding signal** — the one test that separates it from its neighbours | "when the guest is unhappy about something that already happened" | "Can I move rooms?" has no obvious owner |
| **What it does NOT handle** | "Do NOT use this for new bookings or availability questions" | Two similar specialists become interchangeable |
| **Words the guest would actually use** | "refunds", "wifi", "breakfast" | Guests say "the room smells", not "service quality issue" |

The second and third rows are the ones people skip. They are also the ones
that fix most misroutes.

---

## A worked fix: test 4

> *"I booked last week but the room was dirty, can I move to another one?"*

Say you decide this should go to **complaints** — the guest is unhappy, and
a room move after a bad stay is a form of compensation. The current booking
description says it handles "changing dates" and "room types", which pulls
the message the other way.

Add the deciding signal to the booking agent:

    "Do NOT use this for complaints about a stay that has already happened,
     for refunds, or for moving rooms because something was wrong."

Then run `python run_tests.py 4` three or four times. One run proves
nothing — routing varies. Three runs in a row going the same way is a
decision.

If you decide the opposite — that a room move is a booking job — make the
same kind of edit to the complaint agent instead. Either is defensible. What
is not defensible is leaving it to chance.

---

## The triage agent's instructions matter too

The descriptions say *where* each message can go. The triage instructions
say *how* to choose. Two lines in `agents_setup.py` do the work:

    "Do NOT answer the guest's question yourself, even if you know the
     answer. Always hand off."

Without it, the triage agent answers easy questions itself — and skips every
rule the specialists carry (the complaint agent's "never promise a refund"
among them).

    "If a message could go to more than one specialist, choose the one
     matching what the guest most wants resolved."

This is the tie-break rule. Change it to *"prefer the complaint agent when
in doubt"* and you have changed the policy for every ambiguous message at
once.

---

## Habits

- **Edit the description, never the test message.** The guest will not
  rephrase for you.
- **Change one description at a time**, and keep the trace from before and
  after.
- **Re-run all five tests after every edit.** Fixing test 4 by making the
  booking description narrower can quietly break test 1.
- **Read the descriptions side by side.** If you cannot tell from the three
  descriptions alone where a message belongs, neither can the model.
