# Roteiro do vídeo do IAmigo

**Duração prevista:** 13 minutos (limite: 15). **Apresentam:** Rafaela e Pablo. Versão em espanhol: `guion-video.md`.

O roteiro segue a estrutura pedida pelo professor:
1. Problemática
2. Público-alvo
3. Solução proposta
4. Arquitetura
5. Funcionalidades
6. Demonstração prática

**Como a nota é dividida:**
- **80% avaliação técnica:** código, arquitetura, banco de dados, rotas e regras de negócio.
- **20% UX.**

Por isso, a arquitetura mostra código de verdade, e a demonstração mostra a app funcionando de ponta a ponta.

**Como ler este roteiro:**
- **Na tela:** o que aparece no vídeo.
- **Fala:** quem diz o texto (**Rafaela** ou **Pablo**).
- **Tempos:** são aproximados.

---

## Quem faz o quê

O professor pede que a divisão de responsabilidades garanta a colaboração de todos. A divisão abaixo é uma sugestão; ajustem como preferirem.

| Responsabilidade | Quem |
|---|---|
| Roteiro | Rafaela e Pablo |
| Narração: problemática, público-alvo, funcionalidades e demonstração | Rafaela |
| Narração: solução, arquitetura e código | Pablo |
| Demonstração prática (uso da app) | Rafaela |
| Gravação de tela da parte técnica (VS Code) | Pablo |
| Edição e publicação do vídeo | A definir |

> Não é obrigatório aparecer na câmera: pode ser só a tela com a voz.

---

## Antes de gravar

- [ ] **Aiven ligado.** No instituto, usem dados móveis: o Wi-Fi bloqueia a porta do banco.
- [ ] **App em português** (link "Português" no login) e em visualização de celular: F12 → ícone de celular → 390 px. Também dá para gravar o celular.
- [ ] **Conta "Demo" recém-criada,** para mostrar as boas-vindas.
- [ ] **Uma segunda conta já com tarefas,** caso algo falhe.
- [ ] **Uma tarefa para a IA dividir,** por exemplo "Preparar a apresentação de sexta-feira". A IA leva uns 5 segundos: não cortem.
- [ ] **VS Code aberto** com o projeto.
- [ ] **Backend rodando localmente,** para mostrar http://localhost:8000/docs (na app publicada essa página está fechada de propósito).
- [ ] **Som da app ligado** e notificações do computador desligadas.

---

## 1. Problemática · 0:00 – 1:15

**Na tela:** a tela de login, com o logo do IAmigo.

**Pablo:**
> Olá, eu sou o Pablo…

**Rafaela:**
> …e eu sou a Rafaela. Este é o IAmigo.
>
> O problema que escolhemos é a organização do dia a dia para pessoas com TDAH. Não é falta de vontade. Algumas coisas são muito difíceis:
> - **começar** uma tarefa grande, que parece impossível;
> - **perceber o tempo**, quanto passou e quanto falta;
> - **decidir** por onde começar diante de uma lista longa;
> - **lembrar** as ideias que aparecem a qualquer hora.
>
> E tem um problema a mais: os apps de tarefas comuns mostram tarefas atrasadas em vermelho. Isso gera culpa, e a pessoa acaba abandonando o app. É um problema real, que afeta os estudos, o trabalho e a autoestima.

> Nota: se quiserem, citem aqui um dado sobre TDAH em adultos, **com a fonte**. Não incluímos números para não inventar dados.

---

## 2. Público-alvo · 1:15 – 2:00

**Na tela:** a seção "Persona" de `docs/recorrido-v1.md`.

**Rafaela:**
> O IAmigo é para **adultos com TDAH**, especialmente estudantes e jovens que trabalham e usam o celular o dia todo. Por isso a app foi pensada **primeiro para o celular**.
>
> Antes de programar, testamos o desenho com **três pessoas com TDAH**. Isso mudou coisas importantes: ninguém encontrava como dividir uma tarefa, e as três pediram para escolher quantas tarefas fazer por dia. Ajustamos e testamos de novo.

---

## 3. Solução proposta · 2:00 – 3:30

**Na tela:** a tela de boas-vindas da app, com as cinco etapas. Depois, a seção dos sete princípios em `docs/recorrido-v1.md`.

