from .conexao import conectar_bd_magento, conectar_bd_ativo


def _normalizar_ids_evento(id_evento) -> list:
    if isinstance(id_evento, (list, tuple, set)):
        return [int(item) for item in id_evento]

    return [int(item.strip()) for item in str(id_evento).split(",") if item.strip()]


# ---------------------------------------------------------------------------
# Dados de inscrições
# ---------------------------------------------------------------------------

def buscar_dados_magento(id_evento) -> list:
    """
    Busca inscrições no banco Magento para os IDs de evento informados.

    Args:
        id_evento: string com IDs separados por vírgula, ex: "101,102,103"

    Returns:
        Lista de tuplas com 15 campos na mesma ordem de COLUNAS_QUERY.
    """
    ids_evento = _normalizar_ids_evento(id_evento)
    placeholders = ", ".join(["%s"] * len(ids_evento))

    conn = conectar_bd_magento()
    cursor = conn.cursor()
    query = f"""
   SELECT
    b.additional_data AS "N. Peito",
    "Magento" AS "Local",
    d.sku AS "SKU DO EVENTO ",
    p.value AS "ID Evento",
    j.`value` AS "Evento",
    NULL AS "Local Inscrição",
    NULL AS "Balcão",
    a.increment_id AS "Protocolo",
    b.item_id AS "ID Inscrição",
    DATE(k.value) AS "Data Evento",
    DATE(a.created_at) AS "Data Pedido",
    a.state AS "Status Pedido",
    a.`status` AS "Status Confirmado",
    b.price AS "Valor",
    s.VALUE AS "Modalidade",
    s.VALUE AS "Modalidade Ajustada",
    b.`name` AS "Categoria",
    IF(c.group_id = 4, "SIM", "NÃO") AS "Assinante",
    b.ext_order_item_id AS "Pelotão",
    c.entity_id AS "ID Usuario",
    CONCAT(c.firstname, " ", c.lastname) AS "Nome inscrição",
    (vars.cur_year - YEAR(c.dob)) AS "Idade",
    c.email AS "E-mail",
		i.telephone AS "TELEFONE",
		c.taxvat AS "Documento",
    CASE 
        WHEN c.gender = 1 THEN "M"
        WHEN c.gender = 2 THEN "F"
        ELSE c.gender 
    END AS "Sexo",
    i.region AS "Estado",
		i.city AS "Cidade",
    IF(JSON_VALUE(b.ozone_customers, '$[0].custom_1') = "null", NULL, JSON_VALUE(b.ozone_customers, '$[0].custom_1')) AS "Personalização",

    -- Coluna para Tamanho da Camiseta
    MAX(
        CASE 
            WHEN r.attribute_id = 207 AND h.attribute_set_id = 27 THEN s.VALUE
            ELSE NULL
        END
    ) AS "Tamanho Camiseta",

    -- Coluna para Produtos
    GROUP_CONCAT(
        DISTINCT CASE 
            WHEN h3.attribute_set_id NOT IN (30, 28, 27, 31) THEN g2.name
            ELSE NULL
        END
    ) AS "Produtos",
    -- Coluna "Cupom"
    COALESCE(a.coupon_code, '') AS "Cupom",
    -- Coluna "Etiqueta"
    (SELECT nn.label 
     FROM salesrule_label AS nn 
     WHERE f.rule_id = nn.rule_id AND nn.store_id = 1) AS "Etiqueta",
     '' AS "Classificacao Cupom"
FROM
    sales_order AS a
    LEFT JOIN sales_order_item AS b ON b.order_id = a.entity_id
    LEFT JOIN customer_has_related_order_items AS e ON e.sales_order_item_item_id = b.item_id
    LEFT JOIN customer_entity AS c ON e.customer_id = c.entity_id
    LEFT JOIN catalog_product_link AS g ON b.product_id = g.linked_product_id
    LEFT JOIN customer_address_entity AS i ON c.entity_id = i.parent_id
    LEFT JOIN catalog_product_entity_varchar AS p ON b.product_id = p.entity_id
    LEFT JOIN catalog_product_entity_varchar AS j ON p.value = j.entity_id
    LEFT JOIN catalog_product_entity_datetime AS k ON p.value = k.entity_id
    LEFT JOIN catalog_product_entity_varchar AS q ON g.product_id = q.entity_id
    LEFT JOIN sales_order_item AS ab ON ab.parent_item_id = b.item_id
    LEFT JOIN catalog_product_entity_int AS r ON r.entity_id = ab.product_id  
    INNER JOIN eav_attribute_option_value AS s ON r.VALUE = s.option_id
    LEFT JOIN catalog_product_entity AS h ON ab.product_id = h.entity_id
    LEFT JOIN sales_order_item AS g2 ON g2.parent_item_id = b.item_id
    LEFT JOIN catalog_product_entity AS h3 ON g2.product_id = h3.entity_id

    -- JOIN para pegar o SKU Pai
    LEFT JOIN catalog_product_entity_varchar AS pai ON pai.entity_id = b.product_id AND pai.attribute_id = 321
    LEFT JOIN catalog_product_entity AS d ON pai.value = d.entity_id

    -- JOIN para o relacionamento com salesrule
    LEFT JOIN salesrule AS f ON FIND_IN_SET(f.rule_id, a.applied_rule_ids) > 0

    -- CROSS JOIN para otimizar cálculo de idade
    CROSS JOIN (
        SELECT YEAR(CURDATE()) AS cur_year
    ) AS vars

WHERE
    #k.value BETWEEN DATE_SUB(CURRENT_DATE, INTERVAL 6 MONTH) AND DATE_ADD(CURRENT_DATE, INTERVAL 6 MONTH)
    b.product_type = 'Bundle'
    AND p.`value` IN ({placeholders}) 
	#AND a.created_at >= "2026-03-18"
    AND j.attribute_id = 73
    AND q.attribute_id = 73
    AND r.attribute_id IN (206,207)
    AND r.attribute_id IN (206,207)
    AND (k.attribute_id = 195 OR k.attribute_id IS NULL)
    AND a.status IN ('Processing', 'Complete', 'approved', 'aprovado_link', 'pending')
    AND a.state != 'canceled'
    #AND DATE(k.value) >= '2026-01-01'
	#AND DATE(k.value) <= '2026-12-31'
    #AND c.group_id != 4 #(somente não assinantes)
GROUP BY
    b.item_id
ORDER BY
    a.increment_id DESC;
    """
    try:
        print(f"[Magento] Executando query para {len(ids_evento)} evento(s): {ids_evento}")
        cursor.execute(query, ids_evento)
        dados = cursor.fetchall()
        print(f"[Magento] {len(dados)} linha(s) retornada(s).")
        return dados
    except Exception as e:
        print(f"[Magento] ERRO ao buscar dados: {e}")
        import traceback
        traceback.print_exc()
        return []
    finally:
        cursor.close()
        conn.close()
        print("[Magento] Conexão encerrada.")


