# Guion del video de IAmigo

**Duración objetivo:** 13 minutos (límite: 15).
**Presentan:** Rafaela y Pablo.
**Versión en portugués:** `roteiro-video.md` (la que se graba).

El guion sigue la estructura que pidió el profesor: problemática, público objetivo, solución propuesta, arquitectura, funcionalidades y demostración práctica. La nota se reparte así:
- **80 %, evaluación técnica:** código, arquitectura, base de datos, rutas y reglas de negocio.
- **20 %, experiencia de uso.**

Por eso la parte de arquitectura muestra código real y la demo recorre la app de punta a punta.

**Cómo leer este guion:**
- **En pantalla:** lo que se muestra.
- **Texto hablado:** antes de cada parte se indica quién habla, **Rafaela** o **Pablo**.
- **Tiempos:** son aproximados.

---

## Quién hace qué

El profesor pide repartir responsabilidades de forma que colaboren todos. Esta es una sugerencia; cámbienla como quieran.

| Responsabilidad | Quién |
|---|---|
| Guion | Rafaela y Pablo |
| Narración: problemática, público, funcionalidades y demo | Rafaela |
| Narración: solución, arquitectura y código | Pablo |
| Demostración práctica (uso de la app) | Rafaela |
| Grabación de pantalla de la parte técnica (VS Code) | Pablo |
| Edición y publicación del video | Por definir |

> No es obligatorio salir en cámara: puede ser solo la pantalla con la voz.

---

## Antes de grabar

- [ ] **Aiven encendido.** En el instituto, usen datos móviles.
- [ ] **App en portugués** (enlace "Português" en el login) y en vista de celular: F12 → ícono de celular → 390 px.
- [ ] **Cuentas:** una "Demo" recién creada, para mostrar la bienvenida, y otra con tareas, por si algo falla.
- [ ] **Tarea para la IA:** "Preparar a apresentação de sexta-feira". La IA tarda unos 5 s; no corten el video ahí.
- [ ] **VS Code abierto.**
- [ ] **Backend local corriendo,** para mostrar http://localhost:8000/docs. En la app publicada esa página está cerrada a propósito.
- [ ] **Sonido de la app encendido** y notificaciones de la computadora apagadas.

---

## 1. Problemática · 0:00 – 1:15

**En pantalla:** la pantalla de inicio de sesión, con el logo de IAmigo.

**Pablo:**
> Hola, soy Pablo…

**Rafaela:**
> …y yo soy Rafaela. Este es IAmigo.
>
> El problema que elegimos es organizar el día a día de las personas con TDAH. No es falta de ganas. Hay cosas que les cuestan mucho:
> - **empezar** una tarea grande, que parece imposible;
> - **percibir el tiempo**;
> - **decidir** por dónde arrancar frente a una lista larga;
> - **recordar** las ideas que aparecen en cualquier momento.
>
> Y hay un problema más: las apps de tareas comunes muestran las tareas atrasadas en rojo. Eso genera culpa y la persona termina abandonando la app. Es un problema real, que afecta el estudio, el trabajo y la autoestima.

> Nota: si quieren, citen aquí un dato sobre el TDAH en adultos, **con su fuente**. No puse cifras para no inventar datos.

---

## 2. Público objetivo · 1:15 – 2:00

**En pantalla:** la sección "Persona" de `docs/recorrido-v1.md`.

**Rafaela:**
> IAmigo es para **adultos con TDAH**, sobre todo estudiantes y jóvenes que trabajan y usan el celular todo el día. Por eso la app está pensada **primero para celular**.
>
> Antes de programar, probamos el diseño con **tres personas con TDAH**, y eso cambió cosas importantes. Nadie encontraba cómo dividir una tarea, y las tres pidieron elegir cuántas tareas hacer por día. Ajustamos el diseño y lo volvimos a probar.

---

## 3. Solución propuesta · 2:00 – 3:30

**En pantalla:** la bienvenida de la app con las cinco etapas. Después, los siete principios en `docs/recorrido-v1.md`.

