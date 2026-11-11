// Tela Hoy. Por enquanto só saúda e permite sair (H0.3);
// o planejamento do dia chega no Sprint 3.

import { criarElemento } from "../html.js";
import { navegar } from "../roteador.js";
import { encerrarSessao, obterUsuario } from "../sessao.js";

export function telaHoje(raiz) {
  raiz.append(criarElemento(`
    <p class="marca">IAmigo</p>
    <h1 class="saudacao"></h1>
    <p class="subtitulo">Pronto verás aquí tu día.</p>

    <button class="botao botao-secundario empurrar-abaixo" type="button">Cerrar sesión</button>
  `));

  // textContent: o nome vem da pessoa, nunca entra como HTML.
  raiz.querySelector(".saudacao").textContent = `Hola, ${obterUsuario().nome}`;

  raiz.querySelector("button").addEventListener("click", () => {
    encerrarSessao();
    navegar("/login");
  });
}
