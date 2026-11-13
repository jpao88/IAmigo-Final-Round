// Épica 2 · Desmenuzar. Detalhe da tarefa com os passos.
// H2.1 a IA divide · H2.2 editar, apagar, adicionar e reordenar · H2.3 escrever à mão · H2.4 seguir se a IA falhar.
//
// Como na Bandeja, as mudanças aparecem na hora e são guardadas em segundo plano;
// se o servidor recusar, a tela volta ao estado guardado e mostra um aviso curto.

import {
  adicionarPasso, editarPasso, excluirPasso, excluirTarefa, gerarPassos,
  listarPassos, obterTarefa, planejarHoje, renomearTarefa, reordenarPassos,
} from "../api.js";
import { lerFoco, limparFoco } from "../foco-estado.js";
import { obterUsuario } from "../sessao.js";
import { tarefaDaGuia } from "../guia.js";
import { criarElemento } from "../html.js";
import { tituloEmCache } from "../lista-bandeja.js";
import { navegar, TELA_INICIAL } from "../roteador.js";
import { desenharBarraTempo, formatarTempoTotal } from "../tempo.js";
import { t } from "../i18n.js";
import { icone } from "../icones.js";

const MINUTOS_PADRAO = 10;

export function telaTarefa(raiz, { id: tarefaId }) {
  raiz.append(criarElemento(`
    <header class="cabecalho">
      <button class="botao-texto com-icone" type="button" data-acao="voltar">${icone("voltar")}${t("comum.voltar")}</button>
      <p class="subtitulo guia-etapa" hidden></p>
    </header>

    <p class="guia" role="status" hidden></p>

    <h1 class="titulo-tarefa">
      <textarea class="titulo-campo" rows="1" maxlength="200" autocomplete="off" enterkeyhint="done"
        aria-label="${t("tarefa.tituloRotulo")}"></textarea>
    </h1>

    <section class="sem-passos" hidden>
      <p class="subtitulo">${t("tarefa.sugere")}</p>
      <button class="botao" type="button" data-acao="dividir">${t("tarefa.dividir")}</button>
      <button class="botao-texto centro" type="button" data-acao="manual">${t("tarefa.manual")}</button>
    </section>

    <p class="pensando" role="status" hidden>${t("comum.pensando")}</p>
    <p class="aviso" role="alert"></p>

    <section class="com-passos" hidden>
      <div class="tempo-total">
        <div class="titulo-com-acao">
          <p class="tempo-texto"></p>
          <button class="botao-texto" type="button" data-acao="ordenar" aria-pressed="false">${t("comum.ordenar")}</button>
        </div>
        <div class="barra-tempo" aria-hidden="true"></div>
      </div>
      <ol class="lista-passos"></ol>
    </section>

    <form class="novo-passo" novalidate hidden>
      <label class="rotulo-oculto" for="novo-passo-texto">${t("tarefa.novoPasso")}</label>
      <input id="novo-passo-texto" name="texto" type="text" maxlength="255"
        placeholder="${t("tarefa.adicionePasso")}" autocomplete="off" enterkeyhint="done">
      <label class="minutos">
        <input name="minutos" type="number" inputmode="numeric" min="1" max="120"
          placeholder="${MINUTOS_PADRAO}" aria-label="${t("tarefa.minutosNovo")}">
        <span>min</span>
      </label>
      <button class="botao botao-mais" type="submit" aria-label="${t("tarefa.adicionar")}">${icone("mais")}</button>
    </form>

    <button class="botao" type="button" data-acao="listo" hidden>${t("comum.listo")}</button>
    <button class="botao" type="button" data-acao="guia-empezar" hidden>${t("tarefa.guiaEmpezar")}</button>

    <button class="link-secundario link-apagar" type="button" data-acao="apagar-tarefa">${t("tarefa.apagar")}</button>
  `));

  // O título é um campo: tocar nele permite reescrevê-lo (ex.: em outro idioma).
  const titulo = raiz.querySelector(".titulo-campo");
  let tituloGuardado = "";
  const semPassos = raiz.querySelector(".sem-passos");
  const pensando = raiz.querySelector(".pensando");
  const aviso = raiz.querySelector(".aviso");
  const comPassos = raiz.querySelector(".com-passos");
  const tempoTexto = raiz.querySelector(".tempo-texto");
  const barraTempo = raiz.querySelector(".barra-tempo");
  const lista = raiz.querySelector(".lista-passos");
  const formNovo = raiz.querySelector(".novo-passo");
  const botaoListo = raiz.querySelector('[data-acao="listo"]');
  const guiaEtapa = raiz.querySelector(".guia-etapa");
  const guia = raiz.querySelector(".guia");
  const botaoGuia = raiz.querySelector('[data-acao="guia-empezar"]');
  const botaoOrdenar = raiz.querySelector('[data-acao="ordenar"]');

  // H6.2: esta é a primeira tarefa guiada?
  const emGuia = tarefaDaGuia() === tarefaId;

  // Os passos como estão guardados no servidor (só os visíveis, na ordem).
  let passos = [];
  let modoManual = false;
  // Como em Hoy: ↑ ↓ e ✕ só aparecem no modo "Ordenar", para a lista ficar leve.
  let ordenando = false;

  function mostrarTitulo(texto) {
    tituloGuardado = texto;
    titulo.value = texto;
    ajustarAltura(titulo);
  }

  mostrarTitulo(tituloEmCache(tarefaId) ?? "");

  // ---- Desenho ----

  function avisar(mensagem) {
    aviso.textContent = mensagem;
  }

  function desenharTempo() {
    const total = passos.reduce((soma, passo) => soma + passo.minutos_estimados, 0);
    tempoTexto.textContent = formatarTempoTotal(total);
    desenharBarraTempo(barraTempo, passos.map((passo) => passo.minutos_estimados));
  }

  function itemDoPasso(passo, indice) {
    const item = document.createElement("li");
    item.className = "passo";
    item.dataset.id = passo.id;

    item.append(criarElemento(`
      <div class="passo-linha">
        <textarea class="passo-texto" rows="1" maxlength="255" autocomplete="off" enterkeyhint="done"></textarea>
        <label class="minutos">
          <input class="passo-minutos" type="number" inputmode="numeric" min="1" max="120">
          <span>${t("comum.min")}</span>
        </label>
      </div>
      <div class="passo-acoes acoes-ordenar">
        <button class="botao-icone" type="button" data-acao="subir">${icone("subir")}</button>
        <button class="botao-icone" type="button" data-acao="descer">${icone("descer")}</button>
        <button class="botao-icone" type="button" data-acao="apagar">${icone("fechar")}</button>
      </div>
    `));

    const texto = item.querySelector(".passo-texto");
    const minutos = item.querySelector(".passo-minutos");
    texto.value = passo.texto;
    minutos.value = passo.minutos_estimados;

    const numero = indice + 1;
    texto.setAttribute("aria-label", t("tarefa.passo", numero));
    minutos.setAttribute("aria-label", t("tarefa.minutosPasso", numero));
    item.querySelector('[data-acao="subir"]').setAttribute("aria-label", t("tarefa.subirPasso", numero));
    item.querySelector('[data-acao="descer"]').setAttribute("aria-label", t("tarefa.descerPasso", numero));
    item.querySelector('[data-acao="apagar"]').setAttribute("aria-label", t("tarefa.apagarPasso", numero));

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

    if (!temPassos) ordenando = false;
    botaoOrdenar.textContent = ordenando ? t("comum.listo") : t("comum.ordenar");
    botaoOrdenar.setAttribute("aria-pressed", String(ordenando));
    raiz.classList.toggle("ordenando", ordenando);

    lista.replaceChildren(...passos.map(itemDoPasso));
    lista.querySelectorAll(".passo-texto").forEach(ajustarAltura);
    desenharTempo();
    desenharGuia(temPassos);
  }

  // ---- H6.2: dicas da primeira tarefa guiada ----

  function desenharGuia(temPassos) {
    if (!emGuia) return;

    guiaEtapa.hidden = false;
    guia.hidden = false;
    guiaEtapa.textContent = "2 de 3";
    guia.textContent = temPassos
      ? t("tarefa.guiaComPassos")
      : t("tarefa.guiaSemPassos");
    botaoListo.hidden = true;
    botaoGuia.hidden = !temPassos;
  }

  botaoGuia.addEventListener("click", async () => {
    avisar("");
    botaoGuia.disabled = true;
    try {
      await planejarHoje([tarefaId]);
    } catch (erro) {
      // Se já estava em Hoy, segue igual; outro erro, avisa.
      if (erro.detalhe !== "Essa tarefa já está em Hoje ou foi concluída.") {
        avisar(erro.message);
        botaoGuia.disabled = false;
        return;
      }
    }
    navegar(`/foco/${tarefaId}`);
  });

  // O campo do passo cresce com o texto: nada fica cortado.
  function ajustarAltura(campo) {
    campo.style.height = "auto";
    campo.style.height = `${campo.scrollHeight}px`;
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
      mostrarTitulo(tarefa.titulo);
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
      } else if (erro.detalhe === null) {
        // Falha de conexão (não da IA): o botão volta, para tentar de novo.
        desenhar();
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

    // Um passo é uma linha só: quebras coladas viram espaço.
    const texto = item.querySelector(".passo-texto").value.replace(/\s*\n\s*/g, " ").trim();
    const campoMinutos = item.querySelector(".passo-minutos");
    const minutos = campoMinutos.value === "" ? MINUTOS_PADRAO : Number(campoMinutos.value);

    if (texto === passo.texto && minutos === passo.minutos_estimados) return;

    if (!texto) {
      // Texto apagado: volta ao anterior. Para tirar o passo, existe o ✕.
      item.querySelector(".passo-texto").value = passo.texto;
      ajustarAltura(item.querySelector(".passo-texto"));
      avisar(t("tarefa.comoTirar"));
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
    if (evento.key === "Enter" && evento.target.matches("input, textarea")) {
      evento.preventDefault();
      evento.target.blur();
    }
  });

  lista.addEventListener("input", (evento) => {
    if (evento.target.matches(".passo-texto")) ajustarAltura(evento.target);
  });

  botaoOrdenar.addEventListener("click", () => {
    ordenando = !ordenando;
    desenhar();
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
  // Volta para onde a pessoa estava (Hoy ou Bandeja).
  function voltar() {
    if (history.length > 1) history.back();
    else navegar(TELA_INICIAL);
  }

  // ---- Título: editar como um passo; Enter ou sair do campo guarda ----

  async function guardarTitulo() {
    const novo = titulo.value.replace(/\s*\n\s*/g, " ").trim();
    if (novo === tituloGuardado) return;

    if (!novo) {
      mostrarTitulo(tituloGuardado);
      avisar(t("tarefa.tituloVazio"));
      return;
    }

    avisar("");
    const anterior = tituloGuardado;
    mostrarTitulo(novo);
    esquecerCopias();

    try {
      await renomearTarefa(tarefaId, novo);
    } catch (erro) {
      mostrarTitulo(anterior);
      avisar(erro.message);
    }
  }

  titulo.addEventListener("input", () => ajustarAltura(titulo));
  titulo.addEventListener("change", guardarTitulo);
  titulo.addEventListener("keydown", (evento) => {
    if (evento.key === "Enter" && !evento.isComposing) {
      evento.preventDefault();
      titulo.blur();
    }
  });

  // As cópias de Hoy e da Bandeja mostram o título antigo: as telas buscam de novo.
  function esquecerCopias() {
    const id = obterUsuario().id;
    try {
      localStorage.removeItem(`iamigo.hoje.${id}`);
      localStorage.removeItem(`iamigo.bandeja.${id}`);
    } catch {
      // Nada a fazer.
    }
  }

  // ---- Apagar a tarefa (com confirmação) ----

  raiz.querySelector('[data-acao="apagar-tarefa"]').addEventListener("click", async (evento) => {
    if (!window.confirm(t("tarefa.confirmarApagar"))) return;

    const botao = evento.currentTarget;
    botao.disabled = true;
    avisar("");

    try {
      await excluirTarefa(tarefaId);
      esquecerCopias();
      if (lerFoco()?.tarefaId === tarefaId) limparFoco();
      navegar(TELA_INICIAL);
    } catch (erro) {
      botao.disabled = false;
      avisar(erro.message);
    }
  });

  raiz.querySelector('[data-acao="voltar"]').addEventListener("click", voltar);
  botaoListo.addEventListener("click", voltar);

  carregar();
}
