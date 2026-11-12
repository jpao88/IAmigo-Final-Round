// Princípio "O tempo se vê": o total em texto curto e uma barra com um pedaço por item.

// "Unos 45 minutos", "Más o menos 1 hora y 20 minutos".
export function formatarTempoTotal(minutos) {
  if (minutos < 60) return `Unos ${minutos} minutos`;

  const horas = Math.floor(minutos / 60);
  const resto = minutos % 60;
  const textoHoras = horas === 1 ? "1 hora" : `${horas} horas`;

  return resto === 0
    ? `Más o menos ${textoHoras}`
    : `Más o menos ${textoHoras} y ${resto} minutos`;
}

// Preenche a barra: cada item ocupa o tamanho dos seus minutos.
export function desenharBarraTempo(barra, listaDeMinutos) {
  barra.replaceChildren(...listaDeMinutos.map((minutos) => {
    const pedaco = document.createElement("span");
    pedaco.style.flexGrow = Math.max(minutos, 1);
    return pedaco;
  }));
}
