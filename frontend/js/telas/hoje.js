// Épica 3 · Planear hoy. Tela inicial: Ahora, Después, tempo do dia e a Bandeja embaixo.
// H3.1 "+ Hoy" · H3.3 Ahora e Después com tempo total · H3.4 reordenar · H3.6 dia vazio guia.
// O limite (H3.5) muda em "Elegir tareas para hoy", onde ele importa.
//
// Para a tela ficar leve: os botões de ordenar só aparecem no modo "Ordenar",
// e a Bandeja embaixo mostra só as 3 mais recentes.
//
// Como as outras telas: abre com a cópia local, atualiza em silêncio, e cada
// mudança aparece na hora; se o servidor recusar, volta e mostra um aviso.

import { dataLocal, listarHoje, obterDiaPendente, reordenarHoje, tirarDeHoje } from "../api.js";
import { cabecalho, navegacao } from "../componentes.js";
import { criarElemento } from "../html.js";
import { lerFoco, limparFoco } from "../foco-estado.js";
import { precisaDaGuia, tarefaDaGuia } from "../guia.js";
import { criarListaBandeja } from "../lista-bandeja.js";
import { navegar } from "../roteador.js";
import { obterUsuario } from "../sessao.js";
import { criarAnel } from "../anel.js";
import { formatarTempoCurto, formatarTempoTotal } from "../tempo.js";
import { t } from "../i18n.js";
import { icone, itemFeito } from "../icones.js";

// ---- Cópia local do dia ----

function chaveCache() {
  return `iamigo.hoje.${obterUsuario().id}`;
}

function lerCache() {
  try {
    const copia = JSON.parse(localStorage.getItem(chaveCache()));
    // Só vale para o mesmo dia: amanhã, Hoy começa do zero.
    return copia?.data === dataLocal() && Array.isArray(copia.tarefas) ? copia.tarefas : null;
  } catch {
    return null;
  }
}

// O modo foco usa para saber se a tarefa terminada era a última do dia.
export function lerCacheHoje() {
  return lerCache();
}

function salvarCache(tarefas) {
  try {
    localStorage.setItem(chaveCache(), JSON.stringify({ data: dataLocal(), tarefas }));
  } catch {
    // Sem armazenamento: só abre um pouco mais devagar.
  }
}

// ---- H5.4: o dia anterior ficou sem fechar? Pergunta uma vez por dia. ----

function chaveDiaVerificado() {
  return `iamigo.dia-verificado.${obterUsuario().id}`;
}

async function verificarDiaPendente(aindaNaTela) {
  try {
    if (localStorage.getItem(chaveDiaVerificado()) === dataLocal()) return;
  } catch {
    // Sem armazenamento: pergunta sempre.
  }

  try {
    const pendente = await obterDiaPendente();
    try {
      localStorage.setItem(chaveDiaVerificado(), dataLocal());
    } catch {
      // Nada a fazer.
    }
    // "2026-11-11" → "#/cerrar/20261111" (o roteador só aceita números).
    if (pendente && aindaNaTela()) navegar(`/cerrar/${pendente.replaceAll("-", "")}`);
  } catch {
    // Sem conexão: tenta na próxima vez.
  }
}

