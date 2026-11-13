# IAmigo V1

IAmigo es una app web de organización para adultos con TDAH. Lleva a la persona de "tengo mil cosas en la cabeza" a "terminé lo importante de hoy" con un ciclo diario de cinco etapas: capturar, desmenuzar (la IA divide en pasos), planear hoy, hacer (modo foco) y cerrar el día. Se diseña primero para celular.

## Documentación

Antes de proponer o escribir código, consulta lo que corresponda en `docs/`:

- `docs/hoja-de-ruta.md` — fases del proyecto y tareas pendientes. Estamos en la **Fase 2 · Construcción de la V1**.
- `docs/recorrido-v1.md` — recorrido del usuario pantalla por pantalla y los siete principios de diseño.
- `docs/modelo-de-datos.md` — modelo de datos cerrado y decisiones de diseño.
- `docs/backlog-v1.md` — épicas e historias de usuario (IDs H0.1, H1.1…) y definición de terminado.
- `docs/guion-validacion.md` — guion y resultados de la validación con usuarios.
- `database/schema.sql` — esquema MySQL 8. Si cambia el modelo, actualizar también `docs/modelo-de-datos.md`.

## Stack

- Backend en capas (Controller / Service / Repository) con autenticación JWT, basado en IAmigo-Final.
- Base de datos MySQL 8.
- IA con Gemini.
- Front en JavaScript puro, organizado en módulos.

## Convenciones

- **Nombres de código y base de datos en portugués** (tablas, columnas, clases, funciones, variables, endpoints): `tarefas`, `passos`, `data_planejada`, `concluido`…
- **Explicaciones para Pablo en español**: respuestas, resúmenes, planes y mensajes de commit.
- Textos de la interfaz en español y portugués de Brasil, cortos y amables, siguiendo los principios de diseño del recorrido. Nunca se escriben en las pantallas: van en `frontend/js/i18n.js` (las dos lenguas con las mismas claves; `tests/test_traducoes.py` lo controla) y se usan con `t("clave")`.
- Trabajar una tarea de la hoja de ruta a la vez y pedir confirmación antes de pasar a la siguiente.

## Entorno

- Pablo trabaja en una sola laptop personal, que lleva también al instituto.
- GitHub (`https://github.com/jpao88/IAmigo-Final-Round`) guarda el código: hacer `git pull` al empezar y `git push` al terminar.
- Backend en Python con entorno virtual en `backend/.venv` (no se sube). Tests: `.venv\Scripts\python -m unittest discover -s tests` desde `backend/`; no necesitan MySQL.
- **Base de datos: MySQL en Aiven** (plan Free, North America), la misma desde cualquier lugar. Exige SSL con el certificado `ca.pem` de Aiven, guardado fuera del repositorio. Si el servicio no responde, puede estar apagado por inactividad: se enciende desde el panel de Aiven.
- **El Wi-Fi del instituto bloquea el puerto de Aiven** (solo deja salir puertos comunes como 80, 443 y 3306). Allí Pablo usa datos móviles.
- Las claves (JWT, Gemini, base de datos) van en `backend/.env`, que nunca se sube.
- `_referencia/` (copia de IAmigo-Final) está en `.gitignore`; puede no existir y ya no hace falta.

## Estado actual

Actualizar esta sección al terminar cada tarea.

**Fase 1 cerrada el 11 de noviembre de 2026.** Backend conectado a Aiven con SSL (`DB_SSL_CA`), `.env.example` como plantilla, CORS con `CORS_ORIGINS`. Front en `frontend/` con JavaScript puro y módulos ES (`python -m http.server 5500`): `js/api.js` llama al backend y traduce sus errores al español, `js/sessao.js` guarda el token, `js/roteador.js` usa rutas por hash y cada pantalla vive en `js/telas/`. Registro, login y cerrar sesión (H0.1–H0.3) funcionan; una compañera levantó el proyecto solo con el `README.md`. Usuario de prueba: `prueba@iamigo.test` (id 1).

