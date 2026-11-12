// Roteador simples por hash (#/login, #/bandeja...): troca a tela sem recarregar a página.

import { obterSessao } from "./sessao.js";

// Tela aberta depois do login. No Sprint 3 passa a ser Hoy.
export const TELA_INICIAL = "/bandeja";

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
    navegar(logado ? TELA_INICIAL : "/login");
    return;
  }

  if (!rota.publica && !logado) {
    navegar("/login");
    return;
  }

  if (rota.publica && logado) {
    navegar(TELA_INICIAL);
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
