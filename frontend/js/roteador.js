// Roteador simples por hash (#/login, #/bandeja, #/tarefa/12...): troca a tela sem recarregar a página.

import { obterSessao } from "./sessao.js";

// Tela aberta depois do login. No Sprint 3 passa a ser Hoy.
export const TELA_INICIAL = "/bandeja";

const rotas = [];
let raiz = null;

// caminho pode ter parâmetros numéricos: "/tarefa/:id" recebe { id: 12 }.
// publica = true: a tela abre sem sessão (login, cadastro).
export function registrarRota(caminho, montarTela, { publica = false } = {}) {
  rotas.push({ partes: caminho.split("/"), montarTela, publica });
}

function encontrarRota(caminho) {
  const partes = caminho.split("/");

  for (const rota of rotas) {
    if (rota.partes.length !== partes.length) continue;

    const parametros = {};
    const confere = rota.partes.every((parte, i) => {
      if (parte.startsWith(":")) {
        if (!/^\d+$/.test(partes[i])) return false;
        parametros[parte.slice(1)] = Number(partes[i]);
        return true;
      }
      return parte === partes[i];
    });

    if (confere) return { rota, parametros };
  }

  return null;
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
  const encontrada = encontrarRota(caminho);

  if (!encontrada) {
    navegar(logado ? TELA_INICIAL : "/login");
    return;
  }

  const { rota, parametros } = encontrada;

  if (!rota.publica && !logado) {
    navegar("/login");
    return;
  }

  if (rota.publica && logado) {
    navegar(TELA_INICIAL);
    return;
  }

  raiz.replaceChildren();
  rota.montarTela(raiz, parametros);
  window.scrollTo(0, 0);
}

export function iniciarRoteador(elementoRaiz) {
  raiz = elementoRaiz;
  window.addEventListener("hashchange", renderizar);
  renderizar();
}
