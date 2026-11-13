# Guía visual de IAmigo (a partir de las referencias de Tiimo)

**Fecha:** 12/11/2026
**Referencias:** carpeta "IAmigo-Final-Round pantallas de referencia tiimo" (01–03 claro, 04 oscuro, logo)
**Complementa a:** `AUDITORIA-UI-IAmigo.md`. Los tokens de este archivo **reemplazan** los valores de color propuestos en A1, A2 y A3 de la auditoría; los demás puntos de la auditoría siguen vigentes.

---

## 1. Qué tomar de cada referencia

| Ref. | Qué se ve | Qué tomar para IAmigo | Qué NO tomar |
|---|---|---|---|
| **01 claro** (Tiimo, asistente) | Mascota con un brillo lila, pregunta abierta en serif ("What should we tackle next?"), chips de sugerencias, campo grande de texto libre y micrófono | El tono conversacional de la Caixa de entrada: pregunta cálida en serif, chips con atajos ("Organizar meu dia", "Priorizar tarefas") y un textarea grande sin caja visible | Los emojis dentro de los chips (ver auditoría, M4); usar íconos SVG |
| **02 claro** (paleta) | Lavandas muy suaves: `#e5def5` `#ddd4f3` `#d6ccf2` `#d2c6f2` | Fondos y superficies del tema claro | — |
| **03 claro** (Pastel Rainbow) | `#E7C6FF` `#C8B6FF` `#B8C0FF` `#CEE5FF`… | Acentos **de fondo** para distinguir estados o categorías (Agora, Depois, Feito, chips) | Usarlos como color de texto, porque sobre blanco no tienen contraste |
| **04 oscuro** (Day at a glance) | Fondo violeta muy oscuro con degradé, tarjetas translúcidas con borde fino, anillos de progreso, título grande y flecha para volver | El tema oscuro completo: fondo con un brillo radial, tarjetas con borde de 1px, un **anillo de progreso** para el tiempo del día y tarjetas tipo "resumen" en Encerrar o dia | Los datos de salud (pasos, sueño), que no corresponden a la app |
| **Logo** | "IA" en violeta `#C480FC`, "migo" en blanco, punto con brillo sobre la "i", "ASSISTENTE INTELIGENTE" espaciado, fondo `#130828` | Marca en el encabezado, splash/login y el color de acento del tema oscuro | — |

**En resumen:** pasar del azul/gris actual a un **violeta lavanda calmado**. El tema claro sería lavanda pastel y el oscuro, violeta profundo con brillo. La estructura actual de pantallas se mantiene.

---

## 2. Tokens nuevos (reemplazan el bloque `:root` actual)

Todos los pares fueron medidos según WCAG. El texto cumple **AA (≥ 4,5:1)** y los bordes de campos y el foco cumplen **≥ 3:1**.

