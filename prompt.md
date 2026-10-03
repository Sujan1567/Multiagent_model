# Reusable prompts

Two prompts. Copy the fenced block you need into Claude Code (or any capable
model) from inside your project folder, fill in the placeholder, and run it.

| Prompt | What it makes | Use when |
|---|---|---|
| [Prompt 1](#prompt-1--make-me-an-explanationmd) | `explanation.md` — a block-by-block walkthrough of your code | You want the code taught, line by line |
| [Prompt 2](#prompt-2--scaffold-an-existing-project) | `README.md`, `.env.example`, `.gitignore`, `requirements.txt`, `run_examples.py`, `developer-tools/`, `explanation.md` | You have working code and want the whole teaching-project wrapper around it |

Prompt 1 reproduces the style of this project's [explanation.md](explanation.md).
Prompt 2 reproduces the structure of this project as a whole.

---

# Prompt 1 — make me an explanation.md

## The prompt

```text
You are writing a teaching document for a learner who can read code but does
not yet know why it is written the way it is. Your job is to explain the files
I name, block by block, in a file called explanation.md.

FILES TO EXPLAIN
<FILES>            e.g. research_assistant.py and tools.py

STEP 0 — READ EVERYTHING FIRST
Read every named file completely before writing a single word. Do not explain
from memory, from the filename, or from a guess about what a library does. If a
file imports another file in the project, read that too. Never invent a line of
code that is not in the file, and never skip a block because it "looks obvious".

=========================================================================
THE SHAPE OF THE DOCUMENT
=========================================================================

1. A top heading and a two-line intro naming the files and what each one is for.

2. A short "How each block is laid out below" note, listing the four parts a
   reader will see for every block:
       1. the code itself,
       2. What this block does — plain English purpose,
       3. Line by line — every piece of syntax,
       4. sometimes Why it is written this way — the design reason.

3. One PART per file (`# Part 1 — filename.py`).

4. Immediately under each part heading, a one-sentence MAP of the whole file as
   a blockquote, before any code appears. Example of the register to hit:

       > It loads your API key, writes down the agent's instructions, builds
       > the agent object out of those instructions plus three tools, and gives
       > you two ways to run it — ask() for other code, and main() for the
       > command line.

5. Numbered sub-sections through the file IN THE ORDER THE CODE APPEARS
   (## 1.1, ## 1.2 ... ## 2.1, ## 2.2 ...). Each gets a short descriptive title
   naming the thing, not the syntax: "The system prompt", "Creating the agent",
   "Cleaning and validating" — not "Lines 30-42".

6. A horizontal rule (`---`) between sections.

7. A final `# Part 3 — the patterns worth taking away`: a numbered list of 5-8
   cross-cutting lessons, each a bolded one-line principle followed by one or
   two sentences of why, citing the concrete lines in the code that show it.

=========================================================================
THE SHAPE OF EACH BLOCK  — this is the part that matters most
=========================================================================

Every single section follows this order, with no exceptions:

  a) THE CODE, in a fenced ```python block, quoted verbatim from the file.
     If the block is long, quote the first few lines and use `...` for the
     middle — but never paraphrase or retype code inaccurately.

  b) **What this block does:** — ONE OR TWO SENTENCES, in bold lead-in form,
     saying the PURPOSE in plain English before any syntax is discussed. The
     reader must be able to stop after this line and still know why the block
     exists. Write it as if answering "what is this here for?" out loud.

     Good:  "**What this block does:** it is the security gate. Before any of
             the text is executed, it strips commas and then checks that every
             single character is one of a small permitted set — rejecting
             anything else outright."

     Bad:   "**What this block does:** it validates the expression."
             (too thin — says nothing the code doesn't already say)

     Bad:   "This code block does the following. First it calls strip()..."
             (that is the line-by-line, not the purpose)

  c) **Line by line:** — a bulleted list. One bullet per meaningful piece of
     syntax, in the order it appears. Explain:
        - what the construct IS (a decorator, a slice, a set, an f-string,
          a keyword argument, a type hint),
        - what it evaluates to, with a CONCRETE worked example where possible
          ("`\" \".join([\"What\", \"is\"])` gives `\"What is\"`"),
        - what it would do differently if written another way
          ("`data[\"rates\"]` would crash; `.get(\"rates\", {})` returns `{}`").

  d) **Why it is written this way:** — OPTIONAL, only when there is a genuine
     design reason, a trap, or a convention worth naming. Do not pad every
     section with one. Use it for things like: why a timeout is set, why a
     whitelist beats a blacklist, why the failure path returns text instead of
     raising, why an import is grouped a certain way.

  Use the exact bold lead-ins "**What this block does:**", "**Line by line:**"
  and "**Why it is written this way:**" so the document stays scannable.

