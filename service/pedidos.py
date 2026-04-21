from fastapi import HTTPException
from repository.schemas import PedidoEntrada, AtualizarStatus, CancelarPedido, StatusPedido, ORDEM_STATUS
import repository.pedidos as repo


def criar_pedido(db, dados: PedidoEntrada) -> dict:
    total = sum(item.quantidade * item.preco for item in dados.itens)

    pedido = repo.inserir_pedido(db, dados.cliente, total)
    pedido_id = pedido["id"]

    itens = [
        repo.inserir_item(db, pedido_id, item.produto, item.quantidade, item.preco)
        for item in dados.itens
    ]

    repo.inserir_historico(db, pedido_id, StatusPedido.PENDENTE.value, "sistema")
    db.commit()

    return {**pedido, "itens": itens}


def consultar_status(db, pedido_id: int) -> dict:
    pedido = repo.buscar_pedido(db, pedido_id)
    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido não encontrado")

    return {"id": pedido["id"], "cliente": pedido["cliente"], "status": pedido["status"]}


def atualizar_status(db, pedido_id: int, dados: AtualizarStatus) -> dict:
    pedido = repo.buscar_pedido(db, pedido_id)
    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido não encontrado")

    status_atual = pedido["status"]
    novo_status = dados.novo_status

    if novo_status not in ORDEM_STATUS:
        raise HTTPException(status_code=400, detail="Status inválido")

    idx_atual = ORDEM_STATUS.index(StatusPedido(status_atual))
    idx_novo = ORDEM_STATUS.index(novo_status)

    if idx_novo != idx_atual + 1:
        raise HTTPException(
            status_code=400,
            detail=f"Transição inválida: não é possível ir de '{status_atual}' para '{novo_status}'",
        )

    repo.atualizar_status_pedido(db, pedido_id, novo_status.value)
    repo.inserir_historico(db, pedido_id, novo_status.value, dados.alterado_por)
    db.commit()

    return {"id": pedido_id, "status": novo_status, "alterado_por": dados.alterado_por}


def cancelar_pedido(db, pedido_id: int, dados: CancelarPedido) -> dict:
    pedido = repo.buscar_pedido(db, pedido_id)
    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido não encontrado")

    if pedido["status"] == StatusPedido.ENTREGUE:
        raise HTTPException(status_code=400, detail="Não é possível cancelar um pedido já entregue")

    if pedido["status"] == StatusPedido.CANCELADO:
        raise HTTPException(status_code=400, detail="Pedido já está cancelado")

    repo.atualizar_status_pedido(db, pedido_id, StatusPedido.CANCELADO.value)
    repo.inserir_historico(db, pedido_id, StatusPedido.CANCELADO.value, dados.alterado_por)
    db.commit()

    return {"id": pedido_id, "status": StatusPedido.CANCELADO, "alterado_por": dados.alterado_por}


def historico_pedido(db, pedido_id: int) -> dict:
    pedido = repo.buscar_pedido(db, pedido_id)
    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido não encontrado")

    historico = repo.buscar_historico(db, pedido_id)

    return {"pedido_id": pedido["id"], "cliente": pedido["cliente"], "historico": historico}