```css
:root {
  /* Tema claro: lavanda */
  --fundo: #f7f4ff;           /* ref. 02 */
  --superficie: #ffffff;
  --superficie-2: #efe9fd;    /* tarjetas secundarias, chips */
  --texto: #241a3a;           /* 15,1:1 */
  --texto-suave: #6a6380;     /* 5,2:1 */
  --borda: #e5def5;           /* separadores y tarjetas (decorativo) */
  --borda-campo: #8e86a6;     /* inputs: 3,4:1 */
  --primaria: #6b45d9;        /* 5,6:1 sobre fundo · texto blanco 6,0:1 */
  --primaria-texto: #ffffff;
  --primaria-hover: #5f3dc4;
  --primaria-suave: #e7c6ff;  /* ref. 03, solo fondos */
  --foco: #6b45d9;
  --acento-1: #c8b6ff;        /* Agora */
  --acento-2: #b8c0ff;        /* Depois */
  --acento-3: #cee5ff;        /* Feito / info */
  --aviso-fundo: #fff4d6;
  --aviso-texto: #6b5210;
  --brilho: radial-gradient(60% 40% at 50% 0%, #e7c6ff66, transparent 70%);
  --raio: 16px;
  --raio-chip: 999px;
  --espaco: 16px;
  --fonte: "Nunito", system-ui, -apple-system, "Segoe UI", sans-serif;   /* ver sección 4 */
  --fonte-titulo: "Fraunces", Georgia, serif;
}

/* Tema oscuro: violeta profundo (ref. 04 + logo) */
@media (prefers-color-scheme: dark) {
  :root:not([data-tema="claro"]) { /* mismos valores que el bloque de abajo */ }
}
:root[data-tema="escuro"] {
  --fundo: #140b26;           /* fondo del logo */
  --superficie: #221838;
  --superficie-2: #2c2046;
  --texto: #f4f1fb;           /* 17:1 */
  --texto-suave: #b3a9c9;     /* 7,5:1 sobre superficie */
  --borda: #3a2d57;
  --borda-campo: #6e6290;     /* 3,0:1 */
  --primaria: #c98bff;        /* violeta del logo · 6,9:1 */
  --primaria-texto: #140b26;  /* 7,8:1 */
  --primaria-hover: #d6a6ff;
  --primaria-suave: #3a2560;
  --foco: #c98bff;
  --acento-1: #4a3480;
  --acento-2: #2f3a7a;
  --acento-3: #1f3d5c;
  --aviso-fundo: #3a3220;
  --aviso-texto: #f3dc9b;
  --brilho: radial-gradient(70% 45% at 50% 0%, #6b3fb04d, transparent 70%);
}

body { background: var(--brilho), var(--fundo); background-attachment: fixed; }
input, textarea, .minutos { border-color: var(--borda-campo); }
```

> Los colores `--acento-*` se usan siempre como **fondo** con `--texto` encima (entre 9 y 12:1 en claro). Nunca como color de texto.

---

## 3. Cambios por pantalla

### Login / Cadastro (logo)
- Reemplazar el texto "IAmigo" por el wordmark en Nunito 800 (código en la sección 4) y el subtítulo "ASSISTENTE INTELIGENTE".
- Fondo con `--brilho`, que en oscuro reproduce el logo.

### Caixa de entrada (ref. 01)
- Título como pregunta cálida en `--fonte-titulo`: "O que está na sua cabeça?".
- **Chips de sugerencia** con scroll horizontal, encima del textarea: `background: var(--superficie-2); border-radius: var(--raio-chip); min-height: 44px; padding: 0 16px`. Al tocar uno, se completa el textarea.
- Textarea más grande (3–4 líneas visibles, `font-size: 1.15rem`), con el botón "+" adentro, abajo a la derecha, como en la referencia.
- Opcional, para más adelante: botón de micrófono (Web Speech API).

### Hoje (ref. 04)
- Tarjeta "Agora" con `background: var(--superficie)`, borde de 1px `var(--borda)` y una franja o anillo en `--primaria`.
- Reemplazar la barra de tiempo segmentada por un **anillo de progreso** (SVG `circle` + `stroke-dasharray`). Ya existe `.relogio`, así que conviene reutilizarlo en tamaño chico (64px) junto a "Mais ou menos 1h45".
- Secciones Agora / Depois / Feito con un punto de color `--acento-1/2/3` al lado del H2.

### Detalle de tarefa
- Encabezado como en la ref. 04: flecha "←" de 44px con `aria-label="Voltar"` y el título grande al lado.
- Pasos en tarjetas `--superficie` con borde de 1px. La pastilla de minutos en `--superficie-2`.

### Encerrar o dia
- Tarjeta "Resumo" como en la ref. 04: un ícono ✦ en SVG, una frase de cierre y 2 o 3 mini-tarjetas con anillo (tareas hechas, minutos de foco, pasos completados).

### Foco
- El `.relogio` usa `--primaria` sobre `--borda`. En oscuro, agregar `filter: drop-shadow(0 0 12px var(--primaria))` al trazo, el mismo brillo del logo, y desactivarlo con `prefers-reduced-motion`.

---

