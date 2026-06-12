# Portal Campanha

Aplicacao Flask para consultar eventos dos bancos Magento/Running Land e Ativo, selecionar um ou varios eventos manualmente e exportar planilhas Excel com dados brutos, dados limpos ou bases unificadas.

## Sobre o Projeto

O Portal Campanha ajuda a preparar bases de inscritos de eventos, reduzindo trabalho manual na consulta, limpeza, comparacao e exportacao dos dados.

A interface web possui uma sidebar com tres fluxos:

- `Magento`: consulta eventos Magento, exporta dados brutos e dados limpos.
- `Ativo`: consulta eventos Ativo, exporta dados brutos e dados limpos.
- `Magento + Ativo`: consulta eventos dos dois bancos e junta os inscritos em uma base unica com colunas padronizadas.

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

Rotas:

```text
POST /exportar/ativo/dados-brutos
POST /exportar/ativo/dados-limpos
```

Exportacoes:

- `dados_brutos_ativo_*.xlsx`: dados brutos retornados do Ativo.
- `dados_limpos_ativo_*.xlsx`: Excel com as abas `Dados Limpos` e `Removidos`.

A aba `Removidos` possui a coluna `Regra Remocao`, indicando por qual regra o registro foi retirado.

### Magento + Ativo

Neste fluxo, o usuario seleciona manualmente eventos Magento e eventos Ativo e escolhe entre exportar dados brutos ou dados limpos.

Na exportacao de dados brutos, o sistema:

1. Busca inscritos do Magento.
2. Busca inscritos do Ativo.
3. Padroniza a coluna `SKU`.
4. Padroniza colunas equivalentes, como `SKU DO EVENTO` para `SKU`.
5. Junta as linhas do Magento e do Ativo na mesma base, sem aplicar regras de limpeza.
6. Exporta abas de auditoria.

Na exportacao de dados limpos, o sistema aplica as regras de limpeza nas duas bases antes de juntar os registros.

Rotas:

```text
POST /exportar/magento-ativo
POST /exportar/magento-ativo/dados-brutos
POST /exportar/magento-ativo/dados-limpos
```

Abas exportadas nos dados brutos:

- `Magento Bruto`: todos os registros retornados do Magento.
- `Ativo Bruto`: todos os registros retornados do Ativo.
- `Magento + Ativo`: registros Magento e Ativo juntos, com colunas padronizadas.

Abas exportadas nos dados limpos:

- `Magento Bruto`: todos os registros retornados do Magento.
- `Ativo Bruto`: todos os registros retornados do Ativo.
- `Magento Limpo`: registros Magento apos as regras de remocao.
- `Ativo Limpo`: registros Ativo apos as regras de remocao.
- `Magento + Ativo`: registros limpos de Magento e Ativo juntos, com colunas padronizadas.
- `Magento Removidos`: registros Magento removidos pelas regras.
- `Ativo Removidos`: registros Ativo removidos pelas regras.

No fluxo `Magento + Ativo`, a juncao usa as regras de remocao de `Etiqueta`, `Cupom`, `E-mail`, `Categoria`, `Local Inscricao`, `Valor` e `Classificacao Cupom`, conforme a base onde cada coluna existe.

## Regras de Limpeza Magento

As regras atuais removem registros por:

- `Etiqueta`
- `Cupom`
- `E-mail`
- `Categoria`
- `Classificacao Cupom`
- `Local Inscricao`
- `Balcao`
- `Valor`: igual a `0`

Se um registro cair em mais de uma regra, os motivos aparecem juntos:

```text
Cupom; E-mail; Categoria
```

## Regras de Limpeza Ativo

As regras atuais removem registros por:

- `Classificacao Cupom`: contem `grupos`.
- `Local Inscricao`: contem `Balcao`.
- `Categoria`: contem `cortesia`, `cortesias`, `grupos`, `grupo`, `saude corporativa`, `corporativa`, `patrocinador` ou `convidado`.
- `E-mail`: contem `@nortemkt.com`, `@ativo.com`, `@cscdoesporte.com`, `@test.com`, `@teste`, `teste`, `testes`, `grupo` ou `grupos`.
- `Valor`: igual a `0`.

As comparacoes de texto ignoram diferencas entre maiusculas/minusculas e acentos.

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
separar_dados_ativo_por_limpeza(dados)
gerar_planilhas_limpeza_magento(id_evento)
gerar_dados_brutos_ativo(id_evento)
gerar_planilhas_limpeza_ativo(id_evento)
juntar_magento_ativo(df_magento, df_ativo)
gerar_planilhas_magento_ativo(ids_magento, ids_ativo)
```

## Observacoes

- A pasta `templates/` guarda os arquivos HTML renderizados pelo Flask.
- A pasta `static/` guarda CSS e JavaScript servidos diretamente ao navegador.
- O caminho dos arquivos estaticos e gerado no HTML com `url_for('static', filename='...')`.
- A exportacao usa `send_file`, entao quem define a pasta final de download e o navegador.
- A juncao Magento + Ativo empilha os registros dos dois bancos em uma unica base, padronizando colunas equivalentes como `SKU DO EVENTO` para `SKU`.

## Licenca

Este projeto utiliza a licenca MIT. Consulte o arquivo `LICENSE` para mais detalhes.
