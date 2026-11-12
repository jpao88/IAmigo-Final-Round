// Épica 2 · Desmenuzar. Detalhe da tarefa com os passos.
// H2.1 a IA divide · H2.2 editar, apagar, adicionar e reordenar · H2.3 escrever à mão · H2.4 seguir se a IA falhar.
//
// Como na Bandeja, as mudanças aparecem na hora e são guardadas em segundo plano;
// se o servidor recusar, a tela volta ao estado guardado e mostra um aviso curto.

import {
  adicionarPasso, editarPasso, excluirPasso, gerarPassos,
  listarPassos, obterTarefa, reordenarPassos,
} from "../api.js";
import { criarElemento } from "../html.js";
import { navegar } from "../roteador.js";
import { tituloEmCache } from "./bandeja.js";

const MINUTOS_PADRAO = 10;

// "Unos 45 minutos", "Más o menos 1 hora y 20 minutos".
export function formatarTempoTotal(minutos) {
  if (minutos < 60) return `Unos ${minutos} minutos`;

  const horas = Math.floor(minutos / 60);
  const resto = minutos % 60;
  const textoHoras = horas === 1 ? "1 hora" : `${horas} horas`;

  return resto === 0
    ? `Más o menos ${textoHoras}`
    : `Más o menos ${textoHoras} y ${resto} minutos`;
}

