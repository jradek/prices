# Readme


## Basic query

```sql
select
	d.start,
	d.end,
	d.store,
	i.name,
	d.num_servings,
	d.price,
	i.serving_size * d.num_servings as "total servings",
	i.unit,
	round(d.price/ d.num_servings, 2) as "price per serving",
	i.category
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
