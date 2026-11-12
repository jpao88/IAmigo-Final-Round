from services.dia_service import DiaService


class DiaController:
    """Repassa os pedidos da API para o service (Épica 5 · Cerrar el día)."""

    def __init__(self, service=None):
        self.service = service or DiaService()

    def resumo(self, usuario_id, data):
        return self.service.resumo(usuario_id, data)

    def fechar(self, usuario_id, data):
        self.service.fechar(usuario_id, data)

    def dia_pendente(self, usuario_id, hoje):
        return self.service.dia_pendente(usuario_id, hoje)