def buscar_dados_ativo(id_evento: str) -> list:
    """
    Busca inscrições no banco Ativo para os IDs de evento informados.

    Args:
        id_evento: string com IDs separados por vírgula, ex: "201,202"

    Returns:
        Lista de tuplas com 15 campos na mesma ordem de COLUNAS_QUERY.
    """
    conn = conectar_bd_ativo()
    cursor = conn.cursor()
    query = f"""
      SELECT
            a.nr_peito as 'N. Peito',
                "Ativo" as "Local",
            b.id_campanha_salesforce AS 'SKU',
            b.id_evento AS 'ID Evento',
            b.ds_evento AS 'Evento',
            CASE
        WHEN c.fl_local_inscricao = '1' THEN
            'Site'
        WHEN c.fl_local_inscricao = '2' THEN
            'Balcão'
        WHEN c.fl_local_inscricao = '3' THEN
            'Entrega'
        ELSE
            c.fl_local_inscricao
        END AS 'Local Inscrição',
            g.ds_nomebalcao as 'Balcão',
            c.id_pedido AS 'Protocolo',
            a.id_pedido_evento AS 'ID Inscrição',
            date(b.dt_evento) AS 'Data Evento',
                date(c.dt_pedido) AS 'Data Pedido',
            d.ds_status AS 'Status Pedido',
            p.`status` AS 'Status Inscrição',
        q.nm_modalidade as "Modalidade",
        h.ds_categoria as "Categoria",
        IF ( a.fl_assinante = 1, "SIM", "NÃO" ) AS 'Assinante',
        IF(
        IF ( c.fl_local_inscricao = 1, g.pelotao, w.pelotao ) = NULL ,
        'Branco' ,
        IF ( c.fl_local_inscricao = 1, g.pelotao, w.pelotao ))
        AS 'Pelotão',
        IF (
            c.fl_local_inscricao = 1,
            g.id_usuario,
            w.id_usuario
        ) AS 'ID Usuario',
        IF (
            c.fl_local_inscricao = 1,
            g.ds_nomecompleto,
            w.ds_nome
        ) AS 'Nome inscrição',
        IF (
            c.fl_local_inscricao = 1,
        IF (
            SUBSTRING_INDEX(g.ds_nome, " ", 1) = " ",
            SUBSTRING_INDEX(g.ds_nome, " ", 2),
            SUBSTRING_INDEX(g.ds_nome, " ", 1)
        ),
        SUBSTRING_INDEX(w.ds_nome, " ", 1)
        ) AS 'Primeiro Nome',
        IF (
            c.fl_local_inscricao = 1,
            g.ds_email,
            w.ds_email
        ) AS 'e-mail',
        IF (
            c.fl_local_inscricao = 1,
            g.nr_telefone,
            w.ds_telefone
        ) AS 'Telefone',
        IF (
            c.fl_local_inscricao = 1,
            g.nr_celular,
            w.ds_celular
        ) AS 'Celular',
        IF (
            c.fl_local_inscricao = 1,
            YEAR (now()) - YEAR (g.dt_nascimento),
            YEAR (now()) - YEAR (w.dt_nascimento)
        ) AS 'Idade',
        IF (c.fl_local_inscricao = 1,date(g.dt_nascimento),date(w.dt_nascimento)) AS 'Dt Nascimento',
        IF (
            c.fl_local_inscricao = 1,
            g.nr_documento,
            w.nr_documento
        ) AS 'Documento',
        IF (
            c.fl_local_inscricao = 1,
            g.fl_sexo,
            w.fl_sexo
        ) AS 'Sexo',
        y.ds_cidade,
        y.ds_estado,
        concat(g.ds_endereco," ",g.nr_numero," ", g.ds_bairro) as "Endereço",
        g.ds_cep,
        a.nm_camiseta as "Personalização",
        IF ( x.id_tamanho_camiseta = 2 , "BL", x.ds_tamanho ) AS 'Tamanho Camiseta',
        (SELECT max(eql.ds_resposta) from sa_pedido_questionario pqa
        LEFT JOIN sa_evento_questionario_limite eql on pqa.id_evento_questionario_limite = eql.id_evento_questionario_limite
        where
        a.id_pedido_evento = pqa.id_pedido_evento
        and
        eql.ds_resposta in ('Baby look', 'BL','P','M','G','GG')) as  'Produto'
        FROM
            sa_pedido_evento AS a
        INNER JOIN sa_evento AS b ON b.id_evento = a.id_evento
        INNER JOIN sa_pedido AS c ON c.id_pedido = a.id_pedido
        INNER JOIN sa_pedido_status AS d ON d.id_pedido_status = c.id_pedido_status
        LEFT JOIN sa_usuario AS g ON a.id_usuario = g.id_usuario
        LEFT JOIN sa_modalidade_categoria AS h ON a.id_categoria = h.id_categoria
        LEFT JOIN sa_status_detalhado AS p ON a.id_status_detalhado = p.id_status_detalhado
        LEFT JOIN sa_evento_modalidade AS q ON a.id_modalidade = q.id_modalidade
        LEFT JOIN sa_usuario_balcao AS w ON w.id_usuario = a.id_usuario_balcao
        LEFT JOIN sa_cidade AS y ON g.id_cidade = y.id_cidade
        LEFT JOIN sa_tamanho_camiseta AS x ON a.id_tamanho_camiseta = x.id_tamanho_camiseta
        WHERE
        b.id_evento IN ({id_evento}) AND
            (
            c.id_pedido_status = 2
            OR (
                c.fl_local_inscricao = 2
                AND c.id_pedido_status = 1
            )
        ) and
        IF (
            c.fl_local_inscricao = 1,
            g.id_usuario,
            w.id_usuario
        ) is not null
        GROUP BY
            a.id_pedido_evento
        ORDER BY
            b.id_evento, c.id_pedido;
    """
    try:
        print(f"[Ativo] Executando query para {len(str(id_evento).split(','))} evento(s): {id_evento}")
        cursor.execute(query)
        dados = cursor.fetchall()
        print(f"[Ativo] {len(dados)} linha(s) retornada(s).")
        return dados
    except Exception as e:
        print(f"[Ativo] ERRO ao buscar dados: {e}")
        return []
    finally:
        cursor.close()
        conn.close()
        print("[Ativo] Conexão encerrada.")


