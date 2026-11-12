// Ponto de entrada do front: registra as telas e inicia o roteador.

import { quandoPerderSessao } from "./api.js";
import { iniciarRoteador, navegar, registrarRota } from "./roteador.js";
import { telaBandeja } from "./telas/bandeja.js";
import { telaCadastro } from "./telas/cadastro.js";
import { telaElegir } from "./telas/elegir.js";
import { telaFoco } from "./telas/foco.js";
import { telaHoje } from "./telas/hoje.js";
import { telaLogin } from "./telas/login.js";
import { telaTarefa } from "./telas/tarefa.js";

registrarRota("/login", telaLogin, { publica: true });
registrarRota("/cadastro", telaCadastro, { publica: true });
registrarRota("/hoje", telaHoje);
registrarRota("/bandeja", telaBandeja);
registrarRota("/elegir", telaElegir);
registrarRota("/tarefa/:id", telaTarefa);
registrarRota("/foco/:id", telaFoco);

// Token vencido ou recusado: volta ao login sem mensagens de erro.
quandoPerderSessao(() => navegar("/login"));

iniciarRoteador(document.getElementById("app"));
