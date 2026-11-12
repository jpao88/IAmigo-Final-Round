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

**Fase 1 cerrada el 11 de noviembre de 2026.** Backend conectado a Aiven con SSL (`DB_SSL_CA`), `.env.example` como plantilla, CORS con `CORS_ORIGINS`. Front en `frontend/` con JavaScript puro y módulos ES (`python -m http.server 5500`): `js/api.js` llama al backend y traduce sus errores al español, `js/sessao.js` guarda el token, `js/roteador.js` usa rutas por hash y cada pantalla vive en `js/telas/`. Registro, login y cerrar sesión (H0.1–H0.3) funcionan; una compañera levantó el proyecto solo con el `README.md`. Usuario de prueba: `prueba@iamigo.test` (id 1).

**Sprint 1 · Capturar cerrado el 12 de noviembre de 2026** (H1.1–H1.4):
- Backend: `POST /usuarios/{id}/tarefas/lote` (una tarea por línea, ignora vacías, todo o nada, máx. 50 por vez y 200 caracteres) y `GET /usuarios/{id}/tarefas/bandeja?hoje=AAAA-MM-DD` (sin fecha o de días pasados, sin concluir; la fecha la manda el front porque vale la hora local). Las de un mismo lote comparten `criado_em` para conservar el orden en que se escribieron.
- Front: `#/bandeja` es la pantalla de inicio ("¿Qué tienes en la cabeza?" con la Bandeja debajo). Enter guarda, Shift+Enter baja de línea. La tarea aparece al instante y se guarda en segundo plano; si falla, el texto vuelve al campo. Al abrir muestra la copia local (`localStorage`) y actualiza en silencio; "Salir" borra esas copias.
- Hoy (Sprint 3) será otra pantalla; cuando exista, cambiar `TELA_INICIAL` en `js/roteador.js`.

**Siguiente tarea: Sprint 2 · Desmenuzar** (Épica 2, H2.1–H2.4): prompt de la IA con minutos por paso, pantalla de pasos (editar, borrar, agregar y reordenar) y pasos a mano si la IA falla.

**Pendientes para recordar:**
- Desde la laptop cada consulta a Aiven tarda ~420 ms y un pedido hace varias (pre-ping, token, consulta, rollback): la Bandeja tarda ~3 s. El front lo disimula. Se resuelve en la Fase 3 publicando el backend en la misma región que Aiven; Pablo prefirió no quitar `pool_pre_ping`.
