// Épica 1 · Capturar. Aba Bandeja: "¿Qué tienes en la cabeza?" com a Bandeja embaixo.
// H1.1 Enter guarda · H1.2 uma tarefa por linha · H1.3 lista da Bandeja · H1.4 "+" vazio leva ao campo.
//
// A tela não espera o servidor: o que a pessoa anota aparece na hora e é
// guardado em segundo plano. Se o servidor falhar, o texto volta para o campo.

import { criarTarefas } from "../api.js";
import { cabecalho, navegacao } from "../componentes.js";
import { criarElemento } from "../html.js";
import { criarListaBandeja } from "../lista-bandeja.js";
import { t } from "../i18n.js";

export function telaBandeja(raiz) {
  raiz.append(cabecalho(), criarElemento(`
    <h1><label for="captura">${t("bandeja.pergunta")}</label></h1>

    <form class="captura" novalidate>
      <textarea id="captura" name="texto" rows="2" maxlength="10000"
        placeholder="${t("bandeja.placeholder")}" enterkeyhint="done" autocomplete="off"></textarea>
      <button class="botao botao-mais" type="submit" aria-label="${t("bandeja.guardar")}">+</button>
    </form>
    <p class="confirmacao" role="status"></p>
    <p class="aviso" role="alert"></p>
  `));

  const formulario = raiz.querySelector(".captura");
  const campo = formulario.texto;
  const confirmacao = raiz.querySelector(".confirmacao");
  const aviso = raiz.querySelector(".aviso");

  let tempoConfirmacao = null;

  function confirmar(texto) {
    confirmacao.textContent = texto;
    clearTimeout(tempoConfirmacao);
    tempoConfirmacao = setTimeout(() => { confirmacao.textContent = ""; }, 2500);
  }

  const bandeja = criarListaBandeja({
    aviso,
    textoVazia: t("bandeja.vaziaCaptura"),
    aoPlanejar: () => confirmar(t("comum.listaParaHoje")),
  });

  raiz.append(bandeja.elemento, navegacao("bandeja"));

  // ---- Captura ----

  function ajustarAltura() {
    campo.style.height = "auto";
    campo.style.height = `${campo.scrollHeight}px`;
  }

  function devolverAoCampo(linhas) {
    const atual = campo.value.trim();
    campo.value = atual ? `${linhas.join("\n")}\n${atual}` : linhas.join("\n");
    ajustarAltura();
  }

  async function guardar() {
    const linhas = campo.value.split("\n").map((linha) => linha.trim()).filter(Boolean);

    // H1.4: sem texto, o "+" só leva o cursor ao campo.
    if (linhas.length === 0) {
      campo.value = "";
      ajustarAltura();
      campo.focus();
      return;
    }

    // Aparece na hora; o campo já fica livre para a próxima ideia.
    const itens = bandeja.adicionarProvisorias(linhas);
    campo.value = "";
    ajustarAltura();
    campo.focus();
    aviso.textContent = "";

    try {
      const criadas = await criarTarefas(linhas);
      bandeja.confirmarProvisorias(itens, criadas);
      confirmar(criadas.length === 1 ? t("bandeja.guardadaUma") : t("bandeja.guardadas", criadas.length));
    } catch (erro) {
      // Não guardou: tira da lista e devolve o texto, para nada se perder.
      bandeja.descartarProvisorias(itens);
      devolverAoCampo(linhas);
      aviso.textContent = erro.message;
    }
  }

  formulario.addEventListener("submit", (evento) => {
    evento.preventDefault();
    guardar();
  });

  // Enter guarda; Shift+Enter abre uma linha nova (no computador).
  campo.addEventListener("keydown", (evento) => {
    if (evento.key === "Enter" && !evento.shiftKey && !evento.isComposing) {
      evento.preventDefault();
      guardar();
    }
  });

  campo.addEventListener("input", ajustarAltura);

  campo.focus();
  bandeja.carregar();
}
