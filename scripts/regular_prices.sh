#! /usr/bin/env sh

query="
SELECT
    printf('%3d', i.id),
    printf('%40s', i.name),
    printf('%15s', r.store),
    r.date,
    printf('%4d%-6s', r.amount, i.unit),
    printf('%5.2f€',r.price_cent / 100.0)
FROM regular r
INNER JOIN item i ON i.id = r.item_id
GROUP bY store, name
HAVING MAX(date)
ORDER by name, store
"

sqlite3 -list -separator " | " tmp/prices.db "${query}"
