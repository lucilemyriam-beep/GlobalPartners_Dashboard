CREATE VIEW globalpartners_gold_db.discount_effectiveness AS
WITH
order_base AS (
    SELECT
        order_id,
        SUM(CAST(item_price AS DOUBLE) * item_quantity) base_revenue
    FROM globalpartners_silver_db.order_items
    WHERE order_id IS NOT NULL
    GROUP BY order_id
),
discounts AS (
    SELECT
        order_id,
        SUM(
            CASE
                WHEN option_price < 0
                THEN CAST(option_price AS DOUBLE) * COALESCE(option_quantity, 1)
                ELSE 0
            END
        ) discount_amount
    FROM globalpartners_silver_db.order_item_options
    WHERE order_id IS NOT NULL
    GROUP BY order_id
)
SELECT
    CASE
        WHEN COALESCE(d.discount_amount, 0) < 0
        THEN 'Discounted'
        ELSE 'Non-Discounted'
    END discount_status,
    COUNT(*) total_orders,
    ROUND(SUM(b.base_revenue), 2) gross_revenue,
    ROUND(
        SUM(b.base_revenue + COALESCE(d.discount_amount, 0)),
        2
    ) net_revenue,
    ROUND(
        ABS(SUM(COALESCE(d.discount_amount, 0))),
        2
    ) total_discounts,
    ROUND(
        AVG(b.base_revenue + COALESCE(d.discount_amount, 0)),
        2
    ) avg_order_value
FROM order_base b
LEFT JOIN discounts d
    ON b.order_id = d.order_id
GROUP BY 1;
