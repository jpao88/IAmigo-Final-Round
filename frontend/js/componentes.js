// Peças comuns às telas principais (Hoy e Bandeja).

import { criarElemento } from "./html.js";
import { navegar } from "./roteador.js";
import { encerrarSessao, obterUsuario } from "./sessao.js";
import { alternarTema, temaAtual } from "./tema.js";

// O ícone mostra para onde o botão leva: 🌙 no claro, ☀️ no oscuro.
function desenharBotaoTema(botao) {
  const escuro = temaAtual() === "escuro";
  botao.textContent = escuro ? "☀️" : "🌙";
  botao.setAttribute("aria-label", escuro ? "Cambiar a modo claro" : "Cambiar a modo oscuro");
}

// Marca, modo claro/oscuro, "Salir" discreto e a saudação com o nome.
export function cabecalho() {
  const fragmento = criarElemento(`
    <header class="cabecalho">
      <p class="marca">IAmigo</p>
      <div class="cabecalho-acoes">
        <button class="botao-texto botao-tema" type="button"></button>
        <button class="botao-texto" type="button" data-acao="sair">Salir</button>
      </div>
    </header>
    <p class="saudacao subtitulo"></p>
  `);

  // textContent: o nome vem da pessoa, nunca entra como HTML.
  fragmento.querySelector(".saudacao").textContent = `Hola, ${obterUsuario().nome}`;

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
    <nav class="navegacao" aria-label="Secciones">
      <a href="#/hoje" data-aba="hoje">Hoy</a>
      <a href="#/bandeja" data-aba="bandeja">Bandeja</a>
    </nav>
  `);

  fragmento.querySelector(`[data-aba="${ativa}"]`).setAttribute("aria-current", "page");
  return fragmento;
}
