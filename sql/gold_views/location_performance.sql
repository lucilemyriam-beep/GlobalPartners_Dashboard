CREATE VIEW globalpartners_gold_db.location_performance AS
SELECT
    restaurant_id,
    SUM(total_orders) AS total_orders,
    RANK() OVER (
        ORDER BY SUM(total_orders) DESC
    ) AS order_rank
FROM globalpartners_gold_db.restaurant_order_summary
GROUP BY restaurant_id;
