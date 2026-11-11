// Roteador simples por hash (#/login, #/hoje...): troca a tela sem recarregar a página.

import { obterSessao } from "./sessao.js";

const rotas = new Map();
let raiz = null;

// publica = true: a tela abre sem sessão (login, cadastro).
export function registrarRota(caminho, montarTela, { publica = false } = {}) {
  rotas.set(caminho, { montarTela, publica });
}

export function navegar(caminho) {
  if (location.hash === `#${caminho}`) {
    renderizar();
  } else {
    location.hash = caminho;
  }
}

function renderizar() {
  const caminho = location.hash.slice(1) || "/";
  const logado = obterSessao() !== null;
  const rota = rotas.get(caminho);

  if (!rota) {
    navegar(logado ? "/hoje" : "/login");
    return;
  }

  if (!rota.publica && !logado) {
    navegar("/login");
    return;
  }

  if (rota.publica && logado) {
    navegar("/hoje");
    return;
  }

  raiz.replaceChildren();
  rota.montarTela(raiz);
  window.scrollTo(0, 0);
}

export function iniciarRoteador(elementoRaiz) {
  raiz = elementoRaiz;
  window.addEventListener("hashchange", renderizar);
  renderizar();
}
