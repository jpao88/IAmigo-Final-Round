// Épica 1 · Capturar. Tela inicial: "¿Qué tienes en la cabeza?" com a Bandeja embaixo.
// H1.1 Enter guarda · H1.2 uma tarefa por linha · H1.3 lista da Bandeja · H1.4 "+" vazio leva ao campo.
//
// A tela não espera o servidor: o que a pessoa anota aparece na hora e é
// guardado em segundo plano; ao abrir, mostra a última Bandeja conhecida e
// atualiza em silêncio. Se o servidor falhar, o texto volta para o campo.

import { criarTarefas, listarBandeja } from "../api.js";
import { criarElemento } from "../html.js";
import { navegar } from "../roteador.js";
import { encerrarSessao, obterUsuario } from "../sessao.js";

// ---- Cópia local da Bandeja (só para abrir rápido; o servidor é quem manda) ----

function chaveCache() {
  return `iamigo.bandeja.${obterUsuario().id}`;
}

function lerCache() {
  try {
    const tarefas = JSON.parse(localStorage.getItem(chaveCache()));
    return Array.isArray(tarefas) ? tarefas : null;
  } catch {
    return null;
  }
}

// A tela da tarefa usa para mostrar o título na hora, antes do servidor responder.
export function tituloEmCache(tarefaId) {
  return lerCache()?.find((tarefa) => tarefa.id === tarefaId)?.titulo ?? null;
}

function salvarCache(tarefas) {
  try {
    localStorage.setItem(chaveCache(), JSON.stringify(tarefas));
  } catch {
    // Sem armazenamento: a tela só abre um pouco mais devagar.
  }
}

