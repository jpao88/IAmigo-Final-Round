// Épica 4 · Hacer (modo foco). Um passo por vez, com temporizador circular.
// H4.1 um passo · H4.2 Hecho e celebração · H4.3 +5 minutos · H4.4 Me atasqué
// H4.5 Pausar · H4.6 retomar (foco-estado.js) · H4.7 o fim do tempo não assusta.
//
// O temporizador vive só no front (recorrido): conta pela hora real, então não
// se atrasa se o celular bloquear a tela, e sobrevive a fechar a app.

import {
  concluirPasso, concluirTarefa, dividirPasso, listarPassos, obterTarefa,
} from "../api.js";
import { lerFoco, limparFoco, salvarFoco } from "../foco-estado.js";
import { tarefaDaGuia, terminarGuia } from "../guia.js";
import { criarElemento } from "../html.js";
import { tituloEmCache } from "../lista-bandeja.js";
import { navegar } from "../roteador.js";
import { alternarSom, somLigado, somPasso, somTarefa } from "../som.js";
import { lerCacheHoje } from "./hoje.js";

const MINUTO = 60 * 1000;
const MINUTOS_SEM_PASSOS = 10;
const RAIO = 88;
const CIRCUNFERENCIA = 2 * Math.PI * RAIO;

const FRASES_PASSO = ["¡Bien hecho!", "¡Un paso menos!", "¡Así se hace!", "¡Vas muy bien!", "¡Eso es!"];

const esperar = (ms) => new Promise((resolver) => { setTimeout(resolver, ms); });

// "12 min", "Menos de 1 min": minutos, não segundos, para não pressionar.
function textoRestante(ms) {
  if (ms <= 0) return "Tómate tu tiempo";
  const minutos = Math.ceil(ms / MINUTO);
  return minutos <= 1 ? "Menos de 1 min" : `${minutos} min`;
}

