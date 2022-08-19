#! /usr/bin/env python3

import datetime
import math
import sqlite3

from pathlib import Path
import pandas as pd


pd.set_option("display.max_rows", None)
pd.set_option("display.max_columns", None)
pd.set_option("display.width", None)
pd.set_option("display.max_colwidth", None)

CURRENT_DIR = Path(__file__).absolute().parent

INFLATION_ADJUST_DATE = "2022-04-01"

def write_javascript(offers_df: pd.DataFrame):
    fn = CURRENT_DIR / "page" / "current_offers_data.js"
    fn.parent.mkdir(exist_ok=True, parents=True)

    with open(fn, "w") as fp:
        fp.write("// <script>\n\n")

        # export time
        export_date = datetime.datetime.now()
        fp.write(
            f'g_offersExportDate = "{export_date.strftime("%Y-%m-%d %H:%M:%S")}"\n\n'
        )

        # offers
        fp.write("g_offers = [\n")

        for row in offers_df.iterrows():
            row_idx = row[0]
            series = row[1]

            if row_idx == 0:
                line = ", ".join(
                    [f"{idx}: {val}" for idx, val in enumerate(series.index)]
                )
                fp.write(f"// {line}\n")

            items = []
            for val in series:
                if isinstance(val, str):
                    items.append(f'"{val}"')
                elif math.isnan(float(val)):
                    items.append("null")
                else:
                    items.append(str(val))
            fp.write(f'\t[{", ".join(items)}],\n')

        fp.write("]; // offers\n\n")
        fp.write("// </script>\n\n")


def get_offers(con: sqlite3.Connection, today=None) -> pd.DataFrame:
    today = datetime.date.today() if today == None else today
    date = today.strftime("%Y-%m-%d")

    stmt = f"""
SELECT
  calc.*,
  min_price.min_store,
  min_price.min_start,
  min_price.min_price_per_serving,
  -- deal, when price per servin is less then 5% more than min serving
  calc.price_per_serving < min_price.min_price_per_serving * 1.05 AS "is_deal_percent",
  -- deal, when price per serving is less then 5 cent more than min serving
  calc.price_per_serving < min_price.min_price_per_serving + 0.06 AS "is_deal_cent",
  regular.per_serving as "store_regular_per_serving",
  measures.num_measures
FROM (SELECT
    d."start",
    d."end",
    STRFTIME('%s', d.end || ' 22:00:00') - STRFTIME('%s', d.start || ' 07:00:00') <= 2 * 24 * 3600 AS "is_short",
    d.store,
    i.name,
    i.id AS item_id,
    d.amount,
    d.price_cent,
    i.unit,
    i.serving_size,
    i.category,
    ROUND(i.serving_size * d.price_cent * 1.0 / d.amount / 100, 2) AS "price_per_serving"
  FROM discount d
  INNER JOIN item i ON i.id = item_id
) AS calc
JOIN (SELECT
    i.id ,
    d.store AS "min_store",
    d."start" AS "min_start",
    ROUND(i.serving_size * d.price_cent * 1.0 / d.amount / 100, 2) AS "min_price_per_serving"
  FROM discount d
  JOIN item i on i.id = d.item_id
  WHERE d.start >= "{INFLATION_ADJUST_DATE}"
  GROUP BY i.id
  HAVING MIN(ROUND(i.serving_size * d.price_cent * 1.0 / d.amount / 100, 2))
) AS min_price
JOIN (SELECT
    i.id,
    COUNT(*) as num_measures
  FROM discount d
  JOIN item i on i.id = d.item_id
  GROUP BY i.id
) AS measures
LEFT JOIN (
  SELECT
    i.id as "item_id",
    i.name,
    r.store,
    ROUND(r.price_cent * i.serving_size * 1.0 / r.amount / 100, 2) AS "per_serving"
  FROM
    item i
  JOIN (
    SELECT
      item_id,
      store,
      price_cent,
      amount
    FROM regular
    WHERE date >= "{INFLATION_ADJUST_DATE}"
    GROUP BY item_id, store
    HAVING MAX(date)
    ) AS r ON i.id = r.item_id
) AS regular ON (regular.item_id = calc.item_id) AND (regular.store = calc.store)
WHERE "{date}" <= calc."end"
  AND min_price.id = calc.item_id
  AND measures.id = calc.item_id
ORDER BY calc.store, calc."start", calc.name
    """

    df = pd.read_sql(stmt, con)
    return df


def main():
    with sqlite3.connect(CURRENT_DIR / "tmp" / "prices.db") as con:
        offers_df = get_offers(con)
        write_javascript(offers_df)


if __name__ == "__main__":
    main()
