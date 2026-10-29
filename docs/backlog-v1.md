# IAmigo — Backlog de la V1

Oct 27, 2026 · @Pablo

La V1 se construye en siete épicas: una de base y una por cada etapa del ciclo, más el primer uso. Cada historia sale del recorrido validado y del modelo de datos cerrado.

## Cómo leer este backlog

Todas las historias están escritas desde la persona que usa IAmigo, así que se omite el "Como persona usuaria" del inicio. Cada historia tiene un identificador para usarlo en el tablero de Scrum y en los commits.

Una historia está **terminada** cuando cumple todo esto:

- Tiene endpoint, pantalla y prueba funcionando de punta a punta.
- Los datos quedan bien guardados en MySQL, verificado con una consulta.
- Se ve y se usa bien en un celular.
- Respeta los siete principios de diseño del recorrido.
- Solo muestra y modifica datos de la persona que inició sesión.

## Épica 0 · Cuenta y acceso

Se construye en la Fase 1, sobre la autenticación JWT de IAmigo-Final.

| ID | Historia | Criterio de aceptación |
| --- | --- | --- |
| H0.1 | Quiero crear mi cuenta con nombre, correo y contraseña, para guardar mis tareas. | El correo es único; la contraseña tiene al menos 6 caracteres y se guarda con hash. |
| H0.2 | Quiero iniciar sesión con mi correo, para volver a mis tareas desde cualquier dispositivo. | Con datos correctos recibo un token; con datos incorrectos veo "Correo o contraseña incorrectos". |
| H0.3 | Quiero cerrar sesión, para que nadie más use mi cuenta en este celular. | El token se borra y vuelvo a la pantalla de inicio de sesión. |
| H0.4 | Quiero que solo yo pueda ver y cambiar mis tareas y pasos. | Pedir tareas o pasos de otra persona responde 403. |

## Épica 1 · Capturar

Sprint 1. Cubre la pantalla de inicio y la Bandeja.

| ID | Historia | Criterio de aceptación |
| --- | --- | --- |
| H1.1 | Quiero anotar una idea y presionar Enter, para no perderla. | La tarea aparece en la Bandeja sin fecha y el campo queda limpio para la siguiente. |
| H1.2 | Quiero anotar varias cosas seguidas, una por línea, para vaciar la cabeza de una vez. | Cada línea con texto se guarda como una tarea; las líneas vacías se ignoran. |
| H1.3 | Quiero ver mi Bandeja, para saber todo lo que tengo pendiente. | Muestra las tareas sin fecha y las de fechas pasadas sin concluir, sin marcas de "atrasado". |
| H1.4 | Quiero que el botón "+" me lleve al campo si está vacío, para empezar a escribir. | Con el campo vacío, tocar "+" pone el cursor en el campo y no guarda nada. |

## Épica 2 · Desmenuzar

Sprint 2. Cubre la tarea sin pasos y la lista de pasos sugeridos.

| ID | Historia | Criterio de aceptación |
| --- | --- | --- |
| H2.1 | Quiero que IAmigo divida una tarea en pasos, para saber por dónde empezar. | Con "Que IAmigo lo divida" recibo entre 3 y 7 pasos, cada uno con minutos estimados, y veo el total. |
| H2.2 | Quiero editar, borrar, agregar y reordenar los pasos, para que se ajusten a mí. | Cada cambio se guarda; los pasos que agrego quedan marcados como no generados por IA. |
| H2.3 | Quiero escribir los pasos yo, para no depender de la IA. | Con "Prefiero escribirlos yo" agrego pasos a mano; si no indico minutos, se usan 10. |
| H2.4 | Quiero poder seguir aunque la IA falle, para no quedar bloqueada. | Si la IA no responde, veo un aviso de una frase y la opción de escribir los pasos a mano. |

## Épica 3 · Planear hoy

Sprint 3. Cubre Hoy, "+ Hoy" en la Bandeja y la pantalla Elegir para hoy.

