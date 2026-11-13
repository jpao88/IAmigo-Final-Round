// Cliente da API: envia o token, lê a resposta e traduz os erros para espanhol.
// O backend responde em português; a pessoa sempre lê frases curtas em espanhol.

import { API_URL } from "./config.js";
import { encerrarSessao, obterToken, obterUsuario } from "./sessao.js";

const MENSAGENS = {
  "Já existe uma conta com esse e-mail.": "Ya hay una cuenta con ese correo.",
  "A senha precisa ter pelo menos 6 caracteres.": "Usa al menos 6 caracteres en la contraseña.",
  "O nome não pode ficar vazio.": "Escribe tu nombre.",
  "O nome precisa ter pelo menos 3 caracteres.": "Tu nombre necesita al menos 3 letras.",
  "Informe um e-mail válido.": "Revisa tu correo.",
  "Escreva pelo menos uma tarefa.": "Escribe algo primero.",
  "Envie no máximo 50 tarefas por vez.": "Son muchas a la vez. Prueba con menos de 50.",
  "Cada tarefa pode ter no máximo 200 caracteres.": "Una línea es muy larga. Acórtala un poco.",
  "Tarefa não encontrada.": "No encontramos esta tarea.",
  "Passo não encontrado.": "Ese paso ya no está.",
  "A tarefa já tem passos.": "Esta tarea ya tiene pasos.",
  "O texto do passo não pode ficar vazio.": "Escribe el paso primero.",
  "O passo pode ter no máximo 255 caracteres.": "Ese paso es muy largo. Acórtalo un poco.",
  "Os minutos precisam estar entre 1 e 120.": "Usa entre 1 y 120 minutos.",
  "Hoje já está cheio.": "Hoy ya está completo. Puedes cambiar el límite.",
  "Essa tarefa já está em Hoje ou foi concluída.": "Esa tarea ya está en Hoy.",
  "Escolha as tarefas, uma vez cada.": "Elige al menos una tarea.",
  "O limite precisa estar entre 1 e 5.": "Elige entre 1 y 5.",
  "Esse passo foi dividido.": "Ese paso cambió. Sigamos con el siguiente.",
  "Esse passo não pode ser dividido.": "Ese paso ya no se puede dividir.",
  "Muitas tentativas. Tente de novo em alguns minutos.": "Muchos intentos seguidos. Espera unos minutos y vuelve a probar.",
};

const MENSAGEM_GENERICA = "Algo salió mal. Intenta otra vez.";
const MENSAGEM_SEM_CONEXAO = "No pudimos conectar. Intenta otra vez.";

export class ErroApi extends Error {
  // detalhe: a frase original do backend, para a tela reconhecer o erro.
  constructor(status, mensagem, detalhe = null) {
    super(mensagem);
    this.status = status;
    this.detalhe = detalhe;
  }
}

