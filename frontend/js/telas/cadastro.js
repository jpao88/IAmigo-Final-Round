// H0.1 · Crear la cuenta con nombre, correo y contraseña en una sola pantalla.

import { cadastrar, entrar } from "../api.js";
import { comBotaoOcupado, criarElemento } from "../html.js";
import { navegar } from "../roteador.js";
import { salvarSessao } from "../sessao.js";

export function telaCadastro(raiz) {
  raiz.append(criarElemento(`
    <p class="marca">IAmigo</p>
    <h1>Crea tu cuenta</h1>
    <p class="subtitulo">Así guardas tus tareas.</p>

    <form novalidate>
      <label>Tu nombre
        <input name="nome" type="text" autocomplete="given-name" maxlength="100" required>
      </label>
      <label>Correo
        <input name="email" type="email" autocomplete="email" inputmode="email" maxlength="255" required>
      </label>
      <label>Contraseña
        <input name="senha" type="password" autocomplete="new-password" minlength="6" required>
      </label>
      <p class="aviso" role="alert"></p>
      <button class="botao" type="submit">Crear cuenta</button>
    </form>

    <a class="link" href="#/login">Ya tengo cuenta</a>
  `));

  const formulario = raiz.querySelector("form");
  const aviso = raiz.querySelector(".aviso");
  const botao = raiz.querySelector("button");

  formulario.addEventListener("submit", async (evento) => {
    evento.preventDefault();
    aviso.textContent = "";

    const nome = formulario.nome.value.trim();
    const email = formulario.email.value.trim();
    const senha = formulario.senha.value;

    // As mesmas regras do backend, para avisar antes de enviar.
    if (nome.length < 3) {
      aviso.textContent = "Tu nombre necesita al menos 3 letras.";
      return;
    }
    if (!email.includes("@")) {
      aviso.textContent = "Revisa tu correo.";
      return;
    }
    if (senha.length < 6) {
      aviso.textContent = "Usa al menos 6 caracteres en la contraseña.";
      return;
    }

    try {
      // Depois de criar a conta, já entra: a pessoa não digita tudo de novo.
      const sessao = await comBotaoOcupado(botao, "Creando…", async () => {
        await cadastrar(nome, email, senha);
        return entrar(email, senha);
      });
      salvarSessao(sessao);
      // H6.1: conta nova começa pela bienvenida.
      navegar("/bienvenida");
    } catch (erro) {
      aviso.textContent = erro.message;
    }
  });

  formulario.nome.focus();
}
