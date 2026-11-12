// H6.1 · Bienvenida: uma tela só, com as cinco etapas do ciclo em ícones.

import { terminarGuia } from "../guia.js";
import { criarElemento } from "../html.js";
import { navegar, TELA_INICIAL } from "../roteador.js";
import { obterUsuario } from "../sessao.js";

const ETAPAS = [
  ["✏️", "Anota"],
  ["✂️", "Divide"],
  ["📌", "Elige"],
  ["▶️", "Hazlo"],
  ["🎉", "Celebra"],
];

export function telaBienvenida(raiz) {
  raiz.append(criarElemento(`
    <p class="marca">IAmigo</p>
    <h1 class="saudacao-bienvenida"></h1>
    <p class="subtitulo">Te ayudo a terminar lo importante, un paso a la vez.</p>

    <ol class="etapas" aria-label="Así funciona"></ol>

    <button class="botao" type="button" data-acao="probar">Probar con una tarea</button>
    <button class="botao-texto centro" type="button" data-acao="saltar">Ya sé cómo funciona</button>
  `));

  raiz.querySelector(".saudacao-bienvenida").textContent = `Hola, ${obterUsuario().nome}`;

  raiz.querySelector(".etapas").replaceChildren(...ETAPAS.map(([icone, nome]) => {
    const item = document.createElement("li");
    item.append(criarElemento(`<span class="etapa-icone" aria-hidden="true"></span><span></span>`));
    item.firstElementChild.textContent = icone;
    item.lastElementChild.textContent = nome;
    return item;
  }));

  raiz.querySelector('[data-acao="probar"]').addEventListener("click", () => navegar("/primera-tarea"));
  raiz.querySelector('[data-acao="saltar"]').addEventListener("click", () => {
    terminarGuia();
    navegar(TELA_INICIAL);
  });
}
