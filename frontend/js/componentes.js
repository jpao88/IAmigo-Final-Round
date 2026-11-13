// Peças comuns às telas principais (Hoy e Bandeja).

import { criarElemento } from "./html.js";
import { navegar } from "./roteador.js";
import { encerrarSessao, obterUsuario } from "./sessao.js";
import { t, trocarIdioma } from "./i18n.js";
import { icone } from "./icones.js";
import { alternarTema, temaAtual } from "./tema.js";

// O ícone mostra para onde o botão leva: lua no claro, sol no oscuro.
function desenharBotaoTema(botao) {
  const escuro = temaAtual() === "escuro";
  botao.innerHTML = icone(escuro ? "sol" : "lua");
  botao.setAttribute("aria-label", escuro ? t("cab.modoClaro") : t("cab.modoEscuro"));
}

// O logo em texto (Nunito 800). O leitor de tela lê só "IAmigo";
// o desenho (com o "ı" sem pingo e o ponto com brilho) fica escondido dele.
// grande: login, cadastro e bienvenida, com "ASISTENTE INTELIGENTE" embaixo.
export function marca({ grande = false } = {}) {
  return `
    <p class="marca${grande ? " marca-grande" : ""}">
      <span class="rotulo-oculto">IAmigo</span>
      <span aria-hidden="true"><span class="marca-ia">IA</span>m<span class="marca-i">ı</span>go</span>
      ${grande ? `<span class="marca-subtitulo" aria-hidden="true">${t("marca.subtitulo")}</span>` : ""}
    </p>`;
}

// Marca, modo claro/oscuro, "Salir" discreto e a saudação com o nome.
export function cabecalho() {
  const fragmento = criarElemento(`
    <header class="cabecalho">
      ${marca()}
      <div class="cabecalho-acoes">
        <button class="botao-texto botao-idioma" type="button" lang="${t("cab.outroIdioma") === "PT" ? "pt-BR" : "es"}"
          aria-label="${t("cab.trocarIdioma")}">${t("cab.outroIdioma")}</button>
        <button class="botao-texto botao-tema" type="button"></button>
        <button class="botao-texto" type="button" data-acao="sair">${t("cab.sair")}</button>
      </div>
    </header>
    <p class="saudacao subtitulo"></p>
  `);

  // textContent: o nome vem da pessoa, nunca entra como HTML.
  fragmento.querySelector(".saudacao").textContent = t("cab.ola", obterUsuario().nome);
  fragmento.querySelector(".botao-idioma").addEventListener("click", trocarIdioma);

  const botaoTema = fragmento.querySelector(".botao-tema");
  desenharBotaoTema(botaoTema);
  botaoTema.addEventListener("click", () => {
    alternarTema();
    desenharBotaoTema(botaoTema);
  });

  fragmento.querySelector('[data-acao="sair"]').addEventListener("click", () => {
    encerrarSessao();
    navegar("/login");
  });

  return fragmento;
}

// Abas fixas embaixo, ao alcance do polegar.
export function navegacao(ativa) {
  const fragmento = criarElemento(`
    <nav class="navegacao" aria-label="${t("nav.secoes")}">
      <a href="#/hoje" data-aba="hoje">${t("nav.hoje")}</a>
      <a href="#/bandeja" data-aba="bandeja">${t("nav.bandeja")}</a>
    </nav>
  `);

  fragmento.querySelector(`[data-aba="${ativa}"]`).setAttribute("aria-current", "page");
  return fragmento;
}

// Nas telas sem cabeçalho: "Português" / "Español", discreto, embaixo.
export function linkIdioma() {
  const botao = document.createElement("button");
  botao.type = "button";
  botao.className = "botao-texto centro link-idioma";
  botao.lang = t("cab.outroIdioma") === "PT" ? "pt-BR" : "es";
  botao.textContent = t("cab.outroIdiomaNome");
  botao.addEventListener("click", trocarIdioma);
  return botao;
}
