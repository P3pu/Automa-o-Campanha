from pathlib import Path

import pandas as pd

from database.queries import buscar_dados_magento


COLUNAS_MAGENTO = [
    "N. Peito",
    "Local",
    "SKU DO EVENTO ",
    "ID Evento",
    "Evento",
    "Local Inscrição",
    "Balcão",
    "Protocolo",
    "ID Inscrição",
    "Data Evento",
    "Data Pedido",
    "Status Pedido",
    "Status Confirmado",
    "Valor",
    "Modalidade",
    "Modalidade Ajustada",
    "Categoria",
    "Assinante",
    "Pelotão",
    "ID Usuario",
    "Nome inscrição",
    "Idade",
    "E-mail",
    "TELEFONE",
    "Documento",
    "Sexo",
    "Estado",
    "Cidade",
    "Personalização",
    "Tamanho Camiseta",
    "Produtos",
    "Cupom",
    "Etiqueta",
    "Classificacao Cupom",
]

VALORES_REMOVER_ETIQUETA = [
    "cortesia",
    "corteisa",
    "cortesias",
    "grupos",
    "company",
    "teste",
    "testes",
]
VALORES_REMOVER_CUPOM = ["cortesia", "grupos", "grupo", "teste", "testes"]
VALORES_REMOVER_EMAIL = [
    "@nortemkt.com",
    "@ativo.com",
    "@cscdoesporte.com",
    "@test.com",
    "@teste",
    "teste",
    "testes",
    "grupo",
    "grupos",
]
VALORES_REMOVER_CATEGORIA = [
    "cortesia",
    "cortesias",
    "grupos",
    "company",
    "grupo",
    "saude corporativa",
    "corporativa",
    "patrocinador",
    "teste",
    "testes",
]
VALORES_REMOVER_EVENTO = ["cortesia", "cortesias", "grupos", "grupo", "teste", "testes"]

ESTADOS_PARA_UF = {
    "Acre": "AC",
    "Alagoas": "AL",
    "Amapá": "AP",
    "Amazonas": "AM",
    "Bahia": "BA",
    "Ceará": "CE",
    "Distrito Federal": "DF",
    "Espírito Santo": "ES",
    "Goiás": "GO",
    "Maranhão": "MA",
    "Mato Grosso": "MT",
    "Mato Grosso do Sul": "MS",
    "Minas Gerais": "MG",
    "Pará": "PA",
    "Paraíba": "PB",
    "Paraná": "PR",
    "Pernambuco": "PE",
    "Piauí": "PI",
    "Rio de Janeiro": "RJ",
    "Rio Grande do Norte": "RN",
    "Rio Grande do Sul": "RS",
    "Rondônia": "RO",
    "Roraima": "RR",
    "Santa Catarina": "SC",
    "São Paulo": "SP",
    "Sergipe": "SE",
    "Tocantins": "TO",
}


def montar_dataframe_magento(dados):
    return pd.DataFrame(dados, columns=COLUNAS_MAGENTO)


def limpar_dados_magento(dados):
    df = montar_dataframe_magento(dados)

    df = df[~df["Etiqueta"].str.lower().str.contains("|".join(VALORES_REMOVER_ETIQUETA), na=False)]
    df = df[~df["Cupom"].str.lower().str.contains("|".join(VALORES_REMOVER_CUPOM), na=False)]
    df = df[~df["E-mail"].str.lower().str.contains("|".join(VALORES_REMOVER_EMAIL), na=False)]
    df = df[~df["Categoria"].str.lower().str.contains("|".join(VALORES_REMOVER_CATEGORIA), na=False)]
    df = df[~df["Evento"].str.lower().str.contains("|".join(VALORES_REMOVER_EVENTO), na=False)]

    df["Estado"] = df["Estado"].str.strip()
    df["Estado"] = df["Estado"].replace(ESTADOS_PARA_UF)

    df = df[df["Local Inscrição"].isna()]
    df = df[df["Balcão"].isna()]

    return df


def gerar_dados_limpos_magento(id_evento):
    dados = buscar_dados_magento(id_evento)
    return limpar_dados_magento(dados)
