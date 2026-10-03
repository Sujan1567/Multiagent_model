"""
The guardrail.
==============

A guardrail is a check that runs alongside the agent. This one runs BEFORE
the triage agent sees the message, and stops anything that is clearly not
about the guesthouse.

Why bother? Two reasons.

    1. Cost.  Without it, an off-topic message runs the whole system:
              triage, a handoff, a specialist thinking hard about homework.
              You pay for all of it. With it, the expensive part never starts
              — but ONLY if the guardrail runs first (see run_in_parallel below).

    2. Control.  You could write "do not answer homework questions" in the
                 system prompt. Sometimes that works. Sometimes a persuasive
                 message talks the model out of it.

        A rule you can talk a model out of is not a rule. A rule in code is.

You saw this exact idea on Day 18, in the Check and Stamp node of your
Project 1 workflow, where the escalation rule lives in JavaScript rather
than in the prompt. Same principle, different framework.
"""

from pydantic import BaseModel

from agents import (
    Agent,
    GuardrailFunctionOutput,
    RunContextWrapper,
    Runner,
    input_guardrail,
)


class TopicCheck(BaseModel):
    """What the checking agent must return."""

    is_about_guesthouse: bool
    reason: str


# A small, cheap agent whose only job is to decide yes or no.
# Note the model choice — this is Day 3's tiering advice. You do not need
# an expensive model to answer "is this about a hotel?"

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


# run_in_parallel=False means: finish the check FIRST, then start the agent.
#
# By default (True), the SDK starts the check and the triage agent at the SAME
# time. That is faster for normal messages, because nobody waits — but when a
# message is blocked, the triage agent has already made its model call, and
# you have already paid for it. We tested this:
#
#     run_in_parallel=True   → blocked, but the triage agent made 1 model call
#     run_in_parallel=False  → blocked, and the triage agent made 0 calls
#
# Here we choose False: blocked messages cost nothing extra, and every normal
# message waits a moment for the check. Both are valid choices.
@input_guardrail(run_in_parallel=False)
async def guesthouse_topic_guardrail(
    ctx: RunContextWrapper[None],
    agent: Agent,
    user_input: str,
) -> GuardrailFunctionOutput:
    """Stop messages that are clearly not about the guesthouse.

    Returns a tripwire when the message is off-topic. When a tripwire fires,
    the run stops and raises an exception — and you decide what happens next.
    """
    result = await Runner.run(topic_checker, user_input, context=ctx.context)
    check = result.final_output

    # Show the decision in the terminal, at the moment it is made.
    verdict = "passed" if check.is_about_guesthouse else "BLOCKED"
    print(f"\n🛡  GUARDRAIL {verdict}: {check.reason}")

    return GuardrailFunctionOutput(
        output_info=check,
        tripwire_triggered=not check.is_about_guesthouse,
    )
