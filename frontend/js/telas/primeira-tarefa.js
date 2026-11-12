// H6.2 · Primeira tarefa guiada: a pessoa escreve uma tarefa real e a app a acompanha
// para dividir (tela da tarefa), pôr em Hoy e fazer o primeiro passo (modo foco).

import { criarTarefas } from "../api.js";
import { iniciarGuia } from "../guia.js";
import { comBotaoOcupado, criarElemento } from "../html.js";
import { navegar } from "../roteador.js";

export function telaPrimeiraTarefa(raiz) {
  raiz.append(criarElemento(`
    <header class="cabecalho">
      <a class="botao-texto" href="#/bienvenida">← Volver</a>
      <p class="subtitulo guia-etapa">1 de 3</p>
    </header>

    <h1>Escribe una cosa que tengas pendiente</h1>
    <p class="subtitulo">Algo real, aunque sea pequeño. Lo hacemos juntos.</p>

    <form novalidate>
      <label class="rotulo-oculto" for="primeira-tarefa">Tu tarea</label>
      <input id="primeira-tarefa" name="titulo" type="text" maxlength="200"
        placeholder="Por ejemplo: ordenar el escritorio" autocomplete="off" enterkeyhint="go">
      <p class="aviso" role="alert"></p>
      <button class="botao" type="submit">Seguir</button>
    </form>
  `));

  const formulario = raiz.querySelector("form");
  const aviso = raiz.querySelector(".aviso");
  const botao = formulario.querySelector("button");

  formulario.addEventListener("submit", async (evento) => {
    evento.preventDefault();
    aviso.textContent = "";

    const titulo = formulario.titulo.value.trim();
    if (!titulo) {
      aviso.textContent = "Escribe algo primero.";
      return;
    }

    try {
      const [tarefa] = await comBotaoOcupado(botao, "Guardando…", () => criarTarefas([titulo]));
      iniciarGuia(tarefa.id);
      navegar(`/tarefa/${tarefa.id}`);
    } catch (erro) {
      aviso.textContent = erro.message;
    }
  });

  formulario.titulo.focus();
}
