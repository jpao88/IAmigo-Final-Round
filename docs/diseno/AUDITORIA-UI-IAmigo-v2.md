# Auditoría UI/UX de IAmigo, ronda 2 (después del rediseño)

**Fecha:** 13/11/2026 · **URL:** https://iamigo-lzdqn.ondigitalocean.app/
**Cuenta:** prueba (Rafaela) · **Herramientas:** skills ui-ux-pro-max + design, inspección de CSS/JS en vivo y un script de contraste WCAG sobre cada texto visible
**Revisado:** Hoje, Caixa de entrada, Detalle de tarefa y Escolher tarefas, en tema claro y oscuro, a 375px (móvil) y 1280px (escritorio).
**No revisado** (para no cambiar datos): Foco, Encerrar o dia, Login/Cadastro y Bienvenida.

---

## Resumen

El salto es grande. El script de contraste **no encontró ni un solo texto por debajo de AA** en ninguna de las pantallas ni en ninguno de los dos temas. Además:

- La paleta, Fraunces + Nunito y el logo nuevo están aplicados.
- Los emojis se reemplazaron por íconos SVG con `aria-hidden`.
- Hay "Desfazer" al apagar.
- El botón de "Escolher" cambia de texto según lo que marques.
- Hay un anillo de progreso en Hoje.

Lo que queda son detalles de pulido y algunos pendientes de la primera auditoría.

| Prioridad | Cantidad |
|---|---|
| 🔴 Alta | 0 |
| 🟠 Media | 5 |
| 🟢 Baja | 6 |

---

## Estado de la auditoría 1

| Punto | Estado |
|---|---|
| A1 Contraste de la primaria (claro) | ✅ Resuelto (`#6b45d9`) |
| A2 Anillo de foco (claro) | ✅ Resuelto |
| A3 Bordes de campos | ✅ Resuelto (`--borda-campo`) |
| A4 Apagar con "Desfazer" | ✅ Resuelto, `confirm()` eliminado |
| M1 Editables visibles | ✅ Resuelto (subrayado punteado). Ver N3, quedó algo recargado |
| M2 Botón de "Escolher" | ✅ Resuelto ("Adicionar N tarefas a Hoje") |
| M3 Botón de idioma "ES" | ❌ **Pendiente** (ver N1) |
| M4 Emojis → SVG | ✅ Resuelto |
| M5 Pestaña activa | ✅ Mejorado (fondo lavanda) |
| M6 Campo de minutos | ⚠️ Parcial: la pastilla mide 44px pero el input sigue en 40×43px |
| B1 PWA / favicon | ❌ Pendiente |
| B2 meta description | ❌ Pendiente |
| B3 Acciones del encabezado | ❌ Pendiente (ver N1) |
| B4 Placeholder como guía | ⚠️ Sigue "Uma ideia por linha" solo como placeholder |
| B5 Navegación en escritorio | ✅ Aceptable: los ítems están centrados con `max-width` |

---

## 🟠 Prioridad media

### N1. El encabezado tiene botones demasiado angostos
"ES" mide **26px** de ancho y "Sair" **34px**. El mínimo para tocar es 44×44 y están pegados uno al otro, así que es fácil tocar "Sair" queriendo cambiar el idioma. "Sair" además cierra sesión al instante, sin confirmar ni deshacer. Y "ES" sigue siendo una sigla que se lee como "idioma actual" (punto M3).

**Arreglo:**
```css
.cabecalho-acoes button { min-width: 44px; min-height: 44px; }
```
- Mejor todavía: dejar en el encabezado solo el ícono de tema y **un botón de menú** (`more-horizontal` de Lucide) que abra un panel con "Idioma: Español / Português" y "Sair".
- Dentro del panel, "Sair" puede seguir siendo inmediato, porque ya no está a un toque accidental.

### N2. El color del navegador no acompaña al tema oscuro
`<meta name="theme-color" content="#f7f4ff">` es fijo. En el celular con tema oscuro, la barra del navegador queda lavanda clara sobre una app violeta oscura.

**Arreglo:**
```html
<meta name="theme-color" content="#f7f4ff" media="(prefers-color-scheme: light)">
<meta name="theme-color" content="#140b26" media="(prefers-color-scheme: dark)">
```
Cuando el usuario fuerza el tema con el botón, hay que actualizarlo también por JS: `document.querySelector('meta[name=theme-color]').content = ...`.

### N3. El detalle de tarefa quedó visualmente recargado
El subrayado punteado se aplica al título **y a cada uno de los pasos**. Con 7 pasos son 7 líneas punteadas además de la barra segmentada, y para alguien con TDAH es ruido visual. Ademas, a 375px "Mais ou menos 1 hora e 45 minutos" ocupa dos líneas y empuja "Ordenar".

**Arreglo:**
- Dejar el punteado **solo en el título**. En los pasos, quitarlo y mostrar el borde solo con `:focus-within`, porque la tarjeta entera ya se ve tocable.
- Debajo del título, una sola vez y en `--texto-suave`: "Toque em qualquer passo para editar".
- Acortar el texto del tiempo a "≈ 1h 45min" (i18n), así cabe en una línea junto a "Ordenar".

