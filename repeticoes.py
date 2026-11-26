#!/usr/bin/env python3
"""minhas-repeticoes — lê o seu histórico do Claude Code e do Codex, acha o que você digita de novo e de novo,
e diz o que vira ATALHO (texto curto colado) e o que vira SKILL (procedimento com passos).
De quebra mede: quanto vai para cada modelo, com que esforço, quantas vezes bateu no limite e quantos
turnos passaram de 10 minutos.

Tudo local, só biblioteca padrêo do Python. Nada sai da máquina.

Uso:
  python3 repeticoes.py                        # últimos 30 dias, pastas padrêo (~/.claude/projects, ~/.codex/sessions)
  python3 repeticoes.py --dias 7 --saida relatorio-semana
  python3 repeticoes.py --claude <pasta> --codex <pasta> --saida <pasta>
Saída (em --saida, padrêo ./relatorio): relatorio.html, relatorio.md, atalhos.md, skills-rascunho/, numeros.json
numeros.json só tem números (nenhum texto seu) — é o único arquivo pensado para mostrar a alguém.
"""
from __future__ import annotations

import argparse
import difflib
import html
import json
import os
import re
import sys
import time
import unicodedata
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from pathlib import Path

VERSAO = "1.0.0"
LIMIAR = 0.6          # Jaccard mínimo para dois pedidos contarem como "o mesmo"
MIN_REPETE = 3        # aparece 3+ vezes = repetiçêo
CURTO = 120           # até isso de caracteres (já normalizado) = candidato a atalho; acima = skill
TURNO_LONGO_MS = 10 * 60 * 1000

PARADAS = set("""a o e de da do das dos em no na nos nas um uma para pra por com que se isso este esta esse essa
the to and of in on for is it this that me eu voce vc q ai la os as ao ou mais ja tambem agora so
deste desta dessa desse tres todo toda tudo final inicio fazer faca""".split())

LIMITE_RE = re.compile(r"hit your (session|weekly|usage|daily)? ?limit", re.I)
# comandos da própria ferramenta (limpar, sair, trocar modelo) nêo sêo trabalho repetido
COMANDOS_INTERNOS = {"clear", "compact", "exit", "quit", "model", "effort", "resume", "login", "logout", "cost", "status",
                     "config", "help", "mcp", "permissions", "fast", "context", "usage", "rewind", "plugin", "doctor", "memory"}
# pergunta de acompanhamento ("qual a situaçêo?", "o que está rodando?"): nêo vira atalho, vira aviso de fim / status
CHECAGEM_RE = re.compile(r"\b(situ\w*|sist?u\w*cao|andamento|rodand\w*|status|progresso|terminou|acabou)\b")
COMANDO_RE = re.compile(r"<command-name>\s*/?([\w:.-]+)\s*</command-name>")


@dataclass
class Pedido:
    texto: str
    fonte: str              # claude | codex
    modelo: str = "?"
    esforco: str = "?"
    data: str = ""
    comando: str = ""       # /prime, /r7ex… quando já é atalho


@dataclass
class Medidas:
    pedidos: list = field(default_factory=list)
    robo: Counter = field(default_factory=Counter)          # turnos automáticos por fonte
    modelo_humano: Counter = field(default_factory=Counter)
    esforco_humano: Counter = field(default_factory=Counter)  # "modelo|esforço"
    limites: Counter = field(default_factory=Counter)        # session/weekly/codex
    turnos_longos: Counter = field(default_factory=Counter)  # modelo → turnos > 10 min
    turnos: Counter = field(default_factory=Counter)         # modelo → turnos medidos
    arquivos: int = 0
    _vistos: set = field(default_factory=set)          # uuid já contado (sessêo retomada copia o histórico)
    _limites_vistos: set = field(default_factory=set)


# ---------------------------------------------------------------- leitura