**Sprint 1 · Capturar cerrado el 12 de noviembre de 2026** (H1.1–H1.4):
- Backend: `POST /usuarios/{id}/tarefas/lote` (una tarea por línea, ignora vacías, todo o nada, máx. 50 por vez y 200 caracteres) y `GET /usuarios/{id}/tarefas/bandeja?hoje=AAAA-MM-DD` (sin fecha o de días pasados, sin concluir; la fecha la manda el front porque vale la hora local). Las de un mismo lote comparten `criado_em` para conservar el orden en que se escribieron.
- Front: `#/bandeja` es la pantalla de inicio ("¿Qué tienes en la cabeza?" con la Bandeja debajo). Enter guarda, Shift+Enter baja de línea. La tarea aparece al instante y se guarda en segundo plano; si falla, el texto vuelve al campo. Al abrir muestra la copia local (`localStorage`) y actualiza en silencio; "Salir" borra esas copias.
- Hoy (Sprint 3) será otra pantalla; cuando exista, cambiar `TELA_INICIAL` en `js/roteador.js`.

**Sprint 2 · Desmenuzar cerrado el 12 de noviembre de 2026** (H2.1–H2.4):
- IA: `core/ia_service.py` es el único archivo que conoce el proveedor (Gemini `gemini-2.5-flash`, plan gratuito). Prompt en español, respuesta JSON estructurada (texto + minutos), pasos de 5 a 25 min idealmente; `_normalizar` limpia la respuesta (máx. 7, minutos 1–120 o 10). Tarda ~5 s. Si falla o no hay clave: `FalhaIA` → 503.
- Backend: `POST .../passos/gerar` (solo si la tarea no tiene pasos), `POST .../passos` (a mano, 10 min si no se indica), `PUT .../passos/{id}` (texto y minutos), `PUT .../passos/ordem` (todos los pasos visibles, en el orden nuevo), `DELETE .../passos/{id}`. Los `substituido` quedan fuera de la ordem. `TarefaService` recibe `gerador_de_passos` para que los tests no llamen a Gemini.
- Front: `#/tarefa/:id` (`js/telas/tarefa.js`); el roteador acepta parámetros numéricos. Sin pasos: "Que IAmigo lo divida" y "Prefiero escribirlos yo". Con pasos: edición en línea, ↑ ↓ para reordenar, ✕ para borrar, total en texto y barra de tiempo. Todo optimista, como la Bandeja.

**Sprint 3 · Planear hoy cerrado el 12 de noviembre de 2026** (H3.1–H3.6):
- Backend: `GET .../tarefas/hoje?data=` (con `minutos_restantes`: pasos visibles sin concluir, o 10 si no tiene pasos), `POST .../tarefas/hoje` (`ids` + `data`; uno para "+ Hoy", varios para "Elegir"; todo o nada), `PUT .../tarefas/hoje/ordem`, `DELETE .../tarefas/{id}/hoje` (vuelve a la Bandeja) y `PUT /usuarios/{id}/limite-hoje` (1–5). Para el límite solo cuentan las tareas de hoy sin concluir; si no cabe: `LimiteHojeAtingido` → 422 "Hoje já está cheio.".
- Front: `#/hoje` es la pantalla de inicio, con pestañas Hoy · Bandeja (`js/componentes.js`). Hoy: tiempo total con barra (`js/tempo.js`), Ahora (tarjeta grande) y Después; ↑ ↓ y "Quitar" solo en modo "Ordenar"; debajo, las 3 tareas más recientes de la Bandeja con "+ Hoy" y "Ver toda tu Bandeja". `#/elegir`: casillas con contador ("Puedes elegir 2 más") y el cambio de límite. La lista de la Bandeja es un componente compartido (`js/lista-bandeja.js`). `[hidden]` siempre esconde (`display: none !important`).

