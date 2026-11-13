# Prueba de varios días · Fase 3

Objetivo: ver si IAmigo funciona en la vida diaria, no solo en una demo. ¿La gente vuelve a abrirla? ¿Termina lo importante del día? ¿Qué deja de usar?

## Formato

- **Primera ronda (piloto):** 2 personas durante 5 a 7 días, desde el 13 de noviembre de 2026. Sirve para encontrar problemas antes de invitar a más gente.
- **Segunda ronda:** 3 a 5 personas de la validación que no participaron en el desarrollo. Esta es la que cumple el punto de control de la Fase 3. Antes de empezarla, activar la facturación de Gemini.
- **App:** https://iamigo-lzdqn.ondigitalocean.app, cada persona con su propia cuenta.

## Mensaje de invitación

Para copiar y enviar:

> ¡Hola! Te invito a probar IAmigo durante unos días. Es una app para organizar el día cuando la cabeza va a mil: anotas lo pendiente, la app lo divide en pasos chiquitos y lo haces de a uno, con un temporizador.
>
> Lo que te pido:
> 1. Úsala de 5 a 7 días, aunque sea un ratito al día y con cosas reales.
> 2. Cada noche (o cuando quieras) toca "Terminar el día".
> 3. Si algo te confunde o te molesta, mándame un mensaje en el momento, aunque sea corto.
>
> Entra aquí desde el celular: https://iamigo-lzdqn.ondigitalocean.app
> Para tenerla como app: en el menú del navegador elige "Agregar a pantalla de inicio".
>
> Al final te hago unas preguntas de 10 minutos. ¡Gracias!

## Durante la prueba

**Una vez al día** (5 minutos), desde `backend/`:

```
.venv\Scripts\python scripts\resumo_uso.py 2026-11-13
```

Muestra, por persona, cuántas tareas creó, cuántos pasos y tareas terminó, en cuántos días planeó y cerró el día y su último día activo. No muestra el texto de las tareas.

| Señal | Qué puede significar | Qué hacer |
| --- | --- | --- |
| No abre la app hace 2 días o más | Se le olvidó o algo la frenó | Mensaje amable, sin presión: "¿Cómo vas con IAmigo? ¿Algo te frenó?" |
| Crea tareas pero no termina pasos | Le cuesta empezar, o los pasos son muy grandes | Preguntar en la entrevista final |
| Termina pasos pero no cierra el día | "Terminar el día" no se encuentra o no le aporta | Anotar |
| Muchos "Me atasqué" | La IA divide en pasos muy grandes | Revisar el prompt |

**Una vez por semana**, respaldo de la base:

```
.venv\Scripts\python scripts\exportar_dados.py
```

**Anota todo lo que te cuenten**, con la fecha, en la tabla de resultados de abajo.

## Entrevista final (10 minutos)

1. Del 1 al 5, ¿qué tan útil te resultó?
2. ¿Qué día te sirvió más? ¿Qué pasó ese día?
3. ¿Hubo un día que no la abriste? ¿Por qué?
4. ¿Qué parte usabas más? ¿Cuál nunca usaste?
5. ¿Los pasos que sugería IAmigo te servían o los cambiabas mucho?
6. Cuando el tiempo de un paso terminaba, ¿cómo te sentías?
7. ¿Alguna vez te hizo sentir culpa o presión? ¿Dónde?
8. ¿La seguirías usando? ¿Qué le cambiarías primero?

## Resultados

| Persona | Días usados | Pasos hechos | Días cerrados | Nota (1-5) | Lo que más le sirvió | Lo que la frenó o confundió |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | | | | | | |
| 2 | | | | | | |

**Cómo decidir** (igual que en la validación):

- **Lo que se repite en la mayoría:** se corrige antes de la segunda ronda.
- **Lo que aparece en una sola persona:** se anota como candidato para la V2.