def texto_do_conteudo(c) -> str:
    if isinstance(c, str):
        return c
    if isinstance(c, list):
        partes = []
        for b in c:
            if isinstance(b, dict):
                if b.get("type") == "tool_result":
                    return ""          # resposta de ferramenta, nêo é pedido
                if b.get("type") in ("text", "input_text"):
                    partes.append(b.get("text", ""))
        return "\n".join(partes)
    return ""


def e_lixo(t: str) -> bool:
    s = t.lstrip()
    return (not s or s.startswith(("<system-reminder", "<task-notification", "<local-command", "[Image", "[Request interrupted",
                                   "Caveat:", "# AGENTS.md", "<INSTRUCTIONS", "<environment_context", "<user_instructions",
                                   "This session is being continued", "[Memory context]")))


def e_humano_claude(d: dict, t: str) -> bool | None:
    """True = você digitou; False = robô (claude -p, vigia, notificaçêo); None = ignorar."""
    if d.get("isSidechain") or d.get("isMeta"):
        return None
    if "turnOrigin" in d or "promptSource" in d:
        if d.get("turnOrigin") == "human" or d.get("promptSource") in ("typed", "suggestion_accepted"):
            return True
        return False
    # logs antigos, sem os campos novos: só a CLI interativa conta como você
    return d.get("entrypoint", "cli") == "cli"


def ler_claude(raiz: Path, desde: float, m: Medidas):
    for f in sorted(raiz.glob("*/*.jsonl")):
        try:
            if f.stat().st_mtime < desde:
                continue
        except OSError:
            continue
        m.arquivos += 1
        modelo, esforco, aguardando, humano_turno = "?", "?", None, False
        with open(f, errors="ignore") as fh:
            for linha in fh:
                cab = linha[:120]
                if '"api-request"' in cab:
                    try:
                        d = json.loads(linha)
                    except ValueError:
                        continue
                    p = d.get("params") or {}
                    modelo = p.get("model") or modelo
                    esforco = str((p.get("output_config") or {}).get("effort") or esforco)
                    if aguardando is not None:
                        aguardando.modelo, aguardando.esforco = modelo, esforco
                        aguardando = None
                    continue
                if '"role":"assistant"' in linha[:400] or '"role": "assistant"' in linha[:400]:
                    if '"isSidechain":true' in linha[:200] or '"isSidechain": true' in linha[:200]:
                        continue
                    mm = re.search(r'"model":\s*"([^"]+)"', linha)
                    if mm and not mm.group(1).startswith("<"):
                        modelo = mm.group(1)
                        if aguardando is not None and aguardando.modelo == "?":
                            aguardando.modelo = modelo
                    if "isApiErrorMessage" in linha:
                        lm = LIMITE_RE.search(linha)
                        if lm:   # um limite = (dia, aviso "resets …"): a mesma batida em várias sessões conta 1
                            dia = (re.search(r'"timestamp":\s*"(\d{4}-\d\d-\d\d)', linha) or [None, ""])[1]
                            aviso = (re.search(r"resets ([^\"\\(]+)", linha) or [None, ""])[1].strip()
                            chave = ((lm.group(1) or "session").lower(), dia, aviso)
                            if chave not in m._limites_vistos:
                                m._limites_vistos.add(chave)
                                m.limites[chave[0]] += 1
                    continue
                if '"turn_duration"' in linha:
                    try:
                        d = json.loads(linha)
                    except ValueError:
                        continue
                    if humano_turno:
                        m.turnos[modelo] += 1
                        if (d.get("durationMs") or 0) >= TURNO_LONGO_MS:
                            m.turnos_longos[modelo] += 1
                    continue
                if '"type":"user"' not in linha[:600] and '"type": "user"' not in linha[:600]:
                    continue
                try:
                    d = json.loads(linha)
                except ValueError:
                    continue
                if d.get("type") != "user":
                    continue
                u = d.get("uuid")
                if u:
                    if u in m._vistos:
                        continue
                    m._vistos.add(u)
                t = texto_do_conteudo((d.get("message") or {}).get("content"))
                h = e_humano_claude(d, t)
                cm = COMANDO_RE.search(t or "")
                if h is None or (not (t or "").strip()):   # vazio = resposta de ferramenta
                    continue
                if not h:   # turno automático (claude -p, vigia, notificaçêo): conta à parte
                    m.robo["claude"] += 1
                    humano_turno = False
                    continue
                if e_lixo(t) and not cm:
                    continue
                if cm and cm.group(1).lower() in COMANDOS_INTERNOS:
                    continue
                humano_turno = True
                barra_cmd = re.match(r"/([\w:.-]+)", t.strip())
                if barra_cmd and barra_cmd.group(1).lower() in COMANDOS_INTERNOS:
                    continue
                p = Pedido(texto=t.strip(), fonte="claude", modelo=modelo, esforco=esforco,
                           data=(d.get("timestamp") or "")[:10],
                           comando=("/" + cm.group(1)) if cm else (("/" + barra_cmd.group(1)) if barra_cmd else ""))
                if cm:
                    args = re.search(r"<command-args>(.*?)</command-args>", t, re.S)
                    p.texto = p.comando + (" " + args.group(1).strip() if args and args.group(1).strip() else "")
                m.pedidos.append(p)
                aguardando = p


