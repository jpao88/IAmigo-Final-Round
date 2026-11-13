// Idiomas da interface: espanhol (es) e português do Brasil (pt).
//
// t("chave") devolve o texto no idioma atual. Alguns textos são funções,
// para números e plurais: t("elegir.podeMais", 2) → "Puedes elegir 2 más.".
// Os dois dicionários têm as mesmas chaves (tests/test_traducoes.py confere).
//
// Sem escolha, segue o idioma do celular. A escolha fica em "iamigo-idioma"
// (hífen, não ponto): é do aparelho e não se apaga ao sair da conta.

const CHAVE = "iamigo-idioma";
export const IDIOMAS = ["es", "pt"];

const es = {
  // Comuns
  "comum.listo": "Listo",
  "comum.ordenar": "Ordenar",
  "comum.seguir": "Seguir",
  "comum.voltar": "Volver",
  "comum.voltarHoje": "Hoy",
  "comum.voltarAHoje": "Volver a Hoy",
  "comum.guardando": "Guardando…",
  "comum.carregando": "Cargando…",
  "comum.pensando": "IAmigo está pensando…",
  "comum.empezar": "Empezar",
  "comum.subir": (titulo) => `Subir: ${titulo}`,
  "comum.descer": (titulo) => `Bajar: ${titulo}`,
  "comum.min": "min",
  "comum.listaParaHoje": "Lista para hoy.",

  // Encabeçado e abas
  "marca.subtitulo": "ASISTENTE INTELIGENTE",
  "cab.sair": "Salir",
  "cab.ola": (nome) => `Hola, ${nome}`,
  "cab.modoClaro": "Cambiar a modo claro",
  "cab.modoEscuro": "Cambiar a modo oscuro",
  "cab.outroIdioma": "PT",
  "cab.outroIdiomaNome": "Português",
  "cab.trocarIdioma": "Ver en portugués",
  "nav.secoes": "Secciones",
  "nav.hoje": "Hoy",
  "nav.bandeja": "Bandeja",

  // Login e cadastro
  "login.titulo": "Hola de nuevo",
  "login.subtitulo": "Entra para ver tu día.",
  "login.email": "Correo",
  "login.senha": "Contraseña",
  "login.entrar": "Entrar",
  "login.entrando": "Entrando…",
  "login.criarConta": "Crear una cuenta",
  "login.faltam": "Escribe tu correo y tu contraseña.",
  "login.incorretos": "Correo o contraseña incorrectos.",
  "cadastro.titulo": "Crea tu cuenta",
  "cadastro.subtitulo": "Así guardas tus tareas.",
  "cadastro.nome": "Tu nombre",
  "cadastro.criar": "Crear cuenta",
  "cadastro.criando": "Creando…",
  "cadastro.jaTenho": "Ya tengo cuenta",
  "cadastro.nomeCurto": "Tu nombre necesita al menos 3 letras.",
  "cadastro.emailInvalido": "Revisa tu correo.",
  "cadastro.senhaCurta": "Usa al menos 6 caracteres en la contraseña.",

  // Primeiro uso
  "bienvenida.frase": "Te ayudo a terminar lo importante, un paso a la vez.",
  "bienvenida.assim": "Así funciona",
  "bienvenida.anota": "Anota",
  "bienvenida.divide": "Divide",
  "bienvenida.elige": "Elige",
  "bienvenida.hazlo": "Hazlo",
  "bienvenida.celebra": "Celebra",
  "bienvenida.probar": "Probar con una tarea",
  "bienvenida.saltar": "Ya sé cómo funciona",
  "primeira.titulo": "Escribe una cosa que tengas pendiente",
  "primeira.subtitulo": "Algo real, aunque sea pequeño. Lo hacemos juntos.",
  "primeira.rotulo": "Tu tarea",
  "primeira.exemplo": "Por ejemplo: ordenar el escritorio",
  "primeira.vazia": "Escribe algo primero.",

  // Bandeja
  "bandeja.pergunta": "¿Qué tienes en la cabeza?",
  "bandeja.placeholder": "Una idea por línea",
  "bandeja.chipsRotulo": "Ideas para empezar a escribir",
  "bandeja.chips": ["Llamar a", "Comprar", "Pagar", "Responder a"],
  "bandeja.guardar": "Guardar",
  "bandeja.vaziaCaptura": "Aquí aparecerá lo que anotes.",
  "bandeja.guardadaUma": "Guardado en tu Bandeja.",
  "bandeja.guardadas": (n) => `Guardé ${n} cosas.`,
  "bandeja.titulo": "Tu Bandeja",
  "bandeja.verTudo": "Ver toda tu Bandeja",
  "bandeja.maisHoje": "+ Hoy",
  "bandeja.maisHojeRotulo": (titulo) => `Agregar a Hoy: ${titulo}`,
  "bandeja.vazia": "Tu Bandeja está vacía.",

  // Hoy
  "hoje.titulo": "Hoy",
  "apagar.apagada": "Tarea borrada",
  "apagar.desfazer": "Deshacer",
  "elegir.adicionar": (n) => (n === 1 ? "Añadir 1 tarea a Hoy" : `Añadir ${n} tareas a Hoy`),
  "hoje.progresso": (feitas, total) => `${feitas} de ${total} ${total === 1 ? "hecha" : "hechas"}`,
  "hoje.retomar": "¿Seguimos donde quedaste?",
  "hoje.agoraNao": "Ahora no",
  "hoje.diaVazio": "Elige una cosa de tu Bandeja para empezar.",
  "hoje.ahora": "Ahora",
  "hoje.despues": "Después",
  "hoje.completo": "¡Completaste todo lo de hoy!",
  "hoje.terminarDia": "Terminar el día",
  "hoje.elegir": "Elegir tareas para hoy",
  "hoje.elegirMais": "Elegir más tareas",
  "hoje.jaFez": "Ya hiciste hoy",
  "hoje.quitar": "Quitar",
  "hoje.quitarRotulo": (titulo) => `Quitar de Hoy: ${titulo}`,
  "hoje.empezarRotulo": (titulo) => `Empezar: ${titulo}`,
  "hoje.tempoRotulo": (tempo) => `${tempo} en total`,
  "hoje.voltouBandeja": "Volvió a tu Bandeja.",

  // Elegir
  "elegir.mudarLimite": "Cambiar límite",
  "elegir.porDia": "Tareas por día",
  "elegir.vazia": "Tu Bandeja está vacía. Anota algo primero.",
  "elegir.limite": (n) => (n === 1 ? "Hasta 1 tarea por día." : `Hasta ${n} tareas por día.`),
  "elegir.hojeCheio": "Hoy ya está completo.",
  "elegir.diaCompleto": "Listo, tu día está completo.",
  "elegir.podeMais": (n) => (n === 1 ? "Puedes elegir 1 más." : `Puedes elegir ${n} más.`),

  // Tarefa e passos
  "tarefa.sugere": "IAmigo te sugiere los pasos y tú los ajustas.",
  "tarefa.dividir": "Que IAmigo lo divida",
  "tarefa.manual": "Prefiero escribirlos yo",
  "tarefa.novoPasso": "Nuevo paso",
  "tarefa.adicionePasso": "Agrega un paso",
  "tarefa.minutosNovo": "Minutos del nuevo paso",
  "tarefa.adicionar": "Agregar paso",
  "tarefa.guiaEmpezar": "Ponerla en Hoy y empezar",
  "tarefa.passo": (n) => `Paso ${n}`,
  "tarefa.minutosPasso": (n) => `Minutos del paso ${n}`,
  "tarefa.subirPasso": (n) => `Subir el paso ${n}`,
  "tarefa.descerPasso": (n) => `Bajar el paso ${n}`,
  "tarefa.apagarPasso": (n) => `Borrar el paso ${n}`,
  "tarefa.guiaComPassos": "¡Listo! Ajusta los pasos si quieres. Después, ponla en Hoy y haz el primero.",
  "tarefa.guiaSemPassos": "Ahora toca «Que IAmigo lo divida»: la parte en pasos pequeños.",
  "tarefa.comoTirar": "Para quitar un paso, toca Ordenar y luego la X de ese paso.",
  "tarefa.tituloRotulo": "Nombre de la tarea",
  "tarefa.tituloVazio": "Escribe el nombre de la tarea.",
  "tarefa.apagar": "Borrar tarea",

  // Modo foco
  "foco.frases": ["¡Bien hecho!", "¡Un paso menos!", "¡Así se hace!", "¡Vas muy bien!", "¡Eso es!"],
  "foco.semPressa": "Tómate tu tiempo",
  "foco.menosDe1": "Menos de 1 min",
  "foco.minutos": (n) => `${n} min`,
  "foco.guia": "3 de 3 · Haz solo este paso y toca «Hecho» al terminar.",
  "foco.seuPasso": "Tu paso ahora",
  "foco.hecho": "Hecho",
  "foco.mais5": "+5 minutos",
  "foco.pausar": "Pausar",
  "foco.atasquei": "Me atasqué",
  "foco.jaTerminada": "Esta tarea ya está terminada.",
  "foco.silenciar": "Silenciar sonidos",
  "foco.ativarSom": "Activar sonidos",
  "foco.emPausa": (tempo) => `En pausa · ${tempo}`,
  "foco.progresso": (atual, total) => `Paso ${atual} de ${total}`,
  "foco.assimFunciona": "¡Así funciona cada día!",
  "foco.ciclo": "Anota, divide, elige y hazlo, un paso a la vez.",
  "foco.terminaste": "¡Terminaste!",
  "foco.semPassos": "Divide la tarea en pasos primero.",

  // Cerrar el día
  "cerrar.hoje": "Hoy",
  "cerrar.ontem": "Ayer",
  "cerrar.diaDaSemana": (texto) => `El ${texto}`,
  "cerrar.passos": (n) => (n === 1 ? "1 paso" : `${n} pasos`),
  "cerrar.tarefas": (n) => (n === 1 ? "1 tarea" : `${n} tareas`),
  "cerrar.e": " y ",
  "cerrar.frase": (quando, partes) => `${quando} completaste ${partes}.`,
  "cerrar.tranquilo": (quando) => `${quando} fue un día tranquilo. Cerrarlo también cuenta.`,
  "cerrar.pergunta": "¿Qué hacemos con estas?",
  "cerrar.semDecidir": "Lo que no decidas vuelve a tu Bandeja.",
  "cerrar.amanha": "Hacerla mañana",
  "cerrar.hojeTambem": "Hacerla hoy",
  "cerrar.guardar": "Guardarla sin fecha",
  "cerrar.rotulo": (acao, titulo) => `${acao}: ${titulo}`,
  "cerrar.cheio": (amanha) => `${amanha ? "Mañana" : "Hoy"} ya está completo. Guárdala sin fecha o cambia el límite en Elegir.`,
  "cerrar.prontaAmanha": "Lista para mañana.",
  "cerrar.guardada": "Guardada en tu Bandeja.",
  "cerrar.diaFechado": "Día cerrado",
  "cerrar.descansa": "Descansa, te lo ganaste.",

  // Tempo
  "tempo.minutos": (n) => `Unos ${n} minutos`,
  "tempo.horas": (h) => (h === 1 ? "1 hora" : `${h} horas`),
  "tempo.maisOuMenos": (horas) => `Más o menos ${horas}`,
  "tempo.horasEMinutos": (horas, m) => `Más o menos ${horas} y ${m} minutos`,
  "tempo.curto": (n) => `unos ${n} min`,

  // Erros
  "erro.generico": "Algo salió mal. Intenta otra vez.",
  "erro.semConexao": "No pudimos conectar. Intenta otra vez.",
  "erro.dados": "Revisa los datos e intenta otra vez.",
  "erro.ia": "IAmigo no pudo ahora. Puedes escribirlos tú.",
  "erro.iaDividir": "IAmigo no pudo dividirlo ahora. Prueba en un rato.",
};

