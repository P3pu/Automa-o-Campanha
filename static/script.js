const campoEvento = document.querySelector("#evento_magento");
const botaoAdicionar = document.querySelector("#adicionar_evento");
const listaSelecionados = document.querySelector("#eventos_selecionados");
const botoesExportacao = document.querySelectorAll(".acoes-exportacao button");
const form = document.querySelector("form");

const eventosSelecionados = new Map();

function extrairIdEvento(valor) {
    if (!valor) {
        return "";
    }

    return valor.split("-", 1)[0].trim();
}

function separarEventosDigitados(valor) {
    return valor
        .split(",")
        .map((evento) => evento.trim())
        .filter(Boolean);
}

function atualizarBotoesExportacao() {
    const possuiEventos = eventosSelecionados.size > 0;

    botoesExportacao.forEach((botao) => {
        botao.disabled = !possuiEventos;
    });
}

function criarInputEvento(idEvento) {
    const input = document.createElement("input");
    input.type = "hidden";
    input.name = "evento_magento_ids";
    input.value = idEvento;
    return input;
}

function criarItemEvento(idEvento, textoEvento) {
    const item = document.createElement("div");
    item.className = "evento-selecionado";
    item.dataset.eventoId = idEvento;

    const texto = document.createElement("span");
    texto.textContent = textoEvento;

    const botaoRemover = document.createElement("button");
    botaoRemover.type = "button";
    botaoRemover.className = "remover-evento";
    botaoRemover.textContent = "x";
    botaoRemover.setAttribute("aria-label", `Remover evento ${idEvento}`);

    botaoRemover.addEventListener("click", () => {
        eventosSelecionados.delete(idEvento);
        item.remove();
        atualizarBotoesExportacao();
    });

    item.append(texto, botaoRemover, criarInputEvento(idEvento));
    return item;
}

function adicionarEvento() {
    const eventosDigitados = separarEventosDigitados(campoEvento.value);
    let quantidadeAdicionada = 0;

    eventosDigitados.forEach((textoEvento) => {
        const idEvento = extrairIdEvento(textoEvento);

        if (!idEvento || eventosSelecionados.has(idEvento)) {
            return;
        }

        const textoExibicao = textoEvento === idEvento ? `Evento ${idEvento}` : textoEvento;
        eventosSelecionados.set(idEvento, textoExibicao);
        listaSelecionados.appendChild(criarItemEvento(idEvento, textoExibicao));
        quantidadeAdicionada += 1;
    });

    if (quantidadeAdicionada > 0) {
        atualizarBotoesExportacao();
    }

    campoEvento.value = "";
    campoEvento.focus();
}

botaoAdicionar.addEventListener("click", adicionarEvento);

campoEvento.addEventListener("keydown", (event) => {
    if (event.key === "Enter") {
        event.preventDefault();
        adicionarEvento();
    }
});

form.addEventListener("submit", (event) => {
    if (event.submitter === botaoAdicionar || eventosSelecionados.size > 0) {
        return;
    }

    event.preventDefault();
    campoEvento.focus();
});

atualizarBotoesExportacao();