## 4. Tipografía (decidido: Fraunces + Nunito)

| Uso | Fuente | Detalle |
|---|---|---|
| Títulos H1 (pantallas principales, celebración, Encerrar o dia) | **Fraunces** 600 | `font-variation-settings: "SOFT" 100, "WONK" 0` · `letter-spacing: -0.01em` |
| Todo lo demás (texto, botones, pasos, navegación) | **Nunito** 400–800 | Base `18px` (Nunito se ve algo más chica que `system-ui`) |
| Logo | **Nunito 800** | Ver abajo |

Regla: Fraunces **solo** en H1. Nunca en botones, listas ni campos.

```html
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght,SOFT@9..144,600,100&family=Nunito:wght@400..800&display=swap" rel="stylesheet">
```

```css
:root {
  --fonte: "Nunito", system-ui, -apple-system, "Segoe UI", sans-serif;
  --fonte-titulo: "Fraunces", Georgia, serif;
}
body { font-family: var(--fonte); font-size: 18px; }
h1 {
  font-family: var(--fonte-titulo);
  font-weight: 600;
  font-variation-settings: "SOFT" 100, "WONK" 0;
  letter-spacing: -0.01em;
}
```

### Logo (wordmark en Nunito 800)
Comparación visual en `logo-opciones.png`. Se elige **B: Nunito 800**, que es redondo y amable, combina con el resto de la interfaz y se lee bien en tamaño chico.

- "IA" en `--primaria` y "migo" en `--texto`.
- La "i" se escribe sin punto (`ı`, i sin punto) y se reemplaza por un **punto con brillo**, el mismo detalle del logo original.
- El subtítulo "ASSISTENTE INTELIGENTE" va en Nunito 700, `letter-spacing: .42em`, `color: var(--texto-suave)`. Solo en login y splash, no en el encabezado.

```html
<p class="marca" aria-label="IAmigo">
  <span aria-hidden="true"><span class="marca-ia">IA</span>m<span class="marca-i">ı</span>go</span>
</p>
```
```css
.marca { font-family: var(--fonte); font-weight: 800; color: var(--texto); }
.marca-ia { color: var(--primaria); }
.marca-i { position: relative; display: inline-block; }
.marca-i::after {
  content: ""; position: absolute; left: 50%; top: .2em; transform: translateX(-50%);
  width: .15em; height: .15em; border-radius: 50%;
  background: var(--primaria);
  box-shadow: 0 0 .25em .06em var(--primaria);
}
```
> Más adelante, cuando el logo esté definido, conviene pasarlo a un SVG para que se vea igual en todos los dispositivos.

---

## 5. Íconos (ver auditoría, M4)
Reemplazar los emojis por SVG de **Lucide**, con trazo de 1.75 y `currentColor`: `sun`, `moon`, `bell`, `bell-off`, `sparkles` (el ✦ de "Summary"), `arrow-left`, `chevron-right`, `mic`, `plus`, `check`.

---

## 6. Prompt para Claude Code (VS Code)

> Lee `GUIA-VISUAL-IAmigo.md` y `AUDITORIA-UI-IAmigo.md`. Trabaja en este orden y muéstrame el diff antes de cada paso:
> 1. Reemplaza los tokens de color en el CSS por los de la sección 2 de la guía (claro y oscuro), incluido `--borda-campo` y el fondo con `--brilho`.
> 2. Tipografía Fraunces (solo H1) + Nunito (todo lo demás) y el wordmark del logo en Nunito 800 en Login, Cadastro y el encabezado (sección 4).
> 3. Reemplaza los emojis por íconos SVG de Lucide (sección 5).
> 4. Caixa de entrada con chips de sugerencia y un textarea más grande (sección 3).
> 5. Anillo de progreso en Hoje, reutilizando `.relogio` (sección 3).
> 6. Puntos A4, M1 y M2 de la auditoría.
> No cambies la estructura de rutas ni la lógica de la API. Respeta `prefers-reduced-motion` y no bajes de 44px en ningún elemento que se toque.
