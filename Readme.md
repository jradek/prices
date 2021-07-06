# Readme


## Basic query

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
	round(i.serving_size * d.price_cent * 1.0 / d.amount / 100.0, 2) as "price per serving [EUR}"
from discount d
join item i on i.id = d.item_id
```

## Dump DB

```console
./dump_db.sh
```

which creates `prices.sql`

## Create DB from dump

```
sqlite3 <dbname> < prices.sql
```