export function telaHoje(raiz) {
  // H6.1: conta nova (ou que não terminou a guia) começa pela bienvenida.
  if (precisaDaGuia() && tarefaDaGuia() === null) {
    navegar("/bienvenida");
    return;
  }

  raiz.append(cabecalho(), criarElemento(`
    <div class="titulo-com-acao">
      <h1>${t("hoje.titulo")}<span class="tempo-dia" hidden></span></h1>
      <button class="botao-texto" type="button" data-acao="ordenar" aria-pressed="false" hidden>${t("comum.ordenar")}</button>
    </div>

    <section class="retomar" aria-labelledby="titulo-retomar" hidden>
      <h2 id="titulo-retomar">${t("hoje.retomar")}</h2>
      <p class="retomar-passo"></p>
      <div class="retomar-acoes">
        <a class="botao" data-acao="seguir">${t("comum.seguir")}</a>
        <button class="botao-texto" type="button" data-acao="ahora-no">${t("hoje.agoraNao")}</button>
      </div>
    </section>

    <div class="progresso-dia" hidden>
      <p class="progresso-dia-texto"></p>
    </div>

    <p class="dia-vazio subtitulo" hidden>${t("hoje.diaVazio")}</p>

    <section class="ahora" aria-labelledby="titulo-ahora" hidden>
      <h2 id="titulo-ahora">${t("hoje.ahora")}</h2>
      <ol class="lista-dia"></ol>
    </section>

    <section class="despues" aria-labelledby="titulo-despues" hidden>
      <h2 id="titulo-despues">${t("hoje.despues")}</h2>
      <ol class="lista-dia"></ol>
    </section>

    <p class="confirmacao" role="status"></p>
    <p class="aviso" role="alert"></p>

    <section class="dia-completo" hidden>
      <h2>${t("hoje.completo")}</h2>
      <a class="botao" href="#/cerrar">${t("hoje.terminarDia")}</a>
    </section>

    <a class="botao" href="#/elegir" data-acao="elegir">${t("hoje.elegir")}</a>
    <a class="link-secundario" href="#/cerrar" data-acao="cerrar" hidden>${t("hoje.terminarDia")}</a>

    <section class="hecho" aria-labelledby="titulo-hecho" hidden>
      <h2 id="titulo-hecho">${t("hoje.jaFez")}</h2>
      <ul class="lista-hecho"></ul>
    </section>
  `));

  const botaoOrdenar = raiz.querySelector('[data-acao="ordenar"]');
  const tempoDia = raiz.querySelector(".tempo-dia");
  // Anel: tarefas feitas / tarefas do dia (o tempo já está junto ao título).
  const progressoDia = raiz.querySelector(".progresso-dia");
  const progressoTexto = raiz.querySelector(".progresso-dia-texto");
  const anel = criarAnel();
  progressoDia.prepend(anel.elemento);
  const diaVazio = raiz.querySelector(".dia-vazio");
  const secaoAhora = raiz.querySelector(".ahora");
  const secaoDespues = raiz.querySelector(".despues");
  const listaAhora = secaoAhora.querySelector(".lista-dia");
  const listaDespues = secaoDespues.querySelector(".lista-dia");
  const confirmacao = raiz.querySelector(".confirmacao");
  const aviso = raiz.querySelector(".aviso");
  const botaoElegir = raiz.querySelector('[data-acao="elegir"]');
  const secaoHecho = raiz.querySelector(".hecho");
  const listaHecho = raiz.querySelector(".lista-hecho");
  const diaCompleto = raiz.querySelector(".dia-completo");
  const linkCerrar = raiz.querySelector('[data-acao="cerrar"]');

  // As tarefas do dia como estão no servidor, na ordem.
  let tarefas = [];
  let ordenando = false;
  let tempoConfirmacao = null;

  const pendentes = () => tarefas.filter((tarefa) => !tarefa.concluida);

  function confirmar(texto) {
    confirmacao.textContent = texto;
    clearTimeout(tempoConfirmacao);
    tempoConfirmacao = setTimeout(() => { confirmacao.textContent = ""; }, 2500);
  }

  // ---- Desenho ----

  function itemDoDia(tarefa, indice, total) {
    const item = document.createElement("li");
    item.className = indice === 0 ? "tarefa-dia cartao-ahora" : "tarefa-dia";
    item.dataset.id = tarefa.id;

    item.append(criarElemento(`
      <a class="tarefa-link"></a>
      <p class="minutos-dia"></p>
      <div class="passo-acoes acoes-ordenar">
        <button class="botao-icone" type="button" data-acao="subir">${icone("subir")}</button>
        <button class="botao-icone" type="button" data-acao="descer">${icone("descer")}</button>
        <button class="botao-texto" type="button" data-acao="quitar">${t("hoje.quitar")}</button>
      </div>
    `));

    const link = item.querySelector(".tarefa-link");
    link.href = `#/tarefa/${tarefa.id}`;
    link.textContent = tarefa.titulo;
    item.querySelector(".minutos-dia").textContent = `${tarefa.minutos_restantes} min`;

    // H4.1: "Empezar" abre o modo foco; é a ação principal de Hoy.
    if (indice === 0) {
      const empezar = document.createElement("a");
      empezar.className = "botao botao-empezar";
      empezar.href = `#/foco/${tarefa.id}`;
      empezar.textContent = t("comum.empezar");
      empezar.setAttribute("aria-label", t("hoje.empezarRotulo", tarefa.titulo));
      item.querySelector(".passo-acoes").before(empezar);
    }

    const subir = item.querySelector('[data-acao="subir"]');
    const descer = item.querySelector('[data-acao="descer"]');
    subir.disabled = indice === 0;
    descer.disabled = indice === total - 1;
    subir.setAttribute("aria-label", t("comum.subir", tarefa.titulo));
    descer.setAttribute("aria-label", t("comum.descer", tarefa.titulo));
    item.querySelector('[data-acao="quitar"]').setAttribute("aria-label", t("hoje.quitarRotulo", tarefa.titulo));

    return item;
  }

  function desenhar() {
    const lista = pendentes();
    const concluidas = tarefas.filter((tarefa) => tarefa.concluida);
    const temPlano = lista.length > 0;

    listaAhora.replaceChildren(...lista.slice(0, 1).map((t) => itemDoDia(t, 0, lista.length)));
    listaDespues.replaceChildren(...lista.slice(1).map((t, i) => itemDoDia(t, i + 1, lista.length)));
    secaoAhora.hidden = !temPlano;
    secaoDespues.hidden = lista.length < 2;

    // Modo "Ordenar": só aparece com tarefas, e sai sozinho se o dia ficar vazio.
    if (!temPlano) ordenando = false;
    botaoOrdenar.hidden = !temPlano;
    botaoOrdenar.textContent = ordenando ? t("comum.listo") : t("comum.ordenar");
    botaoOrdenar.setAttribute("aria-pressed", String(ordenando));
    raiz.classList.toggle("ordenando", ordenando);

    // H3.6: dia sem plano não fica vazio; "Elegir" vira a ação principal.
    // Com plano, vira um link discreto: o maior da tela é sempre "Ahora".
    // H5: com tudo feito, a ação principal passa a ser fechar o dia.
    const tudoFeito = !temPlano && concluidas.length > 0;
    diaVazio.hidden = temPlano || tudoFeito;
    diaCompleto.hidden = !tudoFeito;
    linkCerrar.hidden = !temPlano;
    botaoElegir.className = temPlano || tudoFeito ? "link-secundario" : "botao";
    botaoElegir.textContent = temPlano || tudoFeito ? t("hoje.elegirMais") : t("hoje.elegir");

    const total = lista.reduce((soma, tarefa) => soma + tarefa.minutos_restantes, 0);
    // H3.3: o tempo do dia junto ao título; embaixo, o anel com o que já foi feito.
    tempoDia.hidden = !temPlano;
    tempoDia.textContent = ` · ${formatarTempoCurto(total)}`;
    tempoDia.setAttribute("aria-label", t("hoje.tempoRotulo", formatarTempoTotal(total)));

    const doDia = lista.length + concluidas.length;
    progressoDia.hidden = doDia === 0;
    progressoTexto.textContent = t("hoje.progresso", concluidas.length, doDia);
    anel.atualizar(doDia === 0 ? 0 : concluidas.length / doDia);

    listaHecho.replaceChildren(...concluidas.map((tarefa) => itemFeito(tarefa.titulo)));
    secaoHecho.hidden = concluidas.length === 0;
  }

  // ---- H4.6: retomar o modo foco ----

  const secaoRetomar = raiz.querySelector(".retomar");

  function desenharRetomar() {
    const foco = lerFoco();
    const tarefa = foco && tarefas.find((t) => t.id === foco.tarefaId);

    // Se a tarefa já foi concluída (ex.: em outra aba), não há o que retomar.
    if (tarefa?.concluida) limparFoco();

    const mostrar = Boolean(foco) && !tarefa?.concluida;
    secaoRetomar.hidden = !mostrar;
    if (!mostrar) return;

    secaoRetomar.querySelector(".retomar-passo").textContent = foco.passoTexto;
    secaoRetomar.querySelector('[data-acao="seguir"]').href = `#/foco/${foco.tarefaId}`;
  }

  secaoRetomar.querySelector('[data-acao="ahora-no"]').addEventListener("click", () => {
    limparFoco();
    secaoRetomar.hidden = true;
  });

  async function carregar() {
    const copia = lerCache();
    if (copia) {
      tarefas = copia;
      desenhar();
    }
    desenharRetomar();

    try {
      tarefas = await listarHoje();
      salvarCache(tarefas);
      desenhar();
      desenharRetomar();
    } catch (erro) {
      if (!copia) aviso.textContent = erro.message;
    }
  }

  // ---- H3.4: reordenar e tirar de Hoy (no modo "Ordenar") ----

  botaoOrdenar.addEventListener("click", () => {
    ordenando = !ordenando;
    desenhar();
  });

  async function mover(tarefaId, deslocamento) {
    const lista = pendentes();
    const de = lista.findIndex((tarefa) => tarefa.id === tarefaId);
    const para = de + deslocamento;
    if (para < 0 || para >= lista.length) return;

    aviso.textContent = "";
    const anteriores = tarefas;
    [lista[de], lista[para]] = [lista[para], lista[de]];
    tarefas = [...lista, ...tarefas.filter((tarefa) => tarefa.concluida)];
    desenhar();

    // Mantém o foco na tarefa que se moveu (teclado e leitor de tela).
    raiz.querySelector(`.tarefa-dia[data-id="${tarefaId}"] [data-acao="${deslocamento < 0 ? "subir" : "descer"}"]`)?.focus();

    try {
      await reordenarHoje(lista.map((tarefa) => tarefa.id));
      salvarCache(tarefas);
    } catch (erro) {
      tarefas = anteriores;
      desenhar();
      aviso.textContent = erro.message;
    }
  }

  async function quitar(tarefaId) {
    aviso.textContent = "";
    const anteriores = tarefas;
    tarefas = tarefas.filter((tarefa) => tarefa.id !== tarefaId);
    desenhar();

    try {
      await tirarDeHoje(tarefaId);
      salvarCache(tarefas);
      confirmar(t("hoje.voltouBandeja"));
      bandeja.carregar();
    } catch (erro) {
      tarefas = anteriores;
      desenhar();
      aviso.textContent = erro.message;
    }
  }

  raiz.addEventListener("click", (evento) => {
    const botao = evento.target.closest(".tarefa-dia button[data-acao]");
    if (!botao) return;

    const tarefaId = Number(botao.closest(".tarefa-dia").dataset.id);
    if (botao.dataset.acao === "subir") mover(tarefaId, -1);
    if (botao.dataset.acao === "descer") mover(tarefaId, 1);
    if (botao.dataset.acao === "quitar") quitar(tarefaId);
  });

  // ---- Bandeja embaixo, só as 3 mais recentes, com "+ Hoy" (H3.1) ----

  const bandeja = criarListaBandeja({
    aviso,
    maximo: 3,
    textoVazia: t("bandeja.vazia"),
    aoPlanejar: () => {
      confirmar(t("comum.listaParaHoje"));
      carregar();
    },
  });

  raiz.append(bandeja.elemento, navegacao("hoje"));

  carregar();
  bandeja.carregar();
  verificarDiaPendente(() => raiz.contains(diaVazio));
}
