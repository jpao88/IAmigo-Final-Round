// Ponto de entrada do front: registra as telas e inicia o roteador.

import { quandoPerderSessao } from "./api.js";
import { iniciarRoteador, navegar, registrarRota } from "./roteador.js";
import { telaBandeja } from "./telas/bandeja.js";
import { telaCadastro } from "./telas/cadastro.js";
import { telaLogin } from "./telas/login.js";
import { telaTarefa } from "./telas/tarefa.js";

registrarRota("/login", telaLogin, { publica: true });
registrarRota("/cadastro", telaCadastro, { publica: true });
registrarRota("/bandeja", telaBandeja);
registrarRota("/tarefa/:id", telaTarefa);

// Token vencido ou recusado: volta ao login sem mensagens de erro.
quandoPerderSessao(() => navegar("/login"));

iniciarRoteador(document.getElementById("app"));
