ï»¿# minhas repetiêÂ§êÂµes

<div align="center">
  <img src="capa/logo.svg" alt="Arckhé AI" height="48" />
  <p><strong>Arckhé AI</strong></p>
</div>


**ê°Å¸â¡Â§ê°Å¸â¡Â· [PortuguêÂªs](README.md) êÂ· ê°Å¸â¡Âºê°Å¸â¡Â¸ [English](README.en.md) êÂ· ê°Å¸â¡Âªê°Å¸â¡Â¸ [EspaêÂ±ol](README.es.md)**

[![Minhas repetiêÂ§êÂµes](guia/assets/banner.jpg)](https://inematds.github.io/minhas-repeticoes/guia/)

ê°Å¸Å½Â¬ VêÂ­deo: https://www.youtube.com/watch?v=3aanGE9Jpz8 êÂ· Short: https://youtube.com/shorts/cEHKKEnX4GU

## O que êÂ©

Um kit gratuito que lêÂª o seu histêÂ³rico do **Claude Code** e do **Codex** e mostra o que vocêÂª digita de novo e de novo.
Para cada repetiêÂ§êÂ£o ele diz se ela vira **atalho** (texto curto colado com um gatilho), **skill** (procedimento com
passos), se êÂ© uma **checagem** ("qual a situaêÂ§êÂ£o?", que pede um aviso de fim, nêÂ£o um atalho) ou se êÂ© sêÂ³ uma
**resposta** ("sim", "continue"). De quebra mede para qual modelo vêÂ£o os seus
pedidos, com que esforêÂ§o, quantas vezes vocêÂª bateu no limite e quantos turnos passaram de 10 minutos.

Roda na sua mêÂ¡quina, sêÂ³ com Python 3 (biblioteca padrêÂ£o). NêÂ£o chama API e nêÂ£o manda nada para lugar nenhum.

## ê°Å¸ââ Guia de uso

Guia completo (landing + passo a passo): **https://inematds.github.io/minhas-repeticoes/guia/**

## Por quêÂª

VocêÂª nêÂ£o percebe o que repete, porque cada vez parece a primeira. Numa mêÂ¡quina de produêÂ§êÂ£o real, em 30 dias: **2.287
pedidos digitados, 12,6% repetidos**, e o campeêÂ£o, "qual a situaêÂ§êÂ£o", apareceu **68 vezes**. Nesse mesmo mêÂªs os robêÂ´s
fizeram 13.505 turnos, quase 6 para cada pedido digitado. Esses nêÂºmeros estêÂ£o em
`exemplos/numeros-maquina-inema-30dias.json`, que sêÂ³ tem contagens, sem nenhum texto.

## O processo, do inêÂ­cio ao fim

| # | Passo | Comando | Quem |
|---|---|---|---|
| 1 | Baixar o kit | `git clone https://github.com/inematds/minhas-repeticoes && cd minhas-repeticoes` | ê°Å¸Â§Â  vocêÂª |
| 2 | Conferir se roda | `python3 -m unittest discover -s testes` (15 testes, dados inventados) | ê¢Å¡â¢ê¯Â¸Â script |
| 3 | Ler o seu histêÂ³rico | `python3 repeticoes.py` (padrêÂ£o: 30 dias, `~/.claude/projects` e `~/.codex/sessions`) | ê¢Å¡â¢ê¯Â¸Â script |
| 4 | Ver o relatêÂ³rio | abrir `relatorio/relatorio.html` no navegador | ê°Å¸Â§Â  vocêÂª |
| 5 | Ligar os atalhos | copiar `relatorio/atalhos-espanso.yml` para a pasta `match` do Espanso (Linux `~/.config/espanso/match/`, Mac `~/Library/Application Support/espanso/match/`) ou colar do `atalhos.md` no seu expansor | ê°Å¸Â§Â  vocêÂª |
| 6 | Virar skill o que tem passos | revisar `relatorio/skills-rascunho/<nome>/SKILL.md`, escrever os passos e mover para `~/.claude/skills/`. Para o agente fazer com vocêÂª: `mkdir -p ~/.claude/skills && cp -r skill/minhas-repeticoes ~/.claude/skills/ && cp repeticoes.py DICAS.md ~/.claude/skills/minhas-repeticoes/` | ê°Å¸Â§Â  vocêÂª (ou ê°Å¸Â¤â o agente, com a skill do kit) |
| 7 | Ajustar modelo e esforêÂ§o | ler `modelo` e `modelo\|esforêÂ§o` no relatêÂ³rio e seguir as dicas 6ê¢â¬â9 de `DICAS.md` | ê°Å¸Â§Â  vocêÂª |
| 8 | Medir de novo em 30 dias | `python3 repeticoes.py --saida relatorio-mes2` e comparar o `numeros.json` | ê¢Å¡â¢ê¯Â¸Â script |

OpêÂ§êÂµes: `--dias 7` êÂ· `--saida <pasta>` êÂ· `--claude <pasta>` êÂ· `--codex <pasta>` êÂ· `--sem-codex`.

## O que sai

| Arquivo | O que tem | Pode mostrar a alguêÂ©m? |
|---|---|---|
| `relatorio.html` | grêÂ¡ficos: repetiêÂ§êÂ£o, grupos, modelo, esforêÂ§o, limite, turnos longos | ê¢ÂÅ tem trechos seus |
| `relatorio.md` | o mesmo em texto | ê¢ÂÅ |
| `atalhos.md` / `atalhos-espanso.yml` | um atalho por pedido curto repetido | ê¢ÂÅ |
| `skills-rascunho/` | um rascunho de SKILL.md por pedido longo repetido | ê¢ÂÅ |
| `numeros.json` | sêÂ³ contagens (nenhum texto) | ê¢Åâ¦ |

## Como ele decide

- **SêÂ³ o que vocêÂª digitou.** Conta o turno com `turnOrigin: human` (Claude Code) ou a sessêÂ£o iniciada pelo usuêÂ¡rio
  (Codex). `claude -p`, vigias, notificaêÂ§êÂµes, subagentes e `codex exec` entram êÂ  parte, como turnos automêÂ¡ticos.
- **SessêÂ£o retomada nêÂ£o conta duas vezes** (o mesmo `uuid` êÂ© lido uma vez sêÂ³).
- **Parecido êÂ© igual.** Junta pedidos com as mesmas palavras (cortadas em 5 letras: publica/publique/publicou) e aceita
  erro de digitaêÂ§êÂ£o nos curtos ("sistuacao" = "situacao"). RepetiêÂ§êÂ£o = 3 vezes ou mais.
- **Atalho êâ skill:** atêÂ© ~120 caracteres êÂ© atalho; acima disso, com passos, êÂ© skill. AtêÂ© 10 caracteres ("sim", "1")
  êÂ© resposta. Pergunta de acompanhamento (situaêÂ§êÂ£o, andamento, rodando, status) êÂ© checagem e nêÂ£o vira atalho.
  Link colado sozinho êÂ© `link`; `/comando` que vocêÂª jêÂ¡ usa êÂ© `ja-e-atalho`.
- **Limite:** o mesmo aviso ("resets 9:10pm") em vêÂ¡rias sessêÂµes conta 1 batida. No Codex conta a sessêÂ£o que chegou a 100%.

## ConteêÂºdo

- `repeticoes.py`: o kit (um arquivo, sem dependêÂªncias)
- `DICAS.md`: 12 dicas do que fazer com o que vocêÂª repete
- `skill/minhas-repeticoes/SKILL.md`: skill para o Claude Code rodar o kit e transformar os grupos em atalho/skill com vocêÂª
- `testes/`: 15 testes com histêÂ³rico inventado (`gerar_dados.py`)
- `exemplos/`: `relatorio-inventado/` (saêÂ­da com dados inventados) e `numeros-maquina-inema-30dias.json` (nêÂºmeros reais, sem texto)

## Limites

- O relatêÂ³rio sai em portuguêÂªs.
- LêÂª o formato de log do Claude Code e do Codex de novembro de 2026. Logs antigos sem `turnOrigin` sêÂ£o tratados pela
  regra antiga (CLI interativa = vocêÂª).
- EsforêÂ§o sêÂ³ aparece quando o Claude Code grava o pedido de API (`?` = sem registro).
- O agrupamento êÂ© por palavras, nêÂ£o por sentido: "posta no portal" e "publique no portal" podem ficar separados.

GrêÂ¡tis no [inema.club](https://inema.club), direto na internet.

---

<div align="center">
  <img src="capa/logo.svg" alt="Arckhé AI" height="32" />
  <p><strong>Arckhé AI</strong></p>
</div>