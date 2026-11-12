// Endereço do backend.
// - No computador (localhost) ou no celular pela rede de casa (192.168.x.x):
//   o mesmo computador de onde a página foi aberta, na porta 8000.
// - Publicada (DigitalOcean): front e API no mesmo domínio; a API fica em /api.

const LOCAL = /^(localhost|127\.0\.0\.1|10\.\d+\.\d+\.\d+|192\.168\.\d+\.\d+|172\.(1[6-9]|2\d|3[01])\.\d+\.\d+)$/;

export const API_URL = LOCAL.test(location.hostname)
  ? `${location.protocol}//${location.hostname}:8000`
  : `${location.origin}/api`;