def ler_codex(raiz: Path, desde: float, m: Medidas):
    for f in sorted(raiz.glob("**/*.jsonl")):
        try:
            if f.stat().st_mtime < desde:
                continue
        except OSError:
            continue
        m.arquivos += 1
        modelo, esforco, gatilho, teto_visto = "?", "?", "user", False
        with open(f, errors="ignore") as fh:
            for linha in fh:
                try:
                    d = json.loads(linha)
                except ValueError:
                    continue
                p = d.get("payload") or {}
                tp = p.get("type")
                if tp == "thread_settings_applied":
                    s = p.get("thread_settings") or {}
                    modelo = s.get("model") or modelo
                    esforco = str(s.get("reasoning_effort") or esforco)
                elif tp == "task_started":
                    gatilho = (p.get("turn_attribution") or {}).get("turn_trigger") or gatilho
                    if gatilho != "user":
                        m.robo["codex"] += 1
                elif tp == "token_count":
                    rl = (p.get("rate_limits") or {}).get("primary") or {}
                    if (rl.get("used_percent") or 0) >= 100 and not teto_visto:
                        m.limites["codex"] += 1
                        teto_visto = True
                elif tp == "message" and p.get("role") == "user" and gatilho == "user":
                    t = texto_do_conteudo(p.get("content"))
                    if e_lixo(t):
                        continue
                    m.pedidos.append(Pedido(texto=t.strip(), fonte="codex", modelo=modelo, esforco=esforco,
                                            data=(d.get("timestamp") or "")[:10]))


# ---------------------------------------------------------------- agrupamento

def normaliza(t: str) -> str:
    t = unicodedata.normalize("NFKD", t.lower())
    t = "".join(c for c in t if not unicodedata.combining(c))
    t = re.sub(r"https?://\S+", " URL ", t)
    t = re.sub(r"(~|/)[\w./-]{3,}", " CAMINHO ", t)
    t = re.sub(r"\b\d+([.,:/]\d+)*\b", " N ", t)
    t = re.sub(r"[^\w\s]", " ", t)
    return re.sub(r"\s+", " ", t).strip()


def palavras(n: str) -> frozenset:
    """Palavras que importam, cortadas em 5 letras: publica/publique/publicou viram 'publi'."""
    return frozenset(w[:5] for w in n.split() if w not in PARADAS and len(w) > 1)


def trigramas(n: str) -> frozenset:
    s = f"  {n} "
    return frozenset(s[i:i + 3] for i in range(len(s) - 2))