export function telaBandeja(raiz) {
  raiz.append(criarElemento(`
    <header class="cabecalho">
      <p class="marca">IAmigo</p>
      <button class="botao-texto" type="button" data-acao="sair">Salir</button>
    </header>

    <p class="saudacao subtitulo"></p>
    <h1><label for="captura">¿Qué tienes en la cabeza?</label></h1>

    <form class="captura" novalidate>
      <textarea id="captura" name="texto" rows="2" maxlength="10000"
        placeholder="Una idea por línea" enterkeyhint="done" autocomplete="off"></textarea>
      <button class="botao botao-mais" type="submit" aria-label="Guardar">+</button>
    </form>
    <p class="confirmacao" role="status"></p>
    <p class="aviso" role="alert"></p>

    <section class="bandeja" aria-labelledby="titulo-bandeja">
      <h2 id="titulo-bandeja">Tu Bandeja</h2>
      <p class="vazia subtitulo" hidden>Aquí aparecerá lo que anotes.</p>
      <ul class="lista-tarefas"></ul>
    </section>
  `));

  const formulario = raiz.querySelector(".captura");
  const campo = formulario.texto;
  const confirmacao = raiz.querySelector(".confirmacao");
  const aviso = raiz.querySelector(".aviso");
  const lista = raiz.querySelector(".lista-tarefas");
  const vazia = raiz.querySelector(".vazia");

  // textContent: o nome vem da pessoa, nunca entra como HTML.
  raiz.querySelector(".saudacao").textContent = `Hola, ${obterUsuario().nome}`;

  raiz.querySelector('[data-acao="sair"]').addEventListener("click", () => {
    encerrarSessao();
    navegar("/login");
  });

  // ---- Lista ----

  // Guardada: vira um link para a tela da tarefa (Desmenuzar).
  function marcarComoGuardada(item, id) {
    item.dataset.id = id;
    item.classList.remove("tarefa-pendente");

    const link = document.createElement("a");
    link.className = "tarefa-link";
    link.href = `#/tarefa/${id}`;
    link.textContent = item.textContent;
    item.replaceChildren(link);
  }

  function itemDaTarefa(titulo, { id = null, nova = false } = {}) {
    const item = document.createElement("li");
    item.className = "tarefa";
    if (nova) item.classList.add("tarefa-nova");
    item.textContent = titulo;

    if (id === null) item.classList.add("tarefa-pendente");
    else marcarComoGuardada(item, id);

    return item;
  }

  function pendentes() {
    return [...lista.querySelectorAll(".tarefa-pendente")];
  }

  // As já guardadas, na ordem da tela, para a cópia local.
  function tarefasGuardadas() {
    return [...lista.querySelectorAll(".tarefa[data-id]")].map((item) => ({
      id: Number(item.dataset.id),
      titulo: item.textContent,
    }));
  }

  // Guardadas nesta tela, as mais novas primeiro. Se a lista do servidor
  // foi pedida antes delas existirem, não podem sumir quando ela chegar.
  const recentes = [];

  function mostrar(tarefas) {
    const ids = new Set(tarefas.map((tarefa) => tarefa.id));
    const faltando = recentes.filter((tarefa) => !ids.has(tarefa.id));

    // As que ainda estão sendo guardadas continuam no topo.
    lista.replaceChildren(
      ...pendentes(),
      ...[...faltando, ...tarefas].map((tarefa) => itemDaTarefa(tarefa.titulo, { id: tarefa.id })),
    );
    vazia.hidden = lista.children.length > 0;
  }

  async function carregarBandeja() {
    const copia = lerCache();
    if (copia) mostrar(copia);

    try {
      const tarefas = await listarBandeja();
      mostrar(tarefas);
      salvarCache(tarefasGuardadas());
    } catch (erro) {
      // Com a cópia local na tela, a pessoa continua usando; só avisa se não há nada.
      if (!copia) aviso.textContent = erro.message;
    }
  }

  // ---- Captura ----

  let tempoConfirmacao = null;

  function ajustarAltura() {
    campo.style.height = "auto";
    campo.style.height = `${campo.scrollHeight}px`;
  }

  function confirmar(quantas) {
    confirmacao.textContent = quantas === 1 ? "Guardado en tu Bandeja." : `Guardé ${quantas} cosas.`;
    clearTimeout(tempoConfirmacao);
    tempoConfirmacao = setTimeout(() => { confirmacao.textContent = ""; }, 2500);
  }

  function devolverAoCampo(linhas) {
    const atual = campo.value.trim();
    campo.value = atual ? `${linhas.join("\n")}\n${atual}` : linhas.join("\n");
    ajustarAltura();
  }

  async function guardar() {
    const linhas = campo.value.split("\n").map((linha) => linha.trim()).filter(Boolean);

    // H1.4: sem texto, o "+" só leva o cursor ao campo.
    if (linhas.length === 0) {
      campo.value = "";
      ajustarAltura();
      campo.focus();
      return;
    }

    // Aparece na hora; o campo já fica livre para a próxima ideia.
    const itens = linhas.map((titulo) => itemDaTarefa(titulo, { nova: true }));
    lista.prepend(...itens);
    vazia.hidden = true;
    campo.value = "";
    ajustarAltura();
    campo.focus();
    aviso.textContent = "";

    try {
      const criadas = await criarTarefas(linhas);
      criadas.forEach((tarefa, indice) => marcarComoGuardada(itens[indice], tarefa.id));
      recentes.unshift(...criadas);
      salvarCache(tarefasGuardadas());
      confirmar(criadas.length);
    } catch (erro) {
      // Não guardou: tira da lista e devolve o texto, para nada se perder.
      itens.forEach((item) => item.remove());
      vazia.hidden = lista.children.length > 0;
      devolverAoCampo(linhas);
      aviso.textContent = erro.message;
    }
  }

  formulario.addEventListener("submit", (evento) => {
    evento.preventDefault();
    guardar();
  });

  // Enter guarda; Shift+Enter abre uma linha nova (no computador).
  campo.addEventListener("keydown", (evento) => {
    if (evento.key === "Enter" && !evento.shiftKey && !evento.isComposing) {
      evento.preventDefault();
      guardar();
    }
  });

  campo.addEventListener("input", ajustarAltura);

  campo.focus();
  carregarBandeja();
}