**Sprint 4 · Hacer (modo foco) cerrado el 12 de noviembre de 2026** (H4.1–H4.7):
- Backend: `POST .../passos/{id}/concluir` (idempotente; devuelve `{passo, tarefa_concluida}` y concluye la tarea al terminar el último paso visible), `POST .../tarefas/{id}/concluir` (solo sin pasos pendientes) y `POST .../passos/{id}/dividir` ("Me atasqué": `ia_service.dividir_passo` da 2–3 pasos; el original queda `substituido`, los nuevos llevan `passo_origem_id` y los siguientes se corren). `TarefaService` recibe `divisor_de_passo` para los tests.
- Front: `#/foco/:id` (`js/telas/foco.js`), con "Empezar" en la tarjeta Ahora. Temporizador circular SVG que cuenta por la hora real y muestra minutos, no segundos; en cero no hay alarma ni rojo: "Tómate tu tiempo". Hecho con celebración (frases que rotan, "¡Terminaste!" al final) y sonido suave generado con Web Audio (`js/som.js`, se silencia con 🔔). Una tarea sin pasos es un paso de 10 min. `js/foco-estado.js` guarda tarea, paso y tiempo (solo el mismo día); Hoy ofrece "¿Seguimos donde quedaste?".

**Sprint 5 · Cerrar el día y primer uso cerrado el 12 de noviembre de 2026** (H5.1–H5.4, H6.1–H6.3):
- Backend: `services/dia_service.py` y `api/rotas_dias.py`: `GET /usuarios/{id}/dias/{data}` (resumen: pasos y tareas concluidos de las tareas planeadas para esa fecha, `concluidas`, `pendentes`, `fechado`), `POST .../dias/{data}/fechar` (idempotente, 204; no acepta fechas que no llegaron) y `GET .../dias/pendente?hoje=` (el último día con plano antes de hoy, si no se cerró; solo el más reciente). `PUT /usuarios/{id}/onboarding` marca la guía como hecha. Lo pendiente usa las rutas de Hoy: "Hacerla mañana" = `POST .../tarefas/hoje` con otra fecha, "Guardarla sin fecha" = `DELETE .../tarefas/{id}/hoje`.
- Front: `#/cerrar` y `#/cerrar/AAAAMMDD` (`js/telas/cerrar.js`; el roteador solo acepta números). Hoy muestra "Terminar el día" y, con todo hecho, "¡Completaste todo lo de hoy!"; el modo foco va al resumen si era la última tarea (mira la copia local de Hoy). Hoy pregunta una vez por día por el día pendiente (`iamigo.dia-verificado.<uid>`). `ErroApi.detalhe` guarda la frase original del backend.
- Primer uso: el registro lleva a `#/bienvenida` (cinco etapas en íconos, "Ya sé cómo funciona" para saltarla) y `#/primera-tarea`; `js/guia.js` recuerda la tarea guiada (`iamigo.guia.<uid>`) y la pantalla de la tarea y el modo foco muestran pistas "2 de 3" / "3 de 3". El primer "Hecho" muestra "¡Así funciona cada día!" y cierra la guía. Hoy manda a la bienvenida a quien tiene `onboarding_concluido = false` y no está en la guía.

**Fase 2 cerrada el 12 de noviembre de 2026.** Punto de control cumplido: una compañera completó el ciclo entero, sola, en la app publicada (anotado en `docs/guion-validacion.md`). La guía para probar en la red local sigue en `docs/prueba-celular.md`.

**Fase 3 · Prueba real y lanzamiento** (orden acordado: proteger rutas → publicar → siete principios → prueba de varios días):
- **Proteger las rutas, revisado el 12 de noviembre de 2026.** Dos barreras: la ruta exige ser el dueño del `{usuario_id}` (`exigir_dono`; solo login y crear cuenta son públicas) y cada service confirma que la tarea o el paso pertenece a esa persona (404 si no). `tests/test_dados_alheios.py` prueba todos los métodos con ids ajenos sin escribir nada; `test_toda_rota_esta_na_matriz` falla si una ruta nueva no está en la matriz de permisos.

