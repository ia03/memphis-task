# Design

Memphis turns a real field project into a repeatable task for AI agents. In October 2026 an AI manager ("Seb") ran two hired
workers in Cairo over Telegram for five shifts, with 7,000 EGP, to get desk lamps built from components; it delivered 2. The task
replays the first two shifts (Thursday 1 October 14:00-17:00 and Sunday 4 October 13:00-17:00, Cairo time) against a simulated
city. The agent under test plays Seb. Score = qualifying lamps delivered to the address by Sunday 17:00, divided by 9, capped at 1.

## Components

```
  agent container                          simulator container
  ---------------                          -------------------
  Codex CLI (agent under test)             hsim/server.py: clock, money ledger, agent API, photos
  agent_tools/field.py   --- HTTP --->       |  events (what Seb did)        ^ timed outputs
  agent_tools/comms.py                       v                               |
  agent_tools/web.py                       hsim/simulator.py: one model (Codex CLI) in its own folder
                                             BRIEF.md, task_rules.md, grading.md, facts.json,
                                             october/ (real record), state.md, log.md
                                           grade call at the end (same folder, read-only)
```

`build_task.py` packages one seed as a Harbor task: an agent container (Codex CLI and the three tools, network limited to the
model API through a proxy), a simulator container, and a verifier that ends the run and reads the score.

### What the agent can do

The same three tools the real manager had:

- `field.py`: `brief`, `status`, `clock`, `inbox`, `message WORKER TEXT`, `spend WORKER AMOUNT PURPOSE` (a numbered spend notice;
  workers may pay only against one), `cancel-spend`, `get-attachment` (photos), `sleep UNTIL`.
- `comms.py`: email and AI phone calls to businesses.
- `web.py`: search and open pages. The corpus is the real search results the manager saw in October, plus the seed's shop pages.

The agent's prompt (`world/agent_prompt.md`) is the real task text with the shorter schedule. The hinted condition adds
`world/hint_note_v3.md`, a page of market notes from "a previous manager".

### The world model

One model (GPT-6.1 Sol at medium effort, through Codex CLI) plays the whole world: both workers, every shop and technician, the
city and time. It works in a folder (`hsim/simulator.py`):

- `BRIEF.md` (`world/simulator_brief.md`, 59 lines): what to simulate, the sources, how hard the real world was, and the rules
  for staying faithful. There are no case rules: nothing about particular plans, shops or outcomes.
- `task_rules.md` and `grading.md`: the agent's rules and how a lamp is judged.
- `facts.json`: this seed's world truth (below). Nothing else exists.
- `october/`: the real record. `worker-chats.json` (798 messages between the real manager and workers), `workers.json` (how each
  worker behaved, with message ids), `incidents.md` (how often things went wrong, and of what kind).
- `state.md` and `log.md`: the model's own memory. It rewrites the state each step and appends what happened to the log.

### A step

The server calls the model whenever Seb does something, when a shift starts or ends, and when the model asked to be woken.
Each call gives the time, everything Seb did since the last call (messages, spend notices, cancellations, calls, emails), what was
delivered and what is still scheduled, and any worker mistakes drawn (below). The model updates its files and returns timed outputs: worker
messages (with a photo label), payments against spend notices, call results, emails, confirmed cancellations, scheduled items to
withdraw, and the next time it needs to decide something. The server delivers each output at its time. Outputs naming an unknown
worker are sent back as an event rather than dropped.

Time runs at 1x while the agent works, stops while the world model thinks, and jumps forward when the agent sleeps
(`hsim/clock.py`). The agent cannot see the model's files, only what workers write and send.

### The seed

`hsim/world.py` builds the facts for a seed. Observed facts come from `world/*.yaml`: the shops the real workers visited keep
their real stock, prices, staff answers and referrals on every seed (`suppliers.yaml`), along with items and their real sizes
(`items.yaml`), the workers (`workers.yaml`) and the delivery address (`delivery.yaml`). Unobserved facts are sampled once per seed
from `priors.yaml`: further walk-in shops of the same kinds in each district, with stock and prices from the range of the real
ones; technician capacity and terms; whether phone and email get answers; and places to work. Ride times, fares and the seed's
traffic come from a model fitted to the 24 recorded trips (`hsim/travel.py`).

### Realism

- **Facts only.** The model may not add a shop, item, price, service or skill. A shop does only what its facts list.
- **Real people.** Worker behaviour comes from their real messages: reply speed, style, initiative, what they refuse, and that
  they are not technical (they never wire, solder or cut).
- **Real friction rates.** `october/incidents.md` lists how often supplier claims were wrong, first asks failed, technician
  promises slipped and trips ran long. The model applies friction of those kinds at about those rates, wherever the facts allow.
- **Worker mistakes drawn in code.** Language models play competent people too competently. So the server draws, for each stretch of
  shift time, which workers make one ordinary mistake, at each real worker's rate (`slips_per_shift_hour` in `workers.yaml`, from the
  record), and which kind, at the record's mix (`mistake_kinds`: misreads, wrong turns, unannounced route changes). The model
  plays it where it fits, as a new mistake, never merged into an earlier one or skipped. The draw uses the seed.
- **Facts first.** Each step is a fresh model session. The brief makes it look up every shop, person, ride and walk the step
  involves in `facts.json`, quote the facts it applies in its log, keep the governing facts in a "Facts in play" section of its
  notes, and let an entity's own facts override the record's general rates (since rc18).
- **Physical consistency.** One place at a time, carried items, travel and work durations from the facts, and parts that can only
  be arranged and held in ways their facts allow.
- **Photos.** Workers send photos by label (item, heads, lamp state, ride quote, invoice, scene). `hsim/media.py` renders ride-app
  screenshots and receipts and picks library photos: generated phone photos (`scripts/photos/`) and 16 real photos from October
  (parts, hands, packaging and a shop receipt; no faces).

### Grading

At 17:00 Sunday a separate call to the same model, read-only on the world folder, lists every lamp that reached the address and
judges it against `world/grading.md`: built from components during the run, works from a 5V USB port (the grader decides power
from the parts and joins), one object that stands stable on a desk or clamps to its edge, lights an open A4-size area of the
desk well enough to read and write there with room for a hand (up to v12.0-rc10 the standard also required the
light about 20 cm or more above the desk; since rc11 the grader judges the lit area, not an exact height), safe to handle. Plans, photos and claims do not count. The server records the score.

### Why 9

When the target was fixed, after round r12, 9 was the highest count shown on every seed. Audited trials have since reached 10 or
more on every seed, so 9 is conservative. See [RESULTS.md](../RESULTS.md).

## Code and model

The code keeps only the clock, the ledger, the API and photo rendering; the world's behaviour is in the brief, the facts and the
record. Core code (`hsim/`, `agent_tools/`, `harbor_ext/`, `build_task.py`) is about 2,000 lines. `tests/` covers the server's
timing, ledger and worker-mistake rules and the photo library.

## What varies between runs

Two runs of the same seed share the facts. They differ because both the agent and the world model sample, and because
different plans lead to different steps, so the seeded worker-mistake draws also fall at different moments. The audits judge each run on its own.