| ID | Historia | Criterio de aceptación |
| --- | --- | --- |
| H3.1 | Quiero agregar una tarea a Hoy desde la Bandeja, para planear rápido. | Con "+ Hoy" la tarea pasa a Hoy con mi fecha local; si llegué al límite, veo un aviso amable y no se agrega. |
| H3.2 | Quiero elegir varias tareas a la vez, para armar el día de una sola vez. | "Elegir tareas para hoy" muestra la Bandeja para marcar, con el contador del límite a la vista. |
| H3.3 | Quiero ver mi día dividido en Ahora y Después, para saber qué hacer primero. | La primera tarea aparece en Ahora y el resto en Después, con el tiempo total estimado del día. |
| H3.4 | Quiero reordenar las tareas de Hoy, para cambiar mis prioridades. | El nuevo orden se guarda y la primera pasa a Ahora. |
| H3.5 | Quiero cambiar mi límite de tareas, para adaptarlo a mi energía. | Puedo elegir entre 1 y 5; por defecto es 3. |
| H3.6 | Quiero que Hoy me guíe si no planeé el día, para no ver una pantalla vacía. | Sin tareas planeadas, Hoy muestra "Elige una cosa de tu Bandeja para empezar". |

## Épica 4 · Hacer (modo foco)

Sprint 4. Es el corazón del ciclo y la épica más grande.

| ID | Historia | Criterio de aceptación |
| --- | --- | --- |
| H4.1 | Quiero ver un solo paso a la vez, para no distraerme. | Al tocar "Empezar" veo "Tu paso ahora", el texto del paso y un temporizador circular con sus minutos. |
| H4.2 | Quiero marcar un paso como hecho, para avanzar y sentir que avancé. | Con "Hecho" veo una celebración breve y el siguiente paso; con el último, la tarea queda concluida y la siguiente pasa a Ahora. |
| H4.3 | Quiero sumar tiempo, para terminar sin presión. | "+5 minutos" agrega 5 minutos al temporizador del paso actual. |
| H4.4 | Quiero pedir ayuda cuando me trabo, para no abandonar. | "Me atasqué" divide el paso en 2 o 3 más chicos; el original queda marcado como sustituido y sigo desde el primero nuevo. |
| H4.5 | Quiero pausar, para atender algo sin perder el lugar. | "Pausar" detiene el temporizador y puedo reanudarlo. |
| H4.6 | Quiero retomar donde quedé, para no empezar de nuevo. | Si cierro la app a mitad de una tarea, al volver veo "¿Seguimos donde quedaste?" con el paso pendiente. |
| H4.7 | Quiero que el fin del tiempo no me asuste. | Cuando el temporizador llega a cero no hay alarma ni rojo; se ofrece "Hecho" o "+5 minutos". |

## Épica 5 · Cerrar el día

Sprint 5, junto con el primer uso.

| ID | Historia | Criterio de aceptación |
| --- | --- | --- |
| H5.1 | Quiero ver lo que logré hoy, para terminar el día con una sensación positiva. | El resumen muestra cuántos pasos y tareas completé, sin mencionar lo que faltó como fracaso. |
| H5.2 | Quiero decidir qué hacer con lo pendiente, para no arrastrarlo con culpa. | Cada tarea sin terminar ofrece "Hacerla mañana" o "Guardarla sin fecha". |
| H5.3 | Quiero cerrar el día cuando yo decida. | "Terminar el día" registra el cierre de esa fecha; no puede haber dos cierres del mismo día. |
| H5.4 | Quiero ver el resumen de ayer si no cerré el día, para no perder lo logrado. | Al abrir la app, si el día anterior no se cerró, aparece primero su resumen. |

## Épica 6 · Primer uso

Sprint 5. Se construye al final porque recorre todas las etapas anteriores.

| ID | Historia | Criterio de aceptación |
| --- | --- | --- |
| H6.1 | Quiero entender el ciclo en segundos, para no leer un tutorial. | Después del registro veo una sola pantalla: "Anota, divide, elige, hazlo, celebra", con las cinco etapas en íconos. |
| H6.2 | Quiero aprender usando una tarea real, para empezar a avanzar desde el primer día. | La app me pide una tarea pendiente y me acompaña a dividirla, ponerla en Hoy y empezar el primer paso. |
| H6.3 | Quiero que la guía aparezca una sola vez. | Al terminar el primer paso, la guía queda marcada como completada y no vuelve a aparecer. |