- **Publicada el 12 de noviembre de 2026 en https://iamigo-lzdqn.ondigitalocean.app** (DigitalOcean App Platform, SFO3, al lado del MySQL de Aiven, que está en DigitalOcean Santa Clara). Una app con `web` (front estático, `/`) y `api` (backend, `/api`, 5 USD/mes); configuración en `.do/deploy.template.yaml` (el repo es privado: la app se creó desde el panel con GitHub conectado). Cada `git push` a `main` vuelve a publicar. Variables secretas en el panel: `DB_*`, `DB_SSL_CA_PEM` (contenido del `ca.pem`), `JWT_SECRET` propio, `GEMINI_API_KEY`; `DOCS_ABERTOS=nao`. Login limitado a 5 fallos en 15 min por correo (`core/limite_login.py`, 429), sesión de 30 días. Publicada, Hoy responde en ~0,5 s (antes ~3 s desde la laptop).
- Botón 🌙/☀️ en el encabezado (`js/tema.js`, clave `iamigo-tema`, que no se borra al salir).

- **IA:** Pablo decidió seguir con Gemini (12 de noviembre de 2026). Mientras solo la use él, plan gratuito; antes de que la usen otras personas, activar la facturación en Google AI Studio (misma clave y modelo, sin cambios de código) para que Google no use los títulos de las tareas. Kimi queda como alternativa.

- **Respaldos, revisado el 12 de noviembre de 2026.** Aiven confirmado en plan Free (1 CPU, 1 GB RAM, 1 GB de disco; el aviso de "trial" es publicidad para servicios pagos). Hace copias completas automáticas en `do-sfo2` con registros de cambios (restaurar = **Fork service**); no hace copias mientras está apagado por inactividad. Respaldo propio: `backend/scripts/exportar_dados.py` exporta `usuarios`, `tarefas`, `passos` y `fechamentos_dia` a JSON en `RESPALDOS_DIR` o `~/IAmigo-respaldos` (fuera del repo: tiene datos personales). Correrlo semanalmente durante la prueba y antes de cambios grandes.

- **Siete principios, revisados el 12 de noviembre de 2026** con capturas a 390 px de las 10 pantallas. Cambios: el texto del paso es un `textarea` que crece (antes se cortaba); en la tarea, ↑ ↓ ✕ solo en modo "Ordenar" (como en Hoy); minutos en una pastilla "10 min"; "Me atasqué" con estilo de enlace (`button.link-secundario`); en Hoy el tiempo va junto al título ("Hoy · unos 55 min", `formatarTempoCurto`) con la barra debajo; tarjetas sin borde (solo Ahora lo tiene; Elegir marca con `box-shadow`); `.confirmacao` es un aviso flotante sobre las pestañas y no ocupa espacio.

- **Prueba de varios días** (`docs/prueba-varios-dias.md`): piloto con 2 personas (Pablo y una compañera) desde el 13 de noviembre de 2026, con Gemini gratuito (decisión de Pablo: son solo 2 personas). `backend/scripts/resumo_uso.py [desde]` muestra por persona tareas creadas, pasos y tareas hechas, días con plan, días cerrados y último día activo, sin el texto de las tareas. La segunda ronda (3 a 5 personas de la validación) cumple el punto de control de la Fase 3; antes de ella, activar la facturación de Gemini.

- **Español y portugués de Brasil (12 de noviembre de 2026).** `js/i18n.js` con los diccionarios `es` y `pt` y `t("clave", ...args)` (algunos textos son funciones para números y plurales). Sin elección sigue el idioma del celular; botón ES/PT en el encabezado y enlace "Português"/"Español" en login, registro y bienvenida; se guarda en `iamigo-idioma` (no se borra al salir) y cambiar recarga la página. En portugués: Hoje, Caixa de entrada, Travei, Feito. Los errores del backend se traducen en `api.js` (pares `{es, pt}`). La IA escribe en el idioma de la persona: `POST .../passos/gerar?idioma=pt` y `.../dividir?idioma=pt` (`Literal["es","pt"]`, por defecto `es`); los prompts están en `TEXTOS` de `core/ia_service.py`.