export function telaFoco(raiz, { id: tarefaId }) {
  raiz.classList.add("tela-foco");
  raiz.append(criarElemento(`
    <header class="cabecalho">
      <a class="botao-texto" href="#/hoje">← Hoy</a>
      <p class="progresso subtitulo"></p>
      <button class="botao-texto botao-som" type="button"></button>
    </header>

    <p class="titulo-foco subtitulo"></p>
    <p class="guia" role="status" hidden>3 de 3 · Haz solo este paso y toca «Hecho» al terminar.</p>

    <section class="foco" aria-live="polite">
      <p class="rotulo-foco">Tu paso ahora</p>
      <p class="passo-foco"></p>

      <div class="relogio" role="timer">
        <svg viewBox="0 0 200 200" aria-hidden="true">
          <circle class="relogio-fundo" cx="100" cy="100" r="${RAIO}"></circle>
          <circle class="relogio-tempo" cx="100" cy="100" r="${RAIO}"
            stroke-dasharray="${CIRCUNFERENCIA}" stroke-dashoffset="0"></circle>
        </svg>
        <p class="relogio-texto"></p>
      </div>
    </section>

    <p class="pensando" role="status" hidden>IAmigo está pensando…</p>
    <p class="aviso" role="alert"></p>

    <div class="acoes-foco">
      <button class="botao botao-hecho" type="button" data-acao="hecho">Hecho</button>
      <div class="acoes-foco-linha">
        <button class="botao botao-contorno" type="button" data-acao="mais5">+5 minutos</button>
        <button class="botao botao-contorno" type="button" data-acao="pausar">Pausar</button>
      </div>
      <button class="link-secundario" type="button" data-acao="atasquei">Me atasqué</button>
    </div>

    <div class="celebracao" role="status" hidden>
      <div class="celebracao-icone" aria-hidden="true">✓</div>
      <p class="celebracao-texto"></p>
      <p class="celebracao-detalhe subtitulo"></p>
      <button class="botao celebracao-seguir" type="button" hidden>Seguir</button>
    </div>

    <section class="foco-fim" hidden>
      <p>Esta tarea ya está terminada.</p>
      <a class="botao" href="#/hoje">Volver a Hoy</a>
    </section>
  `));

  const progresso = raiz.querySelector(".progresso");
  const tituloFoco = raiz.querySelector(".titulo-foco");
  const secaoFoco = raiz.querySelector(".foco");
  const passoFoco = raiz.querySelector(".passo-foco");
  const relogio = raiz.querySelector(".relogio");
  const relogioTempo = raiz.querySelector(".relogio-tempo");
  const relogioTexto = raiz.querySelector(".relogio-texto");
  const pensando = raiz.querySelector(".pensando");
  const aviso = raiz.querySelector(".aviso");
  const acoes = raiz.querySelector(".acoes-foco");
  const botaoPausar = raiz.querySelector('[data-acao="pausar"]');
  const celebracao = raiz.querySelector(".celebracao");
  const celebracaoTexto = raiz.querySelector(".celebracao-texto");
  const celebracaoDetalhe = raiz.querySelector(".celebracao-detalhe");
  const focoFim = raiz.querySelector(".foco-fim");
  const botaoSom = raiz.querySelector(".botao-som");
  const guia = raiz.querySelector(".guia");
  const botaoSeguir = raiz.querySelector(".celebracao-seguir");

  // H6.2: primeira tarefa guiada; o primeiro "Hecho" encerra a guia (H6.3).
  let emGuia = tarefaDaGuia() === tarefaId;
  guia.hidden = !emGuia;

  function desenharBotaoSom() {
    const ligado = somLigado();
    botaoSom.textContent = ligado ? "🔔" : "🔕";
    botaoSom.setAttribute("aria-label", ligado ? "Silenciar sonidos" : "Activar sonidos");
    botaoSom.setAttribute("aria-pressed", String(!ligado));
  }
  desenharBotaoSom();
  botaoSom.addEventListener("click", () => {
    alternarSom();
    desenharBotaoSom();
  });

  let titulo = tituloEmCache(tarefaId) ?? "";
  // Passos visíveis da tarefa, na ordem. Sem passos: um passo "virtual" com o título.
  let passos = [];
  let atual = null;
  let ocupado = false;

  // Temporizador: com ele rodando, o que vale é fimEm; pausado, vale restanteMs.
  let totalMs = 0;
  let restanteMs = 0;
  let fimEm = null;
  let pausado = false;
  let ultimoGuardado = 0;

  tituloFoco.textContent = titulo;

  const naTela = () => raiz.contains(secaoFoco);

  // ---- Temporizador ----

  function calcularRestante() {
    return fimEm === null ? restanteMs : Math.max(fimEm - Date.now(), 0);
  }

  function guardarEstado() {
    if (!atual) return;
    salvarFoco({
      tarefaId, titulo,
      passoId: atual.id, passoTexto: atual.texto,
      restanteMs: calcularRestante(), totalMs, pausado,
    });
    ultimoGuardado = Date.now();
  }

  function desenharRelogio() {
    const restante = calcularRestante();
    const acabou = restante <= 0;

    // Princípio "O tempo se vê": o anel se esvazia. Em zero (H4.7) fica cheio,
    // numa cor calma, sem alarme nem vermelho.
    const fracao = acabou ? 1 : restante / totalMs;
    relogioTempo.setAttribute("stroke-dashoffset", String(CIRCUNFERENCIA * (1 - fracao)));
    relogio.classList.toggle("relogio-acabou", acabou);
    relogio.classList.toggle("relogio-pausado", pausado);
    relogioTexto.textContent = pausado && !acabou ? `En pausa · ${textoRestante(restante)}` : textoRestante(restante);
    acoes.classList.toggle("tempo-acabou", acabou);

    botaoPausar.textContent = pausado ? "Seguir" : "Pausar";
    botaoPausar.disabled = acabou;
  }

  function iniciarRelogio(minutos, salvo = null) {
    totalMs = salvo?.totalMs ?? minutos * MINUTO;
    pausado = salvo?.pausado ?? false;
    restanteMs = salvo?.restanteMs ?? totalMs;
    fimEm = pausado ? null : Date.now() + restanteMs;
    desenharRelogio();
    guardarEstado();
  }

  const intervalo = setInterval(() => {
    if (!naTela()) {
      clearInterval(intervalo);
      return;
    }
    desenharRelogio();
    // Guarda de vez em quando, para retomar perto de onde parou (H4.6).
    if (Date.now() - ultimoGuardado > 10_000) guardarEstado();
  }, 1000);

  // Ao esconder a aba ou fechar a app, guarda o tempo exato.
  function aoSair() {
    if (naTela()) guardarEstado();
  }
  document.addEventListener("visibilitychange", aoSair);
  window.addEventListener("pagehide", aoSair);
  window.addEventListener("hashchange", function sair() {
    aoSair();
    document.removeEventListener("visibilitychange", aoSair);
    window.removeEventListener("pagehide", aoSair);
    window.removeEventListener("hashchange", sair);
  });

  // ---- Passo atual ----

  function pendentes() {
    return passos.filter((passo) => !passo.concluido);
  }

  function mostrarPasso(salvo = null) {
    const lista = pendentes();
    atual = lista[0] ?? null;

    if (!atual) {
      secaoFoco.hidden = true;
      acoes.hidden = true;
      focoFim.hidden = false;
      limparFoco();
      return;
    }

    passoFoco.textContent = atual.texto;
    const feitos = passos.length - lista.length;
    progresso.textContent = passos.length > 1 ? `Paso ${feitos + 1} de ${passos.length}` : "";

    iniciarRelogio(atual.minutos_estimados, salvo);
  }

  async function carregar() {
    try {
      const [tarefa, todos] = await Promise.all([obterTarefa(tarefaId), listarPassos(tarefaId)]);
      titulo = tarefa.titulo;
      tituloFoco.textContent = titulo;

      if (tarefa.concluida) {
        passos = [];
        mostrarPasso();
        return;
      }

      passos = todos.filter((passo) => !passo.substituido);

      // Sem passos: a tarefa inteira é um passo só (recorrido).
      if (passos.length === 0) {
        passos = [{ id: null, texto: tarefa.titulo, minutos_estimados: MINUTOS_SEM_PASSOS, concluido: false }];
      }

      // H4.6: se parou neste mesmo passo, continua com o tempo que faltava.
      const salvo = lerFoco();
      const mesmoPasso = salvo?.tarefaId === tarefaId && salvo.passoId === pendentes()[0]?.id;
      mostrarPasso(mesmoPasso ? salvo : null);
    } catch (erro) {
      aviso.textContent = erro.message;
    }
  }

  // ---- H4.2: Hecho e celebração ----

  async function celebrar(texto, detalhe, duracao) {
    celebracaoTexto.textContent = texto;
    celebracaoDetalhe.textContent = detalhe;
    celebracao.hidden = false;
    await esperar(duracao);
  }

  // Com um botão, a celebração espera a pessoa (há uma frase para ler).
  function esperarToque() {
    botaoSeguir.hidden = false;
    botaoSeguir.focus();
    return new Promise((resolver) => {
      botaoSeguir.addEventListener("click", () => {
        botaoSeguir.hidden = true;
        resolver();
      }, { once: true });
    });
  }

  // H5: se era a última tarefa pendente de Hoy, vai direto ao resumo do dia.
  function destinoDepoisDaTarefa() {
    const doDia = lerCacheHoje();
    if (!doDia?.some((tarefa) => tarefa.id === tarefaId)) return "/hoje";
    const outrasPendentes = doDia.some((tarefa) => tarefa.id !== tarefaId && !tarefa.concluida);
    return outrasPendentes ? "/hoje" : "/cerrar";
  }

  async function hecho() {
    if (ocupado || !atual) return;
    ocupado = true;
    aviso.textContent = "";

    const passo = atual;
    const frase = FRASES_PASSO[(passos.length - pendentes().length) % FRASES_PASSO.length];
    const pedido = passo.id === null
      ? concluirTarefa(tarefaId).then(() => ({ tarefa_concluida: true }))
      : concluirPasso(tarefaId, passo.id);

    somPasso();

    try {
      // A celebração começa na hora; o servidor responde enquanto isso.
      const [resultado] = await Promise.all([pedido, celebrar(frase, "", 1200)]);
      passo.concluido = true;

      // H6.2 e H6.3: o primeiro passo da tarefa guiada fecha a guia com uma frase.
      if (emGuia) {
        emGuia = false;
        guia.hidden = true;
        terminarGuia();
        await celebrar("¡Así funciona cada día!", "Anota, divide, elige y hazlo, un paso a la vez.", 0);
        await esperarToque();
      }

      if (resultado.tarefa_concluida) {
        limparFoco();
        somTarefa();
        await celebrar("¡Terminaste!", titulo, 2200);
        navegar(destinoDepoisDaTarefa());
        return;
      }

      celebracao.hidden = true;
      mostrarPasso();
    } catch (erro) {
      celebracao.hidden = true;
      aviso.textContent = erro.message;
    } finally {
      ocupado = false;
    }
  }

  // ---- H4.3 e H4.5: +5 minutos e pausar ----

  function maisCinco() {
    const restante = calcularRestante();
    restanteMs = restante + 5 * MINUTO;
    // O anel mede o que falta contra o total; se passar do total, o total cresce.
    totalMs = Math.max(totalMs, restanteMs);
    // Se o tempo tinha acabado, volta a contar.
    if (restante <= 0) pausado = false;
    fimEm = pausado ? null : Date.now() + restanteMs;
    desenharRelogio();
    guardarEstado();
  }

  function alternarPausa() {
    if (pausado) {
      pausado = false;
      fimEm = Date.now() + restanteMs;
    } else {
      restanteMs = calcularRestante();
      pausado = true;
      fimEm = null;
    }
    desenharRelogio();
    guardarEstado();
  }

  // ---- H4.4: Me atasqué ----

  async function meAtasquei() {
    if (ocupado || !atual) return;

    if (atual.id === null) {
      // Tarefa sem passos: primeiro é preciso dividir a tarefa, na tela dela.
      aviso.textContent = "Divide la tarea en pasos primero.";
      return;
    }

    ocupado = true;
    aviso.textContent = "";
    pensando.hidden = false;
    acoes.classList.add("acoes-esperando");

    try {
      const novos = await dividirPasso(tarefaId, atual.id);
      const indice = passos.indexOf(atual);
      passos.splice(indice, 1, ...novos);
      mostrarPasso();
    } catch (erro) {
      aviso.textContent = erro.message;
    } finally {
      pensando.hidden = true;
      acoes.classList.remove("acoes-esperando");
      ocupado = false;
    }
  }

  acoes.addEventListener("click", (evento) => {
    const acao = evento.target.closest("[data-acao]")?.dataset.acao;
    if (acao === "hecho") hecho();
    if (acao === "mais5") maisCinco();
    if (acao === "pausar") alternarPausa();
    if (acao === "atasquei") meAtasquei();
  });

  carregar();
}
