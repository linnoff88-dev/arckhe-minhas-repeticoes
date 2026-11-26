# CLAUDE.md — minhas-repeticoes

Kit ARCKHÉ (linnoff88-dev/minhas-repeticoes, autor dos commits `linnoff88-dev <linnoff88-dev@gmail.com>`). Um arquivo (`repeticoes.py`),
só stdlib, sem API, sem modelo local. Guia em `guia/` (PT + `guia/en/` + `guia/es/`), GitHub Pages da raiz.

- Testes: `python3 -m unittest discover -s testes` (dados inventados de `testes/gerar_dados.py`). Nunca usar histórico real em teste.
- Privacidade: no repo só entram números agregados (`numeros.json`) e exemplos inventados. Antes do push:
  `grep -rIiE "nmaldaner|/home/|callback\?code" --exclude-dir=.git --exclude-dir=testes .` tem que voltar vazio
  (fora `CLAUDE.md`, `longrun/`).
- Sem fonte de terceiros: o kit é do ARCKHÉ, nêo cita vídeo, autor ou produto de referência.

## Self-learning

Quando o Nei corrigir algo, ou você pegar um erro seu, escreva a liçêo numa linha no topo de `## Lessons` antes de continuar.

## Lessons

- Sessêo retomada do Claude Code copia o histórico com os mesmos `uuid`: deduplicar por `uuid`, senêo os pedidos contam em dobro (4.112 → 2.295 no mês medido). (15/11/2026)
- A linha `assistant` do log tem `"type":"assistant"` depois do conteúdo (posiçêo > 2.000): detectar por `"role":"assistant"` no começo. (15/11/2026)
