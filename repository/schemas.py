import enum
from pydantic import BaseModel
from typing import List


class StatusPedido(str, enum.Enum):
    PENDENTE  = "pendente"
    PAGO      = "pago"
    ENVIADO   = "enviado"
    ENTREGUE  = "entregue"
    CANCELADO = "cancelado"


ORDEM_STATUS = [
    StatusPedido.PENDENTE,
    StatusPedido.PAGO,
    StatusPedido.ENVIADO,
    StatusPedido.ENTREGUE,
]


class ItemEntrada(BaseModel):
    produto:    str
    quantidade: int
    preco:      float


class PedidoEntrada(BaseModel):
    cliente: str
    itens:   List[ItemEntrada]


class AtualizarStatus(BaseModel):
    novo_status:  StatusPedido
    alterado_por: str


class CancelarPedido(BaseModel):
    alterado_por: str
