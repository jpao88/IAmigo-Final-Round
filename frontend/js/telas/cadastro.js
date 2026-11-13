// H0.1 · Crear la cuenta con nombre, correo y contraseña en una sola pantalla.

import { cadastrar, entrar } from "../api.js";
import { linkIdioma } from "../componentes.js";
import { comBotaoOcupado, criarElemento } from "../html.js";
import { navegar } from "../roteador.js";
import { salvarSessao } from "../sessao.js";
import { t } from "../i18n.js";

export function telaCadastro(raiz) {
  raiz.append(criarElemento(`
    <p class="marca">IAmigo</p>
    <h1>${t("cadastro.titulo")}</h1>
    <p class="subtitulo">${t("cadastro.subtitulo")}</p>

    <form novalidate>
      <label>${t("cadastro.nome")}
        <input name="nome" type="text" autocomplete="given-name" maxlength="100" required>
      </label>
      <label>${t("login.email")}
        <input name="email" type="email" autocomplete="email" inputmode="email" maxlength="255" required>
      </label>
      <label>${t("login.senha")}
        <input name="senha" type="password" autocomplete="new-password" minlength="6" required>
      </label>
      <p class="aviso" role="alert"></p>
      <button class="botao" type="submit">${t("cadastro.criar")}</button>
    </form>

    <a class="link" href="#/login">${t("cadastro.jaTenho")}</a>
  `), linkIdioma());

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
      aviso.textContent = t("cadastro.nomeCurto");
      return;
    }
    if (!email.includes("@")) {
      aviso.textContent = t("cadastro.emailInvalido");
      return;
    }
    if (senha.length < 6) {
      aviso.textContent = t("cadastro.senhaCurta");
      return;
    }

    try {
      // Depois de criar a conta, já entra: a pessoa não digita tudo de novo.
      const sessao = await comBotaoOcupado(botao, t("cadastro.criando"), async () => {
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
