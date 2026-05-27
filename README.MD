# Automação de Estração e Limpeza de Dados

## Descrição

Projeto em Python para extrair dados de inscrições de eventos, consultar bancos Magento/Running Land e Ativo.com, aplicar regras de limpeza e gerar uma planilha Excel pronta para análise.

## Sobre o Projeto

Este projeto ajuda a automatizar a preparação de bases de inscritos, reduzindo trabalho manual e padronizando filtros importantes, como remoção de cortesias, grupos, testes e registros vindos de locais de inscrição específicos. Ele também normaliza informações como estado/UF e exporta o resultado final em formato `.xlsx`.

## Tecnologias Utilizadas

- Python
- Pandas
- OpenPyXL
- MySQL Connector/Python
- python-dotenv
- Flask, disponível nas dependências para evoluções com interface web ou API

## Funcionalidades Principais

- Conexão com banco Magento/Running Land via variáveis de ambiente.
- Conexão com banco Ativo.com via variáveis de ambiente.
- Consulta de inscrições por ID de evento.
- Listagem de eventos disponíveis nas bases Magento e Ativo.
- Limpeza de registros de cortesia, grupos, testes e campanhas internas.
- Normalização de nomes de estados para siglas UF.
- Exportação do resultado tratado para Excel.

## Pré-requisitos

Antes de executar o projeto, tenha instalado:

- Python 3.10 ou superior
- Pip
- Acesso aos bancos MySQL Magento/Running Land e/ou Ativo.com
- Credenciais de banco configuradas em um arquivo `.env`

## Como Instalar e Executar

1. Clone o repositório:

```bash
git clone <url-do-repositorio>
cd portalCampanha
```

2. Crie e ative um ambiente virtual:

```bash
python -m venv .venv
.venv\Scripts\activate
```

3. Instale as dependências:

```bash
pip install -r requirements.txt
```

4. Configure as variáveis de ambiente:

```bash
copy .env.example .env
```

5. No arquivo `.env`, remova o sufixo `_EXEMPLO` dos nomes das variáveis e preencha os dados reais de conexão:

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

6. Ajuste os IDs de evento no arquivo `tratamento.py`, se necessário:

```python
Eventos_Prime = [48133]
```

7. Execute o script:

```bash
python tratamento.py
```

Ao final da execução, o arquivo tratado será salvo na pasta Downloads do usuário com o nome `tratamento.xlsx`.

## Exemplos de Uso

Para buscar inscrições do Magento diretamente no código:

```python
from database.queries import buscar_dados_magento

eventos = [48133]
dados = buscar_dados_magento(eventos)

print(f"Total de registros encontrados: {len(dados)}")
```

Para executar o fluxo completo de tratamento e gerar a planilha:

```bash
python tratamento.py
```

## Como Contribuir

Contribuições são bem-vindas. Para colaborar:

1. Abra uma issue descrevendo o problema ou melhoria.
2. Crie uma branch para sua alteração.
3. Faça commits claros e objetivos.
4. Abra um pull request explicando o que foi alterado e como testar.

## Licença

Este projeto utiliza a licença MIT. Consulte o arquivo `LICENSE` para mais detalhes, quando disponível no repositório.