export function telaTarefa(raiz, { id: tarefaId }) {
  raiz.append(criarElemento(`
    <header class="cabecalho">
      <a class="botao-texto" href="#/bandeja">← Bandeja</a>
    </header>

    <h1 class="titulo-tarefa"></h1>

    <section class="sem-passos" hidden>
      <p class="subtitulo">IAmigo te sugiere los pasos y tú los ajustas.</p>
      <button class="botao" type="button" data-acao="dividir">Que IAmigo lo divida</button>
      <button class="botao-texto centro" type="button" data-acao="manual">Prefiero escribirlos yo</button>
    </section>

    <p class="pensando" role="status" hidden>IAmigo está pensando…</p>
    <p class="aviso" role="alert"></p>

    <section class="com-passos" hidden>
      <div class="tempo-total">
        <p class="tempo-texto"></p>
        <div class="barra-tempo" aria-hidden="true"></div>
      </div>
      <ol class="lista-passos"></ol>
    </section>

    <form class="novo-passo" novalidate hidden>
      <label class="rotulo-oculto" for="novo-passo-texto">Nuevo paso</label>
      <input id="novo-passo-texto" name="texto" type="text" maxlength="255"
        placeholder="Agrega un paso" autocomplete="off" enterkeyhint="done">
      <label class="minutos">
        <input name="minutos" type="number" inputmode="numeric" min="1" max="120"
          placeholder="${MINUTOS_PADRAO}" aria-label="Minutos del nuevo paso">
        <span>min</span>
      </label>
      <button class="botao botao-mais" type="submit" aria-label="Agregar paso">+</button>
    </form>

    <button class="botao" type="button" data-acao="listo" hidden>Listo</button>
  `));

  const titulo = raiz.querySelector(".titulo-tarefa");
  const semPassos = raiz.querySelector(".sem-passos");
  const pensando = raiz.querySelector(".pensando");
  const aviso = raiz.querySelector(".aviso");
  const comPassos = raiz.querySelector(".com-passos");
  const tempoTexto = raiz.querySelector(".tempo-texto");
  const barraTempo = raiz.querySelector(".barra-tempo");
  const lista = raiz.querySelector(".lista-passos");
  const formNovo = raiz.querySelector(".novo-passo");
  const botaoListo = raiz.querySelector('[data-acao="listo"]');

  // Os passos como estão guardados no servidor (só os visíveis, na ordem).
  let passos = [];
  let modoManual = false;

  titulo.textContent = tituloEmCache(tarefaId) ?? "";

  // ---- Desenho ----

  function avisar(mensagem) {
    aviso.textContent = mensagem;
  }

  function desenharTempo() {
    const total = passos.reduce((soma, passo) => soma + passo.minutos_estimados, 0);
    tempoTexto.textContent = formatarTempoTotal(total);

    // Princípio "O tempo se vê": cada passo ocupa na barra o tamanho dos seus minutos.
    barraTempo.replaceChildren(...passos.map((passo) => {
      const pedaco = document.createElement("span");
      pedaco.style.flexGrow = passo.minutos_estimados;
      return pedaco;
    }));
  }

  function itemDoPasso(passo, indice) {
    const item = document.createElement("li");
    item.className = "passo";
    item.dataset.id = passo.id;

    item.append(criarElemento(`
      <div class="passo-linha">
        <input class="passo-texto" type="text" maxlength="255" autocomplete="off">
        <label class="minutos">
          <input class="passo-minutos" type="number" inputmode="numeric" min="1" max="120">
          <span>min</span>
        </label>
      </div>
      <div class="passo-acoes">
        <button class="botao-icone" type="button" data-acao="subir">↑</button>
        <button class="botao-icone" type="button" data-acao="descer">↓</button>
        <button class="botao-icone" type="button" data-acao="apagar">✕</button>
      </div>
    `));

    const texto = item.querySelector(".passo-texto");
    const minutos = item.querySelector(".passo-minutos");
    texto.value = passo.texto;
    minutos.value = passo.minutos_estimados;

    const numero = indice + 1;
    texto.setAttribute("aria-label", `Paso ${numero}`);
    minutos.setAttribute("aria-label", `Minutos del paso ${numero}`);
    item.querySelector('[data-acao="subir"]').setAttribute("aria-label", `Subir el paso ${numero}`);
    item.querySelector('[data-acao="descer"]').setAttribute("aria-label", `Bajar el paso ${numero}`);
    item.querySelector('[data-acao="apagar"]').setAttribute("aria-label", `Borrar el paso ${numero}`);

    item.querySelector('[data-acao="subir"]').disabled = indice === 0;
    item.querySelector('[data-acao="descer"]').disabled = indice === passos.length - 1;

    // Ainda sem id: está sendo guardado; não dá para editar até o servidor responder.
    if (passo.id === null) {
      item.classList.add("passo-pendente");
      item.querySelectorAll("input, button").forEach((elemento) => { elemento.disabled = true; });
    }

    return item;
  }

  function desenhar() {
    const temPassos = passos.length > 0;

    semPassos.hidden = temPassos || modoManual;
    comPassos.hidden = !temPassos;
    formNovo.hidden = !(temPassos || modoManual);
    botaoListo.hidden = !temPassos;

    lista.replaceChildren(...passos.map(itemDoPasso));
    desenharTempo();
  }

  async function recarregarPassos() {
    const todos = await listarPassos(tarefaId);
    passos = todos.filter((passo) => !passo.substituido);
    desenhar();
  }

  // ---- Carregar ----

  async function carregar() {
    try {
      const [tarefa] = await Promise.all([obterTarefa(tarefaId), recarregarPassos()]);
      titulo.textContent = tarefa.titulo;
    } catch (erro) {
      avisar(erro.message);
    }
  }

  // ---- H2.1: IAmigo divide ----

  async function dividirComIA() {
    avisar("");
    semPassos.hidden = true;
    pensando.hidden = false;

    try {
      passos = await gerarPassos(tarefaId);
      desenhar();
    } catch (erro) {
      avisar(erro.message);

      if (erro.status === 400 || erro.status === 422) {
        // Já tinha passos (ex.: dividida em outra aba): mostra os que existem.
        await recarregarPassos().catch(() => {});
      } else {
        // H2.4: a IA falhou; a pessoa segue escrevendo os passos.
        abrirModoManual();
      }
    } finally {
      pensando.hidden = true;
    }
  }

  // ---- H2.3: escrever à mão ----

  function abrirModoManual() {
    modoManual = true;
    desenhar();
    formNovo.texto.focus();
  }

  formNovo.addEventListener("submit", async (evento) => {
    evento.preventDefault();
    avisar("");

    const texto = formNovo.texto.value.trim();
    const minutosDigitados = formNovo.minutos.value === "" ? null : Number(formNovo.minutos.value);

    if (!texto) {
      formNovo.texto.focus();
      return;
    }

    // Aparece na hora; o campo fica livre para o próximo passo.
    const provisorio = { id: null, texto, minutos_estimados: minutosDigitados ?? MINUTOS_PADRAO };
    passos = [...passos, provisorio];
    desenhar();
    lista.lastElementChild.classList.add("passo-novo");
    formNovo.reset();
    formNovo.texto.focus();

    try {
      const criado = await adicionarPasso(tarefaId, texto, minutosDigitados);
      passos = passos.map((passo) => (passo === provisorio ? criado : passo));
      desenhar();
    } catch (erro) {
      passos = passos.filter((passo) => passo !== provisorio);
      desenhar();
      formNovo.texto.value = texto;
      formNovo.minutos.value = minutosDigitados ?? "";
      avisar(erro.message);
    }
  });

  // ---- H2.2: editar, apagar e reordenar ----

  async function guardarEdicao(item) {
    const passo = passos.find((p) => String(p.id) === item.dataset.id);
    if (!passo) return;

    const texto = item.querySelector(".passo-texto").value.trim();
    const campoMinutos = item.querySelector(".passo-minutos");
    const minutos = campoMinutos.value === "" ? MINUTOS_PADRAO : Number(campoMinutos.value);

    if (texto === passo.texto && minutos === passo.minutos_estimados) return;

    if (!texto) {
      // Texto apagado: volta ao anterior. Para tirar o passo, existe o ✕.
      item.querySelector(".passo-texto").value = passo.texto;
      avisar("Para quitar un paso, usa ✕.");
      return;
    }

    avisar("");
    const anterior = { ...passo };
    Object.assign(passo, { texto, minutos_estimados: minutos });
    campoMinutos.value = minutos;
    desenharTempo();

    try {
      await editarPasso(tarefaId, passo.id, texto, minutos);
    } catch (erro) {
      Object.assign(passo, anterior);
      desenhar();
      avisar(erro.message);
    }
  }

  async function apagar(passoId) {
    avisar("");
    const anteriores = passos;
    passos = passos.filter((passo) => passo.id !== passoId);
    desenhar();

    try {
      await excluirPasso(tarefaId, passoId);
    } catch (erro) {
      passos = anteriores;
      desenhar();
      avisar(erro.message);
    }
  }

  async function mover(passoId, deslocamento) {
    // A ordem nova precisa dos ids de todos: espera os passos pendentes serem guardados.
    if (passos.some((passo) => passo.id === null)) return;

    const de = passos.findIndex((passo) => passo.id === passoId);
    const para = de + deslocamento;
    if (para < 0 || para >= passos.length) return;

    avisar("");
    const anteriores = passos;
    passos = [...passos];
    [passos[de], passos[para]] = [passos[para], passos[de]];
    desenhar();
    lista.children[para].querySelector(`[data-acao="${deslocamento < 0 ? "subir" : "descer"}"]`)?.focus();

    try {
      await reordenarPassos(tarefaId, passos.map((passo) => passo.id));
    } catch (erro) {
      passos = anteriores;
      desenhar();
      avisar(erro.message);
    }
  }

  lista.addEventListener("change", (evento) => {
    const item = evento.target.closest(".passo");
    if (item && !item.classList.contains("passo-pendente")) guardarEdicao(item);
  });

  // Enter num passo confirma a edição (no celular fecha o teclado).
  lista.addEventListener("keydown", (evento) => {
    if (evento.key === "Enter" && evento.target.matches("input")) {
      evento.preventDefault();
      evento.target.blur();
    }
  });

  lista.addEventListener("click", (evento) => {
    const botao = evento.target.closest("button[data-acao]");
    const item = evento.target.closest(".passo");
    if (!botao || !item || item.classList.contains("passo-pendente")) return;

    const passoId = Number(item.dataset.id);
    const acao = botao.dataset.acao;

    if (acao === "apagar") apagar(passoId);
    if (acao === "subir") mover(passoId, -1);
    if (acao === "descer") mover(passoId, 1);
  });

  raiz.querySelector('[data-acao="dividir"]').addEventListener("click", dividirComIA);
  raiz.querySelector('[data-acao="manual"]').addEventListener("click", abrirModoManual);
  botaoListo.addEventListener("click", () => navegar("/bandeja"));

  carregar();
}