=========================================================================
HOW TO CHOOSE THE BLOCKS
=========================================================================

- Split by PURPOSE, not by line count. A block is a group of lines that share
  one job. The moment the job changes, start a new section.

- SPLIT LONG FUNCTIONS. Do not explain a 30-line function as one block. Give
  each phase its own numbered sub-section with its own purpose line — e.g.
  "1.7 The main function — choosing the question" and
  "1.7b The main function — running it and showing the answer".
  A function's signature+docstring is often its own block, separate from its body.

- For a group of similar things (several tools, several routes, several
  classes), first give a one-line "What this whole X is for" under the parent
  heading, THEN break it into lettered sub-blocks (2.3a, 2.3b, 2.3c ...).

- Explain the module docstring and the import block too. They are blocks like
  any other, and the import grouping convention is worth teaching.

=========================================================================
TONE AND STYLE RULES
=========================================================================

- Write for someone who has never seen this syntax before, WITHOUT talking down
  to them. Assume intelligence, not knowledge.
- Second person ("you"), present tense, plain words. Short sentences.
- Explain jargon the first time it appears: decorator, slice, falsy, tuple,
  keyword argument, type hint, f-string, whitelist, side effect, exit code.
- Bold the term being defined, not whole sentences.
- Use backticks for every identifier, filename, literal and operator.
- When something is a real trap, say so directly and say what breaks:
  "Without a timeout a hung server can freeze your agent indefinitely."
- Prefer a concrete example over an abstract description, always.
- Use an em-dash aside where it keeps a sentence short. Do not use emoji.
- Do not moralise, do not pad, do not repeat yourself between sections.
- Wrap prose at roughly 80 characters so the file reads well in any editor.

=========================================================================
USE A TABLE WHEN IT EARNS ITS PLACE
=========================================================================

When a block contains a LIST of parallel things — the headings of a prompt, a
set of config keys, an enum, a group of CLI flags — render them as a table with
three columns:

    | Thing | What it is for | What breaks without it |

The third column is the valuable one. Make it specific and concrete
("The agent guesses a rate from memory instead of calling the API"), never
vague ("things go wrong").

Use at most one or two tables in the whole document. Everything else is prose
and bullets.

=========================================================================
THINGS TO CALL OUT WHEREVER YOU FIND THEM
=========================================================================

Hunt for these in the code and explain them properly when they appear:
- error handling: what is caught, what is deliberately NOT caught, and why
- anything that returns a message instead of raising, and what that buys
- input validation and normalisation, and what untrusted input means here
- timeouts, retries, and what happens without them
- secrets and configuration: where they come from, why not in the code
- guards like `if __name__ == "__main__":` and fail-fast checks
- anything that looks dangerous (`eval`, `exec`, shell calls, raw SQL): explain
  precisely what makes it safe or unsafe HERE, and name the safer production
  alternative — do not defend it and do not just condemn it
- code that runs at import time vs code that runs when called
- naming and layout conventions (ALL_CAPS constants, import grouping)

=========================================================================
HARD RULES
=========================================================================

1. Purpose before syntax. Every block starts with what it is FOR. This is the
   rule the document lives or dies by.
2. Quote the code accurately. Never invent, never silently "fix" it.
3. Explain what is actually there. If the code has a flaw, say so plainly in
   one sentence and move on — do not rewrite it unless I ask.
4. Every meaningful token gets explained somewhere. If a beginner would pause
   at it, it needs a bullet.
5. No filler. If a section has nothing to say beyond the obvious, keep it short
   rather than padding it out.
6. Do not modify the source files. Only create explanation.md.

Write the whole document now, and save it as explanation.md.
```

---

## How to use it

1. Copy the fenced block above.
2. Replace `<FILES>` with the files you want explained.
3. Paste it into Claude Code from inside the project folder.

**Optional tweaks:**

| Want | Add this line to the prompt |
|---|---|
| A different audience | "Assume the reader already knows Python; focus on the library and the architecture, not on syntax." |
| A different language | "The files are TypeScript — explain TS-specific syntax (generics, `as const`, union types) with the same care." |
| Shorter | "Keep it to roughly 300 lines. Merge the smallest blocks." |
| A different filename | "Save it as `docs/walkthrough.md` instead." |
| Diagrams | "Add one Mermaid diagram at the top of each Part showing the call flow." |

**One caution:** the `<FILES>` list should be small — two or three files at a
time. The style is deliberately thorough, so pointing it at a whole repository
produces something too long to read. Run it once per pair of related files.

---
---

# Prompt 2 — scaffold an existing project

For when the **code already works** and you want the teaching wrapper around it:
a README, an env example, a gitignore, pinned requirements, a runnable examples
script, a `developer-tools/` reference folder, and the explanation document.

It does not restructure or rewrite your code. It reads what is there and builds
the supporting material to match.

## The prompt

```text
This project already has working code. Do NOT rewrite it, restructure it, or
"improve" it. Your job is to build the supporting material around it so that
someone else could pick it up, run it, understand it, and learn from it.

