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

// Preenche a barra: cada item ocupa o tamanho dos seus minutos.
export function desenharBarraTempo(barra, listaDeMinutos) {
  barra.replaceChildren(...listaDeMinutos.map((minutos) => {
    const pedaco = document.createElement("span");
    pedaco.style.flexGrow = Math.max(minutos, 1);
    return pedaco;
  }));
}
