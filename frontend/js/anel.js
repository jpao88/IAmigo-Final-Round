// Anel de progresso pequeno (Hoy): quanto do dia já foi feito.
// Só desenho: o texto que o acompanha é o que o leitor de tela lê.

const RAIO = 26;
const CIRCUNFERENCIA = 2 * Math.PI * RAIO;

export function criarAnel() {
  const elemento = document.createElement("div");
  elemento.className = "anel";
  elemento.setAttribute("aria-hidden", "true");
  elemento.innerHTML = `
    <svg viewBox="0 0 64 64" focusable="false">
      <circle class="anel-fundo" cx="32" cy="32" r="${RAIO}"></circle>
      <circle class="anel-progresso" cx="32" cy="32" r="${RAIO}"
        stroke-dasharray="${CIRCUNFERENCIA}" stroke-dashoffset="${CIRCUNFERENCIA}"></circle>
    </svg>`;

  const progresso = elemento.querySelector(".anel-progresso");

  // fracao de 0 a 1. Em 0 o arco some (a ponta redonda deixaria um pontinho).
  function atualizar(fracao) {
    const limitada = Math.min(Math.max(fracao, 0), 1);
    progresso.setAttribute("stroke-dashoffset", String(CIRCUNFERENCIA * (1 - limitada)));
    progresso.style.opacity = limitada === 0 ? "0" : "1";
  }

  return { elemento, atualizar };
}
