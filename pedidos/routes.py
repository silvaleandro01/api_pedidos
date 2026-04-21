from fastapi import APIRouter, Depends
from utils.database import get_db
from repository.schemas import PedidoEntrada, AtualizarStatus, CancelarPedido
import service.pedidos as service

router = APIRouter()


@router.post("/pedidos")
def criar_pedido(dados: PedidoEntrada, db=Depends(get_db)):
    return service.criar_pedido(db, dados)


@router.get("/pedidos/{pedido_id}/status")
def consultar_status(pedido_id: int, db=Depends(get_db)):
    return service.consultar_status(db, pedido_id)


@router.patch("/pedidos/{pedido_id}/status")
def atualizar_status(pedido_id: int, dados: AtualizarStatus, db=Depends(get_db)):
    return service.atualizar_status(db, pedido_id, dados)


@router.patch("/pedidos/{pedido_id}/cancelar")
def cancelar_pedido(pedido_id: int, dados: CancelarPedido, db=Depends(get_db)):
    return service.cancelar_pedido(db, pedido_id, dados)


@router.get("/pedidos/{pedido_id}/historico")
def historico_pedido(pedido_id: int, db=Depends(get_db)):
    return service.historico_pedido(db, pedido_id)