**Pablo:**
> **Objetivo:** llevar a la persona de "tengo mil cosas en la cabeza" a "terminé lo importante de hoy". Para eso usamos un ciclo diario de cinco etapas: capturar, desmenuzar, planear el día, hacer y cerrar el día. La meta es que una persona nueva complete el ciclo entero el primer día, sola.
>
> **Diferenciales:**
> - **La IA divide las tareas grandes** en pasos de cinco a veinticinco minutos, con el tiempo de cada uno. Y si la persona se traba en un paso, la IA lo divide en otros más chicos.
> - **La IA sugiere y la persona decide:** todo se puede editar.
> - **Una cosa a la vez:** se destaca solo lo que toca ahora, y hay un límite de tareas por día.
> - **Sin culpa:** no hay rojo ni "atrasado". Lo que no se hizo pasa a mañana.
>
> Estos son algunos de los siete principios de diseño que revisamos en cada pantalla.

---

## 4. Arquitectura · 3:30 – 7:00

> Es lo que más pesa en la nota técnica. Muestren el código con calma y con zoom en VS Code.

### 4.1 Visión general · 3:30 – 4:10
**En pantalla:** el diagrama de la sección "Arquitetura e tecnologias" del `README.md`.

**Pablo:**
> La aplicación tiene tres partes:
> - un **front** en JavaScript puro;
> - una **API** en Python con FastAPI;
> - una base **MySQL 8** en la nube, en Aiven, con conexión cifrada por SSL.
>
> La **IA** es Gemini, de Google. Todo está publicado en **DigitalOcean**.

### 4.2 Backend en capas · 4:10 – 5:10
**En pantalla:**
1. Las carpetas `backend/api/`, `controllers/`, `services/` y `repositories/`.
2. `services/tarefa_service.py`, en `planejar_para_hoje` (línea ~142), con `LimiteHojeAtingido`.

**Pablo:**
> El backend sigue una **arquitectura en capas**, cada una con una sola responsabilidad:
> - las **rutas** reciben el pedido HTTP;
> - el **controller** lo ordena;
> - el **service** tiene las **reglas de negocio**;
> - el **repository** es el único que habla con la base.
>
> Por ejemplo, esta es la regla del límite del día. Antes de poner tareas en Hoy, el service cuenta las que ya hay. Si no caben, devuelve un error claro, "Hoy ya está lleno", con el código 422. Otra regla: al terminar el último paso, la tarea queda concluida automáticamente.

### 4.3 Base de datos · 5:10 – 5:40
**En pantalla:** `database/schema.sql`, con las cuatro tablas.

**Pablo:**
> Son cuatro tablas:
> - `usuarios`;
> - `tarefas`, que pertenecen a un usuario;
> - `passos`, que pertenecen a una tarea;
> - `fechamentos_dia`, con los días cerrados.
>
> El modelo se cerró antes de programar. Una tarea sin fecha está en la Bandeja; con la fecha de hoy, aparece en Hoy.

### 4.4 Rutas y seguridad · 5:40 – 6:20
**En pantalla:**
1. http://localhost:8000/docs, con la lista de rutas.
2. `api/dependencias.py`, en `exigir_dono`.

**Pablo:**
> Las rutas siguen el estilo REST: por ejemplo, `POST /usuarios/{id}/tarefas/lote` para capturar y `GET .../tarefas/hoje` para el día.
>
> El inicio de sesión usa **JWT**, y las contraseñas se guardan con hash, nunca en texto. La seguridad tiene **dos barreras**:
> - la ruta comprueba que la persona sea dueña del `usuario_id`;
> - el service vuelve a comprobar que la tarea o el paso sean suyos.
>
> Además, limitamos los intentos fallidos de inicio de sesión.

### 4.5 IA, front y tests · 6:20 – 7:00
**En pantalla:**
1. `core/ia_service.py`.
2. `frontend/js/`, con la carpeta `telas/` e `i18n.js`.
3. La terminal con `.venv\Scripts\python -m unittest discover -s tests` y el "OK".

**Pablo:**
> - **IA:** todo lo que depende del proveedor está en un solo archivo. Le pedimos la respuesta en JSON y la validamos antes de guardarla.
> - **Front:** es JavaScript puro en módulos, una pantalla por archivo, y todos los textos en español y portugués están en un solo lugar.
> - **Tests:** tenemos más de cien, que corren en segundos, sin la base de datos ni la IA. Uno de ellos falla si alguien agrega una ruta sin declarar sus permisos.

---

## 5. Funcionalidades · 7:00 – 7:45

**En pantalla:** la app, pasando rápido por Hoy y la Bandeja.

