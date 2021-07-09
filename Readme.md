# Readme

## Example queries

* basic

	```sql
	select
		d.start,
		d.end,
		d.store,
		i.name,
		d.amount,
		d.price_cent,
		i.unit,
		i.serving_size,
		i.category,
		round(i.serving_size * d.price_cent * 1.0 / d.amount / 100.0, 2) as "price per serving [EUR]"
	from discount d
	join item i on i.id = d.item_id
	```

* drill down

	```sql
	-- drilldown: min/avg/max price per serving per item, and per store
	SELECT
		summed.name,
		summed.store,
		summed.min_price_per_serving,
		ROUND(summed.summed_price_per_serving / summed.num_measures, 2) AS "avg_price_per_serving",
		summed.max_price_per_serving,
		summed.serving_size,
		summed.unit
	FROM(
		SELECT
			i.name,
			d.store,
			i.unit,
			i.serving_size,
			SUM(i.serving_size * d.price_cent / d.amount * 1.0) / 100.0 AS "summed_price_per_serving",
			COUNT(*) AS "num_measures",
			MAX(i.serving_size * d.price_cent / d.amount * 1.0) / 100.0 AS "max_price_per_serving",
			MIN(i.serving_size * d.price_cent / d.amount * 1.0) / 100.0 AS "min_price_per_serving"
		FROM discount d
		INNER JOIN item i ON i.id = d.item_id
		GROUP BY d.item_id, d.store
	) AS summed
	ORDER BY summed.name, summed.store
	```

## Dump DB

```console
./dump_db.sh
```

which creates `prices.sql`

## Create DB from dump

```console
./create_db.sh
```

which reads `prices.sql` and created `prices.db`
