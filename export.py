import datetime

from pathlib import Path
import pandas as pd

import price_db

pd.set_option("display.max_rows", None)
pd.set_option("display.max_columns", None)
pd.set_option("display.width", None)
pd.set_option("display.max_colwidth", None)

CURRENT_DIR = Path(__file__).absolute().parent


def get_offers(db: price_db.Database, today=None) -> pd.DataFrame:
    today = datetime.date.today() if today == None else today
    date = today.strftime("%Y-%m-%d")

    stmt = f"""
SELECT
	d.start,
	d.end,
	d.store,
	i.name,
	d.amount,
	d.price_cent,
	i.unit,
	i.serving_size,
	i.category,
	round(i.serving_size * d.price_cent * 1.0 / d.amount / 100.0, 2) AS "price_per_serving",
	min_price.store as "min_store",
	min_price.start as "min_start",
	min_price.price_per_serving as "min_price_per_serving",
	measures.num_measures
FROM discount d
JOIN item i ON i.id = d.item_id
JOIN (SELECT
		i.id ,
		d.store,
		d.start,
		round(i.serving_size * d.price_cent * 1.0 / d.amount / 100.0, 2) AS "price_per_serving"
	FROM discount d
	JOIN item i on i.id = d.item_id
	GROUP BY i.id
	HAVING MIN(round(i.serving_size * d.price_cent * 1.0 / d.amount / 100.0, 2))
) AS min_price
JOIN (SELECT
		i.id,
		count(*) as num_measures
	  FROM discount d
	  JOIN item i on i.id = d.item_id
	  GROUP BY i.id
) AS measures
WHERE '{date}' <= d.end
   AND min_price.id = i.id
   and measures.id = i.id
ORDER BY d.store, d.start
    """

    def to_date(r):
        return datetime.datetime.strptime(r, "%Y-%m-%d")

    df = pd.read_sql(stmt, db.get_connection())
    # deal if less than 5% above min price
    df["is_deal"] = df["price_per_serving"] <= df["min_price_per_serving"] * 1.05
    # short if less than 2 days
    df["is_short"] = df["end"].map(to_date) - df["start"].map(to_date) <= "2 days"
    print(df)


def main():
    db = price_db.Database(CURRENT_DIR / "prices.db")
    print(get_offers(db))


if __name__ == "__main__":
    main()
