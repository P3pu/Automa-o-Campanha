from io import BytesIO

from flask import Flask, redirect, render_template, request, send_file, url_for
import pandas as pd

from database.queries import buscar_dados_magento, obter_eventos_magento
from tratamento import gerar_dados_limpos_magento, montar_dataframe_magento

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


def _responder_excel(df, nome_arquivo):
    arquivo = BytesIO()

    with pd.ExcelWriter(arquivo, engine="openpyxl") as writer:
        df.to_excel(writer, index=False)

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
    id_evento = _extrair_id_evento(request.form.get('evento_magento'))

    if not id_evento:
        return redirect(url_for('index'))

    dados = buscar_dados_magento(id_evento)
    df = montar_dataframe_magento(dados)
    return _responder_excel(df, f"dados_brutos_magento_{id_evento}.xlsx")


@app.route('/exportar/dados-limpos', methods=['POST'])
def exportar_dados_limpos():
    id_evento = _extrair_id_evento(request.form.get('evento_magento'))

    if not id_evento:
        return redirect(url_for('index'))

    df = gerar_dados_limpos_magento(id_evento)
    return _responder_excel(df, f"dados_limpos_magento_{id_evento}.xlsx")


if __name__ == '__main__':
    app.run(debug=True)
