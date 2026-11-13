# Tarjeta "Agora": vidrio + borde aurora + anillo

**Fecha:** 13/11/2026 · **Decisión:** en tema oscuro, vidrio (liquid glass) con borde aurora y anillo de tiempo; en tema claro, borde aurora con anillo.
**Vista previa:** `tarjeta-agora-final.png` (izquierda oscuro, derecha claro). Las opciones descartadas están en `tarjeta-agora-opciones.png`.
**Hacer esto antes que la auditoría v2.**

Contraste medido sobre la vista previa: el título da entre 7,8 y 8,9:1 en oscuro sobre el vidrio y 15:1 en claro. "min" dentro del anillo queda por encima de 6:1. El botón no cambia.

---

## 1. Qué se elimina

En `estilos.css`, quitar la franja lateral (el look "muy de Claude"):

```css
/* BORRAR */
.cartao-ahora { border: 2px solid var(--primaria); padding-top: 8px; }
.cartao-ahora .tarefa-link { font-size: 1.3rem; font-weight: 700; }
.cartao-ahora, .retomar { border: 1px solid var(--borda); box-shadow: inset 4px 0 0 var(--primaria); }
```
Si `.cartao-ahora` o `.retomar` aparecen en otras reglas compartidas, como `.tarefa, .tarefa-dia, .passo… { border: … }`, sacarlos solo de esas reglas.

---

## 2. Cambio de HTML (en `js/telas/hoje.js`, donde se arma la tarjeta "Agora")

Agregar el anillo antes del título, ocultar visualmente los minutos (siguen disponibles para el lector de pantalla) y poner el ícono "play" de Lucide en el botón:

```html
<li class="tarefa-dia cartao-ahora" data-id="43">
  <div class="anel-agora" aria-hidden="true">
    <svg viewBox="0 0 64 64" focusable="false">
      <circle class="anel-fundo" cx="32" cy="32" r="28"></circle>
      <circle class="anel-progresso" cx="32" cy="32" r="28"
              stroke-dasharray="175.93" stroke-dashoffset="0"></circle>
    </svg>
    <span class="anel-agora-texto">10<small>min</small></span>
  </div>

  <a class="tarefa-link" href="#/tarefa/43">Llevar a mi perro a la veterinaria</a>
  <p class="minutos-dia rotulo-oculto">10 min</p>

  <a class="botao botao-empezar" href="#/foco/43" aria-label="Começar: Llevar a mi perro a la veterinaria">
    <svg class="icone" viewBox="0 0 24 24" width="18" height="18" fill="currentColor" aria-hidden="true" focusable="false"><path d="M7 4v16l13-8z"/></svg>
    Começar
  </a>
  <!-- .acoes-ordenar sin cambios -->
</li>
```

**Texto dentro del anillo:**
- Menos de 60 min: `10<small>min</small>`.
- 60 o más: `1h<small>30</small>`, o solo `2h` si es exacto.
- Si la tarea no tiene minutos estimados, no mostrar el anillo y que el título ocupe las dos columnas (`grid-column: 1 / -1`).

**El anillo** por ahora siempre está completo (`dashoffset = 0`), porque representa el tiempo estimado. Si más adelante la tarea ya fue empezada (estado "retomar"), se puede vaciar en proporción: `dashoffset = 175.93 × (minutos_hechos / minutos_totales)`.

---

## 3. CSS nuevo (agregar al final de `estilos.css`)