function traduzir(status, detalhe) {
  if (typeof detalhe === "string" && MENSAGENS[detalhe]) {
    return MENSAGENS[detalhe];
  }

  if (status === 422) {
    return "Revisa los datos e intenta otra vez.";
  }

  // H2.4: a IA falhou ou não está configurada.
  if (status === 503) {
    return "IAmigo no pudo ahora. Puedes escribirlos tú.";
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

  // Erro sem JSON: não veio da API, e sim do caminho até ela (ex.: o hosting
  // trocando de versão). Para a pessoa é como uma falha de conexão.
  if (resposta.status >= 500 && conteudo === null) {
    throw new ErroApi(resposta.status, MENSAGEM_SEM_CONEXAO);
  }

  if (resposta.status === 401 && autenticar) {
    encerrarSessao();
    aoPerderSessao();
  }

  throw new ErroApi(resposta.status, traduzir(resposta.status, conteudo?.detail), conteudo?.detail ?? null);
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

// ---- Tarefas (Épica 1 · Capturar) ----

function rotaTarefas() {
  return `/usuarios/${obterUsuario().id}/tarefas`;
}

// Data do celular da pessoa (AAAA-MM-DD), não a do servidor.
export function dataLocal(data = new Date()) {
  const ano = data.getFullYear();
  const mes = String(data.getMonth() + 1).padStart(2, "0");
  const dia = String(data.getDate()).padStart(2, "0");
  return `${ano}-${mes}-${dia}`;
}

export function listarBandeja() {
  return requisitar("GET", `${rotaTarefas()}/bandeja?hoje=${dataLocal()}`);
}

// H1.1 e H1.2: cada linha vira uma tarefa; o backend ignora as vazias.
export function criarTarefas(titulos) {
  return requisitar("POST", `${rotaTarefas()}/lote`, { titulos });
}

export function obterTarefa(tarefaId) {
  return requisitar("GET", `${rotaTarefas()}/${tarefaId}`);
}

// ---- Hoje (Épica 3 · Planear hoy) ----

// H3.3: tarefas do dia na ordem, cada uma com minutos_restantes.
export function listarHoje() {
  return requisitar("GET", `${rotaTarefas()}/hoje?data=${dataLocal()}`);
}

// H3.1 ("+ Hoy", uma) e H3.2 (várias): entram no fim do dia, respeitando o limite.
// H5.2 "Hacerla mañana" usa a mesma rota com outra data.
export function planejarHoje(ids, data = dataLocal()) {
  return requisitar("POST", `${rotaTarefas()}/hoje`, { ids, data });
}

// H3.4: todas as pendentes de hoje, na ordem nova.
export function reordenarHoje(ids) {
  return requisitar("PUT", `${rotaTarefas()}/hoje/ordem`, { ids, data: dataLocal() });
}

export function tirarDeHoje(tarefaId) {
  return requisitar("DELETE", `${rotaTarefas()}/${tarefaId}/hoje`);
}

// H6.3: a guia do primeiro uso não volta a aparecer.
export function concluirOnboarding() {
  return requisitar("PUT", `/usuarios/${obterUsuario().id}/onboarding`);
}

// H3.5: de 1 a 5.
export function alterarLimiteHoje(limite) {
  return requisitar("PUT", `/usuarios/${obterUsuario().id}/limite-hoje`, { limite_hoje: limite });
}

// ---- Passos (Épica 2 · Desmenuzar) ----

function rotaPassos(tarefaId) {
  return `${rotaTarefas()}/${tarefaId}/passos`;
}

export function listarPassos(tarefaId) {
  return requisitar("GET", rotaPassos(tarefaId));
}

// H2.1: a IA sugere de 3 a 7 passos com minutos.
export function gerarPassos(tarefaId) {
  return requisitar("POST", `${rotaPassos(tarefaId)}/gerar`);
}

// H2.3: sem minutos, o backend usa 10.
export function adicionarPasso(tarefaId, texto, minutosEstimados = null) {
  return requisitar("POST", rotaPassos(tarefaId), {
    texto,
    minutos_estimados: minutosEstimados,
  });
}

export function editarPasso(tarefaId, passoId, texto, minutosEstimados) {
  return requisitar("PUT", `${rotaPassos(tarefaId)}/${passoId}`, {
    texto,
    minutos_estimados: minutosEstimados,
  });
}

export function reordenarPassos(tarefaId, ids) {
  return requisitar("PUT", `${rotaPassos(tarefaId)}/ordem`, { ids });
}

export function excluirPasso(tarefaId, passoId) {
  return requisitar("DELETE", `${rotaPassos(tarefaId)}/${passoId}`);
}

// ---- Modo foco (Épica 4 · Hacer) ----

// H4.2: devolve { passo, tarefa_concluida }; com o último passo, a tarefa fica concluída.
export function concluirPasso(tarefaId, passoId) {
  return requisitar("POST", `${rotaPassos(tarefaId)}/${passoId}/concluir`);
}

// Tarefa sem passos: no modo foco é um passo só.
export function concluirTarefa(tarefaId) {
  return requisitar("POST", `${rotaTarefas()}/${tarefaId}/concluir`);
}

// H4.4 "Me atasqué": 2 ou 3 passos menores no lugar do travado.
export async function dividirPasso(tarefaId, passoId) {
  try {
    return await requisitar("POST", `${rotaPassos(tarefaId)}/${passoId}/dividir`);
  } catch (erro) {
    if (erro.status === 503) {
      throw new ErroApi(503, "IAmigo no pudo dividirlo ahora. Prueba en un rato.");
    }
    throw erro;
  }
}

// ---- Cerrar el día (Épica 5) ----

function rotaDias() {
  return `/usuarios/${obterUsuario().id}/dias`;
}

// H5.1 e H5.2: { passos_concluidos, tarefas_concluidas, concluidas, pendentes, fechado }.
export function obterResumoDia(data) {
  return requisitar("GET", `${rotaDias()}/${data}`);
}

// H5.3: fechar de novo não cria um segundo fechamento.
export function fecharDia(data) {
  return requisitar("POST", `${rotaDias()}/${data}/fechar`);
}

// H5.4: o último dia com plano que ficou sem fechar, ou null.
export async function obterDiaPendente() {
  const resposta = await requisitar("GET", `${rotaDias()}/pendente?hoje=${dataLocal()}`);
  return resposta?.data ?? null;
}