PROJECT
<DESCRIBE: what this project is, who it is for, and any course/day/module
context. e.g. "Day 21 of an agents course. A research assistant built on the
OpenAI Agents SDK. The learner already built the same thing in n8n on Day 16.">

=========================================================================
STEP 0 — SURVEY BEFORE YOU WRITE
=========================================================================

Read every source file in the project first. Then work out and write down for
yourself, before creating anything:

  - what the project actually does, in one sentence
  - the entry point: what command a person runs first
  - every external dependency actually imported (not what you assume)
  - every environment variable / secret / config value the code reads
  - every external service it calls, and what happens when one fails
  - the ONE idea this project exists to teach — the thing a reader should
    still remember a month later
  - what already exists in the folder, so you do not overwrite it

If a file in the list below ALREADY EXISTS: read it, keep what is good, and
improve it in place. Never silently replace someone's work. Tell me at the end
which files you created and which you edited.

=========================================================================
WHAT TO CREATE
=========================================================================

1. .gitignore              — FIRST, before anything else
2. .env.example
3. requirements.txt        (or package.json / go.mod — match the language)
4. README.md
5. run_examples.py         (or the equivalent demo runner)
6. developer-tools/        — a numbered reference folder
7. explanation.md          — the line-by-line walkthrough

Details for each follow.

-------------------------------------------------------------------------
1. .gitignore  — write this one FIRST
-------------------------------------------------------------------------
Include the language's standard ignores plus the env file. Open it with a
comment explaining the ordering trap in plain words:

    # Make this file FIRST, before you create .env.
    # If you create .env first and commit it, the key is already in the
    # history and deleting the file later will not remove it.

-------------------------------------------------------------------------
2. .env.example
-------------------------------------------------------------------------
- One entry for EVERY environment variable the code actually reads. Grep for
  getenv / environ / process.env to find them all — do not guess.
- A header comment: copy this to .env, never commit .env.
- Obvious placeholder values (`sk-put-your-key-here`), never a real-looking key.
- Mark which are required and which are optional, and say what each optional
  one unlocks: "# Optional. Only needed for the send_to_discord tool."
- Where a value is awkward to obtain, give the click path to get it:
  "# Discord: Channel Settings > Integrations > Webhooks > New Webhook > Copy URL"

-------------------------------------------------------------------------
3. requirements.txt
-------------------------------------------------------------------------
- Only packages actually imported by the code. No speculative extras.
- Minimum-version pins (`requests>=2.31.0`), not exact pins, for a teaching repo.
- No transitive dependencies — only the ones the project imports directly.

-------------------------------------------------------------------------
4. README.md  — the most important file you will write
-------------------------------------------------------------------------
Aim for something a person can read in three minutes and act on. Use this
skeleton, in this order:

  # <Project name>
  Two or three lines: what it is, and why it exists. If it is a rebuild or a
  comparison of something else, say so and say what the comparison teaches.

  ## Setup — five minutes
  An indented code block of the exact commands, in order, with the Windows
  variant noted inline where it differs:
      python -m venv .venv
      source .venv/bin/activate        # Windows: .venv\Scripts\activate
      pip install -r requirements.txt
      cp .env.example .env             # then put your key in .env
  Follow it with any ordering warning that actually matters (e.g. gitignore
  before .env).

  ## Run it
  Every way to launch it, as literal copy-pasteable commands — the bare run,
  the run with an argument, the examples script, one example by number.

  ## What is in here
  A two-column table: | File | What it is |
  One row per file a reader will touch. Put the one-line point of each file in
  the right column, and bold the instruction where it matters
  ("The three tools. **Read the docstrings**").

  ## The one thing to notice
  A short section on the single most important idea in the project. Name the
  exact file and the exact thing to look at. Say why it matters and what breaks
  if you get it wrong. End with a pull-quote if there is a memorable line.
  THIS SECTION IS THE POINT OF THE README. Do not make it generic.

  ## Exercises  (two or three, no more)
  Concrete, doable in under ten minutes, each teaching something different.
  At least one should be a BREAK IT exercise: change one thing, watch it fail,
  understand why. State what the reader should expect to see.

  ## If something goes wrong
  Point at the troubleshooting doc and name the two things that are usually
  the cause.

Rules for the README: no badges, no emoji, no "Contributing"/"License"/
"Acknowledgements" boilerplate, no feature-list marketing. Horizontal rules
between sections. Commands in indented blocks so they are easy to copy.

-------------------------------------------------------------------------
5. run_examples.py  — the demo runner
-------------------------------------------------------------------------
A script that runs the project through a TEACHING SEQUENCE, not a test suite.

