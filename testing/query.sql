.headers on
SELECT * from (
    SELECT id,
        date,
        price_cent,
        ROW_NUMBER() OVER (
            PARTITION BY id
            ORDER BY date DESC, price_cent DESC
        ) as rn
    from items
)
where rn = 1;

SELECT *
from items
GROUP BY id
HAVING MAX(price_cent) and MAX(date);