### N4. El anillo de progreso en 0 parece un espacio vacío
Con "0 de 1 feita", el anillo es un círculo gris sin contenido. En tema claro casi no se ve (`--borda` sobre `--fundo`) y al principio del día da sensación de "todavía no hiciste nada".

**Arreglo:**
- Poner el número **dentro** del anillo ("0/1") y el texto al lado con un tono motivador: "Vamos pela primeira?".
- Que el trazo de fondo del anillo use `--superficie-2` en claro, para que se vea.
- Cuando no hay tareas en Hoje, ocultar el anillo y mostrar el estado vacío con su acción: "Escolha até 3 tarefas →".

### N5. Las casillas de "Escolher" no siguen el tema
Sin marcar, las casillas usan el estilo del sistema: un cuadrado gris de Windows sobre el violeta oscuro. `accent-color` solo pinta la casilla marcada.

**Arreglo:**
```css
.opcao-elegir input[type=checkbox] {
  appearance: none; width: 26px; height: 26px; border-radius: 8px;
  border: 2px solid var(--borda-campo); background: var(--superficie);
  display: grid; place-content: center; transition: background .15s;
}
.opcao-elegir input:checked { background: var(--primaria); border-color: var(--primaria); }
.opcao-elegir input:checked::after {
  content: ""; width: 12px; height: 7px; margin-top: -3px;
  border: 3px solid var(--primaria-texto); border-top: 0; border-right: 0; transform: rotate(-45deg);
}
.opcao-elegir input:focus-visible { outline: 3px solid var(--foco); outline-offset: 2px; }
```

---

## 🟢 Prioridad baja

- **N6. El punto del logo en tamaño chico.** En el encabezado (unos 18px), el brillo del punto de la "i" se ve como una mancha difusa. A ese tamaño conviene quitar el `box-shadow` y dejar un punto sólido. El brillo queda solo en login y splash:
  `.cabecalho .marca-i::after { box-shadow: none; }`
- **N7. Las sugerencias de la caixa de entrada se cortan sin aviso.** Se desplazan de lado y la última queda cortada contra el borde ("Res…"). Hay dos opciones:
  - Que hagan salto de línea (`flex-wrap: wrap`), en dos filas como la ref. 01.
  - Agregar un degradé al borde derecho: `mask-image: linear-gradient(90deg, #000 85%, transparent)`.
- **N8. El título editable no tiene nombre de encabezado.** En el detalle, el `<h1>` contiene solo un `textarea`, así que su texto queda vacío y el lector de pantalla anuncia "encabezado, campo de texto". Agregar `aria-label` al `h1` con el nombre de la tarea, o un `<span class="rotulo-oculto">` con el título.
- **N9. Minutos (M6 pendiente).** El input mide 40×43px. Hay que hacer que toda la pastilla `.minutos` enfoque el input al tocarla, o envolverla en un `<label>`.
- **N10. PWA, favicon y description (B1, B2 pendientes).** Un `manifest.json` con nombre, `theme_color`, `background_color` e íconos de 192 y 512 hechos con el wordmark "IA". Y `<meta name="description" content="IAmigo: organize seu dia, uma tarefa por vez.">`.
- **N11. Placeholder como única guía (B4).** "Uma ideia por linha" desaparece al escribir. Moverlo a un texto de ayuda permanente debajo del campo.

---

## Lo que ya está muy bien (no tocar)

- **0 fallos de contraste** en claro y oscuro, con todos los textos medidos.
- La tipografía funciona: Fraunces en los H1 le da calidez y Nunito a 18px se lee cómoda.
- La tarjeta "Agora", con la franja violeta y "Começar" a todo el ancho, deja clarísimo qué hacer ahora.
- "Encerrar o dia" bajó a link secundario, así no compite con la tarea actual.
- Los íconos SVG llevan `aria-hidden`, todos los botones tienen nombre accesible y no hay scroll horizontal a 375px.
- Las sugerencias de la caixa de entrada y el textarea grande con el "+" adentro se parecen mucho a la referencia.

---

## Prompt para Claude Code

```
Lee @docs/diseno/AUDITORIA-UI-IAmigo-v2.md. Aplica en este orden, un paso
por vez, mostrándome el diff antes de cada uno:
1. N2 (theme-color por tema) y N6 (punto del logo sin brillo en el encabezado).
2. N1 (encabezado: tema + menú con Idioma y Sair).
3. N5 (casillas de Escolher con el estilo del tema).
4. N3 (detalle de tarefa: punteado solo en el título + texto de ayuda + "≈ 1h 45min").
5. N4 (anillo de progreso con el número adentro y estado vacío).
6. N7, N8, N9 y N11.
7. N10 (manifest.json + íconos + meta description).
No toques la sección "Lo que ya está muy bien".
```
