# Memphis

Memphis is a task for AI agents built from a real-world evaluation. In October 2026 GPT-6.1 Sol, called Seb, managed two hired
workers in Cairo over chat for five shifts with 7,000 EGP, to get USB desk lamps built and delivered. Memphis rebuilds that job as
a [Harbor](https://github.com/harbor-framework/harbor) task: one language model plays the city (both workers and every shop) from
the shops, prices and stock the workers found, the real chats, and how often things went wrong in October.

The paper is on arXiv: [2611.29824](https://arxiv.org/abs/2611.29824). Its source and data are in `paper/`.

| Path | What |
|---|---|
| `build_task.py`, `world/`, `hsim/`, `agent_tools/`, `harbor_ext/` | The task builder, the world's facts and brief, the server that keeps the clock and the budget, the agent's tools, and the Harbor agents for GPT (Codex) and Claude (Claude Code) |
| `work/catalog/` | The October chats and setbacks as the task uses them |
| `october/` | A redacted copy of the October record: Seb's transcript, all worker messages, spending requests, emails and calls, and the workers' photos |
| `paper/` | The paper, its source, and the data and scripts behind each number in it |
| `RESULTS.md`, `docs/` | Every round and its results, the design, the audit method and the history of fixes |
| `scripts/`, `tests/` | Running rounds, checking trials, the photo library, tests |

The raw trials of the final GPT round (r18) and the three Claude rounds, with their tasks and audits, are in this repository's
release `v1.0`.

## Running

A trial needs Docker, Python 3.12, Harbor 0.23 (`pip install -r requirements-lock.txt`), and a Codex sign-in with access to
GPT-6.1 Sol for the world model (and for the agent, if it is GPT). `python3 build_task.py --seed 10 --out tasks/memphis-seed10`
builds a task; `example-config.yaml` runs one.

## What is removed

Both workers agreed in writing to the use of their messages, photos and first names in the paper, the simulator and a public
dataset. In every file, worker A's surname and home street, worker B's phone number, and the client's name and home address
(where the lamps were delivered) are replaced by `[street removed]`, `[phone removed]`, `[name removed]`, `[number removed]` and
`[map link removed]`. Tokens in URLs, the agent's mail account and machine paths are replaced too. Because the address is
replaced, built tasks do not match the checksums recorded in the trials; they run the same way. The transcripts of the phone
calls made in October are removed; each call's summary stays. Businesses keep their names.

## Citation

```bibtex
@misc{ahmed2026memphiscasestudyseeding,
  title={Memphis: A Case Study in Seeding an Agent Task from a Model's Real-World Attempt},
  author={Ibrahim A. Ahmed and Ahmed Sameh Khalil},
  year={2026},
  eprint={2611.29824},
  archivePrefix={arXiv},
  primaryClass={cs.AI},
  url={https://arxiv.org/abs/2611.29824}
}
```

## License

Code: MIT (`LICENSE`). Data, text and photos: CC BY 4.0.
