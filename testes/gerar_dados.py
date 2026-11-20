"""Gera um histórico INVENTADO (nenhum texto real) no formato do Claude Code e do Codex, para os testes e o exemplo."""
import json
import sys
from pathlib import Path


def claude_linha(tipo, uuid, ts, **kw):
    d = {"parentUuid": None, "isSidechain": False, "type": tipo, "uuid": uuid, "timestamp": ts,
         "entrypoint": kw.pop("entrypoint", "cli"), "sessionId": "s"}
    d.update(kw)
    return json.dumps(d, ensure_ascii=False)


def gerar(raiz: Path):
    c = raiz / "claude" / "-home-voce-projeto"
    c.mkdir(parents=True, exist_ok=True)
    linhas, n = [], 0

    def humano(texto, modelo="claude-opus-5-5", esforco="high", dur=60_000):
        nonlocal n
        n += 1
        linhas.append(claude_linha("user", f"u{n}", "2026-11-10T10:00:00Z", promptSource="typed", turnOrigin="human",
                                   message={"role": "user", "content": texto}))
        linhas.append(json.dumps({"type": "api-request", "params": {"model": modelo, "output_config": {"effort": esforco}}}))
        linhas.append(json.dumps({"parentUuid": "x", "isSidechain": False, "message": {"model": modelo, "role": "assistant",
                                  "content": [{"type": "text", "text": "ok"}]}, "type": "assistant", "uuid": f"a{n}"}))
        linhas.append(claude_linha("system", f"d{n}", "2026-11-10T10:01:00Z", subtype="turn_duration", durationMs=dur))

    for t in ["qual a situação?", "qual situacao", "qual a sitaucao", "qual a situação", "qual situação?"]:
        humano(t)
    for t in ["publica no portal", "publique no portal", "publica no portal agora"]:
        humano(t)
    passo = ("crie o repo deste conteúdo, escreva o README com o processo do início ao fim, rode os testes, "
             "faça o guia em três idiomas, publique no portal e me avise no final com os links de tudo")
    for i in range(3):
        humano(passo + f" (pasta {i})", modelo="claude-fable-5-2", esforco="xhigh", dur=25 * 60_000)
    for t in ["sim", "sim", "sim"]:
        humano(t)
    humano("uma pergunta que aparece uma vez só sobre gráficos")
    # comando da ferramenta (não conta) e comando do usuário (já é atalho)
    for _ in range(3):
        humano("<command-name>/clear</command-name><command-args></command-args>")
        humano("<command-name>/prime</command-name><command-args></command-args>")
    # robôs: claude -p e notificação — fora da conta
    for i in range(4):
        linhas.append(claude_linha("user", f"r{i}", "2026-11-10T11:00:00Z", entrypoint="sdk-cli", promptSource="sdk",
                                   turnOrigin="sdk", message={"role": "user", "content": "qual a situação?"}))
    linhas.append(claude_linha("user", "t1", "2026-11-10T11:00:00Z", promptSource="system", turnOrigin="task_notification",
                               message={"role": "user", "content": "<task-notification>x</task-notification>"}))
    # subagente (isSidechain) — fora da conta
    linhas.append(json.dumps({"isSidechain": True, "type": "user", "uuid": "sc1", "turnOrigin": "human",
                              "message": {"role": "user", "content": "qual a situação?"}}))
    # o mesmo limite aparece 2 vezes (duas sessões) = 1 batida; um semanal
    for i in range(2):
        linhas.append(json.dumps({"parentUuid": "y", "isSidechain": False, "message": {"model": "<synthetic>", "role": "assistant",
                                  "content": [{"type": "text", "text": "You've hit your session limit · resets 9:10pm (America/Sao_Paulo)"}]},
                                  "type": "assistant", "isApiErrorMessage": True, "uuid": f"l{i}", "timestamp": "2026-11-10T12:00:00Z"}))
    linhas.append(json.dumps({"parentUuid": "y", "isSidechain": False, "message": {"model": "<synthetic>", "role": "assistant",
                              "content": [{"type": "text", "text": "You've hit your weekly limit · resets Nov 14"}]},
                              "type": "assistant", "isApiErrorMessage": True, "uuid": "lw", "timestamp": "2026-11-11T12:00:00Z"}))
    (c / "sessao1.jsonl").write_text("\n".join(linhas) + "\n")
    # sessão retomada: copia o histórico (mesmos uuid) — não pode contar 2 vezes
    (c / "sessao1-retomada.jsonl").write_text("\n".join(linhas[:8]) + "\n")

    x = raiz / "codex" / "2026" / "11" / "10"
    x.mkdir(parents=True, exist_ok=True)

    def cx(tipo, payload):
        return json.dumps({"timestamp": "2026-11-10T13:00:00Z", "type": tipo, "payload": payload}, ensure_ascii=False)

    sess = [cx("event_msg", {"type": "thread_settings_applied", "thread_settings": {"model": "gpt-6-astra", "reasoning_effort": "high"}}),
            cx("event_msg", {"type": "task_started", "turn_attribution": {"turn_trigger": "user"}}),
            cx("response_item", {"type": "message", "role": "user", "content": [{"type": "input_text", "text": "# AGENTS.md instructions"}]}),
            cx("response_item", {"type": "message", "role": "user", "content": [{"type": "input_text", "text": "publica no portal"}]}),
            cx("event_msg", {"type": "token_count", "rate_limits": {"primary": {"used_percent": 100.0}}})]
    (x / "rollout-humano.jsonl").write_text("\n".join(sess) + "\n")
    robo = [cx("event_msg", {"type": "task_started", "turn_attribution": {"turn_trigger": "exec"}}),
            cx("response_item", {"type": "message", "role": "user", "content": [{"type": "input_text", "text": "traduza isto"}]})]
    (x / "rollout-exec.jsonl").write_text("\n".join(robo) + "\n")


if __name__ == "__main__":
    gerar(Path(sys.argv[1] if len(sys.argv) > 1 else "testes/dados"))
