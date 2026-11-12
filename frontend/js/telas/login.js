// H0.2 · Iniciar sesión con correo y contraseña.

import { entrar } from "../api.js";
import { comBotaoOcupado, criarElemento } from "../html.js";
import { navegar, TELA_INICIAL } from "../roteador.js";
import { salvarSessao } from "../sessao.js";

export function telaLogin(raiz) {
  raiz.append(criarElemento(`
    <p class="marca">IAmigo</p>
    <h1>Hola de nuevo</h1>
    <p class="subtitulo">Entra para ver tu día.</p>

    <form novalidate>
      <label>Correo
        <input name="email" type="email" autocomplete="email" inputmode="email" required>
      </label>
      <label>Contraseña
        <input name="senha" type="password" autocomplete="current-password" required>
      </label>
      <p class="aviso" role="alert"></p>
      <button class="botao" type="submit">Entrar</button>
    </form>

    <a class="link" href="#/cadastro">Crear una cuenta</a>
  `));

  const formulario = raiz.querySelector("form");
  const aviso = raiz.querySelector(".aviso");
  const botao = raiz.querySelector("button");

  formulario.addEventListener("submit", async (evento) => {
    evento.preventDefault();
    aviso.textContent = "";

    const email = formulario.email.value.trim();
    const senha = formulario.senha.value;

    if (!email || !senha) {
      aviso.textContent = "Escribe tu correo y tu contraseña.";
      return;
    }

    try {
      const sessao = await comBotaoOcupado(botao, "Entrando…", () => entrar(email, senha));
      salvarSessao(sessao);
      navegar(TELA_INICIAL);
    } catch (erro) {
      aviso.textContent = erro.message;
    }
  });

  formulario.email.focus();
}
