import pytest
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient
from main import app
from utils.database import get_db


def _mock_db():
    yield MagicMock()


app.dependency_overrides[get_db] = _mock_db

client = TestClient(app)

PEDIDO = {"id": 1, "cliente": "João", "total": 100.0, "status": "pendente"}
ITEM = {"produto": "X", "quantidade": 1, "preco": 100.0}
PAYLOAD_PEDIDO = {"cliente": "João", "itens": [{"produto": "X", "quantidade": 1, "preco": 100.0}]}


class TestRotaCriarPedido:
    def test_post_pedidos_retorna_200(self):
        with patch("service.pedidos.repo") as mock_repo:
            mock_repo.inserir_pedido.return_value = PEDIDO
            mock_repo.inserir_item.return_value = ITEM
            resp = client.post("/pedidos", json=PAYLOAD_PEDIDO)
            assert resp.status_code == 200
            assert resp.json()["id"] == 1


class TestRotaConsultarStatus:
    def test_get_status_retorna_200(self):
        with patch("service.pedidos.repo") as mock_repo:
            mock_repo.buscar_pedido.return_value = PEDIDO
            resp = client.get("/pedidos/1/status")
            assert resp.status_code == 200
            assert resp.json()["status"] == "pendente"

    def test_get_status_retorna_404(self):
        with patch("service.pedidos.repo") as mock_repo:
            mock_repo.buscar_pedido.return_value = None
            resp = client.get("/pedidos/999/status")
            assert resp.status_code == 404


class TestRotaAtualizarStatus:
    def test_patch_status_retorna_200(self):
        with patch("service.pedidos.repo") as mock_repo:
            mock_repo.buscar_pedido.return_value = PEDIDO
            resp = client.patch("/pedidos/1/status", json={"novo_status": "pago", "alterado_por": "op"})
            assert resp.status_code == 200
            assert resp.json()["status"] == "pago"

    def test_patch_status_invalido_retorna_400(self):
        with patch("service.pedidos.repo") as mock_repo:
            mock_repo.buscar_pedido.return_value = PEDIDO
            resp = client.patch("/pedidos/1/status", json={"novo_status": "cancelado", "alterado_por": "op"})
            assert resp.status_code == 400


class TestRotaCancelarPedido:
    def test_patch_cancelar_retorna_200(self):
        with patch("service.pedidos.repo") as mock_repo:
            mock_repo.buscar_pedido.return_value = PEDIDO
            resp = client.patch("/pedidos/1/cancelar", json={"alterado_por": "cliente"})
            assert resp.status_code == 200
            assert resp.json()["status"] == "cancelado"

    def test_patch_cancelar_retorna_404(self):
        with patch("service.pedidos.repo") as mock_repo:
            mock_repo.buscar_pedido.return_value = None
            resp = client.patch("/pedidos/999/cancelar", json={"alterado_por": "cliente"})
            assert resp.status_code == 404


class TestRotaHistoricoPedido:
    def test_get_historico_retorna_200(self):
        with patch("service.pedidos.repo") as mock_repo:
            mock_repo.buscar_pedido.return_value = PEDIDO
            mock_repo.buscar_historico.return_value = []
            resp = client.get("/pedidos/1/historico")
            assert resp.status_code == 200
            assert resp.json()["pedido_id"] == 1

    def test_get_historico_retorna_404(self):
        with patch("service.pedidos.repo") as mock_repo:
            mock_repo.buscar_pedido.return_value = None
            resp = client.get("/pedidos/999/historico")
            assert resp.status_code == 404
