// Ajudantes pequenos para montar telas.

// Cria um elemento a partir de HTML fixo das telas. Nunca passar aqui texto
// digitado pela pessoa: para isso, usar textContent.
export function criarElemento(html) {
  const modelo = document.createElement("template");
  modelo.innerHTML = html.trim();
  return modelo.content;
}

// Desativa o botão enquanto a requisição acontece, para não enviar duas vezes.
export async function comBotaoOcupado(botao, textoOcupado, acao) {
  const textoOriginal = botao.textContent;
  botao.disabled = true;
  botao.textContent = textoOcupado;

  try {
    return await acao();
  } finally {
    botao.disabled = false;
    botao.textContent = textoOriginal;
  }
}
