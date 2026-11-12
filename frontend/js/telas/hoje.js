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
import { desenharBarraTempo, formatarTempoTotal } from "../tempo.js";

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
      <h1>Hoy</h1>
      <button class="botao-texto" type="button" data-acao="ordenar" aria-pressed="false" hidden>Ordenar</button>
    </div>

    <section class="retomar" aria-labelledby="titulo-retomar" hidden>
      <h2 id="titulo-retomar">¿Seguimos donde quedaste?</h2>
      <p class="retomar-passo"></p>
      <div class="retomar-acoes">
        <a class="botao" data-acao="seguir">Seguir</a>
        <button class="botao-texto" type="button" data-acao="ahora-no">Ahora no</button>
      </div>
    </section>

    <div class="tempo-total" hidden>
      <p class="tempo-texto"></p>
      <div class="barra-tempo" aria-hidden="true"></div>
    </div>

    <p class="dia-vazio subtitulo" hidden>Elige una cosa de tu Bandeja para empezar.</p>

    <section class="ahora" aria-labelledby="titulo-ahora" hidden>
      <h2 id="titulo-ahora">Ahora</h2>
      <ol class="lista-dia"></ol>
    </section>

    <section class="despues" aria-labelledby="titulo-despues" hidden>
      <h2 id="titulo-despues">Después</h2>
      <ol class="lista-dia"></ol>
    </section>

    <p class="confirmacao" role="status"></p>
    <p class="aviso" role="alert"></p>

    <section class="dia-completo" hidden>
      <h2>¡Completaste todo lo de hoy!</h2>
      <a class="botao" href="#/cerrar">Terminar el día</a>
    </section>

    <a class="botao" href="#/elegir" data-acao="elegir">Elegir tareas para hoy</a>
    <a class="link-secundario" href="#/cerrar" data-acao="cerrar" hidden>Terminar el día</a>

    <section class="hecho" aria-labelledby="titulo-hecho" hidden>
      <h2 id="titulo-hecho">Ya hiciste hoy</h2>
      <ul class="lista-hecho"></ul>
    </section>
  `));

  const botaoOrdenar = raiz.querySelector('[data-acao="ordenar"]');
  const tempoTotal = raiz.querySelector(".tempo-total");
  const tempoTexto = raiz.querySelector(".tempo-texto");
  const barraTempo = raiz.querySelector(".barra-tempo");
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
        <button class="botao-icone" type="button" data-acao="subir">↑</button>
        <button class="botao-icone" type="button" data-acao="descer">↓</button>
        <button class="botao-texto" type="button" data-acao="quitar">Quitar</button>
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
      empezar.textContent = "Empezar";
      empezar.setAttribute("aria-label", `Empezar: ${tarefa.titulo}`);
      item.querySelector(".passo-acoes").before(empezar);
    }

    const subir = item.querySelector('[data-acao="subir"]');
    const descer = item.querySelector('[data-acao="descer"]');
    subir.disabled = indice === 0;
    descer.disabled = indice === total - 1;
    subir.setAttribute("aria-label", `Subir: ${tarefa.titulo}`);
    descer.setAttribute("aria-label", `Bajar: ${tarefa.titulo}`);
    item.querySelector('[data-acao="quitar"]').setAttribute("aria-label", `Quitar de Hoy: ${tarefa.titulo}`);

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
    botaoOrdenar.textContent = ordenando ? "Listo" : "Ordenar";
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
    botaoElegir.textContent = temPlano || tudoFeito ? "Elegir más tareas" : "Elegir tareas para hoy";

    const total = lista.reduce((soma, tarefa) => soma + tarefa.minutos_restantes, 0);
    tempoTotal.hidden = !temPlano;
    tempoTexto.textContent = `${formatarTempoTotal(total)} en total`;
    desenharBarraTempo(barraTempo, lista.map((tarefa) => tarefa.minutos_restantes));

    listaHecho.replaceChildren(...concluidas.map((tarefa) => {
      const item = document.createElement("li");
      item.textContent = `✓ ${tarefa.titulo}`;
      return item;
    }));
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
      confirmar("Volvió a tu Bandeja.");
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
    textoVazia: "Tu Bandeja está vacía.",
    aoPlanejar: () => {
      confirmar("Lista para hoy.");
      carregar();
    },
  });

  raiz.append(bandeja.elemento, navegacao("hoje"));

  carregar();
  bandeja.carregar();
  verificarDiaPendente(() => raiz.contains(diaVazio));
}