- **Editar el título y borrar tareas (12 de noviembre de 2026, pedido del piloto: las tareas en español no se podían pasar a portugués).** `PUT /usuarios/{id}/tarefas/{id}` con `{titulo}` (`renomear_tarefa`: no vacío, máx. 200). En `#/tarefa/:id` el título es un `textarea.titulo-campo` que parece un título; Enter o salir del campo guarda. "Borrar tarea" al final, gris (sin rojo), con `confirm()`; vuelve a Hoy y limpia el modo foco si era esa tarea. Lo ya escrito no se traduce solo: son palabras de la persona.

- **Rediseño visual (13 de noviembre de 2026, rama `rediseno-visual`)** según `docs/diseno/GUIA-VISUAL-IAmigo.md` y `docs/diseno/AUDITORIA-UI-IAmigo.md`:
  - **Colores:** paleta lavanda (claro) y violeta profundo (oscuro), con contraste AA medido. `--borda-campo` para los campos (≥ 3:1) y brillo radial de fondo.
  - **Tipografía:** Fraunces solo en los `h1` y la frase de celebración; Nunito en todo lo demás (Google Fonts, base 18 px).
  - **Logo:** `marca()` en `js/componentes.js` (Nunito 800, punto con brillo sobre la "ı"); en grande con "ASISTENTE INTELIGENTE" en login, registro y bienvenida.
  - **Íconos:** SVG de Lucide en `js/icones.js`, sin emojis. Las flechas ya no van dentro de los textos traducidos.
  - **Bandeja:** chips con comienzos de tarea ("Llamar a…") que escriben en el campo sin guardar, y campo de 3 líneas con el "+" adentro.
  - **Hoy:** anillo de progreso (`js/anel.js`, tareas hechas / del día) en lugar de la barra; puntos de color en Ahora, Después y Hecho; tarjetas con borde fino y franja violeta en Ahora.
  - **Borrar con "Deshacer"** (`js/apagar-depois.js`): sin `confirm()`; el aviso dura 6 s y recién entonces se borra; si se cierra la app antes, no se borra.
  - **Campos editables:** subrayado punteado en el título y los pasos.
  - **Elegir:** con tareas marcadas, el botón dice "Añadir N tareas a Hoy".
  - Quedan para después M3, M5, M6 y B1–B5 de la auditoría.
- **Tarjeta Ahora nueva (13 de noviembre de 2026, `docs/diseno/TARJETA-AGORA.md`):**
  - **Diseño:** en oscuro, vidrio con borde degradé "aurora"; en claro, tarjeta blanca con el mismo borde. Lleva un anillo de 64 px con el tiempo (`textoAnel` en `js/tempo.js`: "10 min", "1h 30", "2h") y el ícono play en Empezar. `.retomar` usa el mismo borde.
  - **Sin minutos:** no hay anillo y el título ocupa las dos columnas.
  - **Anillo de progreso del día:** solo aparece cuando ya hay al menos una tarea hecha.

**Siguiente tarea:** acompañar el piloto (resumen diario, anotar comentarios en la tabla de resultados) y, al terminar, juntar lo aprendido y corregir lo más grave antes de la segunda ronda.

**Pendientes para recordar:**
- Desde la laptop cada consulta a Aiven tarda ~420 ms (la Bandeja local ~3 s); publicada responde en ~0,5 s. Pablo prefirió no quitar `pool_pre_ping`.
- Gemini en plan gratuito: límites bajos y Google puede usar lo enviado (títulos de tareas). Activar la facturación antes de que la usen otras personas (ver Fase 3 · IA).
- Aiven Free se apaga si nadie lo usa por un tiempo: si la app publicada no carga datos, encenderlo desde el panel.
