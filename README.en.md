# Minhas repetições

[![Minhas repetições](guia/assets/banner-en.jpg)](https://linnoff88-dev.github.io/arckhe-/guia/en/)

**🇧🇷 [Português](README.md) · 🇺🇸 [English](README.en.md) · 🇪🇸 [Español](README.es.md)**

[![Minhas repetições](guia/assets/banner.jpg)](https://linnoff88-dev.github.io/arckhe-/guia/en/)

🎬 Video: https://www.youtube.com/watch?v=3aanGE9Jpz8 · Short: https://youtube.com/shorts/cEHKKEnX4GU

## What it is

A free toolkit that reads your **Claude Code** and **Codex** history and shows what you type over and over.
For each repetition, it tells you whether it becomes a **shortcut** (short text pasted with a trigger), a **skill** (a procedure with steps), a **check-in** (“what’s the status?”, which calls for an end-of-task notification, not a shortcut), or just a **response** (“yes,” “continue”). It also measures which model gets your requests, how much effort they use, how many times you hit the limit, and how many turns lasted more than 10 minutes.

Runs on your machine, using only Python 3 (standard library). It doesn’t call APIs or send anything anywhere.

## 📖 User guide

Complete guide (landing page + walkthrough): **https://linnoff88-dev.github.io/arckhe-/guia/en/**

## Why

You don’t notice what you repeat because each time feels like the first. On a real production machine, over 30 days: **2,287
typed requests, 12.6% repeated**, and the most common one, “what’s the status,” appeared **68 times**. In that same month, the agents ran 13,505 turns, almost 6 for every typed request. These numbers are in
`exemplos/numeros-maquina-ARCKHÉ-30dias.json`, which contains counts only, with no text.

## The process, from start to finish

| # | Step | Command | Who |
|---|---|---|---|
| 1 | Download the kit | `git clone https://github.com/linnoff88-dev/minhas-repeticoes && cd minhas-repeticoes` | 🧠 you |
| 2 | Check that it runs | `python3 -m unittest discover -s testes` (15 tests, made-up data) | ⚙️ script |
| 3 | Read your history | `python3 repeticoes.py` (default: 30 days, `~/.claude/projects` and `~/.codex/sessions`) | ⚙️ script |
| 4 | View the report | Open `relatorio/relatorio.html` in your browser | 🧠 you |
| 5 | Enable shortcuts | Copy `relatorio/atalhos-espanso.yml` to Espanso’s `match` folder (Linux `~/.config/espanso/match/`, Mac `~/Library/Application Support/espanso/match/`) or paste them from `atalhos.md` into your text expander | 🧠 you |
| 6 | Turn requests with steps into a skill | Review `relatorio/skills-rascunho/<nome>/SKILL.md`, write the steps, and move it to `~/.claude/skills/`. To have the agent do it with you: `mkdir -p ~/.claude/skills && cp -r skill/minhas-repeticoes ~/.claude/skills/ && cp repeticoes.py DICAS.md ~/.claude/skills/minhas-repeticoes/` | 🧠 you (or 🤖 the agent, with the kit’s skill) |
| 7 | Adjust the model and effort | Read `model` and `model\|effort` in the report and follow tips 6–9 in `DICAS.md` | 🧠 you |
| 8 | Measure again in 30 days | `python3 repeticoes.py --saida relatorio-mes2` and compare `numeros.json` | ⚙️ script |

Options: `--dias 7` · `--saida <pasta>` · `--claude <pasta>` · `--codex <pasta>` · `--sem-codex`.

## What it outputs

| File | Contents | Can you show it to someone? |
|---|---|---|
| `relatorio.html` | charts: repetition, groups, model, effort, limit, long turns | ❌ contains excerpts from your requests |
| `relatorio.md` | same information in text | ❌ |
| `atalhos.md` / `atalhos-espanso.yml` | one shortcut per repeated short request | ❌ |
| `skills-rascunho/` | one SKILL.md draft per repeated long request | ❌ |
| `numeros.json` | counts only (no text) | ✅ |

## How it decides

- **Only what you typed.** Counts turns with `turnOrigin: human` (Claude Code) or sessions started by the user (Codex). `claude -p`, watchers, notifications, subagents, and `codex exec` are counted separately as automatic turns.
- **Resumed sessions aren’t counted twice** (the same `uuid` is read only once).
- **Similar means equal.** Groups requests with the same words (cut to 5 letters: publica/publique/publicou) and allows typos in short requests (“sistuacao” = “situacao”). A repetition means 3 times or more.
- **Shortcut × skill:** up to ~120 characters is a shortcut; above that, if it has steps, it’s a skill. Up to 10 characters (“sim,” “1”) is a response. A follow-up question (situation, progress, running, status) is a check-in and doesn’t become a shortcut. A pasted link by itself is `link`; a `/command` you already use is `ja-e-atalho`.
- **Limit:** the same notice (“resets 9:10pm”) across multiple sessions counts as 1 hit. In Codex, it counts the session that reached 100%.

## Contents

- `repeticoes.py`: the kit (one file, no dependencies)
- `DICAS.md`: 12 tips for what to do with the things you repeat
- `skill/minhas-repeticoes/SKILL.md`: a skill for Claude Code to run the kit and turn groups into shortcuts/skills with you
- `testes/`: 15 tests with made-up history (`gerar_dados.py`)
- `exemplos/`: `relatorio-inventado/` (output with made-up data) and `numeros-maquina-ARCKHÉ-30dias.json` (real numbers, no text)

## Limitations

- The report is in Portuguese.
- Reads the November 2026 log format for Claude Code and Codex. Older logs without `turnOrigin` are handled by the old rule (interactive CLI = you).
- Effort appears only when Claude Code records the API request (`?` = not recorded).
- Grouping is based on words, not meaning: “posts on the portal” and “publish on the portal” may end up in separate groups.

Free on [ARCKHÉ AI](https://ARCKHÉ AI), right on the internet.
