// Épica 5 · Cerrar el día.
// H5.1 só o que se conseguiu · H5.2 decidir o pendente · H5.3 "Terminar el día"
// H5.4 o mesmo resumo para um dia anterior que ficou sem fechar (#/cerrar/20261111).
//
// Nunca fala do que faltou como fracasso: o pendente aparece como uma decisão.

import { dataLocal, fecharDia, obterResumoDia, planejarHoje, tirarDeHoje } from "../api.js";
import { criarElemento } from "../html.js";
import { navegar } from "../roteador.js";
import { obterUsuario } from "../sessao.js";
import { somTarefa } from "../som.js";

const esperar = (ms) => new Promise((resolver) => { setTimeout(resolver, ms); });

// 20261111 → "2026-11-11"
function dataDoParametro(numero) {
  const texto = String(numero);
  return `${texto.slice(0, 4)}-${texto.slice(4, 6)}-${texto.slice(6, 8)}`;
}

function paraDate(data) {
  const [ano, mes, dia] = data.split("-").map(Number);
  return new Date(ano, mes - 1, dia);
}

function somarDias(data, dias) {
  const resultado = paraDate(data);
  resultado.setDate(resultado.getDate() + dias);
  return dataLocal(resultado);
}

// "Hoy", "Ayer" ou "El martes 11".
function nomeDoDia(data) {
  if (data === dataLocal()) return "Hoy";
  if (data === somarDias(dataLocal(), -1)) return "Ayer";
  const texto = paraDate(data).toLocaleDateString("es", { weekday: "long", day: "numeric" });
  return `El ${texto.replace(",", "")}`;
}

function plural(quantidade, singular, pluralTexto) {
  return `${quantidade} ${quantidade === 1 ? singular : pluralTexto}`;
}

// H5.1: "Hoy completaste 9 pasos y 2 tareas." Sem nada feito, sem reproche.
function fraseDoResumo(quando, passos, tarefas) {
  const partes = [];
  if (passos > 0) partes.push(plural(passos, "paso", "pasos"));
  if (tarefas > 0) partes.push(plural(tarefas, "tarea", "tareas"));

  if (partes.length === 0) return `${quando} fue un día tranquilo. Cerrarlo también cuenta.`;
  return `${quando} completaste ${partes.join(" y ")}.`;
}

// As cópias locais de Hoy e da Bandeja ficaram velhas: as telas buscam de novo.
function esquecerCopias() {
  const id = obterUsuario().id;
  try {
    localStorage.removeItem(`iamigo.hoje.${id}`);
    localStorage.removeItem(`iamigo.bandeja.${id}`);
  } catch {
    // Nada a fazer.
  }
}

