import { t } from "./i18n.js";
// Princípio "O tempo se vê": o total em texto curto e uma barra com um pedaço por item.

// "Unos 45 minutos", "Más o menos 1 hora y 20 minutos".
export function formatarTempoTotal(minutos) {
  if (minutos < 60) return t("tempo.minutos", minutos);

  const horas = Math.floor(minutos / 60);
  const resto = minutos % 60;
  const textoHoras = t("tempo.horas", horas);

  return resto === 0
    ? t("tempo.maisOuMenos", textoHoras)
    : t("tempo.horasEMinutos", textoHoras, resto);
}

// Versão curta, ao lado de um título: "unos 55 min", "1 h 20 min".
export function formatarTempoCurto(minutos) {
  if (minutos < 60) return t("tempo.curto", minutos);

  const horas = Math.floor(minutos / 60);
  const resto = minutos % 60;
  return resto === 0 ? `${horas} h` : `${horas} h ${resto} min`;
}

// Texto dentro do anel da tarjeta Ahora (HTML só com números):
// "10<small>min</small>", "1h<small>30</small>", "2h".
export function textoAnel(minutos) {
  const total = Math.round(Number(minutos));
  if (total < 60) return `${total}<small>min</small>`;

  const horas = Math.floor(total / 60);
  const resto = total % 60;
  return resto === 0 ? `${horas}h` : `${horas}h<small>${String(resto).padStart(2, "0")}</small>`;
}

// Preenche a barra: cada item ocupa o tamanho dos seus minutos.
export function desenharBarraTempo(barra, listaDeMinutos) {
  barra.replaceChildren(...listaDeMinutos.map((minutos) => {
    const pedaco = document.createElement("span");
    pedaco.style.flexGrow = Math.max(minutos, 1);
    return pedaco;
  }));
}
