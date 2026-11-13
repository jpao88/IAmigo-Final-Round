// Lista da Bandeja (H1.3) com "+ Hoy" em cada tarefa (H3.1).
// Usada na aba Bandeja (com a captura) e embaixo de Hoy (como pede o recorrido).
//
// Abre com a cópia local e atualiza em silêncio; as mudanças aparecem na hora
// e, se o servidor recusar, voltam como estavam com um aviso curto.

import { listarBandeja, planejarHoje } from "./api.js";
import { semApagadas } from "./apagar-depois.js";
import { criarElemento } from "./html.js";
import { obterUsuario } from "./sessao.js";
import { t } from "./i18n.js";

// ---- Cópia local (só para abrir rápido; o servidor é quem manda) ----

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

function salvarCache(tarefas) {
  try {
    localStorage.setItem(chaveCache(), JSON.stringify(tarefas));
  } catch {
    // Sem armazenamento: a tela só abre um pouco mais devagar.
  }
}

// A tela da tarefa usa para mostrar o título na hora, antes do servidor responder.
// Procura na cópia da Bandeja e na de Hoy (a tarefa pode ter vindo de qualquer uma).
export function tituloEmCache(tarefaId) {
  let doDia = [];
  try {
    doDia = JSON.parse(localStorage.getItem(`iamigo.hoje.${obterUsuario().id}`))?.tarefas ?? [];
  } catch {
    // Sem cópia de Hoy.
  }

  return [...(lerCache() ?? []), ...doDia].find((tarefa) => tarefa.id === tarefaId)?.titulo ?? null;
}

// aviso: onde mostrar erros · aoPlanejar(tarefa): chamado depois de um "+ Hoy" guardado ·
// maximo: quantas mostrar (embaixo de Hoy, só as mais recentes; o resto na aba Bandeja).
export function criarListaBandeja({ aviso, aoPlanejar = () => {}, textoVazia, maximo = null }) {
  const secao = criarElemento(`
    <section class="bandeja" aria-labelledby="titulo-bandeja">
      <h2 id="titulo-bandeja">${t("bandeja.titulo")}</h2>
      <p class="vazia subtitulo" hidden></p>
      <ul class="lista-tarefas"></ul>
      <a class="link-secundario ver-tudo" href="#/bandeja" hidden>${t("bandeja.verTudo")}</a>
    </section>
  `).firstElementChild;

  const lista = secao.querySelector(".lista-tarefas");
  const vazia = secao.querySelector(".vazia");
  const verTudo = secao.querySelector(".ver-tudo");
  vazia.textContent = textoVazia;

  // Guardadas nesta tela, as mais novas primeiro: se a lista do servidor foi
  // pedida antes delas existirem, não podem sumir quando ela chegar.
  const recentes = [];
  // Enviadas para Hoy nesta tela: não podem voltar com uma lista antiga.
  const foraDaBandeja = new Set();

  // Também esconde as que passam do máximo (sem contar quantas são: princípio "Sem culpa").
  function atualizarVazia() {
    const itens = [...lista.children];
    vazia.hidden = itens.length > 0;

    if (maximo !== null) {
      itens.forEach((item, indice) => { item.hidden = indice >= maximo; });
      verTudo.hidden = itens.length <= maximo;
    }
  }

  // Guardada: vira um link para a tela da tarefa e ganha "+ Hoy".
  function marcarComoGuardada(item, id) {
    item.dataset.id = id;
    item.classList.remove("tarefa-pendente");

    const link = document.createElement("a");
    link.className = "tarefa-link";
    link.href = `#/tarefa/${id}`;
    link.textContent = item.dataset.titulo;

    const botaoHoje = document.createElement("button");
    botaoHoje.className = "botao-hoy";
    botaoHoje.type = "button";
    botaoHoje.textContent = t("bandeja.maisHoje");
    botaoHoje.setAttribute("aria-label", t("bandeja.maisHojeRotulo", item.dataset.titulo));

    item.replaceChildren(link, botaoHoje);
  }

  function itemDaTarefa(titulo, { id = null, nova = false } = {}) {
    const item = document.createElement("li");
    item.className = "tarefa";
    item.dataset.titulo = titulo;
    if (nova) item.classList.add("tarefa-nova");

    if (id === null) {
      item.classList.add("tarefa-pendente");
      item.textContent = titulo;
    } else {
      marcarComoGuardada(item, id);
    }

    return item;
  }

  function guardarCopia() {
    salvarCache([...lista.querySelectorAll(".tarefa[data-id]")].map((item) => ({
      id: Number(item.dataset.id),
      titulo: item.dataset.titulo,
    })));
  }

  function mostrar(tarefas) {
    const ids = new Set(tarefas.map((tarefa) => tarefa.id));
    const visiveis = [...recentes.filter((tarefa) => !ids.has(tarefa.id)), ...tarefas]
      .filter((tarefa) => !foraDaBandeja.has(tarefa.id));
    const semAApagar = semApagadas(visiveis);

    // As que ainda estão sendo guardadas continuam no topo.
    lista.replaceChildren(
      ...lista.querySelectorAll(".tarefa-pendente"),
      ...semAApagar.map((tarefa) => itemDaTarefa(tarefa.titulo, { id: tarefa.id })),
    );
    atualizarVazia();
  }

  async function carregar() {
    const copia = lerCache();
    if (copia) mostrar(copia);

    try {
      mostrar(await listarBandeja());
      guardarCopia();
    } catch (erro) {
      // Com a cópia na tela, a pessoa continua usando; só avisa se não há nada.
      if (!copia) aviso.textContent = erro.message;
    }
  }

  // ---- H3.1: "+ Hoy" ----

  async function paraHoje(item) {
    const id = Number(item.dataset.id);
    const titulo = item.dataset.titulo;
    const seguinte = item.nextElementSibling;

    aviso.textContent = "";
    foraDaBandeja.add(id);
    item.remove();
    atualizarVazia();

    try {
      await planejarHoje([id]);
      guardarCopia();
      aoPlanejar({ id, titulo });
    } catch (erro) {
      // Não coube (ex.: limite): volta para o mesmo lugar.
      foraDaBandeja.delete(id);
      lista.insertBefore(item, seguinte && seguinte.isConnected ? seguinte : null);
      atualizarVazia();
      aviso.textContent = erro.message;
    }
  }

  lista.addEventListener("click", (evento) => {
    const botao = evento.target.closest(".botao-hoy");
    if (botao) paraHoje(botao.closest(".tarefa"));
  });

  // ---- Para a captura (aba Bandeja) ----

  function adicionarProvisorias(titulos) {
    const itens = titulos.map((titulo) => itemDaTarefa(titulo, { nova: true }));
    lista.prepend(...itens);
    atualizarVazia();
    return itens;
  }

  function confirmarProvisorias(itens, criadas) {
    criadas.forEach((tarefa, indice) => marcarComoGuardada(itens[indice], tarefa.id));
    recentes.unshift(...criadas);
    guardarCopia();
  }

  function descartarProvisorias(itens) {
    itens.forEach((item) => item.remove());
    atualizarVazia();
  }

  return { elemento: secao, carregar, adicionarProvisorias, confirmarProvisorias, descartarProvisorias };
}
