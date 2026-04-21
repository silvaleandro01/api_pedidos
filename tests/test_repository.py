import pytest
from unittest.mock import MagicMock
import repository.pedidos as repo


@pytest.fixture
def mock_db():
    return MagicMock()


def _cursor(mock_db, fetchone=None, fetchall=None):
    cur = MagicMock()
    cur.fetchone.return_value = fetchone
    cur.fetchall.return_value = fetchall or []
    mock_db.cursor.return_value = cur
    return cur


class TestInserirPedido:
    def test_retorna_dict_do_banco(self, mock_db):
        row = {"id": 1, "cliente": "João", "total": 100.0, "status": "pendente"}
        _cursor(mock_db, fetchone=row)
        result = repo.inserir_pedido(mock_db, "João", 100.0)
        assert result == row


class TestInserirItem:
    def test_retorna_dict_do_banco(self, mock_db):
        row = {"produto": "Mouse", "quantidade": 2, "preco": 50.0}
        _cursor(mock_db, fetchone=row)
        result = repo.inserir_item(mock_db, 1, "Mouse", 2, 50.0)
        assert result == row


class TestInserirHistorico:
    def test_executa_procedure(self, mock_db):
        cur = _cursor(mock_db)
        repo.inserir_historico(mock_db, 1, "pendente", "sistema")
        cur.execute.assert_called_once()


class TestBuscarPedido:
    def test_retorna_dict_quando_encontrado(self, mock_db):
        row = {"id": 1, "cliente": "João", "total": 100.0, "status": "pendente"}
        _cursor(mock_db, fetchone=row)
        result = repo.buscar_pedido(mock_db, 1)
        assert result == row

    def test_retorna_none_quando_nao_encontrado(self, mock_db):
        _cursor(mock_db, fetchone=None)
        result = repo.buscar_pedido(mock_db, 999)
        assert result is None


class TestAtualizarStatusPedido:
    def test_executa_procedure(self, mock_db):
        cur = _cursor(mock_db)
        repo.atualizar_status_pedido(mock_db, 1, "pago")
        cur.execute.assert_called_once()


class TestBuscarHistorico:
    def test_retorna_lista_de_registros(self, mock_db):
        rows = [{"status": "pendente", "alterado_por": "sistema", "data_hora": "2026-01-01"}]
        _cursor(mock_db, fetchall=rows)
        result = repo.buscar_historico(mock_db, 1)
        assert result == rows

    def test_retorna_lista_vazia(self, mock_db):
        _cursor(mock_db, fetchall=[])
        result = repo.buscar_historico(mock_db, 1)
        assert result == []
