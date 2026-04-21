CREATE OR REPLACE FUNCTION fn_inserir_pedido(
    p_cliente VARCHAR,
    p_total   FLOAT
)
RETURNS TABLE (id INTEGER, cliente VARCHAR, total FLOAT, status VARCHAR)
LANGUAGE plpgsql AS $$
BEGIN
    RETURN QUERY
    INSERT INTO pedidos (cliente, total, status)
    VALUES (p_cliente, p_total, 'pendente')
    RETURNING pedidos.id, pedidos.cliente, pedidos.total, pedidos.status;
END;
$$;


CREATE OR REPLACE FUNCTION fn_buscar_pedido(
    p_pedido_id INTEGER
)
RETURNS TABLE (id INTEGER, cliente VARCHAR, total FLOAT, status VARCHAR)
LANGUAGE plpgsql AS $$
BEGIN
    RETURN QUERY
    SELECT p.id, p.cliente, p.total, p.status
    FROM pedidos p
    WHERE p.id = p_pedido_id;
END;
$$;


CREATE OR REPLACE PROCEDURE pr_atualizar_status_pedido(
    p_pedido_id  INTEGER,
    p_novo_status VARCHAR
)
LANGUAGE plpgsql AS $$
BEGIN
    UPDATE pedidos
    SET status = p_novo_status
    WHERE id = p_pedido_id;
END;
$$;


CREATE OR REPLACE FUNCTION fn_inserir_item(
    p_pedido_id  INTEGER,
    p_produto    VARCHAR,
    p_quantidade INTEGER,
    p_preco      FLOAT
)
RETURNS TABLE (produto VARCHAR, quantidade INTEGER, preco FLOAT)
LANGUAGE plpgsql AS $$
BEGIN
    RETURN QUERY
    INSERT INTO itens_pedido (pedido_id, produto, quantidade, preco)
    VALUES (p_pedido_id, p_produto, p_quantidade, p_preco)
    RETURNING itens_pedido.produto, itens_pedido.quantidade, itens_pedido.preco;
END;
$$;


CREATE OR REPLACE PROCEDURE pr_inserir_historico(
    p_pedido_id    INTEGER,
    p_status_novo  VARCHAR,
    p_alterado_por VARCHAR,
    p_data_hora    TIMESTAMPTZ
)
LANGUAGE plpgsql AS $$
BEGIN
    INSERT INTO historico_pedido (pedido_id, status_novo, alterado_por, data_hora)
    VALUES (p_pedido_id, p_status_novo, p_alterado_por, p_data_hora);
END;
$$;


CREATE OR REPLACE FUNCTION fn_buscar_historico(
    p_pedido_id INTEGER
)
RETURNS TABLE (status VARCHAR, alterado_por VARCHAR, data_hora TIMESTAMPTZ)
LANGUAGE plpgsql AS $$
BEGIN
    RETURN QUERY
    SELECT h.status_novo, h.alterado_por, h.data_hora
    FROM historico_pedido h
    WHERE h.pedido_id = p_pedido_id
    ORDER BY h.data_hora;
END;
$$;
