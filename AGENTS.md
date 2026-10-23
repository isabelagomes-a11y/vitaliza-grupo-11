# Projeto Vitaliza · grupo 11

## O case
A Vitaliza é um app de assinatura para quem treina. O grupo estuda a saída de assinantes:
quem sai, por quê e em quem vale a pena agir. Enunciado e dicionário de dados estão em docs/.

## Os dados
- Os arquivos originais estão em dados/brutos/. Nunca altere, mova ou apague esses arquivos.
- Data de corte: 30/09/2026. Nenhuma análise usa informação posterior ao corte.
- assinaturas.csv é um retrato de 01/10/2026, não um histórico. Para a situação de um
  assinante numa data, use eventos_assinatura.csv.
- As lojas gravam horários em UTC (terminados em "Z"); o site grava em horário de Brasília.
- atividades.parquet é lido com pandas e pyarrow.

## Como trabalhar
- Antes de uma tarefa com mais de um passo, apresente o plano e espere a aprovação.
- Código em notebooks/ ou src/; resultados em saidas/; tabelas intermediárias em dados/processados/.
- Mostre os números intermediários: linhas antes e depois de cada filtro e de cada junção.
- Toda decisão de limpeza (corrigir, remover ou marcar) vai para decisoes.md, com motivo,
  critério e quantidade de linhas afetadas.
- Quando o significado de uma coluna não estiver claro, consulte o dicionário e diga o que
  não encontrou, em vez de supor.

## O que não fazer
- Não coloque chaves de API, senhas ou tokens em nenhum arquivo do projeto, exceto no .env.
- Nunca mostre o conteúdo do .env na tela.
- Não processe o data room inteiro de uma vez: use só os arquivos que a pergunta da vez pede.

## Comandos
- Ambiente (Windows, PowerShell, na pasta do projeto): `.venv\Scripts\Activate.ps1`
  (se o Windows bloquear o script, rode antes: `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`)
- JupyterLab (Windows): `.venv\Scripts\jupyter lab`
- Recriar o ambiente: `python -m venv .venv` e depois `.venv\Scripts\python -m pip install -r requirements.txt`
- Python 3.12; pandas 3.1.0, pyarrow 26.0.0, matplotlib 3.11.2, jupyterlab 4.6.4 (lista completa em requirements.txt)