const pt = {
  "comum.listo": "Pronto",
  "comum.ordenar": "Ordenar",
  "comum.seguir": "Continuar",
  "comum.voltar": "Voltar",
  "comum.voltarHoje": "Hoje",
  "comum.voltarAHoje": "Voltar para Hoje",
  "comum.guardando": "Salvando…",
  "comum.carregando": "Carregando…",
  "comum.pensando": "O IAmigo está pensando…",
  "comum.empezar": "Começar",
  "comum.subir": (titulo) => `Subir: ${titulo}`,
  "comum.descer": (titulo) => `Descer: ${titulo}`,
  "comum.min": "min",
  "comum.listaParaHoje": "Pronta para hoje.",

  "marca.subtitulo": "ASSISTENTE INTELIGENTE",
  "cab.sair": "Sair",
  "cab.ola": (nome) => `Olá, ${nome}`,
  "cab.modoClaro": "Mudar para o modo claro",
  "cab.modoEscuro": "Mudar para o modo escuro",
  "cab.outroIdioma": "ES",
  "cab.outroIdiomaNome": "Español",
  "cab.trocarIdioma": "Ver em espanhol",
  "nav.secoes": "Seções",
  "nav.hoje": "Hoje",
  "nav.bandeja": "Caixa de entrada",

  "login.titulo": "Olá de novo",
  "login.subtitulo": "Entre para ver o seu dia.",
  "login.email": "E-mail",
  "login.senha": "Senha",
  "login.entrar": "Entrar",
  "login.entrando": "Entrando…",
  "login.criarConta": "Criar uma conta",
  "login.faltam": "Escreva seu e-mail e sua senha.",
  "login.incorretos": "E-mail ou senha incorretos.",
  "cadastro.titulo": "Crie sua conta",
  "cadastro.subtitulo": "Assim você guarda suas tarefas.",
  "cadastro.nome": "Seu nome",
  "cadastro.criar": "Criar conta",
  "cadastro.criando": "Criando…",
  "cadastro.jaTenho": "Já tenho conta",
  "cadastro.nomeCurto": "Seu nome precisa de pelo menos 3 letras.",
  "cadastro.emailInvalido": "Confira seu e-mail.",
  "cadastro.senhaCurta": "Use pelo menos 6 caracteres na senha.",

  "bienvenida.frase": "Eu te ajudo a terminar o importante, um passo de cada vez.",
  "bienvenida.assim": "Assim funciona",
  "bienvenida.anota": "Anote",
  "bienvenida.divide": "Divida",
  "bienvenida.elige": "Escolha",
  "bienvenida.hazlo": "Faça",
  "bienvenida.celebra": "Comemore",
  "bienvenida.probar": "Testar com uma tarefa",
  "bienvenida.saltar": "Já sei como funciona",
  "primeira.titulo": "Escreva uma coisa que você tem pendente",
  "primeira.subtitulo": "Algo real, mesmo que pequeno. A gente faz junto.",
  "primeira.rotulo": "Sua tarefa",
  "primeira.exemplo": "Por exemplo: arrumar a escrivaninha",
  "primeira.vazia": "Escreva algo primeiro.",

  "bandeja.pergunta": "O que está na sua cabeça?",
  "bandeja.placeholder": "Uma ideia por linha",
  "bandeja.chipsRotulo": "Ideias para começar a escrever",
  "bandeja.chips": ["Ligar para", "Comprar", "Pagar", "Responder"],
  "bandeja.guardar": "Salvar",
  "bandeja.vaziaCaptura": "Aqui vai aparecer o que você anotar.",
  "bandeja.guardadaUma": "Salvo na sua caixa de entrada.",
  "bandeja.guardadas": (n) => `Salvei ${n} coisas.`,
  "bandeja.titulo": "Sua caixa de entrada",
  "bandeja.verTudo": "Ver toda a caixa de entrada",
  "bandeja.maisHoje": "+ Hoje",
  "bandeja.maisHojeRotulo": (titulo) => `Adicionar a Hoje: ${titulo}`,
  "bandeja.vazia": "Sua caixa de entrada está vazia.",

  "hoje.titulo": "Hoje",
  "apagar.apagada": "Tarefa apagada",
  "apagar.desfazer": "Desfazer",
  "elegir.adicionar": (n) => (n === 1 ? "Adicionar 1 tarefa a Hoje" : `Adicionar ${n} tarefas a Hoje`),
  "hoje.progresso": (feitas, total) => `${feitas} de ${total} ${total === 1 ? "feita" : "feitas"}`,
  "hoje.retomar": "Vamos continuar de onde você parou?",
  "hoje.agoraNao": "Agora não",
  "hoje.diaVazio": "Escolha uma coisa da sua caixa de entrada para começar.",
  "hoje.ahora": "Agora",
  "hoje.despues": "Depois",
  "hoje.completo": "Você concluiu tudo de hoje!",
  "hoje.terminarDia": "Encerrar o dia",
  "hoje.elegir": "Escolher tarefas para hoje",
  "hoje.elegirMais": "Escolher mais tarefas",
  "hoje.jaFez": "Você já fez hoje",
  "hoje.quitar": "Tirar",
  "hoje.quitarRotulo": (titulo) => `Tirar de Hoje: ${titulo}`,
  "hoje.empezarRotulo": (titulo) => `Começar: ${titulo}`,
  "hoje.tempoRotulo": (tempo) => `${tempo} no total`,
  "hoje.voltouBandeja": "Voltou para a sua caixa de entrada.",

  "elegir.mudarLimite": "Mudar limite",
  "elegir.porDia": "Tarefas por dia",
  "elegir.vazia": "Sua caixa de entrada está vazia. Anote algo primeiro.",
  "elegir.limite": (n) => (n === 1 ? "Até 1 tarefa por dia." : `Até ${n} tarefas por dia.`),
  "elegir.hojeCheio": "Hoje já está completo.",
  "elegir.diaCompleto": "Pronto, seu dia está completo.",
  "elegir.podeMais": (n) => (n === 1 ? "Você pode escolher mais 1." : `Você pode escolher mais ${n}.`),

  "tarefa.sugere": "O IAmigo sugere os passos e você ajusta.",
  "tarefa.dividir": "Deixe o IAmigo dividir",
  "tarefa.manual": "Prefiro escrever eu",
  "tarefa.novoPasso": "Novo passo",
  "tarefa.adicionePasso": "Adicione um passo",
  "tarefa.minutosNovo": "Minutos do novo passo",
  "tarefa.adicionar": "Adicionar passo",
  "tarefa.guiaEmpezar": "Colocar em Hoje e começar",
  "tarefa.passo": (n) => `Passo ${n}`,
  "tarefa.minutosPasso": (n) => `Minutos do passo ${n}`,
  "tarefa.subirPasso": (n) => `Subir o passo ${n}`,
  "tarefa.descerPasso": (n) => `Descer o passo ${n}`,
  "tarefa.apagarPasso": (n) => `Apagar o passo ${n}`,
  "tarefa.guiaComPassos": "Pronto! Ajuste os passos se quiser. Depois, coloque em Hoje e faça o primeiro.",
  "tarefa.guiaSemPassos": "Agora toque em «Deixe o IAmigo dividir»: ele divide em passos pequenos.",
  "tarefa.comoTirar": "Para tirar um passo, toque em Ordenar e depois no X desse passo.",
  "tarefa.tituloRotulo": "Nome da tarefa",
  "tarefa.tituloVazio": "Escreva o nome da tarefa.",
  "tarefa.apagar": "Apagar tarefa",

  "foco.frases": ["Muito bem!", "Um passo a menos!", "É isso aí!", "Você está indo muito bem!", "Isso!"],
  "foco.semPressa": "Sem pressa",
  "foco.menosDe1": "Menos de 1 min",
  "foco.minutos": (n) => `${n} min`,
  "foco.guia": "3 de 3 · Faça só este passo e toque em «Feito» ao terminar.",
  "foco.seuPasso": "Seu passo agora",
  "foco.hecho": "Feito",
  "foco.mais5": "+5 minutos",
  "foco.pausar": "Pausar",
  "foco.atasquei": "Travei",
  "foco.jaTerminada": "Esta tarefa já está concluída.",
  "foco.silenciar": "Silenciar sons",
  "foco.ativarSom": "Ativar sons",
  "foco.emPausa": (tempo) => `Em pausa · ${tempo}`,
  "foco.progresso": (atual, total) => `Passo ${atual} de ${total}`,
  "foco.assimFunciona": "É assim todos os dias!",
  "foco.ciclo": "Anote, divida, escolha e faça, um passo de cada vez.",
  "foco.terminaste": "Você terminou!",
  "foco.semPassos": "Divida a tarefa em passos primeiro.",

  "cerrar.hoje": "Hoje",
  "cerrar.ontem": "Ontem",
  // "Na terça" mas "No sábado": pelo número do dia fica sempre certo.
  "cerrar.diaDaSemana": (texto, data) => `No dia ${data.getDate()}`,
  "cerrar.passos": (n) => (n === 1 ? "1 passo" : `${n} passos`),
  "cerrar.tarefas": (n) => (n === 1 ? "1 tarefa" : `${n} tarefas`),
  "cerrar.e": " e ",
  "cerrar.frase": (quando, partes) => `${quando} você concluiu ${partes}.`,
  "cerrar.tranquilo": (quando) => `${quando} foi um dia tranquilo. Encerrar o dia também conta.`,
  "cerrar.pergunta": "O que fazemos com estas?",
  "cerrar.semDecidir": "O que você não decidir volta para a caixa de entrada.",
  "cerrar.amanha": "Fazer amanhã",
  "cerrar.hojeTambem": "Fazer hoje",
  "cerrar.guardar": "Guardar sem data",
  "cerrar.rotulo": (acao, titulo) => `${acao}: ${titulo}`,
  "cerrar.cheio": (amanha) => `${amanha ? "Amanhã" : "Hoje"} já está completo. Guarde sem data ou mude o limite em Escolher.`,
  "cerrar.prontaAmanha": "Pronta para amanhã.",
  "cerrar.guardada": "Guardada na sua caixa de entrada.",
  "cerrar.diaFechado": "Dia encerrado",
  "cerrar.descansa": "Descanse, você merece.",

  "tempo.minutos": (n) => `Uns ${n} minutos`,
  "tempo.horas": (h) => (h === 1 ? "1 hora" : `${h} horas`),
  "tempo.maisOuMenos": (horas) => `Mais ou menos ${horas}`,
  "tempo.horasEMinutos": (horas, m) => `Mais ou menos ${horas} e ${m} minutos`,
  "tempo.curto": (n) => `uns ${n} min`,

  "erro.generico": "Algo deu errado. Tente de novo.",
  "erro.semConexao": "Não conseguimos conectar. Tente de novo.",
  "erro.dados": "Confira os dados e tente de novo.",
  "erro.ia": "O IAmigo não conseguiu agora. Você pode escrevê-los.",
  "erro.iaDividir": "O IAmigo não conseguiu dividir agora. Tente daqui a pouco.",
};

export const DICIONARIOS = { es, pt };

function detectar() {
  try {
    const salvo = localStorage.getItem(CHAVE);
    if (IDIOMAS.includes(salvo)) return salvo;
  } catch {
    // Sem armazenamento: usa o do celular.
  }
  return (navigator.language || "").toLowerCase().startsWith("pt") ? "pt" : "es";
}

let atual = detectar();
document.documentElement.lang = atual === "pt" ? "pt-BR" : "es";

export function idioma() {
  return atual;
}

// Para datas: "martes 11" / "terça-feira 11".
export function localeDatas() {
  return atual === "pt" ? "pt-BR" : "es";
}

export function t(chave, ...argumentos) {
  const valor = DICIONARIOS[atual][chave] ?? es[chave];
  if (valor === undefined) {
    console.warn(`Falta o texto "${chave}".`);
    return chave;
  }
  return typeof valor === "function" ? valor(...argumentos) : valor;
}

// Troca e recarrega: todas as telas se desenham de novo no idioma novo.
export function trocarIdioma() {
  atual = atual === "es" ? "pt" : "es";
  try {
    localStorage.setItem(CHAVE, atual);
  } catch {
    // Sem armazenamento: vale até recarregar.
  }
  location.reload();
}
