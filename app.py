from io import BytesIO

from flask import Flask, redirect, render_template, request, send_file, url_for
import pandas as pd

from database.queries import buscar_dados_magento, obter_eventos_ativos, obter_eventos_magento
from tratamento import (
    gerar_dados_brutos_ativo,
    gerar_planilhas_limpeza_ativo,
    gerar_planilhas_limpeza_magento,
    gerar_planilhas_magento_ativo,
    montar_dataframe_magento,
)

app = Flask(__name__)


def _formatar_data_evento(data):
    if not data:
        return ""

    if hasattr(data, "strftime"):
        return data.strftime("%d/%m/%Y")

    return str(data)


def _extrair_id_evento(valor_evento):
    if not valor_evento:
        return None

    return valor_evento.split("-", 1)[0].strip()


def _extrair_ids_eventos(valor_eventos):
    if not valor_eventos:
        return []

    ids_eventos = []

    for valor_evento in valor_eventos.split(","):
        id_evento = _extrair_id_evento(valor_evento.strip())

        if id_evento:
            ids_eventos.append(id_evento)

    return ids_eventos


def _obter_ids_eventos_formulario(campo_texto, campo_ids):
    ids_eventos = [
        id_evento.strip()
        for id_evento in request.form.getlist(campo_ids)
        if id_evento.strip()
    ]

    if ids_eventos:
        return ids_eventos

    return _extrair_ids_eventos(request.form.get(campo_texto))


def _formatar_nome_exportacao(ids_eventos):
    if len(ids_eventos) == 1:
        return ids_eventos[0]

    return f"{len(ids_eventos)}_eventos"


def _responder_excel(df, nome_arquivo):
    return _responder_excel_abas({nome_arquivo.removesuffix(".xlsx")[:31]: df}, nome_arquivo)


def _responder_excel_abas(planilhas, nome_arquivo):
    arquivo = BytesIO()

    with pd.ExcelWriter(arquivo, engine="openpyxl") as writer:
        for nome_aba, df in planilhas.items():
            df.to_excel(writer, sheet_name=nome_aba[:31], index=False)

    arquivo.seek(0)
    return send_file(
        arquivo,
        as_attachment=True,
        download_name=nome_arquivo,
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )


@app.route('/')
def index():
    eventos_magento = []
    eventos_ativo = []
    erro_eventos_magento = None
    erro_eventos_ativo = None

    try:
        eventos_magento = [
            {
                "id": id_evento,
                "nome": nome,
                "data": _formatar_data_evento(data),
            }
            for id_evento, nome, data in obter_eventos_magento()
        ]
    except Exception as exc:
        erro_eventos_magento = f"Nao foi possivel carregar os eventos do Magento: {exc}"

    try:
        eventos_ativo = [
            {
                "id": id_evento,
                "nome": nome,
                "data": _formatar_data_evento(data),
            }
            for id_evento, nome, data in obter_eventos_ativos()
        ]
    except Exception as exc:
        erro_eventos_ativo = f"Nao foi possivel carregar os eventos do Ativo: {exc}"

    return render_template(
        'index.html',
        eventos_magento=eventos_magento,
        eventos_ativo=eventos_ativo,
        erro_eventos_magento=erro_eventos_magento,
        erro_eventos_ativo=erro_eventos_ativo,
    )


@app.route('/exportar/dados-brutos', methods=['POST'])
def exportar_dados_brutos():
    ids_eventos = _obter_ids_eventos_formulario('evento_magento', 'evento_magento_ids')

    if not ids_eventos:
        return redirect(url_for('index'))

    dados = buscar_dados_magento(ids_eventos)
    df = montar_dataframe_magento(dados)
    sufixo = _formatar_nome_exportacao(ids_eventos)
    return _responder_excel(df, f"dados_brutos_magento_{sufixo}.xlsx")


@app.route('/exportar/dados-limpos', methods=['POST'])
def exportar_dados_limpos():
    ids_eventos = _obter_ids_eventos_formulario('evento_magento', 'evento_magento_ids')

    if not ids_eventos:
        return redirect(url_for('index'))

    planilhas = gerar_planilhas_limpeza_magento(ids_eventos)
    sufixo = _formatar_nome_exportacao(ids_eventos)
    return _responder_excel_abas(planilhas, f"dados_limpos_magento_{sufixo}.xlsx")


@app.route('/exportar/ativo/dados-brutos', methods=['POST'])
def exportar_dados_brutos_ativo():
    ids_eventos = _obter_ids_eventos_formulario('evento_ativo', 'evento_ativo_ids')

    if not ids_eventos:
        return redirect(url_for('index'))

    df = gerar_dados_brutos_ativo(ids_eventos)
    sufixo = _formatar_nome_exportacao(ids_eventos)
    return _responder_excel(df, f"dados_brutos_ativo_{sufixo}.xlsx")


@app.route('/exportar/ativo/dados-limpos', methods=['POST'])
def exportar_dados_limpos_ativo():
    ids_eventos = _obter_ids_eventos_formulario('evento_ativo', 'evento_ativo_ids')

    if not ids_eventos:
        return redirect(url_for('index'))

    planilhas = gerar_planilhas_limpeza_ativo(ids_eventos)
    sufixo = _formatar_nome_exportacao(ids_eventos)
    return _responder_excel_abas(planilhas, f"dados_limpos_ativo_{sufixo}.xlsx")


@app.route('/exportar/magento-ativo', methods=['POST'])
def exportar_magento_ativo():
    ids_magento = _obter_ids_eventos_formulario(
        'evento_magento_merge',
        'evento_magento_merge_ids',
    )
    ids_ativo = _obter_ids_eventos_formulario(
        'evento_ativo_merge',
        'evento_ativo_merge_ids',
    )

    if not ids_magento or not ids_ativo:
        return redirect(url_for('index'))

    planilhas = gerar_planilhas_magento_ativo(ids_magento, ids_ativo)
    sufixo_magento = _formatar_nome_exportacao(ids_magento)
    sufixo_ativo = _formatar_nome_exportacao(ids_ativo)
    return _responder_excel_abas(
        planilhas,
        f"magento_ativo_{sufixo_magento}_{sufixo_ativo}.xlsx",
    )


if __name__ == '__main__':
    app.run(debug=True)
