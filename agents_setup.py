"""
The agents.
===========

Four agents: three specialists, and one triage agent that routes between them.

Read the handoff_description of each specialist. That text is what the triage
agent uses to choose. It is not documentation — it is a prompt.

    A handoff is a tool call. The tool happens to be another agent.

So everything you learned on Day 13 about tool descriptions applies here,
one level up: say when to use it, and say when NOT to.
"""

from agents import Agent, ModelSettings

# Every agent says exactly which model it uses, so you can see what runs
# and what it costs. The triage agent uses a very low temperature, because
# routing must be steady. The specialists use a little more, so their
# replies sound natural.
MODEL = "gpt-4o-mini"


# ---------------------------------------------------------------------------
# Specialist 1 — bookings
# ---------------------------------------------------------------------------

booking_agent = Agent(
    name="Booking agent",
    model=MODEL,
    model_settings=ModelSettings(temperature=0.4),
    handoff_description=(
        "Handles new bookings, changing dates, checking availability, room "
        "types and cancellations. Use this for anything about rooms, dates or "
        "availability. Do NOT use this for complaints about a stay that has "
        "already happened, or for refunds."
    ),
    instructions=(
        "You handle room bookings for a guesthouse in Thamel, Kathmandu.\n\n"
        "Be brief and warm. Two or three sentences.\n"
        "Always confirm the dates back to the guest before anything else.\n"
        "Give all prices in NPR.\n"
        "If you do not know the availability, say so and offer to check — "
        "never invent a room as available."
    ),
)


# ---------------------------------------------------------------------------
# Specialist 2 — complaints
# ---------------------------------------------------------------------------

complaint_agent = Agent(
    name="Complaint agent",
    model=MODEL,
    model_settings=ModelSettings(temperature=0.4),
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


# ---------------------------------------------------------------------------
# Specialist 3 — general questions
# ---------------------------------------------------------------------------

general_agent = Agent(
    name="General questions agent",
    model=MODEL,
    model_settings=ModelSettings(temperature=0.4),
    handoff_description=(
        "Handles practical questions about the guesthouse: breakfast times, "
        "wifi, airport pickup, luggage storage, directions, check-in and "
        "check-out times. Use this for anything factual about the property "
        "itself. Do NOT use this for bookings or complaints."
    ),
    instructions=(
        "You answer practical questions about a guesthouse in Thamel, "
        "Kathmandu.\n\n"
        "Be short and helpful. One or two sentences.\n"
        "If you do not know the answer, say so plainly and offer to find out. "
        "Never invent a time, a price or a facility."
    ),
)


# ---------------------------------------------------------------------------
# The triage agent — routes, and nothing else
# ---------------------------------------------------------------------------
#
# Notice what its instructions forbid. Without that line, a triage agent will
# often answer the question itself instead of handing it over, because
# answering is the more helpful-looking thing to do.
# ---------------------------------------------------------------------------

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
    handoffs=[booking_agent, complaint_agent, general_agent],
)
