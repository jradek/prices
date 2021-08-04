#! /usr/bin/env sh

if [ $# -lt 1 ]; then
    now=$(date +"%Y-%m-%d")
    echo "using ${now}"
else
    now=$1
fi

# create db from scratch
# scripts/create_db.sh

query="
SELECT 
    d.start, 
    d.end, 
    printf('%12s', d.store), 
    printf('%3d', i.id),
    printf('%45s', i.name), 
    printf('%4d', d.amount), 
    printf('%6s', i.unit), 
    printf('%2.2f€',(d.price_cent * 0.01)) AS price
FROM discount d
INNER JOIN item i ON d.item_id = i.id
WHERE d.end >= \"$now\"
ORDER BY 
    d.store, 
    d.start, 
    i.name
"

sqlite3 -list -separator " | " tmp/prices.db "${query}"
