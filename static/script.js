const paineis = document.querySelectorAll(".painel");
const itensMenu = document.querySelectorAll(".menu-item");
const seletoresEvento = document.querySelectorAll("[data-event-picker]");

function ativarPainel(idPainel) {
    paineis.forEach((painel) => {
        painel.classList.toggle("ativo", painel.id === idPainel);
    });

    itensMenu.forEach((item) => {
        item.classList.toggle("ativo", item.dataset.panelTarget === idPainel);
    });
}

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

function criarInputEvento(idEvento, nomeCampo) {
    const input = document.createElement("input");
    input.type = "hidden";
    input.name = nomeCampo;
    input.value = idEvento;
    return input;
}

function atualizarBotoesFormulario(form) {
    const seletoresDoForm = form.querySelectorAll("[data-event-picker]");
    const todosComEvento = Array.from(seletoresDoForm).every((seletor) => {
        const campoEvento = seletor.querySelector("[data-event-input]");
        const possuiSelecionados = seletor.eventosSelecionados && seletor.eventosSelecionados.size > 0;
        const possuiTextoDigitado = campoEvento.value.trim().length > 0;
        return possuiSelecionados || possuiTextoDigitado;
    });

    form.querySelectorAll(".acoes-exportacao button").forEach((botao) => {
        botao.disabled = !todosComEvento;
    });
}

function criarItemEvento(seletor, idEvento, textoEvento) {
    const listaSelecionados = seletor.querySelector("[data-selected-events]");
    const nomeCampo = listaSelecionados.dataset.hiddenName;
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
        seletor.eventosSelecionados.delete(idEvento);
        item.remove();
        atualizarBotoesFormulario(seletor.closest("form"));
    });

    item.append(texto, botaoRemover, criarInputEvento(idEvento, nomeCampo));
    return item;
}

function adicionarEvento(seletor) {
    const campoEvento = seletor.querySelector("[data-event-input]");
    const listaSelecionados = seletor.querySelector("[data-selected-events]");
    const eventosDigitados = separarEventosDigitados(campoEvento.value);
    let quantidadeAdicionada = 0;

    eventosDigitados.forEach((textoEvento) => {
        const idEvento = extrairIdEvento(textoEvento);

        if (!idEvento || seletor.eventosSelecionados.has(idEvento)) {
            return;
        }

        const textoExibicao = textoEvento === idEvento ? `Evento ${idEvento}` : textoEvento;
        seletor.eventosSelecionados.set(idEvento, textoExibicao);
        listaSelecionados.appendChild(criarItemEvento(seletor, idEvento, textoExibicao));
        quantidadeAdicionada += 1;
    });

    if (quantidadeAdicionada > 0) {
        atualizarBotoesFormulario(seletor.closest("form"));
    }

    campoEvento.value = "";
    campoEvento.focus();
}

itensMenu.forEach((item) => {
    item.addEventListener("click", () => {
        ativarPainel(item.dataset.panelTarget);
    });
});

seletoresEvento.forEach((seletor) => {
    const campoEvento = seletor.querySelector("[data-event-input]");
    const botaoAdicionar = seletor.querySelector("[data-add-event]");
    seletor.eventosSelecionados = new Map();

    botaoAdicionar.addEventListener("click", () => adicionarEvento(seletor));

    campoEvento.addEventListener("keydown", (event) => {
        if (event.key === "Enter") {
            event.preventDefault();
            adicionarEvento(seletor);
        }
    });

    campoEvento.addEventListener("input", () => atualizarBotoesFormulario(seletor.closest("form")));

    atualizarBotoesFormulario(seletor.closest("form"));
});

document.querySelectorAll("form").forEach((form) => {
    form.addEventListener("submit", (event) => {
        const seletoresDoForm = form.querySelectorAll("[data-event-picker]");
        const todosComEvento = Array.from(seletoresDoForm).every((seletor) => {
            const campoEvento = seletor.querySelector("[data-event-input]");
            const possuiSelecionados = seletor.eventosSelecionados && seletor.eventosSelecionados.size > 0;
            const possuiTextoDigitado = campoEvento.value.trim().length > 0;
            return possuiSelecionados || possuiTextoDigitado;
        });

        if (todosComEvento) {
            return;
        }

        event.preventDefault();
        const primeiroVazio = Array.from(seletoresDoForm).find((seletor) => {
            return !seletor.eventosSelecionados || seletor.eventosSelecionados.size === 0;
        });
        primeiroVazio?.querySelector("[data-event-input]")?.focus();
    });
});
