// Modo claro / oscuro.
// Sem escolha, segue o celular (prefers-color-scheme). Com escolha, vale a da pessoa.
// A chave usa "iamigo-" (hífen) e não "iamigo.": é uma preferência do aparelho,
// então não se apaga ao sair da conta (sessao.js apaga só as "iamigo.*").
// index.html aplica o modo salvo antes de desenhar, para a tela não piscar.

const CHAVE = "iamigo-tema";
const COR_BARRA = { claro: "#f6f4ef", escuro: "#1c1b22" };

const celularEscuro = () => window.matchMedia?.("(prefers-color-scheme: dark)").matches ?? false;

// "claro" ou "escuro", o que está na tela agora.
export function temaAtual() {
  const escolhido = document.documentElement.dataset.tema;
  if (escolhido === "claro" || escolhido === "escuro") return escolhido;
  return celularEscuro() ? "escuro" : "claro";
}

function aplicar(tema) {
  document.documentElement.dataset.tema = tema;
  // A barra do navegador no celular acompanha o fundo.
  document.querySelector('meta[name="theme-color"]')?.setAttribute("content", COR_BARRA[tema]);
}

export function alternarTema() {
  const novo = temaAtual() === "escuro" ? "claro" : "escuro";
  aplicar(novo);
  try {
    localStorage.setItem(CHAVE, novo);
  } catch {
    // Sem armazenamento: vale até recarregar.
  }
  return novo;
}

// Ao abrir, ajusta a cor da barra do navegador ao modo salvo.
const salvo = document.documentElement.dataset.tema;
if (salvo === "claro" || salvo === "escuro") aplicar(salvo);
