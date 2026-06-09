# Portal Campanha

Aplicacao Flask para consultar eventos dos bancos Magento/Running Land e Ativo, selecionar um ou varios eventos manualmente e exportar planilhas Excel com dados brutos, dados limpos ou cruzamentos por SKU.

## Sobre o Projeto

O Portal Campanha ajuda a preparar bases de inscritos de eventos, reduzindo trabalho manual na consulta, limpeza, comparacao e exportacao dos dados.

A interface web possui uma sidebar com tres fluxos:

- `Magento`: consulta eventos Magento, exporta dados brutos e dados limpos.
- `Ativo`: consulta eventos Ativo e exporta dados brutos.
- `Magento + Ativo`: consulta eventos dos dois bancos e cruza os inscritos pelo SKU.

## Tecnologias Utilizadas

- Python
- Flask
- Pandas
- OpenPyXL
- MySQL Connector/Python
- python-dotenv
- HTML, CSS e JavaScript

## Estrutura do Projeto

```text
portalCampanha/
  app.py
  tratamento.py
  requirements.txt
  README.MD
  database/
    conexao.py
    queries.py
  templates/
    index.html
  static/
    style.css
    script.js
```

## Funcionalidades

### Selecionar Eventos

Em cada fluxo, o usuario pode:

- Pesquisar evento por ID, nome ou data.
- Clicar em `Adicionar evento`.
- Informar varios IDs separados por virgula:

```text
48133, 48134, 48135
```

- Remover eventos selecionados antes de exportar.

### Magento

Usa:

```python
obter_eventos_magento()
buscar_dados_magento(ids_eventos)
```

Rotas:

```text
POST /exportar/dados-brutos
POST /exportar/dados-limpos
```

Exportacoes:

- `dados_brutos_magento_*.xlsx`: dados retornados diretamente do Magento.
- `dados_limpos_magento_*.xlsx`: Excel com as abas `Dados Limpos` e `Removidos`.

A aba `Removidos` possui a coluna `Regra Remocao`, indicando por qual regra o registro foi retirado.

### Ativo

Usa:

```python
obter_eventos_ativos()
buscar_dados_ativo(ids_eventos)
```

Rota:

```text
POST /exportar/ativo/dados-brutos
```

Exportacao:

- `dados_brutos_ativo_*.xlsx`: dados brutos retornados do Ativo.

Por enquanto, o Ativo nao aplica regras de limpeza.

### Magento + Ativo

Neste fluxo, o usuario seleciona manualmente eventos Magento e eventos Ativo. Depois, o sistema:

1. Busca inscritos do Magento.
2. Busca inscritos do Ativo.
3. Converte as duas bases para DataFrames.
4. Padroniza a coluna `SKU`.
5. Faz um `outer merge` pelo SKU.
6. Exporta abas de auditoria.

Rota:

```text
POST /exportar/magento-ativo
```

Abas exportadas:

- `Magento Bruto`: todos os registros retornados do Magento.
- `Ativo Bruto`: todos os registros retornados do Ativo.
- `Magento + Ativo`: resultado do cruzamento por SKU.
- `Somente Magento`: registros sem correspondencia no Ativo.
- `Somente Ativo`: registros sem correspondencia no Magento.

## Regras de Limpeza Magento

As regras atuais removem registros por:

- `Etiqueta`
- `Cupom`
- `E-mail`
- `Categoria`
- `Evento`
- `Local Inscricao`
- `Balcao`

Se um registro cair em mais de uma regra, os motivos aparecem juntos:

```text
Cupom; E-mail; Categoria
```

## Pre-requisitos

Antes de executar o projeto, tenha instalado:

- Python 3.10 ou superior
- Pip
- Acesso aos bancos MySQL Magento/Running Land e Ativo
- Credenciais configuradas em um arquivo `.env`

## Configuracao

1. Crie e ative o ambiente virtual:

```bash
python -m venv .venv
.venv\Scripts\activate
```

2. Instale as dependencias:

```bash
pip install -r requirements.txt
```

3. Copie o arquivo de exemplo:

```bash
copy .env.example .env
```

4. Configure o `.env` com as credenciais reais:

```env
DB_MAGENTO_HOST=seu_host_magento
DB_MAGENTO_PORT=3306
DB_MAGENTO_USER=seu_usuario_magento
DB_MAGENTO_PASSWORD=sua_senha_magento
DB_MAGENTO_DATABASE=nome_do_banco_magento

DB_ATIVO_HOST=seu_host_ativo
DB_ATIVO_USER=seu_usuario_ativo
DB_ATIVO_PASSWORD=sua_senha_ativo
DB_ATIVO_DATABASE=nome_do_banco_ativo
```

## Como Executar Localmente

Com o ambiente virtual ativo, execute:

```bash
python -m flask --app app run --host 127.0.0.1 --port 5000
```

Depois acesse:

```text
http://127.0.0.1:5000/
```

Tambem e possivel rodar diretamente:

```bash
python app.py
```

## Principais Funcoes

Em `database/queries.py`:

```python
obter_eventos_magento()
obter_eventos_ativos()
buscar_dados_magento(id_evento)
buscar_dados_ativo(id_evento)
```

Em `tratamento.py`:

```python
montar_dataframe_magento(dados)
montar_dataframe_ativo(dados)
separar_dados_magento_por_limpeza(dados)
gerar_planilhas_limpeza_magento(id_evento)
gerar_dados_brutos_ativo(id_evento)
juntar_magento_ativo(df_magento, df_ativo)
gerar_planilhas_magento_ativo(ids_magento, ids_ativo)
```

## Observacoes

- A pasta `templates/` guarda os arquivos HTML renderizados pelo Flask.
- A pasta `static/` guarda CSS e JavaScript servidos diretamente ao navegador.
- O caminho dos arquivos estaticos e gerado no HTML com `url_for('static', filename='...')`.
- A exportacao usa `send_file`, entao quem define a pasta final de download e o navegador.
- O cruzamento Magento + Ativo usa `outer merge`, preservando registros dos dois bancos mesmo quando nao ha correspondencia.

## Licenca

Este projeto utiliza a licenca MIT. Consulte o arquivo `LICENSE` para mais detalhes.