def jaccard(a: frozenset, b: frozenset) -> float:
    if not a or not b:
        return 1.0 if a == b else 0.0
    return len(a & b) / len(a | b)


def agrupar(pedidos: list[Pedido], limiar: float = LIMIAR) -> list[list[Pedido]]:
    """Agrupa pedidos parecidos. Guloso: cada pedido entra no 1º grupo cujo representante passa do limiar.
    Índice invertido por palavra para nêo comparar com tudo."""
    grupos: list[list[Pedido]] = []
    reps: list[frozenset] = []
    reps_tri: list[frozenset] = []
    textos: list[str] = []
    # curtos primeiro: o representante de cada grupo é a forma mais enxuta do pedido
    pedidos = sorted(pedidos, key=lambda p: len(normaliza(p.texto)))
    indice: dict[str, set[int]] = defaultdict(set)
    exatos: dict[str, int] = {}
    for p in pedidos:
        n = normaliza(p.texto)[:600]
        if n in exatos:
            grupos[exatos[n]].append(p)
            continue
        w = palavras(n)
        tri = trigramas(n) if len(n) <= 60 else frozenset()
        candidatos = set()
        for x in w:
            candidatos |= indice.get(x, set())
        melhor, nota = -1, 0.0
        for g in candidatos:
            j = jaccard(w, reps[g])
            if tri and reps_tri[g] and j < limiar:   # pedido curto: aceita erro de digitaçêo ("sistuacao" = "situacao")
                j = max(j, difflib.SequenceMatcher(None, n, textos[g]).ratio() - 0.15)
            if j > nota:
                melhor, nota = g, j
        if melhor >= 0 and nota >= limiar:
            grupos[melhor].append(p)
            exatos[n] = melhor
            continue
        grupos.append([p])
        reps.append(w)
        reps_tri.append(tri)
        textos.append(n)
        exatos[n] = len(grupos) - 1
        for x in w:
            indice[x].add(len(grupos) - 1)
    return grupos