**Pablo:**
> **Objetivo:** levar a pessoa de "estou com mil coisas na cabeça" para "terminei o mais importante de hoje", com um ciclo diário de cinco etapas: anotar, dividir, planejar o dia, fazer e encerrar o dia. A meta é que uma pessoa nova complete o ciclo inteiro no primeiro dia, sozinha.
>
> **Diferenciais:**
> - **A IA divide tarefas grandes** em passos de cinco a vinte e cinco minutos, com o tempo de cada um. E se a pessoa travar num passo, a IA divide esse passo em outros menores.
> - **A IA sugere e a pessoa decide:** tudo pode ser editado.
> - **Uma coisa por vez:** a tela destaca só o que é para fazer agora, e existe um limite de tarefas por dia.
> - **Sem culpa:** não tem vermelho nem "atrasado". O que não foi feito passa para amanhã.
>
> Esses são alguns dos sete princípios de design que revisamos em cada tela.

---

## 4. Arquitetura · 3:30 – 7:00

> Esta é a parte que mais pesa na nota técnica. Mostrem o código com calma, com zoom no VS Code.

### 4.1 Visão geral · 3:30 – 4:10
**Na tela:** o diagrama da seção "Arquitetura e tecnologias" do `README.md`.

**Pablo:**
> A aplicação tem três partes:
> - um **front** em JavaScript puro;
> - uma **API** em Python com FastAPI;
> - um banco **MySQL 8** na nuvem, na Aiven, com conexão criptografada por SSL.
>
> A **IA** é o Gemini, do Google. Tudo está publicado na **DigitalOcean**.

### 4.2 Backend em camadas · 4:10 – 5:10
**Na tela:** VS Code, abrindo `backend/api/`, `controllers/`, `services/` e `repositories/`. Depois, `services/tarefa_service.py` na função `planejar_para_hoje` (linha ~142), mostrando o `LimiteHojeAtingido`.

**Pablo:**
> O backend segue uma **arquitetura em camadas**, e cada uma tem uma única responsabilidade:
> - as **rotas** recebem o pedido HTTP;
> - o **controller** organiza;
> - o **service** tem as **regras de negócio**;
> - o **repository** é o único que fala com o banco.
>
> Por exemplo, aqui está a regra do limite do dia. Antes de colocar tarefas em Hoje, o service confere quantas já existem. Se não couberem, devolve um erro claro, "Hoje já está cheio", com o código 422. Outra regra: quando a pessoa conclui o último passo, a tarefa fica concluída automaticamente.

### 4.3 Banco de dados · 5:10 – 5:40
**Na tela:** `database/schema.sql`, nas quatro tabelas.

**Pablo:**
> O banco tem quatro tabelas:
> - `usuarios`;
> - `tarefas`, que pertencem a um usuário;
> - `passos`, que pertencem a uma tarefa;
> - `fechamentos_dia`, os dias que a pessoa encerrou.
>
> O modelo foi fechado antes de programar. Uma tarefa sem data fica na caixa de entrada; com a data de hoje, aparece em Hoje.

### 4.4 Rotas e segurança · 5:40 – 6:20
**Na tela:** http://localhost:8000/docs, com a lista de rotas. Depois, `api/dependencias.py`, na função `exigir_dono`.

**Pablo:**
> As rotas seguem o padrão REST: por exemplo, `POST /usuarios/{id}/tarefas/lote` para anotar e `GET .../tarefas/hoje` para o dia.
>
> O login usa **JWT**, e as senhas são guardadas com hash, nunca em texto. A segurança tem **duas barreiras**:
> - a rota confere se a pessoa é dona do `usuario_id`;
> - o service confere de novo se a tarefa ou o passo são dela.
>
> Também limitamos as tentativas de login erradas.

### 4.5 IA, front e testes · 6:20 – 7:00
**Na tela:** `core/ia_service.py`. Depois, `frontend/js/` com a pasta `telas/` e o `i18n.js`. Por fim, o terminal rodando `.venv\Scripts\python -m unittest discover -s tests` até aparecer "OK".

**Pablo:**
> **IA:** tudo o que depende do fornecedor está num único arquivo. Pedimos a resposta em JSON e validamos antes de salvar.
>
> **Front:** é JavaScript puro em módulos, uma tela por arquivo, com todos os textos em português e espanhol num só arquivo.
>
> **Testes:** temos mais de cem testes automáticos que rodam em segundos, sem precisar do banco nem da IA. Um deles falha se alguém criar uma rota sem declarar as permissões.

---

## 5. Funcionalidades · 7:00 – 7:45

**Na tela:** a app, passando rapidamente pelas abas Hoje e Caixa de entrada.

