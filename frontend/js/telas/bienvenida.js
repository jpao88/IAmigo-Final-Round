// H6.1 · Bienvenida: uma tela só, com as cinco etapas do ciclo em ícones.

import { linkIdioma, marca } from "../componentes.js";
import { terminarGuia } from "../guia.js";
import { criarElemento } from "../html.js";
import { navegar, TELA_INICIAL } from "../roteador.js";
import { obterUsuario } from "../sessao.js";
import { t } from "../i18n.js";
import { icone } from "../icones.js";

const ETAPAS = [
  ["lapis", "bienvenida.anota"],
  ["tesoura", "bienvenida.divide"],
  ["alfinete", "bienvenida.elige"],
  ["play", "bienvenida.hazlo"],
  ["festa", "bienvenida.celebra"],
];

export function telaBienvenida(raiz) {
  raiz.append(criarElemento(`
    ${marca({ grande: true })}
    <h1 class="saudacao-bienvenida"></h1>
    <p class="subtitulo">${t("bienvenida.frase")}</p>

    <ol class="etapas" aria-label="${t("bienvenida.assim")}"></ol>

    <button class="botao" type="button" data-acao="probar">${t("bienvenida.probar")}</button>
    <button class="botao-texto centro" type="button" data-acao="saltar">${t("bienvenida.saltar")}</button>
  `), linkIdioma());

  raiz.querySelector(".saudacao-bienvenida").textContent = t("cab.ola", obterUsuario().nome);

  raiz.querySelector(".etapas").replaceChildren(...ETAPAS.map(([nomeIcone, nome]) => {
    const item = document.createElement("li");
    item.append(criarElemento(`<span class="etapa-icone" aria-hidden="true"></span><span></span>`));
    item.firstElementChild.innerHTML = icone(nomeIcone);
    item.lastElementChild.textContent = t(nome);
    return item;
  }));

  raiz.querySelector('[data-acao="probar"]').addEventListener("click", () => navegar("/primera-tarea"));
  raiz.querySelector('[data-acao="saltar"]').addEventListener("click", () => {
    terminarGuia();
    navegar(TELA_INICIAL);
  });
}
