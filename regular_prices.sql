SELECT
     i.name,
     all_stores.store
FROM
     item i,
     (
          SELECT 
               DISTINCT d.store
          FROM
               discount d
     ) AS all_stores


-- SELECT
--      calc.*,
--      min_price.min_store,
--      min_price.min_start,
--      min_price.min_price_per_serving,
--      -- deal, when price per servin is less then 5% more than min serving
--      calc.price_per_serving < min_price.min_price_per_serving * 1.05 AS "is_deal_percent",
--      -- deal, when price per serving is less then 5 cent more than min serving
--      calc.price_per_serving < min_price.min_price_per_serving + 0.06 AS "is_deal_cent",
-- 	 -- deal, when lower than regular price for store
-- 	 calc.price_per_serving <  regular.per_serving AS "is_deal_store",
-- 	 regular.per_serving as "regular_per_serving",
--      measures.num_measures
-- FROM (SELECT
--      d."start",
--      d."end",
--      STRFTIME('%s', d.end || ' 22:00:00') - STRFTIME('%s', d.start || ' 07:00:00') <= 2 * 24 * 3600 AS "is_short",
--      d.store,
--      i.name,
--      i.id AS item_id,
--      d.amount,
--      d.price_cent,
--      i.unit,
--      i.serving_size,
--      i.category,
--      round(i.serving_size * d.price_cent * 1.0 / d.amount / 100.0, 2) AS "price_per_serving"
--      FROM discount d
--      INNER JOIN item i ON i.id = item_id
-- ) AS calc
-- JOIN (SELECT
--      i.id ,
--      d.store AS "min_store",
--      d."start" AS "min_start",
--      round(i.serving_size * d.price_cent * 1.0 / d.amount / 100.0, 2) AS "min_price_per_serving"
--      FROM discount d
--      JOIN item i on i.id = d.item_id
--      GROUP BY i.id
--      HAVING MIN(round(i.serving_size * d.price_cent * 1.0 / d.amount / 100.0, 2))
-- ) AS min_price
-- JOIN (SELECT
--      i.id,
--      count(*) as num_measures
--      FROM discount d
--      JOIN item i on i.id = d.item_id
--      GROUP BY i.id
-- ) AS measures
-- LEFT JOIN (
-- 	SELECT
-- 		i.id as "item_id",
-- 		i.name,
-- 		r.store,
-- 		round(r.price_cent * i.serving_size * 1.0 / r.amount / 100.0, 2) AS "per_serving"
-- 	FROM item i
-- 	JOIN (
-- 		SELECT item_id, store, price_cent, amount
-- 		FROM regular
-- 		GROUP BY item_id, store
-- 		HAVING `date` <= "2021-07-27"
-- 	) AS r ON i.id = r.item_id
-- ) AS regular ON (regular.item_id = calc.item_id) AND (regular.store = calc.store)
-- WHERE "2021-07-27" <= calc."end"
--   AND min_price.id = calc.item_id
--   AND measures.id = calc.item_id
-- ORDER BY calc.store, calc."start", calc.name