- A module docstring showing both usages: run all, run one by number.
- A single list/array of examples, each carrying three things:
      a TITLE saying what this example demonstrates,
      the INPUT itself,
      a NOTE explaining what to watch for and why it matters.
- Order them so each example shows something the one before it did not.
  A good progression: the warm-up (proves the wiring works) → the main demo
  (the thing this project exists to show) → the interesting edge (where it
  chooses NOT to act) → the honest failure (a gap it must admit to rather than
  fake) → the full combination → a mixed case.
- Print each run clearly: a separator line, the number and title, the input,
  the output, then the note in brackets underneath.
- Accept an index argument to run just one: `python run_examples.py 2`.
- Import the project's own entry function; do not duplicate its logic.
- Where an example needs extra config, say so in its note.

-------------------------------------------------------------------------
6. developer-tools/  — the reference folder
-------------------------------------------------------------------------
Numbered markdown files, `00-START-HERE.md` first. Adapt the list to the
project, but this set covers most of them:

  00-START-HERE.md        the map: a table of | File | What it answers |,
                          plus the mental model the reader needs before
                          reading any of it
  01-setup-guide.md       the long-form setup, including the things that go
                          wrong and the platform differences
  02-<tech>-reference.md  what the main framework/library actually gives you,
                          the parts this project uses, and the parts it does not
  03-<the-core-skill>.md  how to do the central thing WELL — the craft doc
  04-<debugging>.md       how to find out why it did what it did. Include an
                          ordered checklist table: | Step | Question | Where the
                          bug usually is |
  05-troubleshooting.md   symptom → cause → fix, as a table or clear headings.
                          Real errors the reader will actually hit.
  06-comparison-with-X.md this approach vs the obvious alternative, as an
                          honest table with a blank column for the reader to
                          fill in. There is no right answer; the point is
                          learning the trade-off.
  07-experiments.md       things to try that teach something. Each one:
                          what to change, what you should see, why it matters.
                          Mark the most important one with a ★.
  08-limitations.md       what this tool CANNOT do well, honestly. For each:
                          what it is, why it matters in practice, and what to
                          use instead.

Style for these: same register as the README. Short. Concrete. Tables where
things are parallel. Real examples over abstractions. Each file opens with one
or two lines saying what question it answers. Never pad a file to look thorough
— a two-paragraph doc that answers its question beats a page that does not.

-------------------------------------------------------------------------
7. explanation.md
-------------------------------------------------------------------------
Write this LAST, and follow Prompt 1 in prom.md exactly: for every block —
the code, then "**What this block does:**" in plain English, then
"**Line by line:**", then "**Why it is written this way:**" where there is a
real design reason. Purpose before syntax, always.

=========================================================================
RULES THAT APPLY TO EVERYTHING
=========================================================================

1. DO NOT TOUCH THE SOURCE CODE. Adding docs must not change behaviour. If you
   spot a real bug, list it at the end and let me decide — do not fix it.
2. Describe what the code ACTUALLY does. Every command you write in the README
   must work as typed. Every env var must be one the code really reads.
3. Never put a real secret in any file you create. Placeholders only.
4. Write in second person, present tense, plain words, short sentences.
5. Teach the trade-off, not the sales pitch. Say what this approach costs as
   readily as what it gives. The limitations file is not an afterthought.
6. Every document earns its length. Cut anything that is filler.
7. No emoji, no badges, no boilerplate sections nobody reads.
8. Wrap prose at roughly 80 characters.
9. When you are done, print a summary: files created, files edited, any env var
   or dependency you were unsure about, and anything you could not verify.

Survey the project now, then build all of it.
```

---

## How to use Prompt 2

1. Copy the fenced block.
2. Replace `<DESCRIBE: ...>` with a couple of sentences about your project —
   the more context you give about *who it is for*, the better the README and
   the experiments come out.
3. Run it from inside the project folder.

**If you only want part of it,** delete the numbered items you do not need from
the "WHAT TO CREATE" list and their matching detail sections. The prompt works
fine with just, say, items 1–4.

**Adapting to another language:**

| Change | Add this line |
|---|---|
| Node/TypeScript | "This is a Node project — use `package.json` scripts instead of `requirements.txt`, and `examples.ts` run via `npm run examples`." |
| Go / Rust | "Use `go.mod` / `Cargo.toml`. The examples runner is a `examples/` folder of runnable programs." |
| No secrets involved | "Skip `.env.example`; there are no secrets. Mention config in the README instead." |
| Not a teaching repo | "Drop the exercises and experiments. Keep the tone practical rather than instructional." |

**A note on ordering:** the prompt deliberately makes `.gitignore` first and
`explanation.md` last. The first prevents committing a key before one exists;
the last is easier to write once the model has already surveyed the whole
project for the README.
