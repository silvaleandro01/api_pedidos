import pytest
from unittest.mock import MagicMock, patch
from fastapi import HTTPException
from repository.schemas import (
    PedidoEntrada, ItemEntrada, AtualizarStatus, CancelarPedido, StatusPedido,
)
import service.pedidos as service


@pytest.fixture
def db():
    return MagicMock()


PEDIDO = {"id": 1, "cliente": "João", "total": 100.0, "status": "pendente"}


class TestCriarPedido:
    def test_cria_pedido_e_faz_commit(self, db):
        dados = PedidoEntrada(
            cliente="João",
            itens=[ItemEntrada(produto="A", quantidade=2, preco=10.0)],
        )
        with patch("service.pedidos.repo") as mock_repo:
            mock_repo.inserir_pedido.return_value = PEDIDO
            mock_repo.inserir_item.return_value = {"produto": "A", "quantidade": 2, "preco": 10.0}

            result = service.criar_pedido(db, dados)

            assert result["id"] == 1
            assert len(result["itens"]) == 1
            mock_repo.inserir_pedido.assert_called_once_with(db, "João", 20.0)
            mock_repo.inserir_historico.assert_called_once_with(db, 1, "pendente", "sistema")
            db.commit.assert_called_once()


class TestConsultarStatus:
    def test_retorna_status_do_pedido(self, db):
        with patch("service.pedidos.repo") as mock_repo:
            mock_repo.buscar_pedido.return_value = PEDIDO
            result = service.consultar_status(db, 1)
            assert result == {"id": 1, "cliente": "João", "status": "pendente"}

    def test_404_quando_nao_encontrado(self, db):
        with patch("service.pedidos.repo") as mock_repo:
            mock_repo.buscar_pedido.return_value = None
            with pytest.raises(HTTPException) as exc:
                service.consultar_status(db, 999)
            assert exc.value.status_code == 404


class TestAtualizarStatus:
    def test_404_quando_pedido_nao_existe(self, db):
        dados = AtualizarStatus(novo_status="pago", alterado_por="op")
        with patch("service.pedidos.repo") as mock_repo:
            mock_repo.buscar_pedido.return_value = None
            with pytest.raises(HTTPException) as exc:
                service.atualizar_status(db, 1, dados)
            assert exc.value.status_code == 404

    def test_400_quando_novo_status_nao_e_progressao(self, db):
        dados = AtualizarStatus(novo_status="cancelado", alterado_por="op")
        with patch("service.pedidos.repo") as mock_repo:
            mock_repo.buscar_pedido.return_value = PEDIDO
            with pytest.raises(HTTPException) as exc:
                service.atualizar_status(db, 1, dados)
            assert exc.value.status_code == 400

    def test_400_quando_transicao_pula_status(self, db):
        dados = AtualizarStatus(novo_status="enviado", alterado_por="op")
        with patch("service.pedidos.repo") as mock_repo:
            mock_repo.buscar_pedido.return_value = PEDIDO
            with pytest.raises(HTTPException) as exc:
                service.atualizar_status(db, 1, dados)
            assert exc.value.status_code == 400

    def test_atualiza_status_com_transicao_valida(self, db):
        dados = AtualizarStatus(novo_status="pago", alterado_por="op")
        with patch("service.pedidos.repo") as mock_repo:
            mock_repo.buscar_pedido.return_value = PEDIDO
            result = service.atualizar_status(db, 1, dados)
            assert result["status"] == StatusPedido.PAGO
            assert result["alterado_por"] == "op"
            db.commit.assert_called_once()


class TestCancelarPedido:
    def test_404_quando_pedido_nao_existe(self, db):
        dados = CancelarPedido(alterado_por="cliente")
        with patch("service.pedidos.repo") as mock_repo:
            mock_repo.buscar_pedido.return_value = None
            with pytest.raises(HTTPException) as exc:
                service.cancelar_pedido(db, 1, dados)
            assert exc.value.status_code == 404

    def test_400_quando_pedido_ja_entregue(self, db):
        dados = CancelarPedido(alterado_por="cliente")
        pedido_entregue = {**PEDIDO, "status": "entregue"}
        with patch("service.pedidos.repo") as mock_repo:
            mock_repo.buscar_pedido.return_value = pedido_entregue
            with pytest.raises(HTTPException) as exc:
                service.cancelar_pedido(db, 1, dados)
            assert exc.value.status_code == 400

    def test_400_quando_pedido_ja_cancelado(self, db):
        dados = CancelarPedido(alterado_por="cliente")
        pedido_cancelado = {**PEDIDO, "status": "cancelado"}
        with patch("service.pedidos.repo") as mock_repo:
            mock_repo.buscar_pedido.return_value = pedido_cancelado
            with pytest.raises(HTTPException) as exc:
                service.cancelar_pedido(db, 1, dados)
            assert exc.value.status_code == 400

    def test_cancela_pedido_pendente_com_sucesso(self, db):
        dados = CancelarPedido(alterado_por="cliente")
        with patch("service.pedidos.repo") as mock_repo:
            mock_repo.buscar_pedido.return_value = PEDIDO
            result = service.cancelar_pedido(db, 1, dados)
            assert result["status"] == StatusPedido.CANCELADO
            db.commit.assert_called_once()


class TestHistoricoPedido:
    def test_retorna_historico_do_pedido(self, db):
        historico = [{"status": "pendente", "alterado_por": "sistema", "data_hora": "2026-01-01"}]
        with patch("service.pedidos.repo") as mock_repo:
            mock_repo.buscar_pedido.return_value = PEDIDO
            mock_repo.buscar_historico.return_value = historico
            result = service.historico_pedido(db, 1)
            assert result["pedido_id"] == 1
            assert result["historico"] == historico

    def test_404_quando_pedido_nao_existe(self, db):
        with patch("service.pedidos.repo") as mock_repo:
            mock_repo.buscar_pedido.return_value = None
            with pytest.raises(HTTPException) as exc:
                service.historico_pedido(db, 999)
            assert exc.value.status_code == 404