# ---------------------------------------------------------------------------
# Listagem de eventos (para os comboboxes)
# ---------------------------------------------------------------------------

def obter_eventos_magento() -> list:
    """
    Lista eventos disponíveis no Magento para seleção na interface.
    Retorna: [(id_evento, nome, data), ...]
    """
    conn = conectar_bd_magento()
    cursor = conn.cursor()
    query = """
    SELECT DISTINCT
        j.entity_id AS 'Id_evento',
        j.`value` AS 'Evento',
        DATE(k.`value`) AS 'Data'
    FROM catalog_product_entity AS a
    LEFT JOIN catalog_product_entity_int AS b ON a.entity_id = b.entity_id
    LEFT JOIN catalog_product_entity_varchar AS j ON a.entity_id = j.entity_id
    LEFT JOIN catalog_product_entity_datetime AS k ON j.entity_id = k.entity_id
    WHERE
        k.`value` > '2023-01-01' AND
        a.attribute_set_id = 23 AND
        j.attribute_id = 73 AND
        k.attribute_id = 195 AND
        b.attribute_id = 320 AND
        b.value = 1
    ORDER BY k.`value`;
    """
    cursor.execute(query)
    eventos = cursor.fetchall()
    cursor.close()
    conn.close()
    return eventos


def obter_eventos_ativos() -> list:
    """
    Lista eventos disponíveis no Ativo para seleção na interface.
    Retorna: [(id_evento, nome, data), ...]
    """
    conn = conectar_bd_ativo()
    cursor = conn.cursor()
    query = """
    SELECT
        a.id_evento AS 'ID_evento',
        a.ds_evento AS 'Evento',
        DATE(a.dt_evento) AS 'Data'
    FROM
        sa_evento AS a
    WHERE
        a.fl_evento_da_casa = 2 AND
        DATE(a.dt_evento) >= '2023-01-01'
    ORDER BY
        a.ds_evento;
    """
    cursor.execute(query)
    eventos = cursor.fetchall()
    cursor.close()
    conn.close()
    return eventos

