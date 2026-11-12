# IAmigo V1

App web de organización para adultos con TDAH. Acompaña un ciclo diario de cinco etapas: capturar, desmenuzar (la IA divide en pasos), planear hoy, hacer (modo foco) y cerrar el día. Está pensada primero para celular.

- **Backend:** Python (FastAPI) en capas Controller / Service / Repository, con login JWT.
- **Base de datos:** MySQL 8 (en el equipo usamos Aiven).
- **IA:** Gemini.
- **Front:** JavaScript puro con módulos ES, sin compilación.

La documentación del producto está en [`docs/`](docs/): recorrido del usuario, modelo de datos, backlog y hoja de ruta.

## Qué necesitas

- [Git](https://git-scm.com/)
- [Python 3.12](https://www.python.org/) o más nuevo
- Una base MySQL 8: la de Aiven del equipo o un MySQL local
- [MySQL Workbench](https://www.mysql.com/products/workbench/), para crear las tablas y revisar los datos

## 1. Clonar el repositorio

```
git clone https://github.com/jpao88/IAmigo-Final-Round.git
cd IAmigo-Final-Round
```

## 2. Crear la base de datos

Abre [`database/schema.sql`](database/schema.sql) en Workbench y ejecútalo completo. Crea la base `iamigo` con sus cuatro tablas, y se puede ejecutar más de una vez sin borrar nada.

Si usas **Aiven**:

1. En el panel de Aiven, en **Overview → Connection information**, copia host, puerto, usuario y contraseña, y descarga el **CA certificate** (`ca.pem`).
2. Guarda el `ca.pem` **fuera del repositorio**, por ejemplo en `C:/Users/<tu-usuario>/Certs/ca.pem`.
3. En Workbench, en la pestaña **SSL** de la conexión, elige `Require and Verify CA` e indica la ruta del `ca.pem`.

Si Aiven no responde, puede que el servicio esté apagado por inactividad: enciéndelo desde su panel. Algunas redes, como el Wi-Fi del instituto, bloquean el puerto de Aiven; en ese caso usa datos móviles.

## 3. Configurar el backend

Desde la carpeta `backend/`:

```
python -m venv .venv
.venv\Scripts\python -m pip install -r requirements.txt
copy .env.example .env
```

En macOS o Linux, usa `.venv/bin/python` y `cp` en lugar de `.venv\Scripts\python` y `copy`.

Completa `backend/.env`:

| Variable | Qué poner |
| --- | --- |
| `DB_HOST`, `DB_PORT`, `DB_USER`, `DB_PASSWORD` | Datos de la conexión a MySQL |
| `DB_NAME` | `iamigo` |
| `DB_SSL_CA` | Ruta del `ca.pem`, escrita con `/`. Déjala vacía si usas un MySQL local sin SSL. |
| `JWT_SECRET` | Una clave aleatoria. Puedes generarla con `.venv\Scripts\python -c "import secrets; print(secrets.token_urlsafe(48))"` |
| `GEMINI_API_KEY` | Clave de Gemini. Solo hace falta para dividir tareas en pasos. |
| `CORS_ORIGINS` | Direcciones del front. La que viene en el ejemplo sirve para trabajar en local. |

El `.env` nunca se sube a GitHub.

## 4. Levantar el proyecto

Necesitas dos terminales.

**Backend**, desde `backend/`:

```
.venv\Scripts\python -m uvicorn api_app:app --reload --port 8000
```

La documentación interactiva de la API queda en http://localhost:8000/docs.

**Front**, desde `frontend/`:

```
python -m http.server 5500
```

Abre http://localhost:5500, crea una cuenta e inicia sesión.

Para probarlo en el celular, usa las herramientas de desarrollo del navegador (en Chrome, **F12** y luego el ícono de dispositivo móvil).

## 5. Tests

Desde `backend/`:

```
.venv\Scripts\python -m unittest discover -s tests
```

No necesitan MySQL ni Gemini.

## 6. Publicar (DigitalOcean)

La app se publica en DigitalOcean App Platform, en la región de San Francisco, la misma del MySQL de Aiven. La configuración está en [`.do/deploy.template.yaml`](.do/deploy.template.yaml):

- **web**: el front estático (`frontend/`), en `/`.
- **api**: el backend (`backend/`), en `/api`. El front lo detecta solo (`js/config.js`).

Cada `git push` a `main` vuelve a publicar.

**Variables del backend** (se escriben en el panel de DigitalOcean, nunca en el repositorio):

| Variable | Valor |
| --- | --- |
| `DB_HOST`, `DB_PORT`, `DB_USER`, `DB_PASSWORD`, `DB_NAME` | Los mismos de tu `.env` |
| `DB_SSL_CA_PEM` | El contenido completo de `ca.pem` (desde `-----BEGIN CERTIFICATE-----` hasta `-----END CERTIFICATE-----`) |
| `JWT_SECRET` | Uno nuevo, distinto del local: `python -c "import secrets; print(secrets.token_urlsafe(48))"` |
| `GEMINI_API_KEY` | La clave de la IA |
| `DOCS_ABERTOS` | `nao` |
| `CORS_ORIGINS` | Vacío (front y API comparten dominio) |

Si la app publicada no puede conectarse a la base, revisa en Aiven que el servicio esté encendido y que no tenga una lista de IPs permitidas que deje fuera a DigitalOcean.

## 7. Respaldos

Aiven hace copias automáticas (pestaña **Backups** del servicio; se restaura con **Fork service**). Además hay un respaldo propio que guarda cuentas, tareas, pasos y cierres de día en un archivo JSON. Desde `backend/`:

```
.venv\Scripts\python scripts\exportar_dados.py
```

El archivo queda en `RESPALDOS_DIR` del `.env` o, si no está, en `~/IAmigo-respaldos`. Tiene datos personales (nombres, correos): nunca va al repositorio ni se comparte. Conviene correrlo una vez por semana y antes de cambios grandes en la base.

## Convenciones

- El código y la base de datos usan nombres en portugués: `tarefas`, `passos`, `data_planejada`…
- Los textos de la interfaz van en español, cortos y amables, siguiendo los siete principios de [`docs/recorrido-v1.md`](docs/recorrido-v1.md).
- El backend responde en portugués y el front traduce los mensajes que ve la persona.