**Rafaela:**
> Las funcionalidades principales siguen el ciclo:
> - **capturar** ideas en segundos;
> - **dividir** tareas con IA;
> - **elegir** las del día, con un límite;
> - **hacer** cada paso en modo foco, con temporizador;
> - **cerrar** el día con un resumen.
>
> Además, la app está en portugués y español, tiene modo claro y oscuro, y permite deshacer al borrar una tarea. Ahora lo muestro funcionando.

---

## 6. Demostración práctica · 7:45 – 12:30

### 6.1 Primer uso · 7:45 – 8:15
**En pantalla:** crear la cuenta → bienvenida → "Probar con una tarea".

**Rafaela:**
> Al crear la cuenta, IAmigo muestra el ciclo en una pantalla y propone probarlo con una tarea real.

### 6.2 Capturar · 8:15 – 9:00
**En pantalla:**
1. La Bandeja.
2. Escribir dos o tres ideas, una por línea, y apretar Enter.
3. Tocar el atajo "Llamar a…".

**Rafaela:**
> "¿Qué tienes en la cabeza?" Escribo una idea por línea, aprieto Enter y quedan guardadas al instante, sin elegir fecha ni prioridad. Si cuesta empezar a escribir, estos atajos ayudan.

### 6.3 Desmenuzar con IA · 9:00 – 10:00
**En pantalla:**
1. "Que IAmigo lo divida" y esperar los pasos.
2. Editar un paso y cambiar sus minutos.
3. Borrar un paso con "Ordenar".

**Rafaela:**
> La IA divide la tarea en pasos chicos y estima los minutos. Puedo cambiar el texto, los minutos y el orden, o borrar un paso. Si la IA falla, escribo los pasos yo misma.

### 6.4 Planear hoy · 10:00 – 10:40
**En pantalla:**
1. "Elegir tareas para hoy".
2. Marcar 2 tareas: el botón cambia a "Añadir 2 tareas a Hoy".
3. La pantalla Hoy, con la tarjeta Ahora.

**Rafaela:**
> Elijo qué voy a hacer hoy, con un límite de tres por defecto. Hoy destaca solo **Ahora**, con el tiempo en un anillo, y arriba muestra el total del día.

### 6.5 Hacer: modo foco · 10:40 – 11:50
**En pantalla:**
1. "Empezar".
2. "Hecho": aparece la celebración, con sonido.
3. "Me atasqué": la IA divide el paso en otros más chicos.

**Rafaela:**
> El modo foco muestra un paso por vez con un temporizador circular. Cuando el tiempo termina no hay alarma: solo dice "Tómate tu tiempo". Cada paso terminado tiene una celebración. Si me trabo, "Me atasqué" divide el paso. Y si cierro la app, al volver me ofrece seguir donde quedé.

### 6.6 Cerrar el día · 11:50 – 12:30
**En pantalla:**
1. "Terminar el día".
2. El resumen.
3. Una tarea pendiente, con "Hacerla mañana" y "Guardarla sin fecha".

**Rafaela:**
> Al final del día, IAmigo muestra lo que hice, no lo que me faltó. Lo pendiente pasa a mañana o vuelve a la Bandeja, sin castigo.

---

## 7. Cierre · 12:30 – 13:15

**En pantalla:** la pantalla Hoy.

**Pablo:**
> La app está publicada y en uso real. Empezamos una prueba de varios días, y Rafaela ya completó el ciclo entero sola. Lo que más aprendimos es que **validar antes de programar ahorra mucho trabajo**.

**Rafaela:**
> Lo próximo es terminar esa prueba, corregir lo que salga y probar con más personas.

**Los dos:**
> ¡Gracias por ver! Esto es IAmigo.

---

## Si algo falla mientras graban

| Qué falla | Qué hacer |
|---|---|
| La IA no responde | Mostrarlo como parte de la demo: tocar "Prefiero escribirlos yo". |
| No cargan los datos | Puede que Aiven esté apagado. Encenderlo desde su panel y recargar. |
| El video queda largo | Acortar la parte 6.1 y unir las partes 5 y 6. |

---

## Entrega

- [ ] **Video** en YouTube (no listado), Google Drive u OneDrive, con permiso de visualización. Prueben el enlace en una ventana de incógnito.
- [x] **Repositorio público:** https://github.com/jpao88/IAmigo-Final-Round
- [ ] **`README.md` en portugués,** con instalación, dependencias y ejecución.
