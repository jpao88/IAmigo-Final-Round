// Endereço do backend: o mesmo computador de onde a página foi aberta, na porta 8000.
// Funciona com localhost e também no celular pela rede local (http://192.168.x.x:5500).
// Ao publicar a app (Fase 3), trocar pela URL do hosting.
export const API_URL = `${location.protocol}//${location.hostname}:8000`;
