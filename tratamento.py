from pathlib import Path
import unicodedata

import pandas as pd

from database.queries import buscar_dados_ativo, buscar_dados_magento


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

COLUNAS_ATIVO = [
    "N. Peito",
    "Local",
    "SKU",
    "ID Evento",
    "Evento",
    "Local Inscrição",
    "Balcão",
    "Protocolo",
    "ID Inscrição",
    "Data Evento",
    "Data Pedido",
    "Status Pedido",
    "Status Inscrição",
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
    "Documento",
    "TELEFONE",
    "Sexo",
    "Estado",
    "Cidade",
    "Personalização",
    "Tamanho Camiseta",
    "Produtos",
    "Cupom",
    "Etiqueta",
    "Classificação Cupom",
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

VALORES_REMOVER_CLASSIFICACAO_CUPOM_ATIVO = ["grupos"]
VALORES_REMOVER_LOCAL_INSCRICAO_ATIVO = ["balcão"]
VALORES_REMOVER_CATEGORIA_ATIVO = [
    "cortesia",
    "cortesias",
    "grupos",
    "grupo",
    "saúde corporativa",
    "saude corporativa",
    "corporativa",
    "patrocinador",
    "convidado",
]
VALORES_REMOVER_EMAIL_ATIVO = [
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


def montar_dataframe_ativo(dados):
    return pd.DataFrame(dados, columns=COLUNAS_ATIVO)


def _criar_chave_sku(df, prefixo):
    sku = df["SKU"].astype("string").str.strip()
    chave = sku.mask(sku.isna() | sku.eq(""))
    sem_sku = chave.isna()
    chave.loc[sem_sku] = [f"__{prefixo}_SEM_SKU_{indice}" for indice in df.index[sem_sku]]
    return sku, chave


def preparar_magento_para_merge(df_magento):
    df = df_magento.copy()
    df["SKU"] = df["SKU DO EVENTO "]
    df["SKU"], df["_SKU_MERGE"] = _criar_chave_sku(df, "MAGENTO")
    return df


def preparar_ativo_para_merge(df_ativo):
    df = df_ativo.copy()
    df["SKU"], df["_SKU_MERGE"] = _criar_chave_sku(df, "ATIVO")
    return df


def juntar_magento_ativo(df_magento, df_ativo):
    magento = preparar_magento_para_merge(df_magento)
    ativo = preparar_ativo_para_merge(df_ativo)

    df_merge = magento.merge(
        ativo,
        on="_SKU_MERGE",
        how="outer",
        suffixes=("_magento", "_ativo"),
        indicator=True,
    )

    sku_magento = df_merge.get("SKU_magento")
    sku_ativo = df_merge.get("SKU_ativo")

    if sku_magento is not None and sku_ativo is not None:
        df_merge.insert(0, "SKU", sku_magento.combine_first(sku_ativo))
        df_merge = df_merge.drop(columns=["SKU_magento", "SKU_ativo", "_SKU_MERGE"])

    return df_merge


def _adicionar_motivo_remocao(motivos, mascara, motivo):
    motivos.loc[mascara] = motivos.loc[mascara].apply(
        lambda valor: f"{valor}; {motivo}" if valor else motivo
    )


def _normalizar_texto(valor):
    texto = "" if pd.isna(valor) else str(valor)
    texto = unicodedata.normalize("NFKD", texto)
    texto = "".join(caractere for caractere in texto if not unicodedata.combining(caractere))
    return texto.strip().lower()


def _contem_qualquer_valor(serie, valores):
    serie_normalizada = serie.map(_normalizar_texto)
    mascara = pd.Series(False, index=serie.index)

    for valor in valores:
        mascara = mascara | serie_normalizada.str.contains(
            _normalizar_texto(valor),
            regex=False,
            na=False,
        )

    return mascara


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
    remover_por_valor_zero = pd.to_numeric(df["Valor"], errors="coerce").eq(0)

    motivos = pd.Series("", index=df.index, dtype="object")
    _adicionar_motivo_remocao(motivos, remover_por_etiqueta, "Etiqueta")
    _adicionar_motivo_remocao(motivos, remover_por_cupom, "Cupom")
    _adicionar_motivo_remocao(motivos, remover_por_email, "E-mail")
    _adicionar_motivo_remocao(motivos, remover_por_categoria, "Categoria")
    _adicionar_motivo_remocao(motivos, remover_por_evento, "Evento")
    _adicionar_motivo_remocao(motivos, remover_por_local_inscricao, "Local Inscrição")
    _adicionar_motivo_remocao(motivos, remover_por_balcao, "Balcão")
    _adicionar_motivo_remocao(motivos, remover_por_valor_zero, "Valor = 0")

    mascara_removidos = (
        remover_por_etiqueta
        | remover_por_cupom
        | remover_por_email
        | remover_por_categoria
        | remover_por_evento
        | remover_por_local_inscricao
        | remover_por_balcao
        | remover_por_valor_zero
    )

    dados_limpos = df[~mascara_removidos].copy()
    dados_removidos = df[mascara_removidos].copy()
    dados_removidos.insert(0, "Regra Remoção", motivos[mascara_removidos])

    return dados_limpos, dados_removidos


def separar_dados_ativo_por_limpeza(dados):
    df = montar_dataframe_ativo(dados)

    if df.empty:
        dados_removidos = df.copy()
        dados_removidos.insert(0, "Regra Remoção", pd.Series(dtype="object"))
        return df.copy(), dados_removidos

    remover_por_classificacao_cupom = _contem_qualquer_valor(
        df["Classificação Cupom"],
        VALORES_REMOVER_CLASSIFICACAO_CUPOM_ATIVO,
    )
    remover_por_local_inscricao = _contem_qualquer_valor(
        df["Local Inscrição"],
        VALORES_REMOVER_LOCAL_INSCRICAO_ATIVO,
    )
    remover_por_categoria = _contem_qualquer_valor(
        df["Categoria"],
        VALORES_REMOVER_CATEGORIA_ATIVO,
    )
    remover_por_email = _contem_qualquer_valor(
        df["E-mail"],
        VALORES_REMOVER_EMAIL_ATIVO,
    )
    remover_por_valor_zero = pd.to_numeric(df["Valor"], errors="coerce").eq(0)

    motivos = pd.Series("", index=df.index, dtype="object")
    _adicionar_motivo_remocao(
        motivos,
        remover_por_classificacao_cupom,
        "Classificação Cupom",
    )
    _adicionar_motivo_remocao(motivos, remover_por_local_inscricao, "Local Inscrição")
    _adicionar_motivo_remocao(motivos, remover_por_categoria, "Categoria")
    _adicionar_motivo_remocao(motivos, remover_por_email, "E-mail")
    _adicionar_motivo_remocao(motivos, remover_por_valor_zero, "Valor = 0")

    mascara_removidos = (
        remover_por_classificacao_cupom
        | remover_por_local_inscricao
        | remover_por_categoria
        | remover_por_email
        | remover_por_valor_zero
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


def gerar_dados_brutos_ativo(id_evento):
    dados = buscar_dados_ativo(id_evento)
    return montar_dataframe_ativo(dados)


def gerar_planilhas_limpeza_ativo(id_evento):
    dados = buscar_dados_ativo(id_evento)
    dados_limpos, dados_removidos = separar_dados_ativo_por_limpeza(dados)
    return {
        "Dados Limpos": dados_limpos,
        "Removidos": dados_removidos,
    }


def gerar_planilhas_magento_ativo(ids_magento, ids_ativo):
    df_magento = montar_dataframe_magento(buscar_dados_magento(ids_magento))
    df_ativo = montar_dataframe_ativo(buscar_dados_ativo(ids_ativo))
    df_merge = juntar_magento_ativo(df_magento, df_ativo)

    somente_magento = df_merge[df_merge["_merge"] == "left_only"].copy()
    somente_ativo = df_merge[df_merge["_merge"] == "right_only"].copy()

    return {
        "Magento Bruto": df_magento,
        "Ativo Bruto": df_ativo,
        "Magento + Ativo": df_merge,
        "Somente Magento": somente_magento,
        "Somente Ativo": somente_ativo,
    }
