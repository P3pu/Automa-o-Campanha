from io import BytesIO

from flask import Flask, redirect, render_template, request, send_file, url_for
import pandas as pd

from database.queries import buscar_dados_magento, obter_eventos_magento
from tratamento import gerar_planilhas_limpeza_magento, montar_dataframe_magento

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


def _obter_ids_eventos_formulario():
    ids_eventos = [
        id_evento.strip()
        for id_evento in request.form.getlist('evento_magento_ids')
        if id_evento.strip()
    ]

    if ids_eventos:
        return ids_eventos

    return _extrair_ids_eventos(request.form.get('evento_magento'))


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
    eventos = []
    erro_eventos = None

    try:
        eventos = [
            {
                "id": id_evento,
                "nome": nome,
                "data": _formatar_data_evento(data),
            }
            for id_evento, nome, data in obter_eventos_magento()
        ]
    except Exception as exc:
        erro_eventos = f"Nao foi possivel carregar os eventos do Magento: {exc}"

    return render_template(
        'index.html',
        eventos=eventos,
        erro_eventos=erro_eventos,
    )


@app.route('/exportar/dados-brutos', methods=['POST'])
def exportar_dados_brutos():
    ids_eventos = _obter_ids_eventos_formulario()

    if not ids_eventos:
        return redirect(url_for('index'))

    dados = buscar_dados_magento(ids_eventos)
    df = montar_dataframe_magento(dados)
    sufixo = _formatar_nome_exportacao(ids_eventos)
    return _responder_excel(df, f"dados_brutos_magento_{sufixo}.xlsx")


@app.route('/exportar/dados-limpos', methods=['POST'])
def exportar_dados_limpos():
    ids_eventos = _obter_ids_eventos_formulario()

    if not ids_eventos:
        return redirect(url_for('index'))

    planilhas = gerar_planilhas_limpeza_magento(ids_eventos)
    sufixo = _formatar_nome_exportacao(ids_eventos)
    return _responder_excel_abas(planilhas, f"dados_limpos_magento_{sufixo}.xlsx")


if __name__ == '__main__':
    app.run(debug=True)
