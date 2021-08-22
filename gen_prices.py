#! /usr/bin/env python3

import datetime
import logging
import math
import sqlite3
import pandas as pd

from pathlib import Path

pd.set_option("display.max_rows", None)
pd.set_option("display.max_columns", None)
pd.set_option("display.width", None)
pd.set_option("display.max_colwidth", None)

CURRENT_DIR = Path(__file__).absolute().parent

LOGGER = logging.getLogger("gen_prices")


def get_item_data(con: sqlite3.Connection) -> pd.DataFrame:
    # query item data and min/avg/max per store
    ITEM_QUERY = """
WITH overall AS (
 SELECT
    i.id,
    i.name,
    ROUND(MIN(i.serving_size * d.price_cent * 1.0 / d.amount) / 100, 2) AS "min_price_per_serving",
    ROUND(AVG(i.serving_size * d.price_cent * 1.0 / d.amount) / 100, 2) AS "avg_price_per_serving",
    ROUND(MAX(i.serving_size * d.price_cent * 1.0 / d.amount) / 100, 2) AS "max_price_per_serving",
    COUNT(*) AS "num_measures"
  FROM
	discount d
  INNER JOIN
    item i ON i.id = d.item_id
  GROUP BY
    d.item_id
)
SELECT
  i.id,
  i.name,
  i.serving_size,
  i.unit,
  i.category,
  i.usual_package_size,
  overall.min_price_per_serving,
  overall.avg_price_per_serving,
  overall.max_price_per_serving,
  overall.num_measures
FROM
  item i
LEFT JOIN overall ON overall.id = i.id
ORDER BY
  i.name
"""
    df = pd.read_sql(ITEM_QUERY, con)
    return df


def get_prices_per_store(con: sqlite3.Connection) -> pd.DataFrame:
    STORE_QUERY = """
WITH price_per_serving_euro AS (
  SELECT
    i.id as item_id,
    i.name,
    d.store,
    ROUND(i.serving_size * d.price_cent * 1.0 / d.amount / 100, 2) as price_per_serving_euro,
    d.start,
    d.end
  FROM
    discount d
  INNER JOIN item i ON i.id = d.item_id
),
all_stores AS (
  SELECT DISTINCT
    store
  FROM
    discount
),
latest_regular_price_per_serving_euro AS (
  SELECT
    r.item_id,
    r.store,
    r.date,
    ROUND(i.serving_size * r.price_cent * 1.0 / r.amount / 100, 2) as price_per_serving_euro
  FROM
    regular r
  INNER JOIN item i ON i.id = r.item_id
  GROUP BY
    r.item_id,
    r.store
  HAVING MAX(r.date)
)
SELECT
  i.id AS item_id,
  -- i.name,
  --i.serving_size,
  --i.unit,
  --i.category,
  all_stores.store,
  min_price.price_per_serving_euro AS min_price_per_serving_euro,
  min_price.start AS min_date,
  avg_price.price_per_serving_euro AS avg_price_per_serving_euro,
  max_price.price_per_serving_euro AS max_price_per_serving_euro,
  max_price.end AS max_date,
  max_price.num_measures,
  regular.price_per_serving_euro AS regular_price_per_serving_euro,
  regular.date AS regular_date
FROM item i, all_stores
LEFT JOIN (
  SELECT
    t.item_id,
    t.store,
    t.price_per_serving_euro,
    t.start
  FROM
    price_per_serving_euro t
  GROUP BY t.item_id, t.store
  HAVING
     MIN(t.price_per_serving_euro)
) AS min_price ON min_price.item_id = i.id AND min_price.store = all_stores.store
LEFT JOIN (
  SELECT
    t.item_id,
    t.store,
    ROUND(AVG(t.price_per_serving_euro), 2) AS price_per_serving_euro
  FROM
    price_per_serving_euro t
  GROUP BY t.item_id, t.store
) AS avg_price ON avg_price.item_id = i.id AND avg_price.store = all_stores.store
LEFT JOIN (
  SELECT
    t.item_id,
    t.store,
    t.price_per_serving_euro,
    t.end,
    count(*) AS num_measures
  FROM
    price_per_serving_euro t
  GROUP BY t.item_id, t.store
  HAVING
     MAX(t.price_per_serving_euro)
) AS max_price ON max_price.item_id = i.id AND max_price.store = all_stores.store
LEFT JOIN (
  SELECT
    r.item_id,
    r.store,
    r.date,
    r.price_per_serving_euro
  FROM
    latest_regular_price_per_serving_euro r
) AS regular ON regular.item_id = i.id AND regular.store = all_stores.store
WHERE
  (min_price.store IS NOT NULL) OR (regular.store IS NOT NULL)
ORDER BY
  i.id,
  all_stores.store
"""
    df = pd.read_sql(STORE_QUERY, con)
    return df


def write_javascript(items_df: pd.DataFrame, prices_per_store_df: pd.DataFrame):
    fn = CURRENT_DIR / "page" / "prices_data.js"
    fn.parent.mkdir(exist_ok=True, parents=True)

    with open(fn, "w") as fp:
        fp.write("// <script>\n\n")

        # export time
        export_date = datetime.datetime.now()
        fp.write(
            f'g_pricesExportDate = "{export_date.strftime("%Y-%m-%d %H:%M:%S")}"\n\n'
        )

        # items
        fp.write("g_items = [\n")
        for row in items_df.iterrows():
            row_idx = row[0]
            series = row[1]

            if row_idx == 0:
                line = ", ".join(
                    [f"{idx}: {val}" for idx, val in enumerate(series.index)]
                )
                fp.write(f"// {line}\n")

            items = []
            for val in series:
                if val is None:
                    items.append("null")
                elif isinstance(val, str):
                    items.append(f'"{val}"')
                elif math.isnan(float(val)):
                    items.append("null")
                else:
                    items.append(str(val))

            fp.write(f'  [{", ".join(items)}],\n')
        fp.write("]; // items \n\n")

        # prices
        fp.write("g_pricesPerStore = {\n")
        last_item_id = None
        for row in prices_per_store_df.iterrows():
            row_idx = row[0]
            series = row[1]

            if row_idx == 0:
                line = ", ".join(
                    [f"{idx}: {val}" for idx, val in enumerate(series.index)]
                )
                fp.write(f"// {line}\n")
            if series["item_id"] != last_item_id:
                if row_idx != 0:
                    fp.write("],\n")
                fp.write(f"{series['item_id']}: [\n")

            items = []
            for val in series:
                if val is None:
                    items.append("null")
                elif isinstance(val, str):
                    items.append(f'"{val}"')
                elif math.isnan(float(val)):
                    items.append("null")
                else:
                    items.append(str(val))

            fp.write(f'  [{", ".join(items)}],\n')

            last_item_id = series["item_id"]
        fp.write("]\n};\n // prices per store\n\n")

        fp.write("// </script>\n\n")


def main():
    with sqlite3.connect(CURRENT_DIR / "tmp" / "prices.db") as con:
        items_df = get_item_data(con)
        prices_per_store_df = get_prices_per_store(con)
        write_javascript(items_df, prices_per_store_df)


if __name__ == "__main__":
    main()
