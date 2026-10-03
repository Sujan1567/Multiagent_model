# 5. Troubleshooting

## Setup

| Symptom | Fix |
|---|---|
| `ModuleNotFoundError: agents` | Activate `.venv`, then `pip install -r requirements.txt` |
| `No OPENAI_API_KEY found` | The file must be `.env`, not `env` or `.env.txt` |
| `ModuleNotFoundError: pydantic` | `pip install pydantic` |
| `RuntimeError: asyncio.run() cannot be called...` | You are inside a notebook. Use `await handle(msg)` directly |
| `TypeError: ... unexpected keyword argument 'run_in_parallel'` | Your `openai-agents` is older than 0.6.0. `pip install -U openai-agents` |
| `UnicodeEncodeError: 'charmap' codec...` | Windows, output redirected to a file or pipe. Set `PYTHONUTF8=1` first — see `07-setup-guide.md` |
| `ValueError: invalid literal for int()` from `run_tests.py` | The argument must be a test number: `python run_tests.py 4`, not `test4` |

---

## Routing problems

**Almost all of these are fixed by editing a `handoff_description`.**

| What you see | What is actually wrong | Fix |
|---|---|---|
| It always picks the same specialist | The others do not say when to use them | Add "Use this for..." to each |
| It picks the wrong one of two similar agents | Their descriptions overlap | Add "Do NOT use this for..." to both |
| It answers without handing off | The triage instruction does not forbid it | Add the "never answer yourself" line |
| It hands off but the reply is off-topic | The specialist's instructions are too broad | Tighten the specialist, not the router |
| Routing changes between identical runs | Normal variation | Test with all five messages, not one |

---

## Guardrail problems

| Symptom | Cause | Fix |
|---|---|---|
| It blocks legitimate guest messages | The checker is too strict | Make the checking instruction more generous |
| It lets homework through | The checker is too loose | Give it clearer examples of what is off-topic |
| The guardrail is slow | The checking model is too large | Use a smaller model for the checker |
| `InputGuardrailTripwireTriggered` crashes the program | You did not catch it | Wrap the run in try/except |

---

## The three questions

Before changing anything, answer these:

1. Did the guardrail let it through?
2. Which specialist did it choose?  (the `✔ Answered by` line in the trace)
3. Was that choice reasonable given the descriptions you wrote?

Most of the time, answering question 3 honestly solves it.

---

## Trace and limit messages

| What you see | What it means | What to do |
|---|---|---|
| `🛡 GUARDRAIL BLOCKED` on a real guest message | The checker is too strict | Make the checker's instructions more generous |
| No `↪ HANDOFF` line at all | The triage agent answered by itself | Strengthen "never answer yourself" in its instructions |
| "The agents stopped after 10 steps" | The step limit worked | Read the trace: which agent kept repeating, and what was it asking for? |
| `ModuleNotFoundError: live_trace` | `live_trace.py` is missing | Put `live_trace.py` in the same folder as `guesthouse_router.py` |
