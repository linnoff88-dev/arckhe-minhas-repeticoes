# minhas repetiÃ§Ãµes

<div align="center">
  <img src="capa/logo.svg" alt="Arckhé AI" height="48" />
  <p><strong>Arckhé AI</strong></p>
</div>


**ðŸ‡§ðŸ‡· [PortuguÃªs](README.md) Â· ðŸ‡ºðŸ‡¸ [English](README.en.md) Â· ðŸ‡ªðŸ‡¸ [EspaÃ±ol](README.es.md)**

[![Minhas repetiÃ§Ãµes](guia/assets/banner.jpg)](https://inematds.github.io/minhas-repeticoes/guia/)

ðŸŽ¬ VÃ­deo: https://www.youtube.com/watch?v=3aanGE9Jpz8 Â· Short: https://youtube.com/shorts/cEHKKEnX4GU

## O que Ã©

Um kit gratuito que lÃª o seu histÃ³rico do **Claude Code** e do **Codex** e mostra o que vocÃª digita de novo e de novo.
Para cada repetiÃ§Ã£o ele diz se ela vira **atalho** (texto curto colado com um gatilho), **skill** (procedimento com
passos), se Ã© uma **checagem** ("qual a situaÃ§Ã£o?", que pede um aviso de fim, nÃ£o um atalho) ou se Ã© sÃ³ uma
**resposta** ("sim", "continue"). De quebra mede para qual modelo vÃ£o os seus
pedidos, com que esforÃ§o, quantas vezes vocÃª bateu no limite e quantos turnos passaram de 10 minutos.

Roda na sua mÃ¡quina, sÃ³ com Python 3 (biblioteca padrÃ£o). NÃ£o chama API e nÃ£o manda nada para lugar nenhum.

## ðŸ“– Guia de uso

Guia completo (landing + passo a passo): **https://inematds.github.io/minhas-repeticoes/guia/**

## Por quÃª

VocÃª nÃ£o percebe o que repete, porque cada vez parece a primeira. Numa mÃ¡quina de produÃ§Ã£o real, em 30 dias: **2.287
pedidos digitados, 12,6% repetidos**, e o campeÃ£o, "qual a situaÃ§Ã£o", apareceu **68 vezes**. Nesse mesmo mÃªs os robÃ´s
fizeram 13.505 turnos, quase 6 para cada pedido digitado. Esses nÃºmeros estÃ£o em
`exemplos/numeros-maquina-inema-30dias.json`, que sÃ³ tem contagens, sem nenhum texto.

## O processo, do inÃ­cio ao fim

| # | Passo | Comando | Quem |
|---|---|---|---|
| 1 | Baixar o kit | `git clone https://github.com/inematds/minhas-repeticoes && cd minhas-repeticoes` | ðŸ§  vocÃª |
| 2 | Conferir se roda | `python3 -m unittest discover -s testes` (15 testes, dados inventados) | âš™ï¸ script |
| 3 | Ler o seu histÃ³rico | `python3 repeticoes.py` (padrÃ£o: 30 dias, `~/.claude/projects` e `~/.codex/sessions`) | âš™ï¸ script |
| 4 | Ver o relatÃ³rio | abrir `relatorio/relatorio.html` no navegador | ðŸ§  vocÃª |
| 5 | Ligar os atalhos | copiar `relatorio/atalhos-espanso.yml` para a pasta `match` do Espanso (Linux `~/.config/espanso/match/`, Mac `~/Library/Application Support/espanso/match/`) ou colar do `atalhos.md` no seu expansor | ðŸ§  vocÃª |
| 6 | Virar skill o que tem passos | revisar `relatorio/skills-rascunho/<nome>/SKILL.md`, escrever os passos e mover para `~/.claude/skills/`. Para o agente fazer com vocÃª: `mkdir -p ~/.claude/skills && cp -r skill/minhas-repeticoes ~/.claude/skills/ && cp repeticoes.py DICAS.md ~/.claude/skills/minhas-repeticoes/` | ðŸ§  vocÃª (ou ðŸ¤– o agente, com a skill do kit) |
| 7 | Ajustar modelo e esforÃ§o | ler `modelo` e `modelo\|esforÃ§o` no relatÃ³rio e seguir as dicas 6â€“9 de `DICAS.md` | ðŸ§  vocÃª |
| 8 | Medir de novo em 30 dias | `python3 repeticoes.py --saida relatorio-mes2` e comparar o `numeros.json` | âš™ï¸ script |

OpÃ§Ãµes: `--dias 7` Â· `--saida <pasta>` Â· `--claude <pasta>` Â· `--codex <pasta>` Â· `--sem-codex`.

## O que sai

| Arquivo | O que tem | Pode mostrar a alguÃ©m? |
|---|---|---|
| `relatorio.html` | grÃ¡ficos: repetiÃ§Ã£o, grupos, modelo, esforÃ§o, limite, turnos longos | âŒ tem trechos seus |
| `relatorio.md` | o mesmo em texto | âŒ |
| `atalhos.md` / `atalhos-espanso.yml` | um atalho por pedido curto repetido | âŒ |
| `skills-rascunho/` | um rascunho de SKILL.md por pedido longo repetido | âŒ |
| `numeros.json` | sÃ³ contagens (nenhum texto) | âœ… |

## Como ele decide

- **SÃ³ o que vocÃª digitou.** Conta o turno com `turnOrigin: human` (Claude Code) ou a sessÃ£o iniciada pelo usuÃ¡rio
  (Codex). `claude -p`, vigias, notificaÃ§Ãµes, subagentes e `codex exec` entram Ã  parte, como turnos automÃ¡ticos.
- **SessÃ£o retomada nÃ£o conta duas vezes** (o mesmo `uuid` Ã© lido uma vez sÃ³).
- **Parecido Ã© igual.** Junta pedidos com as mesmas palavras (cortadas em 5 letras: publica/publique/publicou) e aceita
  erro de digitaÃ§Ã£o nos curtos ("sistuacao" = "situacao"). RepetiÃ§Ã£o = 3 vezes ou mais.
- **Atalho Ã— skill:** atÃ© ~120 caracteres Ã© atalho; acima disso, com passos, Ã© skill. AtÃ© 10 caracteres ("sim", "1")
  Ã© resposta. Pergunta de acompanhamento (situaÃ§Ã£o, andamento, rodando, status) Ã© checagem e nÃ£o vira atalho.
  Link colado sozinho Ã© `link`; `/comando` que vocÃª jÃ¡ usa Ã© `ja-e-atalho`.
- **Limite:** o mesmo aviso ("resets 9:10pm") em vÃ¡rias sessÃµes conta 1 batida. No Codex conta a sessÃ£o que chegou a 100%.

## ConteÃºdo

- `repeticoes.py`: o kit (um arquivo, sem dependÃªncias)
- `DICAS.md`: 12 dicas do que fazer com o que vocÃª repete
- `skill/minhas-repeticoes/SKILL.md`: skill para o Claude Code rodar o kit e transformar os grupos em atalho/skill com vocÃª
- `testes/`: 15 testes com histÃ³rico inventado (`gerar_dados.py`)
- `exemplos/`: `relatorio-inventado/` (saÃ­da com dados inventados) e `numeros-maquina-inema-30dias.json` (nÃºmeros reais, sem texto)

## Limites

- O relatÃ³rio sai em portuguÃªs.
- LÃª o formato de log do Claude Code e do Codex de novembro de 2026. Logs antigos sem `turnOrigin` sÃ£o tratados pela
  regra antiga (CLI interativa = vocÃª).
- EsforÃ§o sÃ³ aparece quando o Claude Code grava o pedido de API (`?` = sem registro).
- O agrupamento Ã© por palavras, nÃ£o por sentido: "posta no portal" e "publique no portal" podem ficar separados.

GrÃ¡tis no [inema.club](https://inema.club), direto na internet.

---

<div align="center">
  <img src="capa/logo.svg" alt="Arckhé AI" height="32" />
  <p><strong>Arckhé AI</strong></p>
</div>