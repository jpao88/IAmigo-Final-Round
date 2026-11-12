// Épica 6 · Primer uso. A primeira tarefa guiada (H6.2) e o fim da guia (H6.3).
// Enquanto a pessoa percorre a tarefa (dividir, pôr em Hoy, primeiro passo),
// guarda-se qual é a tarefa guiada; as telas mostram uma dica curta.

import { concluirOnboarding } from "./api.js";
import { atualizarUsuario, obterUsuario } from "./sessao.js";

function chave() {
  return `iamigo.guia.${obterUsuario().id}`;
}

export function precisaDaGuia() {
  return obterUsuario()?.onboarding_concluido === false;
}

export function iniciarGuia(tarefaId) {
  try {
    localStorage.setItem(chave(), JSON.stringify({ tarefaId }));
  } catch {
    // Sem armazenamento: a tarefa fica criada, só sem as dicas.
  }
}

// A tarefa guiada, ou null.
export function tarefaDaGuia() {
  try {
    return JSON.parse(localStorage.getItem(chave()))?.tarefaId ?? null;
  } catch {
    return null;
  }
}

// H6.3: marca na hora neste navegador e avisa o servidor em segundo plano.
export function terminarGuia() {
  const usuario = obterUsuario();
  try {
    localStorage.removeItem(chave());
  } catch {
    // Nada a fazer.
  }
  atualizarUsuario({ ...usuario, onboarding_concluido: true });
  concluirOnboarding().then(atualizarUsuario).catch(() => {});
}