export function telaCerrar(raiz, { dia } = {}) {
  const data = dia ? dataDoParametro(dia) : dataLocal();
  const ehHoje = data === dataLocal();
  // Para um dia que já passou, "mañana" é hoje.
  const dataSeguinte = ehHoje ? somarDias(data, 1) : dataLocal();
  const textoAdiar = ehHoje ? "Hacerla mañana" : "Hacerla hoy";

  raiz.append(criarElemento(`
    <header class="cabecalho">
      <a class="botao-texto" href="#/hoje">← Hoy</a>
    </header>

    <section class="resumo-dia" aria-live="polite">
      <div class="celebracao-icone" aria-hidden="true">✓</div>
      <h1 class="resumo-frase"></h1>
    </section>

    <ul class="lista-hecho"></ul>

    <section class="pendentes-dia" aria-labelledby="titulo-pendentes" hidden>
      <h2 id="titulo-pendentes">¿Qué hacemos con estas?</h2>
      <p class="subtitulo">Lo que no decidas vuelve a tu Bandeja.</p>
      <ul class="lista-pendentes"></ul>
    </section>

    <p class="confirmacao" role="status"></p>
    <p class="aviso" role="alert"></p>

    <button class="botao" type="button" data-acao="fechar" hidden></button>

    <div class="celebracao" role="status" hidden>
      <div class="celebracao-icone" aria-hidden="true">🌙</div>
      <p class="celebracao-texto">Día cerrado</p>
      <p class="celebracao-detalhe subtitulo">Descansa, te lo ganaste.</p>
    </div>
  `));

  const frase = raiz.querySelector(".resumo-frase");
  const listaHecho = raiz.querySelector(".lista-hecho");
  const secaoPendentes = raiz.querySelector(".pendentes-dia");
  const listaPendentes = raiz.querySelector(".lista-pendentes");
  const confirmacao = raiz.querySelector(".confirmacao");
  const aviso = raiz.querySelector(".aviso");
  const botaoFechar = raiz.querySelector('[data-acao="fechar"]');
  const celebracao = raiz.querySelector(".celebracao");

  let pendentes = [];
  let fechado = false;

  // ---- Desenho ----

  function desenharPendentes() {
    listaPendentes.replaceChildren(...pendentes.map((tarefa) => {
      const item = document.createElement("li");
      item.className = "pendente-dia";
      item.dataset.id = tarefa.id;
      item.append(criarElemento(`
        <p class="pendente-titulo"></p>
        <div class="pendente-acoes">
          <button class="botao botao-contorno" type="button" data-acao="adiar"></button>
          <button class="botao-texto" type="button" data-acao="guardar">Guardarla sin fecha</button>
        </div>
      `));
      item.querySelector(".pendente-titulo").textContent = tarefa.titulo;
      const adiar = item.querySelector('[data-acao="adiar"]');
      adiar.textContent = textoAdiar;
      adiar.setAttribute("aria-label", `${textoAdiar}: ${tarefa.titulo}`);
      item.querySelector('[data-acao="guardar"]').setAttribute("aria-label", `Guardarla sin fecha: ${tarefa.titulo}`);
      return item;
    }));
    secaoPendentes.hidden = pendentes.length === 0;
  }

  function desenhar(resumo) {
    frase.textContent = fraseDoResumo(nomeDoDia(data), resumo.passos_concluidos, resumo.tarefas_concluidas);

    listaHecho.replaceChildren(...resumo.concluidas.map((tarefa) => {
      const item = document.createElement("li");
      item.textContent = `✓ ${tarefa.titulo}`;
      return item;
    }));

    pendentes = resumo.pendentes;
    fechado = resumo.fechado;
    desenharPendentes();

    botaoFechar.hidden = false;
    botaoFechar.textContent = fechado ? "Volver a Hoy" : ehHoje ? "Terminar el día" : "Listo";
  }

  async function carregar() {
    try {
      desenhar(await obterResumoDia(data));
    } catch (erro) {
      aviso.textContent = erro.message;
    }
  }

  // ---- H5.2: decidir o pendente, uma tarefa por vez ----

  function mensagemDeErro(erro) {
    if (erro.detalhe === "Hoje já está cheio.") {
      return `${ehHoje ? "Mañana" : "Hoy"} ya está completo. Guárdala sin fecha o cambia el límite en Elegir.`;
    }
    return erro.message;
  }

  async function decidir(tarefaId, acao) {
    aviso.textContent = "";
    const anteriores = pendentes;
    pendentes = pendentes.filter((tarefa) => tarefa.id !== tarefaId);
    desenharPendentes();

    try {
      if (acao === "adiar") await planejarHoje([tarefaId], dataSeguinte);
      else await tirarDeHoje(tarefaId);
      esquecerCopias();
      confirmacao.textContent = acao === "adiar"
        ? (ehHoje ? "Lista para mañana." : "Lista para hoy.")
        : "Guardada en tu Bandeja.";
    } catch (erro) {
      pendentes = anteriores;
      desenharPendentes();
      aviso.textContent = mensagemDeErro(erro);
    }
  }

  listaPendentes.addEventListener("click", (evento) => {
    const botao = evento.target.closest("button[data-acao]");
    if (!botao) return;
    decidir(Number(botao.closest(".pendente-dia").dataset.id), botao.dataset.acao);
  });

  // ---- H5.3: fechar o dia ----

  botaoFechar.addEventListener("click", async () => {
    if (fechado) {
      navegar("/hoje");
      return;
    }

    aviso.textContent = "";
    botaoFechar.disabled = true;
    try {
      await fecharDia(data);
      somTarefa();
      celebracao.hidden = false;
      await esperar(2200);
      navegar("/hoje");
    } catch (erro) {
      aviso.textContent = erro.message;
      botaoFechar.disabled = false;
    }
  });

  carregar();
}
