# IAmigo V1

IAmigo es una app web de organización para adultos con TDAH. Lleva a la persona de "tengo mil cosas en la cabeza" a "terminé lo importante de hoy" con un ciclo diario de cinco etapas: capturar, desmenuzar (la IA divide en pasos), planear hoy, hacer (modo foco) y cerrar el día. Se diseña primero para celular.

## Documentación

Antes de proponer o escribir código, consulta lo que corresponda en `docs/`:

- `docs/hoja-de-ruta.md` — fases del proyecto y tareas pendientes. Estamos en la **Fase 1 · Base técnica**.
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
- Textos de la interfaz en español, cortos y amables, siguiendo los principios de diseño del recorrido.
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

**Fase 1 hecha:** repositorio, base del backend copiada sin TPAC ni consola, base de datos creada desde `database/schema.sql` y login por correo (`POST /auth/login` con `email` y `senha`). El nombre del usuario no es único: solo se usa para el saludo.

**`.env`, CORS y tests hecho:** `backend/.env.example` como plantilla y `backend/.env` completo en la laptop. `DB_SSL_CA` conecta a Aiven con SSL (TLS 1.3) y, si la ruta no existe, avisa al arrancar. CORS se configura con `CORS_ORIGINS`. Las tablas ya están en Aiven y se probó de punta a punta: registro (`POST /usuarios`), login, 401 con contraseña mala y contraseña guardada en hash (`pbkdf2_sha256`). Quedó un usuario de prueba `prueba@iamigo.test` (id 1).

**Front y README hechos:** `frontend/` en JavaScript puro con módulos ES, sin compilación (`python -m http.server 5500`). `js/api.js` traduce los errores del backend al español, `js/sessao.js` guarda el token, `js/roteador.js` usa rutas por hash (`#/login`, `#/cadastro`, `#/hoje`) y cada pantalla vive en `js/telas/`. Registro (H0.1), login (H0.2) y cerrar sesión (H0.3) probados por Pablo en el navegador. El `README.md` explica cómo levantar todo.

**Siguiente paso: punto de control de la Fase 1.** Una persona del equipo clona el repo, lo levanta con el README, se registra e inicia sesión. Después viene la Fase 2, Sprint 1 · Capturar.

**Pendientes para recordar:**
- El backend responde en portugués; el front debe mostrar el error de login en español ("Correo o contraseña incorrectos", H0.2) a partir del status 401.
