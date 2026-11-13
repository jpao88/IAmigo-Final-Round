# Auditoría UI/UX — IAmigo

**Fecha:** 12/11/2026 · **URL:** https://iamigo-lzdqn.ondigitalocean.app/
**Cuenta usada:** cuenta de prueba (Rafaela) · **Herramientas:** skills ui-ux-pro-max + design, inspección del DOM/CSS y cálculo de contraste WCAG
**Pantallas revisadas:** Login, Hoje, Caixa de entrada, Detalle de tarefa, Escolher tarefas. Tema claro y oscuro.
**No revisadas** (para no modificar datos): Foco (temporizador), Encerrar o dia, Bienvenida/Onboarding y Cadastro.

---

## Resumen

La base es muy buena para una app pensada para personas con TDAH:

- Una sola columna (máx. 440px).
- Un límite de 3 tareas por día.
- Tareas divididas en pasos con minutos estimados.
- Celebración al terminar.
- Tokens CSS con tema claro y oscuro.
- `prefers-reduced-motion` respetado.
- `:focus-visible` en casi todo.
- Áreas táctiles ≥ 44px, labels reales y `aria-live` en las pantallas.

Los problemas importantes son de **contraste en el tema claro** y de **bordes poco visibles**. Además hay detalles de **affordance**, porque no siempre se nota qué cosas son editables o qué botón realiza la acción.

| Prioridad | Cantidad |
|---|---|
| 🔴 Alta (accesibilidad / puede bloquear) | 4 |
| 🟠 Media (fricción de uso) | 6 |
| 🟢 Baja (pulido) | 5 |

---

## 🔴 Prioridad alta

### A1. Color primario del tema claro sin contraste suficiente
`--primaria: #4f6df5` tiene **3,95:1** sobre `--fundo` y **4,34:1** sobre blanco. El texto blanco del botón principal también queda en **4,34:1**. Los tres casos están por debajo del 4,5:1 que exige WCAG AA. Afecta a "+ Hoje", los links ("Escolher mais tarefas", "Crear una cuenta"), "Você pode escolher mais 3." y los botones "Entrar", "Pronto" y "Encerrar o dia".

**Arreglo** (en `:root`, tema claro):
```css
--primaria: #3d5ae0;        /* 5,11:1 sobre fundo · 5,62:1 texto blanco */
--primaria-hover: #3249c4;
```

### A2. El anillo de foco no se ve en el tema claro
`--foco: #9fb0ff` tiene **1,89:1** sobre el fondo, y el mínimo para indicadores de foco es 3:1. Quien navega con teclado no sabe dónde está parado. En el tema oscuro (`#5b6fd6`, 3,82:1) sí cumple.

**Arreglo:**
```css
:root { --foco: #3d5ae0; }   /* igual a la primaria nueva, 5,1:1 */
```

### A3. Los bordes de los campos casi no se ven (ambos temas)
`--borda` frente a `--superficie` da **1,34:1** en oscuro y **1,39:1** en claro. Para delimitar un campo de formulario WCAG 1.4.11 pide 3:1. En oscuro, además, la superficie del input apenas se distingue del fondo (1,13:1). El problema se ve en "Contraseña" en el login y en el textarea de la caixa de entrada: cuesta saber dónde se escribe.

**Arreglo:** crear un token solo para campos y dejar `--borda` como está para tarjetas y separadores.
```css
:root { --borda-campo: #8a8679; }                 /* 3,6:1 sobre blanco */
/* oscuro (en los dos bloques) */ --borda-campo: #75737f;   /* 3,3:1 */

input, textarea, .minutos { border-color: var(--borda-campo); }
```

### A4. "Apagar tarefa" no tiene forma de deshacerse
`tarefa.js` usa `confirm()` del navegador, que es feo, no respeta el tema y se acepta sin leer. Para personas con TDAH es mejor no confirmar antes y ofrecer **deshacer** después: un toast "Tarefa apagada · Desfazer" durante unos 6 segundos, aprovechando el `.confirmacao` que ya existe.

---

## 🟠 Prioridad media

### M1. No se nota que los pasos y el título se pueden editar
En el detalle de tarefa, el título y cada paso son textareas con borde transparente, y el borde solo aparece con `:hover`. En el celular no hay hover, así que parecen texto fijo.
**Arreglo:** mostrar siempre un borde sutil o un ícono de lápiz al costado. También sirve un subrayado punteado debajo del título.

### M2. En "Escolher tarefas" el botón principal no hace lo que parece
El botón grande dice **"Voltar para Hoje"** aunque haya tareas marcadas, y arriba también está "← Hoje". Hay dos salidas y ninguna dice "confirmar".
**Arreglo:**
- Con 0 marcadas, el botón dice "Voltar para Hoje", como ahora.
- Con 1 o más marcadas, cambia a **"Adicionar 2 tarefas a Hoje"**.

