# Portal Campanha

Aplicacao Flask para consultar eventos do banco Magento/Running Land, selecionar um ou varios eventos e exportar planilhas Excel com dados brutos ou dados tratados.

## Sobre o Projeto

O Portal Campanha ajuda a preparar bases de inscritos de eventos, reduzindo trabalho manual na consulta, limpeza e exportacao dos dados.

A interface web permite:

- Pesquisar eventos vindos da funcao `obter_eventos_magento()`.
- Selecionar um ou mais eventos pela busca.
- Informar varios IDs de evento separados por virgula.
- Exportar dados brutos do Magento.
- Exportar dados limpos com uma aba adicional contendo os registros removidos pelas regras de limpeza.

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

### Interface Web

A tela principal esta em `templates/index.html` e usa arquivos estaticos em `static/`.

O usuario pode:

- Pesquisar um evento por ID, nome ou data.
- Clicar em `Adicionar evento`.
- Digitar IDs separados por virgula, por exemplo:

```text
48133, 48134, 48135
```

- Remover eventos selecionados antes de exportar.
- Exportar a selecao como planilha Excel.

### Exportar Dados Brutos

O botao `Exportar dados brutos` chama a rota:

```text
POST /exportar/dados-brutos
```

Essa rota usa:

```python
buscar_dados_magento(ids_eventos)
```

O arquivo baixado contem os dados retornados diretamente da consulta Magento, organizados nas colunas definidas em `tratamento.py`.

### Exportar Dados Limpos

O botao `Exportar dados limpos` chama a rota:

```text
POST /exportar/dados-limpos
```

Essa rota usa:

```python
gerar_planilhas_limpeza_magento(ids_eventos)
```

O Excel gerado contem duas abas:

- `Dados Limpos`: registros aprovados pelas regras de limpeza.
- `Removidos`: registros removidos, com a coluna `Regra Remocao` indicando o motivo.

Possiveis regras de remocao:

- `Etiqueta`
- `Cupom`
- `E-mail`
- `Categoria`
- `Evento`
- `Local Inscricao`
- `Balcao`

Se um registro cair em mais de uma regra, os motivos aparecem juntos, por exemplo:

```text
Cupom; E-mail; Categoria
```

## Pre-requisitos

Antes de executar o projeto, tenha instalado:

- Python 3.10 ou superior
- Pip
- Acesso ao banco MySQL Magento/Running Land
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

## Como Usar

1. Abra `http://127.0.0.1:5000/`.
2. Pesquise um evento no campo `Evento Magento`.
3. Clique em `Adicionar evento`.
4. Repita o processo para selecionar mais eventos, ou digite IDs separados por virgula.
5. Clique em `Exportar dados brutos` ou `Exportar dados limpos`.
6. O navegador baixara o arquivo `.xlsx` na pasta padrao de downloads.

## Script de Tratamento

O arquivo `tratamento.py` concentra as regras de montagem e limpeza dos dados.

Principais funcoes:

```python
montar_dataframe_magento(dados)
limpar_dados_magento(dados)
separar_dados_magento_por_limpeza(dados)
gerar_dados_limpos_magento(id_evento)
gerar_planilhas_limpeza_magento(id_evento)
```

O script tambem pode ser executado diretamente:

```bash
python tratamento.py
```

Nesse modo, ele usa o filtro definido no bloco `if __name__ == "__main__":`.

## Observacoes

- A pasta `templates/` guarda os arquivos HTML renderizados pelo Flask.
- A pasta `static/` guarda CSS e JavaScript servidos diretamente ao navegador.
- O caminho dos arquivos estaticos e gerado no HTML com `url_for('static', filename='...')`.
- A exportacao usa `send_file`, entao quem define a pasta final de download e o navegador.

## Licenca

Este projeto utiliza a licenca MIT. Consulte o arquivo `LICENSE` para mais detalhes.
