---
name: avaliar-completude
description: Avalia a completude de uma base estruturada do data room da Vitaliza (percentual de faltantes por coluna e criticidade alta/média/baixa de cada falta) e grava o resultado em saidas/. Use quando pedirem para avaliar completude, dados faltantes, vazios ou nulos de uma base como usuarios, assinaturas, amizades, campanha_ago26, eventos_assinatura, pagamentos, uso_mensal, atividades ou onboarding.
---

# Avaliar completude de uma base

Processo usado no onboarding.csv, repetido para qualquer base estruturada do projeto.
Cobre: usuarios, assinaturas, amizades, campanha_ago26, eventos_assinatura, pagamentos,
uso_mensal, atividades e onboarding. Não cobre pesquisa_saida, feed_posts,
tickets_suporte e heatmaps_90d (texto e imagem).

Uma base por vez: avalie só a base pedida e não carregue as outras, exceto o
`user_id` de usuarios.csv, que o script lê para contar contas ausentes.

## Regras do projeto que valem aqui

- Não altere, mova ou apague nada em `dados/brutos/`.
- Data de corte: 30/09/2026. Aponte datas posteriores, se aparecerem.
- Nunca mostre o conteúdo do `.env`.
- Mostre os números do meio do caminho (linhas lidas, contagens por coluna).
- Se o significado de uma coluna não estiver claro, diga o que não achou no dicionário em vez de supor.
- Trabalhe na branch `dev`, com um commit por passo. Não faça push nem PR sem pedido.

## Passos

Antes de começar, apresente estes passos como plano e espere aprovação.

1. **Dicionário.** Leia a seção da base em `docs/Vitaliza - Dicionário de dados.pdf`:
   o que é uma linha, número de linhas esperado e descrição de cada coluna. Anote o
   que o dicionário não esclarece (valores possíveis, colunas opcionais, fuso horário).

2. **Carregar e descrever, sem análise.** Mostre linhas e colunas (e compare com o
   dicionário), tipos e uma amostra de ~8 linhas. No Windows, imprima em UTF-8
   (`sys.stdout.reconfigure(encoding="utf-8")`), porque há acentos e emojis. Liste as
   dúvidas do passo 1 e pare para o usuário responder.

3. **Medir.** Rode `.venv\Scripts\python src/completude.py <base>`. O script mostra,
   por coluna, os vazios (nulo, vazio ou só espaços), os candidatos a "sem conteúdo"
   (valores curtos e muito repetidos em colunas de texto livre, como "ok", "asdf",
   "-") e as contas de usuarios.csv que não aparecem na base.
   - Apresente os vazios.
   - Apresente os candidatos sem decidir por eles. Só entram na conta se o usuário
     aprovar a lista; aí ela vai em `sem_conteudo` da base em
     `src/completude_config.json`, e o script é rodado de novo.

4. **Classificar a criticidade de cada coluna**, com justificativa curta:
   - **alta:** a falta do dado pode afetar uma decisão de negócio;
   - **média:** dá para inferir, mas num processo mais detalhado o faltante pode levar
     a uma direção equivocada;
   - **baixa:** dá para seguir em frente, com menos detalhe ou qualificação.

   Pense no uso do dado no case (contar a base e o churn, explicar a subida de 2026,
   segmentar, prever a saída até 29/11/2026, escolher quem contatar e com qual
   mensagem) e se outra base supre a falta (ex.: `canal_aquisicao` em usuarios.csv).
   Coluna completa ainda recebe a criticidade que teria se faltasse. Distinga falta de
   padronização: grafias diferentes do mesmo valor não são faltante. Proponha a tabela
   e espere aprovação.

5. **Gravar.** Coloque a criticidade aprovada em `src/completude_config.json`
   (`criticidade`: coluna → [nível, motivo]; `nota_contas` para as contas ausentes)
   e rode o script de novo. Ele grava `saidas/completude_<base>.csv` e
   `saidas/completude_<base>.md`. Mostre a tabela final.

6. **Registrar e commitar.** `decisoes.md` só muda se o usuário aprovar uma decisão de
   limpeza (o critério de "sem conteúdo" conta como uma), com motivo, critério e
   linhas afetadas. Faça um commit na `dev` com a configuração e as saídas da base.
   Pergunte antes de fazer push.

## Formato da resposta final

Uma tabela por coluna (vazios, % vazios, vazios + sem conteúdo, %, criticidade), a
justificativa de cada nível, as contas ausentes e as dúvidas que ficaram em aberto.