def classifica(grupo: list[Pedido]) -> str:
    """ja-e-atalho (já é /comando) · resposta (sim, ok, 1, continue: nêo vale atalho) · atalho · skill"""
    if all(p.comando for p in grupo):
        return "ja-e-atalho"
    n = normaliza(min((p.texto for p in grupo), key=len))
    if n.lower() == "url":
        return "link"
    if len(n) <= 60 and CHECAGEM_RE.search(n):
        return "checagem"
    if len(n) <= 10 and len(n.split()) <= 2:
        return "resposta"
    tam = sorted(len(normaliza(p.texto)) for p in grupo)[len(grupo) // 2]
    return "atalho" if tam <= CURTO else "skill"


def nome_sugerido(grupo: list[Pedido]) -> str:
    c = Counter()
    for p in grupo:
        c.update({w for w in normaliza(p.texto).split() if w.isalpha() and w.islower() and w not in PARADAS and len(w) > 3})
    ws = [w for w, _ in sorted(c.items(), key=lambda x: (-x[1], x[0]))[:2]] or ["pedido"]   # determinístico
    return "-".join(ws)[:40]


# ---------------------------------------------------------------- relatório

def calcula(m: Medidas) -> dict:
    grupos = agrupar(m.pedidos)
    rep = [g for g in grupos if len(g) >= MIN_REPETE]
    rep.sort(key=len, reverse=True)
    em_rep = sum(len(g) for g in rep)
    total = len(m.pedidos)
    tipos = Counter()
    for g in rep:
        tipos[classifica(g)] += len(g)
    for p in m.pedidos:
        m.modelo_humano[p.modelo] += 1
        m.esforco_humano[f"{p.modelo}|{p.esforco}"] += 1
    numeros = {
        "versao": VERSAO,
        "arquivos_lidos": m.arquivos,
        "pedidos_seus": total,
        "turnos_automaticos": dict(m.robo),
        "grupos_repetidos": len(rep),
        "pedidos_em_repeticao": em_rep,
        "pct_repeticao": round(100 * em_rep / total, 1) if total else 0.0,
        "pedidos_por_tipo": dict(tipos),
        "grupos_atalho": sum(1 for g in rep if classifica(g) == "atalho"),
        "grupos_skill": sum(1 for g in rep if classifica(g) == "skill"),
        "grupos_ja_atalho": sum(1 for g in rep if classifica(g) == "ja-e-atalho"),
        "grupos_resposta": sum(1 for g in rep if classifica(g) == "resposta"),
        "grupos_link": sum(1 for g in rep if classifica(g) == "link"),
        "grupos_checagem": sum(1 for g in rep if classifica(g) == "checagem"),
        "maior_grupo": len(rep[0]) if rep else 0,
        "top10_cobrem_pct": round(100 * sum(len(g) for g in rep[:10]) / total, 1) if total else 0.0,
        "modelo": dict(m.modelo_humano.most_common()),
        "esforco": dict(m.esforco_humano.most_common()),
        "limites": dict(m.limites),
        "turnos_medidos": dict(m.turnos),
        "turnos_mais_de_10min": dict(m.turnos_longos),
    }
    return {"numeros": numeros, "repetidos": rep}


def barra(rotulos_valores, cor="#FACC15"):
    tot = max([v for _, v in rotulos_valores] or [1])
    linhas = []
    for r, v in rotulos_valores:
        w = 100 * v / tot if tot else 0
        linhas.append(f'<div class="b"><span class="r">{html.escape(str(r))}</span>'
                      f'<span class="t"><i style="width:{w:.1f}%;background:{cor}"></i></span><b>{v}</b></div>')
    return "\n".join(linhas)


def forma_comum(g: list[Pedido]) -> str:
    """O jeito que você mais escreveu o pedido (empate: o mais curto)."""
    c = Counter(re.sub(r"\s+", " ", p.texto.strip()) for p in g)
    return min(c, key=lambda t: (-c[t], len(t)))


def amostra(g: list[Pedido], n=160) -> str:
    t = forma_comum(g)
    t = re.sub(r"\s+", " ", t)
    return t[:n] + ("…" if len(t) > n else "")


def escreve(res: dict, saida: Path, dias: int):
    saida.mkdir(parents=True, exist_ok=True)
    N, rep = res["numeros"], res["repetidos"]
    (saida / "numeros.json").write_text(json.dumps(N, ensure_ascii=False, indent=2))

    # atalhos.md — o que colar no seu expansor de texto (Espanso, atalho do teclado, snippet do editor)
    at = ["# Seus atalhos (gerado por minhas-repeticoes)", "",
          "Cada bloco é um pedido que você repetiu. Cole no seu expansor de texto com o gatilho sugerido.", ""]
    sk, esp, usados = [], [], Counter()
    for g in rep:
        tipo = classifica(g)
        nome = nome_sugerido(g)
        usados[nome] += 1
        if usados[nome] > 1:
            nome = f"{nome}{usados[nome]}"
        if tipo == "atalho":
            at += [f"## ;{nome}  ({len(g)}×)", "", "```", forma_comum(g), "```", ""]
            esp.append((nome, forma_comum(g)))
        elif tipo == "skill":
            sk.append((nome, g))
    (saida / "atalhos.md").write_text("\n".join(at))
    # mesmo conteúdo no formato do Espanso (expansor de texto livre: Linux, Mac, Windows)
    y = ["# gerado por minhas-repeticoes. Copie para a pasta match do Espanso:",
         "#   Linux ~/.config/espanso/match/ · Mac ~/Library/Application Support/espanso/match/ · Windows %APPDATA%\\espanso\\match\\",
         "matches:"]
    vistos = Counter()
    for nome, t in esp:
        g = nome[:20]
        vistos[g] += 1
        if vistos[g] > 1:
            g = f"{g[:18]}{vistos[g]}"
        y += [f'  - trigger: ";{g}"', f"    replace: {json.dumps(t, ensure_ascii=False)}"]
    (saida / "atalhos-espanso.yml").write_text("\n".join(y) + "\n")
    sd = saida / "skills-rascunho"
    if sd.is_dir():   # pasta gerada por este script: refaz do zero a cada rodada
        import shutil
        shutil.rmtree(sd)
    sd.mkdir()
    for nome, g in sk[:15]:
        d = sd / nome
        d.mkdir(exist_ok=True)
        ex = "\n\n".join(f"### Exemplo {i+1}\n\n```\n{p.texto.strip()[:1500]}\n```" for i, p in enumerate(g[:3]))
        (d / "SKILL.md").write_text(
            f"---\nname: {nome}\ndescription: RASCUNHO — você pediu isto {len(g)} vezes. Reescreva a descriçêo: quando usar e o que entrega.\n---\n\n"
            f"# {nome}\n\nRascunho montado a partir de {len(g)} pedidos parecidos. Junte os passos que se repetem,\n"
            f"tire o que muda de um pedido para outro (vira argumento) e teste com /{nome} antes de usar.\n\n"
            f"## Passos (preencha)\n\n1. \n2. \n3. \n\n## Como você pediu\n\n{ex}\n")

    # relatorio.md
    md = [f"# Minhas repetições — últimos {dias} dias", "",
          f"- Pedidos seus: **{N['pedidos_seus']}** (turnos automáticos fora da conta: {sum(N['turnos_automaticos'].values())})",
          f"- Em repetiçêo (3+ vezes): **{N['pedidos_em_repeticao']} = {N['pct_repeticao']}%**, em {N['grupos_repetidos']} grupos",
          f"- Os 10 maiores grupos cobrem {N['top10_cobrem_pct']}% de tudo que você digitou",
          f"- Viram atalho: {N['grupos_atalho']} grupos · viram skill: {N['grupos_skill']} · já sêo comando: {N['grupos_ja_atalho']} · "
          f"checagens (pedem aviso de fim, nêo atalho): {N['grupos_checagem']} · respostas curtas (sim, ok): {N['grupos_resposta']}",
          "- Limites batidos: " + (", ".join(f"{k} {v}" for k, v in N["limites"].items()) or "nenhum"),
          "- Turnos de mais de 10 min: " + (", ".join(f"{k} {v}" for k, v in N["turnos_mais_de_10min"].items()) or "nenhum"), "",
          "## Os grupos que mais se repetem", ""]
    for i, g in enumerate(rep[:40], 1):
        md.append(f"{i}. **{len(g)}×** `{classifica(g)}` — {amostra(g)}")
    md += ["", "## Modelo dos seus pedidos", ""] + [f"- {k}: {v}" for k, v in N["modelo"].items()]
    md += ["", "## Modelo | esforço", ""] + [f"- {k}: {v}" for k, v in N["esforco"].items()]
    (saida / "relatorio.md").write_text("\n".join(md))

    # relatorio.html (abre no navegador, sem internet)
    tops = "".join(f"<li><b>{len(g)}×</b> <em class='{classifica(g)}'>{classifica(g)}</em> {html.escape(amostra(g))}</li>"
                   for g in rep[:25])
    pct = N["pct_repeticao"]
    h = f"""<!doctype html><html lang="pt-BR"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Minhas repetições</title><style>
:root{{--f:#0c0c10;--c:#16161d;--t:#f4f4f5;--m:#a1a1aa;--a:#FACC15}}
body{{margin:0;background:var(--f);color:var(--t);font:16px/1.5 system-ui,sans-serif}}
main{{max-width:900px;margin:auto;padding:24px 16px}} h1,h2{{font-family:Sora,system-ui}} h1{{font-size:28px}}
.k{{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:12px}}
.k div{{background:var(--c);border-radius:12px;padding:16px}} .k b{{display:block;font-size:34px;color:var(--a)}}
.b{{display:grid;grid-template-columns:minmax(120px,34%) 1fr 60px;gap:8px;align-items:center;margin:6px 0}}
.r{{color:var(--m);font-size:14px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}}
.t{{background:#222;border-radius:6px;height:14px;overflow:hidden}} .t i{{display:block;height:100%}}
.pie{{width:160px;height:160px;border-radius:50%;background:conic-gradient(var(--a) 0 {pct}%,#2a2a33 {pct}% 100%)}}
li{{margin:8px 0}} em{{font-style:normal;font-size:12px;padding:2px 6px;border-radius:6px;background:#333}}
em.atalho{{background:#854d0e}} em.checagem{{background:#166534}} em.skill{{background:#1e3a8a}} .m{{color:var(--m)}}
</style><main>
<h1>Você repete {pct}% do que digita</h1>
<p class="m">Últimos {dias} dias · {N['pedidos_seus']} pedidos seus · {N['arquivos_lidos']} sessões lidas · gerado local por minhas-repeticoes {VERSAO}</p>
<div style="display:flex;gap:24px;align-items:center;flex-wrap:wrap"><div class="pie"></div>
<div class="k" style="flex:1"><div><b>{N['grupos_repetidos']}</b>grupos repetidos</div><div><b>{N['grupos_atalho']}</b>viram atalho</div>
<div><b>{N['grupos_skill']}</b>viram skill</div><div><b>{N['grupos_checagem']}</b>checagens (pedem aviso de fim)</div><div><b>{N['top10_cobrem_pct']}%</b>só nos 10 maiores</div></div></div>
<h2>O que mais se repete</h2><ol>{tops}</ol>
<h2>Para qual modelo vêo os seus pedidos</h2>{barra(list(N['modelo'].items())[:8])}
<h2>Modelo | esforço</h2>{barra(list(N['esforco'].items())[:10], '#60a5fa')}
<h2>Limite batido</h2>{barra(list(N['limites'].items()) or [('nenhum', 0)], '#f87171')}
<h2>Turnos de mais de 10 minutos</h2>{barra(list(N['turnos_mais_de_10min'].items()) or [('nenhum', 0)], '#a78bfa')}
<p class="m">Atalhos prontos em atalhos.md · rascunhos de skill em skills-rascunho/ · só números em numeros.json</p>
</main></html>"""
    (saida / "relatorio.html").write_text(h)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Acha o que você repete no Claude Code e no Codex.")
    ap.add_argument("--claude", default=str(Path.home() / ".claude/projects"))
    ap.add_argument("--codex", default=str(Path.home() / ".codex/sessions"))
    ap.add_argument("--dias", type=int, default=30)
    ap.add_argument("--saida", default="relatorio")
    ap.add_argument("--sem-codex", action="store_true")
    a = ap.parse_args(argv)
    desde = time.time() - a.dias * 86400
    m = Medidas()
    t0 = time.time()
    if Path(a.claude).is_dir():
        ler_claude(Path(a.claude), desde, m)
    if not a.sem_codex and Path(a.codex).is_dir():
        ler_codex(Path(a.codex), desde, m)
    if not m.pedidos:
        print("nenhum pedido seu encontrado nessas pastas/dias", file=sys.stderr)
        return 2
    res = calcula(m)
    escreve(res, Path(a.saida), a.dias)
    N = res["numeros"]
    print(f"{N['pedidos_seus']} pedidos seus · {N['pct_repeticao']}% em repetiçêo · {N['grupos_atalho']} atalhos · "
          f"{N['grupos_skill']} skills · {time.time()-t0:.0f}s → {a.saida}/relatorio.html")
    return 0


if __name__ == "__main__":
    sys.exit(main())
