// H4.6 · Onde a pessoa parou no modo foco: tarefa, passo e tempo que faltava.
// Fica neste navegador (o temporizador vive só no front na V1) e vale só para o mesmo dia.

import { dataLocal } from "./api.js";
import { obterUsuario } from "./sessao.js";

function chave() {
  return `iamigo.foco.${obterUsuario().id}`;
}

// { tarefaId, titulo, passoId, passoTexto, restanteMs, totalMs, pausado }
export function salvarFoco(estado) {
  try {
    localStorage.setItem(chave(), JSON.stringify({ ...estado, data: dataLocal() }));
  } catch {
    // Sem armazenamento: só não dá para retomar depois.
  }
}

export function lerFoco() {
  try {
    const estado = JSON.parse(localStorage.getItem(chave()));
    return estado?.data === dataLocal() ? estado : null;
  } catch {
    return null;
  }
}

export function limparFoco() {
  try {
    localStorage.removeItem(chave());
  } catch {
    // Nada a fazer.
  }
}
