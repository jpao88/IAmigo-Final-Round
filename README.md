# IAmigo

**Aplicação web de organização para adultos com TDAH.** Leva a pessoa de "estou com mil coisas na cabeça" a "terminei o mais importante de hoje" com um ciclo diário de cinco etapas: **anotar, dividir** (a IA divide a tarefa em passos), **planejar o dia, fazer** (modo foco) e **encerrar o dia**. Foi pensada primeiro para o celular.

- **App publicada:** https://iamigo-lzdqn.ondigitalocean.app
- **Equipe:** Rafaela e Pablo
- **Idiomas da interface:** português do Brasil e espanhol

> 🇪🇸 La versión en español está [al final de este archivo](#iamigo-versión-en-español).

---

## Sumário

1. [O problema e o público-alvo](#o-problema-e-o-público-alvo)
2. [A solução](#a-solução)
3. [Funcionalidades](#funcionalidades)
4. [Arquitetura e tecnologias](#arquitetura-e-tecnologias)
5. [Instalação e execução](#instalação-e-execução)
6. [Testes](#testes)
7. [Publicação (DigitalOcean)](#publicação-digitalocean)
8. [Backups](#backups)
9. [Documentação do projeto](#documentação-do-projeto)

---

## O problema e o público-alvo

**Público-alvo:** adultos com TDAH, especialmente estudantes e jovens trabalhadores que usam o celular o dia todo.

**O que é difícil para essas pessoas:**

| Dificuldade | O que acontece |
|---|---|
| **Começar** | Uma tarefa grande ("fazer o trabalho final") parece impossível e fica para depois. |
| **Perceber o tempo** | Não percebem quanto tempo passou nem quanto algo vai levar. |
| **Decidir** | Diante de uma lista longa, não sabem por onde começar. |
| **Lembrar** | As ideias aparecem a qualquer momento e se perdem se não forem anotadas rápido. |
| **Manter o hábito** | Abandonam apps de tarefas porque as tarefas atrasadas em vermelho geram culpa. |

## A solução

**Objetivo:** que uma pessoa nova complete o ciclo inteiro no primeiro dia, sozinha, com uma tarefa real.

**Diferenciais:**

- **A IA divide tarefas grandes** em passos de 5 a 25 minutos, com o tempo estimado de cada um. **A IA sugere e a pessoa decide:** tudo pode ser editado, reordenado ou apagado.
- **"Travei":** se a pessoa trava num passo, a IA o divide em dois ou três passos menores.
- **Uma coisa por vez:** a tela Hoje destaca só a tarefa de **Agora**, e o modo foco mostra um passo por vez com um cronômetro circular.
- **Limite diário** de tarefas (3 por padrão, configurável), para não planejar demais.
- **Sem culpa:** não há vermelho nem "atrasado". O que não foi feito vai para amanhã ou volta para a caixa de entrada.
- **Validado com pessoas reais:** o fluxo foi testado com 3 pessoas com TDAH antes de programar, e o desenho mudou com o que aprendemos.

Cada tela segue **sete princípios de design**:
1. uma coisa por vez;
2. anotar em segundos;
3. o tempo se vê;
4. sem culpa;
5. recompensa imediata;
6. linguagem curta e gentil;
7. a IA sugere e a pessoa decide.

Detalhes em [`docs/recorrido-v1.md`](docs/recorrido-v1.md).

## Funcionalidades

| Etapa | O que a pessoa faz |
|---|---|
| **Primeiro uso** | Cria a conta, vê o ciclo numa tela de boas-vindas e testa com uma tarefa guiada. |
| **Anotar** | Escreve uma ideia por linha em "O que está na sua cabeça?" e elas vão para a **caixa de entrada**. Atalhos como "Ligar para…" ajudam a começar a escrever. |
| **Dividir** | "Deixe o IAmigo dividir" gera os passos com minutos. A pessoa também pode editá-los, reordená-los, apagá-los ou escrevê-los à mão. |
| **Planejar o dia** | Escolhe tarefas da caixa de entrada para **Hoje**. Vê o **Agora** em destaque, com o tempo num anel, o **Depois** e o tempo total do dia. |
| **Fazer** | Modo foco com cronômetro circular e os botões **Feito**, **+5 minutos**, **Pausar** e **Travei**. Cada passo concluído tem uma comemoração com som. Ao voltar para a app, ela oferece continuar de onde parou. |
| **Encerrar o dia** | Mostra um resumo do que foi feito. O que ficou pendente vai para "Fazer amanhã" ou "Guardar sem data". |

**Além disso:**
- Português e espanhol.
- Modo claro e escuro.
- "Desfazer" ao apagar uma tarefa.
- Interface acessível: contraste AA, áreas de toque de 44 px e animações que respeitam a opção "reduzir movimento".

## Arquitetura e tecnologias

```
Celular / navegador
        │
        ▼
Front (JavaScript puro, módulos ES)  ──HTTP + JWT──►  API (Python, FastAPI)
                                                          │
                                         ┌────────────────┼────────────────┐
                                         ▼                                 ▼
                                 MySQL 8 (Aiven, SSL)               Gemini (IA)
```

| Camada | Tecnologia |
|---|---|
| **Backend** | Python 3.12+ com FastAPI e Uvicorn |
| **Acesso a dados** | SQLAlchemy 2 + mysql-connector-python |
| **Banco de dados** | MySQL 8 (na nuvem: Aiven, com SSL) |
| **Autenticação** | JWT (PyJWT), senhas com hash e limite de tentativas de login |
| **IA** | Google Gemini (`google-genai`, modelo `gemini-2.5-flash`) |
| **Front** | HTML, CSS e JavaScript puro em módulos ES, sem frameworks e sem build |
| **Testes** | `unittest` do Python (rodam sem MySQL e sem Gemini) |
| **Publicação** | DigitalOcean App Platform |

### Backend em camadas

```
backend/
├── api_app.py        # cria a app FastAPI, CORS e rotas
├── api/              # rotas (endpoints), schemas e dependências (JWT, dono dos dados)
├── controllers/      # recebem o pedido da rota e chamam o service
├── services/         # regras de negócio (limite do dia, conclusão de tarefas, encerrar o dia…)
├── repositories/     # único acesso ao banco de dados
├── models/           # tabelas (SQLAlchemy)
├── core/             # IA (ia_service.py), segurança, erros e limite de login
├── config/           # configuração (.env) e conexão com o banco
├── scripts/          # backup e resumo de uso
└── tests/            # testes automáticos
```

**Regras importantes:**
- **Duas barreiras de segurança.** Cada rota exige que a pessoa seja dona do `{usuario_id}` (403). Cada service confere que a tarefa ou o passo pertencem a ela (404).
- **A IA fica num único arquivo,** [`core/ia_service.py`](backend/core/ia_service.py). Trocar de fornecedor muda só esse arquivo. A resposta vem em JSON e é limpa e validada antes de salvar.
- **Erros de domínio** viram códigos HTTP claros:

  | Situação | Código |
  |---|---|
  | Não encontrado | 404 |
  | Dados inválidos | 422 |
  | Credenciais inválidas | 401 |
  | Limite do dia | 422 |
  | IA indisponível | 503 |
  | Muitas tentativas | 429 |

### Banco de dados

Esquema em [`database/schema.sql`](database/schema.sql). Decisões de projeto em [`docs/modelo-de-datos.md`](docs/modelo-de-datos.md).

| Tabela | Para quê |
|---|---|
| `usuarios` | Conta, limite diário de tarefas e se já fez o primeiro uso |
| `tarefas` | Título, data planejada (vazia = caixa de entrada), ordem no dia e se foi concluída |
| `passos` | Passos de cada tarefa, com minutos estimados, ordem, se foi concluído e de que passo veio (quando a IA divide um passo) |
| `fechamentos_dia` | Os dias que a pessoa encerrou |

### Principais rotas da API

Todas, exceto login e criar conta, exigem `Authorization: Bearer <token>`.

| Método e rota | O que faz |
|---|---|
| `POST /usuarios` · `POST /auth/login` | Criar conta · entrar |
| `POST /usuarios/{id}/tarefas/lote` | Anotar várias tarefas (uma por linha) |
| `GET /usuarios/{id}/tarefas/bandeja` | Caixa de entrada |
| `GET` · `POST /usuarios/{id}/tarefas/hoje` | Tarefas do dia · escolher para hoje |
| `PUT /usuarios/{id}/tarefas/hoje/ordem` | Reordenar o dia |
| `POST /usuarios/{id}/tarefas/{id}/passos/gerar` | A IA divide a tarefa em passos |
| `POST /usuarios/{id}/tarefas/{id}/passos/{id}/dividir` | "Travei": a IA divide um passo |
| `POST /usuarios/{id}/tarefas/{id}/passos/{id}/concluir` | Concluir um passo |
| `GET /usuarios/{id}/dias/{data}` · `POST .../fechar` | Resumo do dia · encerrar o dia |

Com a API rodando localmente, a lista completa e interativa fica em http://localhost:8000/docs.

### Front

```
frontend/
├── index.html
├── css/estilos.css   # tokens de cor (claro e escuro) e estilos
└── js/
    ├── app.js        # registra as telas e inicia o roteador
    ├── roteador.js   # rotas por hash (#/hoje, #/tarefa/12…)
    ├── api.js        # chamadas à API e tradução dos erros
    ├── i18n.js       # todos os textos, em espanhol e português
    ├── telas/        # uma tela por arquivo (hoje, bandeja, tarefa, foco, cerrar…)
    └── …             # componentes, ícones, tema, som, tempo
```

A interface é **otimista**: o que a pessoa anota aparece na hora e é salvo em segundo plano. Se o servidor falhar, o texto volta para o campo e nada se perde.

---

## Instalação e execução

### O que você precisa

- [Git](https://git-scm.com/)
- [Python 3.12](https://www.python.org/) ou mais novo
- Um banco **MySQL 8**: local ou na nuvem (nós usamos o [Aiven](https://aiven.io/), plano gratuito)
- Opcional: [MySQL Workbench](https://www.mysql.com/products/workbench/), para criar as tabelas e ver os dados
- Opcional: uma chave da API do [Gemini](https://aistudio.google.com/), só para a IA dividir as tarefas

### Dependências do backend

Estão em [`backend/requirements.txt`](backend/requirements.txt):

| Pacote | Para quê |
|---|---|
| `fastapi`, `uvicorn[standard]` | API e servidor |
| `SQLAlchemy`, `mysql-connector-python` | Acesso ao MySQL |
| `PyJWT` | Login com token |
| `python-dotenv` | Ler o `.env` |
| `google-genai` | IA (Gemini) |
| `httpx` | Cliente HTTP usado nos testes |

O front não tem dependências: é só servir a pasta `frontend/`.

### 1. Clonar o repositório

```
git clone https://github.com/jpao88/IAmigo-Final-Round.git
cd IAmigo-Final-Round
```

### 2. Criar o banco de dados

Abra [`database/schema.sql`](database/schema.sql) no Workbench (ou no cliente MySQL) e execute o arquivo inteiro. Ele cria o banco `iamigo` com as quatro tabelas e pode ser executado mais de uma vez sem apagar nada.

**Se usar o Aiven:**

1. No painel do Aiven, em **Overview → Connection information**, copie host, porta, usuário e senha e baixe o **CA certificate** (`ca.pem`).
2. Guarde o `ca.pem` **fora do repositório**, por exemplo em `C:/Users/<seu-usuario>/Certs/ca.pem`.
3. No Workbench, na aba **SSL** da conexão, escolha `Require and Verify CA` e indique o caminho do `ca.pem`.

Se o Aiven não responder, o serviço pode estar desligado por inatividade: ligue-o pelo painel. Algumas redes, como Wi-Fis de instituições, bloqueiam a porta do Aiven; nesse caso, use dados móveis.

### 3. Configurar o backend

Na pasta `backend/`:

```
python -m venv .venv
.venv\Scripts\python -m pip install -r requirements.txt
copy .env.example .env
```

No macOS ou Linux, use `.venv/bin/python` e `cp` em vez de `.venv\Scripts\python` e `copy`.

Preencha o `backend/.env`:

| Variável | O que colocar |
|---|---|
| `DB_HOST`, `DB_PORT`, `DB_USER`, `DB_PASSWORD` | Dados da conexão com o MySQL |
| `DB_NAME` | `iamigo` |
| `DB_SSL_CA` | Caminho do `ca.pem`, escrito com `/`. Deixe vazio se usar um MySQL local sem SSL. |
| `JWT_SECRET` | Uma chave aleatória: `.venv\Scripts\python -c "import secrets; print(secrets.token_urlsafe(48))"` |
| `GEMINI_API_KEY` | Chave do Gemini. Só é necessária para dividir tarefas com a IA; sem ela, os passos podem ser escritos à mão. |
| `CORS_ORIGINS` | Endereços do front. O do exemplo serve para rodar localmente. |

O `.env` nunca vai para o GitHub.

### 4. Rodar o projeto

São necessários dois terminais.

**Backend**, na pasta `backend/`:

```
.venv\Scripts\python -m uvicorn api_app:app --reload --port 8000
```

A documentação interativa da API fica em http://localhost:8000/docs.

**Front**, na pasta `frontend/`:

```
python -m http.server 5500
```

Abra http://localhost:5500, crie uma conta e entre.

Para ver como no celular, use as ferramentas de desenvolvedor do navegador: no Chrome, **F12** e depois o ícone de dispositivo móvel.

## Testes

Na pasta `backend/`:

```
.venv\Scripts\python -m unittest discover -s tests
```

**O que cobrem:** regras de negócio, permissões e IA.
- **Permissões:** um teste falha se uma rota nova não estiver na matriz de permissões, e outro confere que ninguém acessa dados de outra pessoa.
- **IA:** a montagem dos prompts e a limpeza da resposta.
- **Traduções:** os dois idiomas têm as mesmas chaves.

Os testes não precisam de MySQL nem de Gemini.

## Publicação (DigitalOcean)

A app é publicada no DigitalOcean App Platform, na região de São Francisco, a mesma do MySQL do Aiven. A configuração está em [`.do/deploy.template.yaml`](.do/deploy.template.yaml):

- **web:** o front estático (`frontend/`), em `/`.
- **api:** o backend (`backend/`), em `/api`. O front detecta sozinho (`js/config.js`).

Cada `git push` na `main` publica de novo.

**Variáveis do backend** (escritas no painel da DigitalOcean, nunca no repositório):

| Variável | Valor |
|---|---|
| `DB_HOST`, `DB_PORT`, `DB_USER`, `DB_PASSWORD`, `DB_NAME` | Os mesmos do `.env` |
| `DB_SSL_CA_PEM` | O conteúdo completo do `ca.pem` (de `-----BEGIN CERTIFICATE-----` até `-----END CERTIFICATE-----`) |
| `JWT_SECRET` | Uma chave nova, diferente da local |
| `GEMINI_API_KEY` | A chave da IA |
| `DOCS_ABERTOS` | `nao` |
| `CORS_ORIGINS` | Vazio (front e API usam o mesmo domínio) |

## Backups

O Aiven faz cópias automáticas: aba **Backups** do serviço, e a restauração é feita com **Fork service**.

Também há um backup próprio, que salva contas, tarefas, passos e encerramentos do dia num arquivo JSON. Na pasta `backend/`:

```
.venv\Scripts\python scripts\exportar_dados.py
```

O arquivo fica em `RESPALDOS_DIR` do `.env` ou, se não houver, em `~/IAmigo-respaldos`. Ele tem dados pessoais e nunca vai para o repositório.

## Documentação do projeto

| Arquivo | Conteúdo |
|---|---|
| [`docs/hoja-de-ruta.md`](docs/hoja-de-ruta.md) | Fases do projeto e pontos de controle |
| [`docs/recorrido-v1.md`](docs/recorrido-v1.md) | Caminho da pessoa usuária, tela por tela, e os sete princípios de design |
| [`docs/modelo-de-datos.md`](docs/modelo-de-datos.md) | Modelo de dados e decisões |
| [`docs/backlog-v1.md`](docs/backlog-v1.md) | Épicos e histórias de usuário |
| [`docs/guion-validacion.md`](docs/guion-validacion.md) | Roteiro e resultados da validação com pessoas com TDAH |
| [`docs/diseno/`](docs/diseno/) | Guia visual e auditorias de interface |

**Convenções:**
- Código e banco de dados com nomes em português: `tarefas`, `passos`, `data_planejada`…
- Textos da interface em `frontend/js/i18n.js`, usados com `t("chave")`. Toda chave nova vai nos dois idiomas.
- O backend responde em português e o front traduz as mensagens que a pessoa vê.

---
---

# IAmigo (versión en español)

**App web de organización para adultos con TDAH.** Lleva a la persona de "tengo mil cosas en la cabeza" a "terminé lo importante de hoy" con un ciclo diario de cinco etapas: **capturar, desmenuzar** (la IA divide la tarea en pasos), **planear hoy, hacer** (modo foco) y **cerrar el día**. Está pensada primero para celular.

- **App publicada:** https://iamigo-lzdqn.ondigitalocean.app
- **Equipo:** Rafaela y Pablo
- **Idiomas de la interfaz:** español y portugués de Brasil

## El problema y el público

**Público:** adultos con TDAH, sobre todo estudiantes y trabajadores jóvenes que usan el celular todo el día.

**Lo que les cuesta:**

| Dificultad | Qué pasa |
|---|---|
| **Empezar** | Una tarea grande parece imposible y se posterga. |
| **Percibir el tiempo** | No notan cuánto pasó ni cuánto llevará algo. |
| **Decidir** | Frente a una lista larga, no saben por dónde arrancar. |
| **Recordar** | Las ideas aparecen en cualquier momento y se pierden si no se anotan rápido. |
| **Sostener el hábito** | Abandonan las apps de tareas porque las tareas atrasadas en rojo generan culpa. |

## La solución

**Objetivo:** que una persona nueva complete el ciclo entero el primer día, sola y con una tarea real.

**Diferenciales:**

- **La IA divide las tareas grandes** en pasos de 5 a 25 minutos, con el tiempo estimado de cada uno. **La IA sugiere y la persona decide:** todo se puede editar, reordenar o borrar.
- **"Me atasqué":** si la persona se traba en un paso, la IA lo divide en dos o tres pasos más chicos.
- **Una cosa a la vez:** la pantalla Hoy destaca solo la tarea de **Ahora**, y el modo foco muestra un paso por vez con un temporizador circular.
- **Límite diario** de tareas (3 por defecto, configurable), para no planear de más.
- **Sin culpa:** no hay rojo ni "atrasado". Lo que no se hizo pasa a mañana o vuelve a la Bandeja.
- **Validado con personas reales:** el recorrido se probó con 3 personas con TDAH antes de programar, y el diseño cambió con lo que aprendimos.

## Funcionalidades

| Etapa | Qué hace la persona |
|---|---|
| **Primer uso** | Crea la cuenta, ve el ciclo en una pantalla de bienvenida y lo prueba con una tarea guiada. |
| **Capturar** | Escribe una idea por línea en "¿Qué tienes en la cabeza?" y van a la **Bandeja**. Atajos como "Llamar a…" ayudan a empezar a escribir. |
| **Desmenuzar** | "Que IAmigo lo divida" genera los pasos con minutos. La persona también puede editarlos, reordenarlos, borrarlos o escribirlos a mano. |
| **Planear hoy** | Elige tareas de la Bandeja para **Hoy**. Ve **Ahora** destacado, con el tiempo en un anillo, **Después** y el tiempo total del día. |
| **Hacer** | Modo foco con temporizador circular y los botones **Hecho**, **+5 minutos**, **Pausar** y **Me atasqué**. Cada paso terminado tiene una celebración con sonido. Al volver a la app, ofrece seguir donde quedó. |
| **Cerrar el día** | Muestra un resumen de lo hecho. Lo pendiente va a "Hacerla mañana" o "Guardarla sin fecha". |

**Además:**
- Español y portugués.
- Modo claro y oscuro.
- "Deshacer" al borrar una tarea.
- Interfaz accesible: contraste AA, zonas táctiles de 44 px y animaciones que respetan "reducir movimiento".

## Arquitectura y tecnologías

| Capa | Tecnología |
|---|---|
| **Backend** | Python 3.12+ con FastAPI y Uvicorn, en capas: rutas → controller → service → repository |
| **Acceso a datos** | SQLAlchemy 2 + mysql-connector-python |
| **Base de datos** | MySQL 8 (en la nube: Aiven, con SSL). Tablas: `usuarios`, `tarefas`, `passos`, `fechamentos_dia` |
| **Autenticación** | JWT, contraseñas con hash y límite de intentos de inicio de sesión |
| **IA** | Google Gemini, aislada en `backend/core/ia_service.py` |
| **Front** | HTML, CSS y JavaScript puro en módulos ES, sin frameworks ni compilación |
| **Tests** | `unittest` de Python (corren sin MySQL ni Gemini) |
| **Publicación** | DigitalOcean App Platform |

**Seguridad:** hay dos barreras. Cada ruta exige ser el dueño del `{usuario_id}` (403), y cada service confirma que la tarea o el paso pertenecen a esa persona (404).

La estructura de carpetas, las tablas y las rutas principales están detalladas en la versión en portugués, más arriba.

## Instalación y ejecución

**Necesitas:**
- Git y Python 3.12 o más nuevo.
- Una base MySQL 8 (local o en Aiven).
- Opcional: MySQL Workbench y una clave de Gemini.

1. **Clonar:**
   ```
   git clone https://github.com/jpao88/IAmigo-Final-Round.git
   cd IAmigo-Final-Round
   ```
2. **Base de datos:** ejecutar [`database/schema.sql`](database/schema.sql) completo. Con Aiven:
   - Descargar el `ca.pem` y guardarlo **fuera del repositorio**.
   - En Workbench, elegir SSL `Require and Verify CA`.
3. **Backend**, desde `backend/`:
   ```
   python -m venv .venv
   .venv\Scripts\python -m pip install -r requirements.txt
   copy .env.example .env
   ```
   Completar en el `.env`:
   - `DB_HOST`, `DB_PORT`, `DB_USER`, `DB_PASSWORD` y `DB_NAME=iamigo`;
   - `DB_SSL_CA` (ruta del `ca.pem`, o vacío para un MySQL local sin SSL);
   - `JWT_SECRET` (clave aleatoria);
   - `GEMINI_API_KEY` (opcional);
   - `CORS_ORIGINS`.

   El `.env` nunca se sube a GitHub.
4. **Levantar**, en dos terminales:
   - Backend, desde `backend/`: `.venv\Scripts\python -m uvicorn api_app:app --reload --port 8000` (documentación de la API en http://localhost:8000/docs).
   - Front, desde `frontend/`: `python -m http.server 5500`. Luego abrir http://localhost:5500.
5. **Tests**, desde `backend/`: `.venv\Scripts\python -m unittest discover -s tests`

La publicación en DigitalOcean, los respaldos y la documentación del proyecto están explicados en las secciones en portugués, más arriba.
