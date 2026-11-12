// H3.2 · Elegir varias tareas de la Bandeja para Hoy, con el contador del límite a la vista.
// H3.5 · El límite se cambia aquí, que es donde importa.
// A ordem em que a pessoa marca é a ordem em que entram no dia.

import { alterarLimiteHoje, listarBandeja, listarHoje, planejarHoje } from "../api.js";
import { comBotaoOcupado, criarElemento } from "../html.js";
import { navegar } from "../roteador.js";
import { atualizarUsuario, obterUsuario } from "../sessao.js";

export function telaElegir(raiz) {
  raiz.append(criarElemento(`
    <header class="cabecalho">
      <a class="botao-texto" href="#/hoje">← Hoy</a>
    </header>

    <h1>Elegir tareas para hoy</h1>
    <p class="contador" role="status"></p>

    <div class="limite">
      <p class="limite-texto"></p>
      <button class="botao-texto" type="button" data-acao="cambiar-limite" aria-expanded="false">Cambiar límite</button>
    </div>
    <div class="seletor-limite" role="group" aria-label="Tareas por día" hidden></div>

    <p class="aviso" role="alert"></p>

    <p class="vazia subtitulo" hidden>Tu Bandeja está vacía. Anota algo primero.</p>
    <ul class="lista-elegir"></ul>

    <button class="botao" type="button" data-acao="listo">Listo</button>
  `));

  const contador = raiz.querySelector(".contador");
  const aviso = raiz.querySelector(".aviso");
  const vazia = raiz.querySelector(".vazia");
  const lista = raiz.querySelector(".lista-elegir");
  const botaoListo = raiz.querySelector('[data-acao="listo"]');

  const limiteTexto = raiz.querySelector(".limite-texto");
  const botaoLimite = raiz.querySelector('[data-acao="cambiar-limite"]');
  const seletorLimite = raiz.querySelector(".seletor-limite");

  let limite = obterUsuario().limite_hoje;
  let jaEmHoje = 0;
  // Ids na ordem em que foram marcados.
  const escolhidas = [];

  function vagas() {
    return Math.max(limite - jaEmHoje, 0);
  }

  function desenharLimite() {
    limiteTexto.textContent = limite === 1 ? "Hasta 1 tarea por día." : `Hasta ${limite} tareas por día.`;

    seletorLimite.replaceChildren(...[1, 2, 3, 4, 5].map((numero) => {
      const botao = document.createElement("button");
      botao.type = "button";
      botao.className = "opcao-limite";
      botao.textContent = numero;
      botao.dataset.limite = numero;
      botao.setAttribute("aria-pressed", String(numero === limite));
      return botao;
    }));
  }

  function atualizar() {
    desenharLimite();

    // Se o limite baixou, desmarca as últimas escolhidas que já não cabem.
    while (escolhidas.length > vagas()) {
      const id = escolhidas.pop();
      const caixa = lista.querySelector(`input[value="${id}"]`);
      if (caixa) caixa.checked = false;
    }

    const restantes = vagas() - escolhidas.length;

    if (vagas() === 0) contador.textContent = "Hoy ya está completo.";
    else if (restantes === 0) contador.textContent = "Listo, tu día está completo.";
    else if (restantes === 1) contador.textContent = "Puedes elegir 1 más.";
    else contador.textContent = `Puedes elegir ${restantes} más.`;

    // No limite, as não marcadas ficam desativadas; nunca se marca além do que cabe.
    lista.querySelectorAll("input").forEach((caixa) => {
      caixa.disabled = !caixa.checked && restantes <= 0;
    });

    botaoListo.textContent = escolhidas.length > 0 ? "Listo" : "Volver a Hoy";
  }

  function itemDaTarefa(tarefa) {
    const item = document.createElement("li");
    item.append(criarElemento(`
      <label class="opcao-elegir">
        <input type="checkbox">
        <span></span>
      </label>
    `));

    const caixa = item.querySelector("input");
    caixa.value = tarefa.id;
    item.querySelector("span").textContent = tarefa.titulo;
    return item;
  }

  lista.addEventListener("change", (evento) => {
    const caixa = evento.target;
    const id = Number(caixa.value);

    if (caixa.checked) escolhidas.push(id);
    else escolhidas.splice(escolhidas.indexOf(id), 1);

    atualizar();
  });

  // ---- H3.5: limite ----

  botaoLimite.addEventListener("click", () => {
    const abrir = seletorLimite.hidden;
    seletorLimite.hidden = !abrir;
    botaoLimite.setAttribute("aria-expanded", String(abrir));
  });

  seletorLimite.addEventListener("click", async (evento) => {
    const botao = evento.target.closest("[data-limite]");
    if (!botao) return;

    const novo = Number(botao.dataset.limite);
    const anterior = limite;
    if (novo === anterior) return;

    aviso.textContent = "";
    limite = novo;
    atualizar();

    try {
      atualizarUsuario(await alterarLimiteHoje(novo));
    } catch (erro) {
      limite = anterior;
      atualizar();
      aviso.textContent = erro.message;
    }
  });

  botaoListo.addEventListener("click", async () => {
    if (escolhidas.length === 0) {
      navegar("/hoje");
      return;
    }

    aviso.textContent = "";

    try {
      await comBotaoOcupado(botaoListo, "Guardando…", () => planejarHoje(escolhidas));
      navegar("/hoje");
    } catch (erro) {
      aviso.textContent = erro.message;
      atualizar();
    }
  });

  async function carregar() {
    contador.textContent = "Cargando…";

    try {
      const [bandeja, hoje] = await Promise.all([listarBandeja(), listarHoje()]);
      jaEmHoje = hoje.filter((tarefa) => !tarefa.concluida).length;
      lista.replaceChildren(...bandeja.map(itemDaTarefa));
      vazia.hidden = bandeja.length > 0;
      atualizar();
    } catch (erro) {
      contador.textContent = "";
      aviso.textContent = erro.message;
    }
  }

  desenharLimite();
  carregar();
}
