# 7. Setup guide

How do I get this running from nothing, and what goes wrong on the way?

---

## What you need

- **Python 3.10 or newer.** The `openai-agents` package refuses to install on
  3.9. Check with `python --version`. This project was built on 3.11.
- **An OpenAI API key** with a little credit on it. A full run of the five
  tests is about fifteen calls to `gpt-4o-mini` — a fraction of a cent.

---

## The steps, in order

**1. Make the virtual environment.** A private copy of Python for this
project, so its packages do not collide with anything else.

    python -m venv .venv

**2. Activate it.** Your prompt should start with `(.venv)` afterwards.

| Shell | Command |
|---|---|
| macOS / Linux | `source .venv/bin/activate` |
| Windows PowerShell | `.venv\Scripts\Activate.ps1` |
| Windows cmd | `.venv\Scripts\activate.bat` |
| Git Bash on Windows | `source .venv/Scripts/activate` |

If PowerShell says *"running scripts is disabled on this system"*, run this
once, then activate again:

    Set-ExecutionPolicy -Scope CurrentUser RemoteSigned

**3. Install the packages.**

    pip install -r requirements.txt

**4. Check `.gitignore` exists.** It does, and it lists `.env`. That must be
true *before* step 5. If you create `.env` first and commit it, the key is in
the git history for good — deleting the file later does not remove it.

**5. Make your `.env`.**

    cp .env.example .env             # Windows: copy .env.example .env

Open `.env` and replace `sk-put-your-key-here` with your real key. No quotes,
no spaces around the `=`.

**6. Run it.**

    python guesthouse_router.py

You should see `🛡  GUARDRAIL passed`, a `↪  HANDOFF` line to the Booking
agent, and a short reply confirming Friday and Saturday night.

---

## Things that go wrong

| Symptom | Cause | Fix |
|---|---|---|
| `No OPENAI_API_KEY found` | `.env` is missing, or named `env` / `.env.txt` | Windows Explorer hides extensions — check with `dir` or `ls -a` |
| `ModuleNotFoundError: No module named 'agents'` | The venv is not active, so `python` is the system one | Activate it; your prompt should show `(.venv)` |
| `TypeError: input_guardrail() got an unexpected keyword argument 'run_in_parallel'` | An old `openai-agents` (before 0.6.0) | `pip install -U openai-agents` |
| `UnicodeEncodeError: 'charmap' codec can't encode character` | Windows, with output redirected to a file or pipe | See below |
| `AuthenticationError` / `401` in the reply | The key is wrong, revoked, or has a stray space | Copy it again from the dashboard |
| `RateLimitError` / `429` | No credit on the account | Add credit in billing settings |

### The Windows emoji problem

The trace prints symbols like `🛡` and `↪`. In a normal Windows terminal that
is fine. But if you redirect the output — `python run_tests.py > out.txt`, or
pipe it into another command — Python falls back to the old `cp1252`
encoding and crashes on the first symbol. Tell Python to use UTF-8 instead:

    $env:PYTHONUTF8 = "1"            # PowerShell, this session only
    set PYTHONUTF8=1                 # cmd
    export PYTHONUTF8=1              # Git Bash

---

## A note on the SDK's own tracing

The Agents SDK also uploads a trace of every run to the OpenAI dashboard
(platform.openai.com > Logs > Traces). That is separate from the live trace
this project prints. If you would rather it did not upload, add this line to
`.env`:

    OPENAI_AGENTS_DISABLE_TRACING=true

The project's own code does not read this variable — the SDK does.
