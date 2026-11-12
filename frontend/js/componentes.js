// Peças comuns às telas principais (Hoy e Bandeja).

import { criarElemento } from "./html.js";
import { navegar } from "./roteador.js";
import { encerrarSessao, obterUsuario } from "./sessao.js";

// Marca, "Salir" discreto e a saudação com o nome.
export function cabecalho() {
  const fragmento = criarElemento(`
    <header class="cabecalho">
      <p class="marca">IAmigo</p>
      <button class="botao-texto" type="button">Salir</button>
    </header>
    <p class="saudacao subtitulo"></p>
  `);

  // textContent: o nome vem da pessoa, nunca entra como HTML.
  fragmento.querySelector(".saudacao").textContent = `Hola, ${obterUsuario().nome}`;
  fragmento.querySelector("button").addEventListener("click", () => {
    encerrarSessao();
    navegar("/login");
  });

  return fragmento;
}

// Abas fixas embaixo, ao alcance do polegar.
export function navegacao(ativa) {
  const fragmento = criarElemento(`
    <nav class="navegacao" aria-label="Secciones">
      <a href="#/hoje" data-aba="hoje">Hoy</a>
      <a href="#/bandeja" data-aba="bandeja">Bandeja</a>
    </nav>
  `);

  fragmento.querySelector(`[data-aba="${ativa}"]`).setAttribute("aria-current", "page");
  return fragmento;
}
