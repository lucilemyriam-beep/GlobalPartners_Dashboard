CREATE VIEW globalpartners_gold_db.restaurant_revenue_performance AS
WITH restaurant_sales AS (
    SELECT
        restaurant_id,
        COUNT(DISTINCT order_id) AS total_orders,
        SUM(CAST(item_price AS DOUBLE) * item_quantity) AS total_revenue
    FROM globalpartners_silver_db.order_items
    WHERE restaurant_id IS NOT NULL
      AND order_id IS NOT NULL
    GROUP BY restaurant_id
)
SELECT
    restaurant_id,
    total_orders,
    ROUND(total_revenue, 2) AS total_revenue,
    ROUND(
        total_revenue / NULLIF(total_orders, 0),
        2
    ) AS avg_order_value,
    RANK() OVER (
        ORDER BY total_revenue DESC
    ) AS revenue_rank
FROM restaurant_sales;
