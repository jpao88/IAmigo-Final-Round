// A4 · Apagar com "Deshacer" em vez de pedir confirmação antes.
//
// A tarefa some na hora, aparece um aviso "Tarea borrada · Deshacer" por 6 s
// e só então o servidor apaga. Se a pessoa fechar a app nesses 6 s, a tarefa
// não é apagada (erra para o lado seguro).
// O aviso fica no <body>, fora da tela: continua visível quando a rota muda.

import { excluirTarefa } from "./api.js";
import { limparFoco, lerFoco } from "./foco-estado.js";
import { t } from "./i18n.js";

const ESPERA_MS = 6000;

// Só uma por vez: apagar outra confirma a anterior na hora.
let pendente = null; // { tarefaId, temporizador, aoDesfazer }
let aviso = null;

function elementoAviso() {
  if (aviso) return aviso;

  aviso = document.createElement("div");
  aviso.className = "aviso-desfazer";
  aviso.setAttribute("role", "status");
  aviso.hidden = true;
  aviso.innerHTML = '<span class="aviso-desfazer-texto"></span><button type="button" class="aviso-desfazer-botao"></button>';
  aviso.querySelector("button").addEventListener("click", desfazer);
  document.body.append(aviso);
  return aviso;
}

function mostrarAviso(texto, comBotao) {
  const elemento = elementoAviso();
  elemento.querySelector(".aviso-desfazer-texto").textContent = texto;
  const botao = elemento.querySelector("button");
  botao.textContent = t("apagar.desfazer");
  botao.hidden = !comBotao;
  elemento.hidden = false;
}

function esconderAviso() {
  if (aviso) aviso.hidden = true;
}

async function confirmar() {
  if (!pendente) return;

  const { tarefaId, temporizador } = pendente;
  clearTimeout(temporizador);
  pendente = null;
  esconderAviso();

  try {
    await excluirTarefa(tarefaId);
    if (lerFoco()?.tarefaId === tarefaId) limparFoco();
  } catch (erro) {
    // Não apagou: a tarefa volta a aparecer na próxima vez que a lista carregar.
    mostrarAviso(erro.message, false);
    setTimeout(esconderAviso, 4000);
  }
}

function desfazer() {
  if (!pendente) return;

  const { temporizador, aoDesfazer } = pendente;
  clearTimeout(temporizador);
  pendente = null;
  esconderAviso();
  aoDesfazer();
}

// aoDesfazer: o que fazer se a pessoa tocar em "Deshacer" (ex.: voltar à tarefa).
export function apagarComDesfazer(tarefaId, { aoDesfazer = () => {} } = {}) {
  if (pendente) confirmar();

  pendente = {
    tarefaId,
    aoDesfazer,
    temporizador: setTimeout(confirmar, ESPERA_MS),
  };
  mostrarAviso(t("apagar.apagada"), true);
}

// As listas escondem a tarefa que está esperando para ser apagada.
export function semApagadas(tarefas) {
  return pendente ? tarefas.filter((tarefa) => tarefa.id !== pendente.tarefaId) : tarefas;
}
