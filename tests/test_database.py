from unittest.mock import MagicMock, patch


def test_get_connection_chama_psycopg2():
    with patch("psycopg2.connect") as mock_connect:
        mock_connect.return_value = MagicMock()
        from utils.database import get_connection
        conn = get_connection()
        assert conn is not None
        mock_connect.assert_called_once()


def test_get_db_yields_e_fecha_conexao():
    mock_conn = MagicMock()
    with patch("utils.database.get_connection", return_value=mock_conn):
        from utils.database import get_db
        gen = get_db()
        conn = next(gen)
        assert conn is mock_conn
        gen.close()
        mock_conn.close.assert_called_once()
