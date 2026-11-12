// Sons de celebração do modo foco (H4.2). Gerados com Web Audio: sem arquivos para baixar.
// Notas suaves (onda senoidal, volume baixo): comemoram sem assustar.
// A pessoa pode desligar; a preferência fica neste navegador.

const CHAVE = "iamigo.som";

let contexto = null;

function obterContexto() {
  const Contexto = window.AudioContext || window.webkitAudioContext;
  if (!Contexto) return null;
  // O navegador só deixa tocar depois de um toque da pessoa; "Hecho" é esse toque.
  contexto ??= new Contexto();
  if (contexto.state === "suspended") contexto.resume();
  return contexto;
}

export function somLigado() {
  try {
    return localStorage.getItem(CHAVE) !== "nao";
  } catch {
    return true;
  }
}

export function alternarSom() {
  const ligado = !somLigado();
  try {
    localStorage.setItem(CHAVE, ligado ? "sim" : "nao");
  } catch {
    // Sem armazenamento: vale só até recarregar.
  }
  return ligado;
}

function tocarNotas(frequencias, intervalo, duracao, volume) {
  if (!somLigado()) return;
  const ctx = obterContexto();
  if (!ctx) return;

  frequencias.forEach((frequencia, i) => {
    const inicio = ctx.currentTime + i * intervalo;
    const oscilador = ctx.createOscillator();
    const ganho = ctx.createGain();

    oscilador.type = "sine";
    oscilador.frequency.value = frequencia;
    ganho.gain.setValueAtTime(0, inicio);
    ganho.gain.linearRampToValueAtTime(volume, inicio + 0.02);
    ganho.gain.exponentialRampToValueAtTime(0.001, inicio + duracao);

    oscilador.connect(ganho).connect(ctx.destination);
    oscilador.start(inicio);
    oscilador.stop(inicio + duracao + 0.05);
  });
}

// Um passo: duas notas curtas que sobem (dó e mi).
export function somPasso() {
  tocarNotas([1046.5, 1318.5], 0.09, 0.35, 0.15);
}

// Tarefa terminada: um arpejo um pouco mais longo (dó, mi, sol, dó).
export function somTarefa() {
  tocarNotas([523.25, 659.25, 783.99, 1046.5], 0.11, 0.6, 0.15);
}
