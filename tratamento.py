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


def _adicionar_motivo_remocao(motivos, mascara, motivo):
    motivos.loc[mascara] = motivos.loc[mascara].apply(
        lambda valor: f"{valor}; {motivo}" if valor else motivo
    )


def separar_dados_magento_por_limpeza(dados):
    df = montar_dataframe_magento(dados)

    if df.empty:
        return df.copy(), df.copy()

    df["Estado"] = df["Estado"].str.strip()
    df["Estado"] = df["Estado"].replace(ESTADOS_PARA_UF)

    remover_por_etiqueta = df["Etiqueta"].str.lower().str.contains(
        "|".join(VALORES_REMOVER_ETIQUETA),
        na=False,
    )
    remover_por_cupom = df["Cupom"].str.lower().str.contains(
        "|".join(VALORES_REMOVER_CUPOM),
        na=False,
    )
    remover_por_email = df["E-mail"].str.lower().str.contains(
        "|".join(VALORES_REMOVER_EMAIL),
        na=False,
    )
    remover_por_categoria = df["Categoria"].str.lower().str.contains(
        "|".join(VALORES_REMOVER_CATEGORIA),
        na=False,
    )
    remover_por_evento = df["Evento"].str.lower().str.contains(
        "|".join(VALORES_REMOVER_EVENTO),
        na=False,
    )
    remover_por_local_inscricao = df["Local Inscrição"].notna()
    remover_por_balcao = df["Balcão"].notna()

    motivos = pd.Series("", index=df.index, dtype="object")
    _adicionar_motivo_remocao(motivos, remover_por_etiqueta, "Etiqueta")
    _adicionar_motivo_remocao(motivos, remover_por_cupom, "Cupom")
    _adicionar_motivo_remocao(motivos, remover_por_email, "E-mail")
    _adicionar_motivo_remocao(motivos, remover_por_categoria, "Categoria")
    _adicionar_motivo_remocao(motivos, remover_por_evento, "Evento")
    _adicionar_motivo_remocao(motivos, remover_por_local_inscricao, "Local Inscrição")
    _adicionar_motivo_remocao(motivos, remover_por_balcao, "Balcão")

    mascara_removidos = (
        remover_por_etiqueta
        | remover_por_cupom
        | remover_por_email
        | remover_por_categoria
        | remover_por_evento
        | remover_por_local_inscricao
        | remover_por_balcao
    )

    dados_limpos = df[~mascara_removidos].copy()
    dados_removidos = df[mascara_removidos].copy()
    dados_removidos.insert(0, "Regra Remoção", motivos[mascara_removidos])

    return dados_limpos, dados_removidos


def limpar_dados_magento(dados):
    dados_limpos, _ = separar_dados_magento_por_limpeza(dados)
    return dados_limpos


def gerar_dados_limpos_magento(id_evento):
    dados = buscar_dados_magento(id_evento)
    return limpar_dados_magento(dados)


def gerar_planilhas_limpeza_magento(id_evento):
    dados = buscar_dados_magento(id_evento)
    dados_limpos, dados_removidos = separar_dados_magento_por_limpeza(dados)
    return {
        "Dados Limpos": dados_limpos,
        "Removidos": dados_removidos,
    }
