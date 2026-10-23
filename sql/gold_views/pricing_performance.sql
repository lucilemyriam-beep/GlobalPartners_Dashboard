CREATE VIEW globalpartners_gold_db.pricing_performance AS
WITH order_pricing AS (
    SELECT
        restaurant_id,
        order_id,
        SUM(CAST(item_price AS DOUBLE) * item_quantity) AS order_revenue,
        SUM(item_quantity) AS total_items
    FROM globalpartners_silver_db.order_items
    WHERE restaurant_id IS NOT NULL
      AND order_id IS NOT NULL
      AND item_price IS NOT NULL
      AND item_quantity IS NOT NULL
    GROUP BY restaurant_id, order_id
)
SELECT
    restaurant_id,
    COUNT(*) AS total_orders,
    ROUND(SUM(order_revenue), 2) AS total_revenue,
    ROUND(AVG(order_revenue), 2) AS avg_order_value,
    ROUND(
        SUM(order_revenue) / NULLIF(SUM(total_items), 0),
        2
    ) AS avg_item_price,
    SUM(total_items) AS total_items_sold
FROM order_pricing
GROUP BY restaurant_id;
