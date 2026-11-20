---
name: minhas-repeticoes
description: Lê o histórico do Claude Code e do Codex (local), mostra o que o usuário repete e transforma os grupos em atalhos (Espanso) e skills com ele. Use quando pedirem "o que eu repito", "meus atalhos", "transforma meus pedidos repetidos em skill", "quanto uso cada modelo/esforço", "quantas vezes bati no limite".
---

# minhas-repeticoes

1. Rode `python3 ~/.claude/skills/minhas-repeticoes/repeticoes.py --dias 30 --saida relatorio` (o script fica ao lado deste SKILL.md; se não estiver, use o do clone do kit ou pergunte o caminho). Sem rede, ~1 min para 10 mil sessões.
   Se sair com código 2, não há histórico nessas pastas: pergunte onde ficam (`--claude`, `--codex`).
2. Leia `relatorio/relatorio.md` e mostre ao usuário, em 5 linhas: % de repetição, os 5 maiores grupos, quantos viram
   atalho e quantos viram skill, modelo e esforço dominantes, e limites batidos.
3. **Atalhos:** mostre `relatorio/atalhos-espanso.yml` e pergunte quais ele quer. Só copie para
   `~/.config/espanso/match/` depois do sim dele, e nunca sobrescreva um arquivo que já existe lá.
4. **Skills:** para cada rascunho em `relatorio/skills-rascunho/`, leia os exemplos e proponha os passos que se
   repetem. O que muda de um pedido para outro vira argumento. Mostre o SKILL.md proposto. Só grave em
   `~/.claude/skills/<nome>/` com o OK dele.
5. **Respostas e checagens** (`resposta`, "qual a situação"): não faça atalho. Sugira o que tira a pergunta do caminho
   (aviso de fim, barra de status, o agente perguntar menos). Veja `DICAS.md` 3–4 (copiado ao lado deste SKILL.md na instalação; senão, no clone do kit).
6. Nunca mande o relatório, os atalhos ou trechos dos pedidos para fora da máquina. `numeros.json` é o único arquivo
   sem texto do usuário.