### M3. El idioma de la interfaz es confuso
El botón "ES" en el encabezado dice a qué idioma vas a cambiar, no en cuál estás: con la interfaz en portugués aparece "ES". Una sigla suelta se lee fácil como "estado actual". El `<html lang>` sí se actualiza bien (`pt-BR`).
**Arreglo:** escribir el idioma completo, "Español", igual que en el login, o usar un ícono de globo con el texto "Idioma".

### M4. Íconos hechos con emoji
El tema (☀️ / 🌙), el sonido (🔔 / 🔕) y la bienvenida (✏ ✂ 📌 🎉) usan emoji. Cada sistema operativo los dibuja distinto, no heredan el color del tema y algunos lectores de pantalla los leen en voz alta ("sol con rayos").
**Arreglo:** reemplazarlos por SVG inline con `stroke="currentColor"` y `aria-hidden="true"`. El texto accesible ya está en el `aria-label` del botón. Lucide sirve como fuente (sun, moon, bell, bell-off, pencil, scissors, pin, party-popper).

### M5. La pestaña activa de la navegación inferior se distingue poco
La pestaña activa usa `--fundo` sobre `--superficie`, con una diferencia de 1,13:1. Solo la distingue el color del texto.
**Arreglo:** agregar un indicador más visible, como una barra de 3px arriba en `--primaria` o un fondo `color-mix(in srgb, var(--primaria) 14%, var(--superficie))`. Sumar un ícono a cada pestaña también ayuda a ubicarse rápido.

### M6. Los minutos se editan con un campo diminuto
`.minutos input` tiene `width: 2.2em`. La pastilla entera mide 44px de alto, pero la parte que realmente se puede tocar es muy angosta.
**Arreglo:** hacer que al tocar la pastilla se enfoque el input (`label` envolvente o `onclick → input.focus()`). Una alternativa es reemplazarlo por botones −/+ de 5 minutos.

---

## 🟢 Prioridad baja (pulido)

- **B1. No es instalable como app (PWA).** Faltan `manifest.json`, favicon e íconos. Para una app de uso diario, poder "agregarla a la pantalla de inicio" ayuda mucho a crear el hábito. `theme-color` ya existe.
- **B2. Falta `<meta name="description">`.** Se nota cuando se comparte el link.
- **B3. El encabezado tiene tres acciones chicas juntas** (ES, tema, Sair). "Sair" está al alcance de un toque accidental y no pide confirmación. Se podrían mover a un menú "⋯" o a una pantalla de ajustes.
- **B4. Placeholder como única guía.** "Uma ideia por linha" desaparece al escribir. Mejor dejarlo como texto de ayuda debajo del campo, en `--texto-suave`.
- **B5. En escritorio la barra inferior ocupa todo el ancho** y el contenido mide 440px. Habría que limitar `.navegacao` con `max-width` y centrarla, o pasar a un riel lateral en pantallas de 900px o más.

---

## Lo que ya está bien (no tocar)

- Jerarquía clara: un H1 por pantalla y un solo CTA principal.
- Límite diario de tareas, pasos con minutos y barra de tiempo total: reducen la carga cognitiva.
- `prefers-reduced-motion`, `:focus-visible`, `aria-pressed` y `aria-current`, labels ocultos (`.rotulo-oculto`) y `autocomplete` correctos en el login.
- Áreas táctiles ≥ 44px y `env(safe-area-inset-bottom)` en la navegación.
- Tokens CSS bien organizados: con ellos, los arreglos A1–A3 son cambios de pocas líneas.
- El tema oscuro cumple AA en todo el texto (entre 5,6 y 7,2:1).

---

## Contrastes medidos

| Par | Oscuro | Claro |
|---|---|---|
| Texto suave / fondo | 7,23 ✅ | 4,88 ✅ |
| Primaria / fondo | 6,35 ✅ | **3,95 ❌** |
| Texto del botón / primaria | 6,86 ✅ | **4,34 ❌** |
| Foco / fondo | 3,82 ✅ | **1,89 ❌** |
| Borde / superficie | **1,34 ❌** | **1,39 ❌** |
| Aviso | 9,37 ✅ | 6,75 ✅ |

---

## Prompt sugerido para Claude Code (VS Code)

> Lee `AUDITORIA-UI-IAmigo.md` y aplica primero A1, A2 y A3 (solo cambios de tokens CSS). Después implementa A4 con un toast de "Desfazer" reutilizando `.confirmacao`, y luego M1 y M2. No cambies nada de la sección "Lo que ya está bien". Muéstrame el diff antes de cada bloque.
