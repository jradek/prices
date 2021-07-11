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

* drilldown: min/avg/max price per serving per item and per store and overall

	```sql
	-- drilldown: min/avg/max price per serving per item and per store and overall
	SELECT
		per_store.id,
		per_store.name,
		per_store.store,
		per_store.min_price_per_serving,
		per_store.avg_price_per_serving,
		per_store.max_price_per_serving,
		per_store.serving_size,
		per_store.unit,
		per_store.num_measures
	FROM(
		SELECT
			i.id,
			i.name,
			d.store,
			i.unit,
			i.serving_size,
			MIN(i.serving_size * d.price_cent / d.amount * 1.0) / 100.0 AS "min_price_per_serving",
			ROUND(AVG(i.serving_size * d.price_cent / d.amount * 1.0) / 100.0, 2) AS "avg_price_per_serving",
			MAX(i.serving_size * d.price_cent / d.amount * 1.0) / 100.0 AS "max_price_per_serving",
			COUNT(*) AS "num_measures"
		FROM discount d
		INNER JOIN item i ON i.id = d.item_id
		GROUP BY d.item_id, d.store
	) AS per_store
	UNION
	SELECT
		overall.id,
		overall.name,
		"_all_stores_",
		overall.min_price_per_serving,
		overall.avg_price_per_serving,
		overall.max_price_per_serving,
		overall.serving_size,
		overall.unit,
		overall.num_measures
	FROM (
		SELECT
			i.id,
			i.name,
			i.unit,
			i.serving_size,
			MIN(i.serving_size * d.price_cent / d.amount * 1.0) / 100.0 AS "min_price_per_serving",
			ROUND(AVG(i.serving_size * d.price_cent / d.amount * 1.0) / 100, 2)  AS "avg_price_per_serving",
			MAX(i.serving_size * d.price_cent / d.amount * 1.0) / 100.0 AS "max_price_per_serving",
			COUNT(*) AS "num_measures"
		FROM discount d
		INNER JOIN item i ON i.id = d.item_id
		GROUP BY d.item_id
	) AS overall
	ORDER BY name, store
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
