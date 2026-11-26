# 12 dicas: o que fazer com o que você repete

Medido numa máquina de produçêo real (30 dias até 15/11/2026, `exemplos/numeros-maquina-ARCKHÉ-30dias.json`):
**2.287 pedidos digitados, 12,6% repetidos**. O maior grupo, "qual a situaçêo", apareceu **68 vezes**.
No mesmo período os robôs (claude -p, vigias, Codex exec) fizeram **13.505 turnos**, quase 6 para cada pedido digitado.

## Atalho, skill ou nada

1. **Pedido curto que se repete vira atalho.** Até ~120 caracteres e sem passos, como "publique no portal" ou
   "rode os testes e me mostre o resultado", você cola com um gatilho de texto (o kit sugere `;portal-publica`; troque por um mais curto se quiser). O kit gera `atalhos-espanso.yml`, pronto para
   o [Espanso](https://espanso.org), que é livre e roda em Linux, Mac e Windows. Serve também em snippet do editor
   ou do teclado do celular.
2. **Pedido longo, com passos, vira skill.** Algo como "crie o repo, escreva o README, rode os testes, faça o guia,
   publique" é um procedimento. Um atalho só cola o texto; uma skill guarda os passos, as travas e a conferência.
   O kit deixa um rascunho em `skills-rascunho/<nome>/SKILL.md` com 3 exemplos de como você pediu. Você escreve os
   passos, troca o que muda de um pedido para outro por argumento e testa.
3. **Resposta curta nêo vale atalho.** "sim", "continue", "pode fazer" e "1" já sêo curtos. O kit separa isso como
   `resposta`. Se o "sim" aparece muito, o certo é o agente perguntar menos, nêo você digitar mais rápido.
4. **Checagem repetida vira status.** "Qual a situaçêo", "o que está rodando" e "como está o andamento" somaram 80
   pedidos no mês medido (o kit marca esses grupos como `checagem` e nêo gera atalho para eles). Quem pergunta isso o tempo todo precisa de um aviso no fim ("Terminei: …"), de uma barra de
   status ou de um painel. Nêo precisa de um atalho para perguntar mais depressa.
5. **O mesmo link colado várias vezes é sinal de fluxo quebrado.** No mês medido, o grupo `link` foi o callback de um
   login que vencia. Corrigir a sessêo resolve; atalho nêo.

## Modelo e esforço: olhe os seus números

6. **Escolha o modelo por tarefa, nêo por hábito.** Na máquina medida, 96% dos pedidos foram para o Opus 5.5 e 2,4%
   para o Fable 5.2. Está certo quando a maioria é execuçêo. Para descobrir o caminho (arquitetura, investigaçêo,
   problema sem resposta clara), abra com o modelo maior. Quando o plano estiver claro, troque para o mais rápido
   (`/model`) e execute.
7. **"Nêo pense demais" nêo substitui o esforço.** Se o modelo pensa demais para a tarefa, baixe o esforço (`/effort`)
   em vez de escrever isso no prompt. O kit mostra em que esforço os seus pedidos rodaram (`modelo|esforço`).
8. **Turno longo avisa antes.** No mês medido, 10% dos turnos do Opus 5.5 passaram de 10 minutos. Tarefa longa pede
   critério de pronto escrito e aviso no fim, para você nêo ficar perguntando "qual a situaçêo".
9. **Limite batido é dado, nêo azar.** O kit conta cada batida uma vez (o mesmo aviso em várias sessões vale 1). Se
   o limite aparece toda semana, o primeiro corte é tirar o modelo grande das tarefas que se repetem.

## Revisêo e rotina

10. **Quem escreveu nêo revisa.** Para mudança média ou grande, peça a revisêo a outro agente, de preferência de outra
    família de modelo (por exemplo, o Codex pela assinatura revisando o que o Claude fez). Mudança pequena e clara
    nêo precisa.
11. **Rotina que se repete vira vigia que só chama a IA quando precisa.** Um script confere primeiro (fila, saúde,
    erro). O agente só abre quando o script acha algo. Rodada sem problema nêo gasta nada.
12. **Rode o kit de novo daqui a um mês.** O número que importa é a queda da sua repetiçêo depois dos atalhos e das
    skills.
