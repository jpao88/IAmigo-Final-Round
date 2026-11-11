// Cliente da API: envia o token, lê a resposta e traduz os erros para espanhol.
// O backend responde em português; a pessoa sempre lê frases curtas em espanhol.

import { API_URL } from "./config.js";
import { encerrarSessao, obterToken } from "./sessao.js";

const MENSAGENS = {
  "Já existe uma conta com esse e-mail.": "Ya hay una cuenta con ese correo.",
  "A senha precisa ter pelo menos 6 caracteres.": "Usa al menos 6 caracteres en la contraseña.",
  "O nome não pode ficar vazio.": "Escribe tu nombre.",
  "O nome precisa ter pelo menos 3 caracteres.": "Tu nombre necesita al menos 3 letras.",
  "Informe um e-mail válido.": "Revisa tu correo.",
};

const MENSAGEM_GENERICA = "Algo salió mal. Intenta otra vez.";
const MENSAGEM_SEM_CONEXAO = "No pudimos conectar. Intenta otra vez.";

export class ErroApi extends Error {
  constructor(status, mensagem) {
    super(mensagem);
    this.status = status;
  }
}

function traduzir(status, detalhe) {
  if (typeof detalhe === "string" && MENSAGENS[detalhe]) {
    return MENSAGENS[detalhe];
  }

  if (status === 422) {
    return "Revisa los datos e intenta otra vez.";
  }

  return MENSAGEM_GENERICA;
}

// Chamado quando o token expira ou é recusado; app.js decide para onde ir.
let aoPerderSessao = () => {};

export function quandoPerderSessao(funcao) {
  aoPerderSessao = funcao;
}

export async function requisitar(metodo, caminho, corpo, { autenticar = true } = {}) {
  const cabecalhos = { "Content-Type": "application/json" };
  const token = obterToken();

  if (autenticar && token) {
    cabecalhos.Authorization = `Bearer ${token}`;
  }

  let resposta;

  try {
    resposta = await fetch(`${API_URL}${caminho}`, {
      method: metodo,
      headers: cabecalhos,
      body: corpo === undefined ? undefined : JSON.stringify(corpo),
    });
  } catch {
    throw new ErroApi(0, MENSAGEM_SEM_CONEXAO);
  }

  const conteudo = await resposta.json().catch(() => null);

  if (resposta.ok) {
    return conteudo?.dados ?? conteudo;
  }

  if (resposta.status === 401 && autenticar) {
    encerrarSessao();
    aoPerderSessao();
  }

  throw new ErroApi(resposta.status, traduzir(resposta.status, conteudo?.detail));
}

// ---- Autenticação (Épica 0) ----

export async function entrar(email, senha) {
  try {
    return await requisitar("POST", "/auth/login", { email, senha }, { autenticar: false });
  } catch (erro) {
    // H0.2: mesma frase para correo inexistente e senha errada.
    if (erro.status === 401) {
      throw new ErroApi(401, "Correo o contraseña incorrectos.");
    }
    throw erro;
  }
}

export function cadastrar(nome, email, senha) {
  return requisitar("POST", "/usuarios", { nome, email, senha }, { autenticar: false });
}
