from flask import Flask, render_template

from database.queries import obter_eventos_magento

app = Flask(__name__)


def _formatar_data_evento(data):
    if not data:
        return ""

    if hasattr(data, "strftime"):
        return data.strftime("%d/%m/%Y")

    return str(data)


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


if __name__ == '__main__':
    app.run(debug=True)
