CREATE VIEW globalpartners_gold_db.loyalty_impact AS
WITH
order_level AS (
    SELECT
        user_id,
        order_id,
        MAX(
            CASE
                WHEN is_loyalty = true THEN 1
                ELSE 0
            END
        ) loyalty_flag,
        SUM(
            COALESCE(item_price, 0) *
            COALESCE(item_quantity, 0)
        ) order_revenue
    FROM globalpartners_silver_db.order_items
    WHERE user_id IS NOT NULL
      AND order_id IS NOT NULL
    GROUP BY user_id, order_id
),
customer_level AS (
    SELECT
        user_id,
        MAX(loyalty_flag) loyalty_flag,
        COUNT(*) total_orders,
        SUM(order_revenue) customer_value
    FROM order_level
    GROUP BY user_id
)
SELECT
    CASE
        WHEN loyalty_flag = 1 THEN 'Loyalty'
        ELSE 'Non-Loyalty'
    END loyalty_status,
    COUNT(*) total_customers,
    SUM(total_orders) total_orders,
    SUM(customer_value) total_revenue,
    AVG(customer_value) avg_customer_value,
    SUM(customer_value) /
        NULLIF(SUM(total_orders), 0) avg_order_value,
    (1E2 * COUNT_IF(total_orders > 1)) /
        NULLIF(COUNT(*), 0) repeat_purchase_rate
FROM customer_level
GROUP BY loyalty_flag;