```css
/* ===== Tarjeta "Agora": vidrio + borde aurora + anillo ===== */

/* Tokens (claro) */
:root {
  --agora-fundo:
    radial-gradient(90% 80% at 0% 0%, #e7c6ff59, transparent 60%) padding-box,
    linear-gradient(var(--superficie), var(--superficie)) padding-box;
  --agora-borda: linear-gradient(135deg, #6b45d9, #8197ff 50%, #b8c0ff);
  --agora-sombra: 0 0 24px #6b45d92e, 0 8px 24px #6b45d914;
  --agora-reflexo: none;
  --agora-blur: none;
}
/* Tokens (oscuro): mismos valores en los dos bloques */
@media (prefers-color-scheme: dark) {
  :root:not([data-tema="claro"]) {
    --agora-fundo:
      linear-gradient(135deg, #ffffff0f, #ffffff05) padding-box,
      radial-gradient(80% 90% at 0% 0%, #9b5cff40, transparent 60%) padding-box,
      radial-gradient(70% 80% at 100% 100%, #4f6df52e, transparent 60%) padding-box,
      linear-gradient(#1d1430d1, #1d1430d1) padding-box;
    --agora-borda: linear-gradient(135deg, #c98bff, #7f93ff 50%, #cee5ff);
    --agora-sombra: 0 0 28px #c98bff40, 0 10px 30px #00000059;
    --agora-reflexo: inset 0 1px 0 #ffffff2e;
    --agora-blur: blur(16px) saturate(150%);
  }
}
:root[data-tema="escuro"] {
  --agora-fundo:
    linear-gradient(135deg, #ffffff0f, #ffffff05) padding-box,
    radial-gradient(80% 90% at 0% 0%, #9b5cff40, transparent 60%) padding-box,
    radial-gradient(70% 80% at 100% 100%, #4f6df52e, transparent 60%) padding-box,
    linear-gradient(#1d1430d1, #1d1430d1) padding-box;
  --agora-borda: linear-gradient(135deg, #c98bff, #7f93ff 50%, #cee5ff);
  --agora-sombra: 0 0 28px #c98bff40, 0 10px 30px #00000059;
  --agora-reflexo: inset 0 1px 0 #ffffff2e;
  --agora-blur: blur(16px) saturate(150%);
}

/* Tarjeta: reemplaza la franja lateral (box-shadow inset 4px) */
.cartao-ahora {
  position: relative;
  border: 1.5px solid transparent;
  border-radius: 24px;
  padding: 16px;
  background:
    var(--agora-fundo),
    var(--agora-borda) border-box;
  box-shadow: var(--agora-reflexo), var(--agora-sombra);
  -webkit-backdrop-filter: var(--agora-blur);
  backdrop-filter: var(--agora-blur);
  display: grid;
  grid-template-columns: 64px 1fr;
  grid-template-areas:
    "anel   titulo"
    "botao  botao";
  column-gap: 14px;
  row-gap: 14px;
  align-items: center;
}
.cartao-ahora .anel-agora     { grid-area: anel; }
.cartao-ahora .tarefa-link    { grid-area: titulo; padding: 0; font-size: 1.3rem; font-weight: 800; line-height: 1.25; }
.cartao-ahora .tarefa-link:hover { background: none; text-decoration: underline; text-decoration-color: var(--primaria); }
.cartao-ahora .botao-empezar  { grid-area: botao; margin: 0; }
.cartao-ahora .acoes-ordenar  { grid-column: 1 / -1; }

/* Anillo del tiempo estimado */
.anel-agora { position: relative; width: 64px; height: 64px; }
.anel-agora svg { width: 100%; height: 100%; display: block; }
.anel-agora circle { fill: none; stroke-width: 6; }
.anel-agora .anel-fundo { stroke: var(--superficie-2); }
.anel-agora .anel-progresso { stroke: var(--primaria); stroke-linecap: round; transform: rotate(-90deg); transform-origin: 50% 50%; }
.anel-agora-texto {
  position: absolute; inset: 0; display: flex; flex-direction: column;
  align-items: center; justify-content: center; line-height: 1;
  font-weight: 800; font-size: 1.05rem; color: var(--texto);
}
.anel-agora-texto small { font-size: .7rem; font-weight: 700; color: var(--texto); opacity: .85; margin-top: 2px; }

/* "Retomar" comparte el borde aurora, sin vidrio */
.retomar {
  border: 1.5px solid transparent;
  border-radius: 24px;
  background: linear-gradient(var(--superficie), var(--superficie)) padding-box, var(--agora-borda) border-box;
  box-shadow: none;
}

/* Accesibilidad: sin transparencia si el usuario lo pide */
@media (prefers-reduced-transparency: reduce) {
  .cartao-ahora { background: linear-gradient(var(--superficie), var(--superficie)) padding-box, var(--agora-borda) border-box; backdrop-filter: none; -webkit-backdrop-filter: none; }
}
/* Modo alto contraste de Windows */
@media (forced-colors: active) {
  .cartao-ahora, .retomar { border: 2px solid CanvasText; background: Canvas; }
}
```

---

## 4. Verificar al terminar

- [ ] Tema oscuro: la tarjeta se ve translúcida, con el brillo violeta arriba a la izquierda y el borde degradé.
- [ ] Tema claro: tarjeta blanca con borde degradé y un brillo suave; **sin** desenfoque.
- [ ] Con el botón de tema forzado (`data-tema`) se ve igual que con el tema del sistema.
- [ ] A 375px el título hace salto de línea al lado del anillo y nada se sale de la tarjeta.
- [ ] Con "Ordenar" activo, los botones subir/bajar/tirar aparecen debajo del botón, a todo el ancho.
- [ ] El lector de pantalla lee "Llevar a mi perro… 10 min" y el botón "Começar: …".
- [ ] "Vamos continuar de onde você parou?" (`.retomar`) usa el mismo borde aurora.

## 5. Prompt para Claude Code

```
Lee @docs/diseno/TARJETA-AGORA.md y mira @docs/diseno/tarjeta-agora-final.png.
Aplica las secciones 1, 2 y 3 tal cual: primero el CSS (borrar + agregar), después
el cambio de HTML en hoje.js con el formato de horas del anillo. Muéstrame el diff
y luego revisa el checklist de la sección 4.
```