**Rafaela:**
> As principais funcionalidades acompanham o ciclo:
> - **anotar** ideias em segundos;
> - **dividir** tarefas com IA;
> - **escolher** as tarefas do dia, com um limite;
> - **fazer** cada passo no modo foco, com cronômetro;
> - **encerrar** o dia com um resumo.
>
> Além disso: português e espanhol, modo claro e escuro, e "Desfazer" ao apagar uma tarefa. Agora vou mostrar tudo funcionando.

---

## 6. Demonstração prática · 7:45 – 12:30

### 6.1 Primeiro uso · 7:45 – 8:15
**Na tela:** criar a conta → boas-vindas → "Testar com uma tarefa".

**Rafaela:**
> Quando alguém cria a conta, o IAmigo mostra o ciclo numa tela e propõe testar com uma tarefa real.

### 6.2 Anotar · 8:15 – 9:00
**Na tela:** a Caixa de entrada.
1. Escrever duas ou três ideias, uma por linha, e apertar Enter.
2. Tocar em "Ligar para…" e completar.

**Rafaela:**
> "O que está na sua cabeça?" Escrevo uma ideia por linha, aperto Enter e elas ficam salvas na hora, sem precisar escolher data nem prioridade. Se for difícil começar a escrever, esses atalhos ajudam.

### 6.3 Dividir com IA · 9:00 – 10:00
**Na tela:**
1. Abrir "Preparar a apresentação de sexta-feira" → "Deixe o IAmigo dividir".
2. Esperar os passos.
3. Editar um passo, mudar os minutos e apagar um passo com "Ordenar".

**Rafaela:**
> A IA divide a tarefa em passos pequenos e estima os minutos. Posso mudar o texto, os minutos e a ordem, ou apagar. Se a IA falhar, escrevo os passos eu mesma.

### 6.4 Planejar o dia · 10:00 – 10:40
**Na tela:**
1. Hoje → "Escolher tarefas para hoje".
2. Marcar 2: o botão muda para "Adicionar 2 tarefas a Hoje".
3. Hoje, com o cartão Agora.

**Rafaela:**
> Escolho o que vou fazer hoje, com um limite de três por padrão. A tela Hoje destaca só o **Agora**, com o tempo num anel, e mostra o total do dia em cima.

### 6.5 Fazer: modo foco · 10:40 – 11:50
**Na tela:**
1. "Começar".
2. "Feito" → comemoração com som.
3. Em outro passo, "Travei" → passos menores.

**Rafaela:**
> No modo foco aparece um passo por vez, com um cronômetro circular. Quando o tempo acaba não tem alarme: aparece "Sem pressa". Cada passo concluído ganha uma comemoração. Se eu travar, toco em "Travei" e a IA divide o passo em outros menores. E, se eu fechar a app, quando volto ela pergunta se vamos continuar de onde parei.

### 6.6 Encerrar o dia · 11:50 – 12:30
**Na tela:** "Encerrar o dia" → resumo → uma tarefa pendente com "Fazer amanhã" e "Guardar sem data".

**Rafaela:**
> No fim do dia, o IAmigo mostra o que eu fiz, não o que faltou. O que ficou pendente vai para amanhã ou volta para a caixa de entrada, sem castigo.

---

## 7. Encerramento · 12:30 – 13:15

**Na tela:** a tela Hoje da app.

**Pablo:**
> A app está publicada e em uso real: começamos uma prova de vários dias, e a Rafaela já completou o ciclo inteiro sozinha. O que mais aprendemos foi que **validar antes de programar economiza muito trabalho**.

**Rafaela:**
> Os próximos passos são terminar essa prova, corrigir o que aparecer e testar com mais pessoas.

**Os dois:**
> Obrigado por assistir. Este é o IAmigo!

---

## Se algo der errado durante a gravação

| O que falha | O que fazer |
|---|---|
| A IA não responde | Mostrar como parte da demonstração: tocar em "Prefiro escrever eu". |
| Os dados não carregam | A Aiven pode estar desligada: ligar pelo painel e recarregar. |
| O vídeo fica longo | Encurtar a parte 6.1 e juntar as partes 5 e 6. |

---

## Entrega

- [ ] **Vídeo** no YouTube (modo não listado), Google Drive ou OneDrive, **com a visualização liberada**. Abram o link numa janela anônima para conferir.
- [x] **Repositório público:** https://github.com/jpao88/IAmigo-Final-Round
- [ ] **`README.md` em português,** com instalação, dependências e execução.
