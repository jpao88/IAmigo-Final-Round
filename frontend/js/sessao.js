// Guarda a sessão (token JWT e dados do usuário) no navegador.

const CHAVE = "iamigo.sessao";

// Cópia em memória: funciona mesmo se o navegador bloquear o localStorage.
let sessaoEmMemoria = null;

function ler() {
  try {
    return JSON.parse(localStorage.getItem(CHAVE));
  } catch {
    return null;
  }
}

export function salvarSessao({ access_token, expires_in, usuario }) {
  const sessao = {
    token: access_token,
    expiraEm: Date.now() + expires_in * 1000,
    usuario,
  };

  try {
    localStorage.setItem(CHAVE, JSON.stringify(sessao));
  } catch {
    // Navegador sem armazenamento (ex.: modo privado restrito): a sessão vale só nesta aba.
  }

  sessaoEmMemoria = sessao;
}

export function obterSessao() {
  const sessao = sessaoEmMemoria || ler();

  if (!sessao || !sessao.token || Date.now() >= sessao.expiraEm) {
    return null;
  }

  return sessao;
}

export function obterToken() {
  return obterSessao()?.token || null;
}

export function obterUsuario() {
  return obterSessao()?.usuario || null;
}

// Depois de mudar algo do perfil (ex.: limite de Hoy), guarda a versão nova.
export function atualizarUsuario(usuario) {
  const sessao = obterSessao();
  if (!sessao) return;

  sessaoEmMemoria = { ...sessao, usuario };

  try {
    localStorage.setItem(CHAVE, JSON.stringify(sessaoEmMemoria));
  } catch {
    // A cópia em memória basta até fechar a aba.
  }
}

// H0.3: ao sair, apaga o token e as cópias locais (ex.: a Bandeja),
// para ninguém ver as tarefas de outra pessoa neste celular.
export function encerrarSessao() {
  sessaoEmMemoria = null;

  try {
    Object.keys(localStorage)
      .filter((chave) => chave.startsWith("iamigo."))
      .forEach((chave) => localStorage.removeItem(chave));
  } catch {
    // Nada a fazer.
  }
}
