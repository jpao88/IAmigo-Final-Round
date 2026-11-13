// H0.2 · Iniciar sesión con correo y contraseña.

import { entrar } from "../api.js";
import { linkIdioma } from "../componentes.js";
import { comBotaoOcupado, criarElemento } from "../html.js";
import { navegar, TELA_INICIAL } from "../roteador.js";
import { salvarSessao } from "../sessao.js";
import { t } from "../i18n.js";

export function telaLogin(raiz) {
  raiz.append(criarElemento(`
    <p class="marca">IAmigo</p>
    <h1>${t("login.titulo")}</h1>
    <p class="subtitulo">${t("login.subtitulo")}</p>

    <form novalidate>
      <label>${t("login.email")}
        <input name="email" type="email" autocomplete="email" inputmode="email" required>
      </label>
      <label>${t("login.senha")}
        <input name="senha" type="password" autocomplete="current-password" required>
      </label>
      <p class="aviso" role="alert"></p>
      <button class="botao" type="submit">${t("login.entrar")}</button>
    </form>

    <a class="link" href="#/cadastro">${t("login.criarConta")}</a>
  `), linkIdioma());

  const formulario = raiz.querySelector("form");
  const aviso = raiz.querySelector(".aviso");
  const botao = raiz.querySelector("button");

  formulario.addEventListener("submit", async (evento) => {
    evento.preventDefault();
    aviso.textContent = "";

    const email = formulario.email.value.trim();
    const senha = formulario.senha.value;

    if (!email || !senha) {
      aviso.textContent = t("login.faltam");
      return;
    }

    try {
      const sessao = await comBotaoOcupado(botao, t("login.entrando"), () => entrar(email, senha));
      salvarSessao(sessao);
      navegar(TELA_INICIAL);
    } catch (erro) {
      aviso.textContent = erro.message;
    }
  });

  formulario.email.focus();
}
