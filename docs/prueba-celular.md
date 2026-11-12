# Prueba en el celular · Punto de control de la Fase 2

Objetivo: una persona nueva completa el ciclo entero con una tarea real, sin ayuda, desde su celular.

## 1. Preparar la laptop (una vez)

1. **Misma red.** La laptop y el celular tienen que estar en la misma Wi-Fi.
   - En casa: la Wi-Fi de siempre.
   - En el instituto la Wi-Fi bloquea Aiven: activa el **punto de acceso del celular** y conecta la laptop a él. El celular que comparte la red puede abrir la app igual.
2. **Red privada.** En Windows: Configuración → Red e Internet → Wi-Fi → la red conectada → Tipo de perfil de red: **Privada**.
3. **Permitir los puertos en el firewall.** En PowerShell **como administrador**, una sola vez:

   ```powershell
   New-NetFirewallRule -DisplayName "IAmigo prueba" -Direction Inbound -Protocol TCP -LocalPort 5500,8000 -Action Allow -Profile Private
   ```

4. **Permitir el origen en el backend.** En `backend/.env` agrega (o completa) esta línea:

   ```
   CORS_ORIGIN_REGEX=http://(192\.168|10|172)\.[0-9.]+:5500
   ```

   Acepta cualquier IP local en el puerto 5500, así no hay que cambiarla al cambiar de red. Cuando la app esté publicada, se deja vacía.

## 2. Levantar la app para la red

En dos terminales:

```powershell
# Terminal 1 · backend, abierto a la red (no solo a localhost)
cd backend
.venv\Scripts\python -m uvicorn api_app:app --host 0.0.0.0 --port 8000

# Terminal 2 · front
cd frontend
..\backend\.venv\Scripts\python -m http.server 5500
```

Busca la IP de la laptop con `ipconfig` → "Dirección IPv4" (por ejemplo `192.168.2.105`). Cambia según la red.

## 3. Comprobar antes de que llegue la persona

En tu celular abre `http://<IP>:5500` (por ejemplo `http://192.168.2.105:5500`).

| Qué pasa | Qué revisar |
| --- | --- |
| La página no abre | Misma red, firewall (paso 1.3), terminal 2 corriendo |
| Abre, pero "No pudimos conectar" al entrar | Backend con `--host 0.0.0.0`, firewall del puerto 8000, `CORS_ORIGIN_REGEX` y reiniciar el backend |
| Tarda unos segundos en cada acción | Normal: cada consulta viaja a Aiven. Mejora al publicar |
| "IAmigo no pudo ahora" al dividir | Clave de Gemini o límite del plan gratuito |

Crea una cuenta tuya de prueba y recorre todo una vez. Si funciona, el celular de la persona también.

## 4. Durante la prueba

**Qué decirle (solo esto):**

> "Esta es una app para organizar el día. Crea tu cuenta y úsala con algo que de verdad tengas pendiente. Piensa en voz alta. Yo solo miro; si te trabas, intenta resolverlo como lo harías sin mí."

**Reglas para ti:** no señales la pantalla, no expliques y no respondas cómo se hace algo. Si pregunta, devuelve: "¿Qué harías tú?". Solo intervienes si queda trabada más de 2 minutos; eso se anota como **ayuda**.

**Qué tiene que completar:**

| Etapa | Lo logra si… | Anotar |
| --- | --- | --- |
| Registro y bienvenida | Crea la cuenta y toca "Probar con una tarea" | ¿Leyó las cinco etapas? |
| Capturar | Escribe una tarea real | ¿Qué tarea eligió? |
| Desmenuzar | Usa "Que IAmigo lo divida" (o escribe pasos) | ¿Ajustó los pasos? ¿Le parecieron útiles? |
| Planear | Toca "Ponerla en Hoy y empezar" | |
| Hacer | Termina al menos un paso con "Hecho" | ¿Usó +5, Pausar o Me atasqué? ¿Reacción a la celebración y al sonido? |
| Cerrar el día | Llega al resumen y toca "Terminar el día" | ¿Decidió algo con lo pendiente? |

Para que llegue a Cerrar el día en la misma sesión, la tarea puede ser corta (por ejemplo, ordenar algo o responder un mensaje) o puede terminar solo un paso y luego tocar "Terminar el día" en Hoy.

**Anota en cada etapa:** dudas en voz alta, pausas largas, toques en el lugar equivocado y frases textuales.

## 5. Al terminar (5 minutos)

1. Del 1 al 5, ¿qué tan fácil fue?
2. ¿Hubo un momento en que no supiste qué hacer?
3. ¿Qué fue lo que más te gustó?
4. ¿La usarías mañana? ¿Qué te lo impediría?

## 6. Resultado

**Punto de control cumplido** si completó las seis etapas sin ayuda. Si necesitó ayuda en alguna, se corrige esa pantalla y se repite con otra persona.

Los resultados se anotan en `docs/guion-validacion.md`.
