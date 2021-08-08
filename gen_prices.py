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
SELECT
  i.id,
  i.name,
  i.serving_size,
  i.unit,
  i.category,
  overall.min_price_per_serving,
  overall.avg_price_per_serving,
  overall.max_price_per_serving,
  overall.num_measures
FROM
  item i
LEFT JOIN (
  SELECT
    i.id,
    i.name,
    MIN(i.serving_size * d.price_cent / d.amount * 1.0) / 100.0 AS "min_price_per_serving",
    ROUND(AVG(i.serving_size * d.price_cent / d.amount * 1.0) / 100, 2)  AS "avg_price_per_serving",
    MAX(i.serving_size * d.price_cent / d.amount * 1.0) / 100.0 AS "max_price_per_serving",
    COUNT(*) AS "num_measures"
  FROM 
	discount d
  INNER JOIN 
    item i ON i.id = d.item_id
  GROUP BY 
    d.item_id
  ) AS overall ON overall.id = i.id
ORDER BY
  i.name
"""
    df = pd.read_sql(ITEM_QUERY, con)
    return df


def get_min_prices(con: sqlite3.Connection) -> pd.DataFrame:
    stmt = """
	SELECT
		per_store.id,
		per_store.name,
		per_store.store,
		per_store.min_price_per_serving,
		per_store.avg_price_per_serving,
		per_store.max_price_per_serving,
		per_store.serving_size,
		per_store.unit,
        per_store.category,
		per_store.num_measures,
        regular.regular_per_serving
	FROM(
		SELECT
			i.id,
			i.name,
			d.store,
			i.unit,
			i.serving_size,
            i.category,
			MIN(i.serving_size * d.price_cent / d.amount * 1.0) / 100.0 AS "min_price_per_serving",
			ROUND(AVG(i.serving_size * d.price_cent / d.amount * 1.0) / 100.0, 2) AS "avg_price_per_serving",
			MAX(i.serving_size * d.price_cent / d.amount * 1.0) / 100.0 AS "max_price_per_serving",
			COUNT(*) AS "num_measures"
		FROM discount d
		INNER JOIN item i ON i.id = d.item_id
		GROUP BY d.item_id, d.store
	) AS per_store
	LEFT JOIN (
		SELECT r.item_id, i.name, r.store, r.amount, r.price_cent, i.serving_size * r.price_cent * 1.0 / r.amount / 100.0 AS "regular_per_serving"
		FROM regular r
		INNER JOIN item i ON i.id = r.item_id
		GROUP BY store, item_id
		HAVING MAX(date)
	) AS regular ON per_store.store = regular.store AND per_store.id = regular.item_id
	UNION
	SELECT
		overall.id,
		overall.name,
		"_all_stores_" AS "store",
		overall.min_price_per_serving,
		overall.avg_price_per_serving,
		overall.max_price_per_serving,
		overall.serving_size,
		overall.unit,
        overall.category,
		overall.num_measures,
        null as "regular_per_serving"
	FROM (
		SELECT
			i.id,
			i.name,
			i.unit,
			i.serving_size,
            i.category,
			MIN(i.serving_size * d.price_cent / d.amount * 1.0) / 100.0 AS "min_price_per_serving",
			ROUND(AVG(i.serving_size * d.price_cent / d.amount * 1.0) / 100, 2)  AS "avg_price_per_serving",
			MAX(i.serving_size * d.price_cent / d.amount * 1.0) / 100.0 AS "max_price_per_serving",
			COUNT(*) AS "num_measures"
		FROM discount d
		INNER JOIN item i ON i.id = d.item_id
		GROUP BY d.item_id
	) AS overall
	ORDER BY name, id, store
"""
    df = pd.read_sql(stmt, con)
    return df


def write_javascript_2(items_df: pd.DataFrame):
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
                if isinstance(val, str):
                    items.append(f'"{val}"')
                elif math.isnan(float(val)):
                    items.append("null")
                else:
                    items.append(str(val))
                    
            fp.write(f'  [{", ".join(items)}],\n')
        fp.write("]; // items \n\n")


def write_javascript(prices_df: pd.DataFrame):
    fn = CURRENT_DIR / "page" / "prices_data.js"
    fn.parent.mkdir(exist_ok=True, parents=True)

    with open(fn, "w") as fp:
        fp.write("// <script>\n\n")

        # export time
        export_date = datetime.datetime.now()
        fp.write(
            f'g_pricesExportDate = "{export_date.strftime("%Y-%m-%d %H:%M:%S")}"\n\n'
        )

        # prices
        fp.write("g_prices = [\n")

        is_first = True
        explain_entries = True
        for row in prices_df.iterrows():
            row_idx = row[0]
            series = row[1]

            if row_idx == 0:
                line = ", ".join(
                    [f"{idx}: {val}" for idx, val in enumerate(series.index)]
                )
                fp.write(f"// {line}\n")

            entry = row[1]

            regular_per_serving = (
                "null"
                if math.isnan(entry["regular_per_serving"])
                else entry["regular_per_serving"]
            )

            if entry["store"] == "_all_stores_":
                line = ""
                if not is_first:
                    line = "  ]\n],\n"
                line += f"""[{entry['id']}, "{entry['name']}", {entry['min_price_per_serving']}, {entry['avg_price_per_serving']}, {entry['max_price_per_serving']}, {entry['serving_size']}, "{entry['unit']}", "{entry['category']}", {entry['num_measures']},\n  [\n"""
                fp.write(line)
                is_first = False
            else:
                if explain_entries:
                    line = "// 0: store, 1: min_price_per_serving, 2: avg_price_per_serving, 3: max_price_per_serving, 4: regular_price_per_serving, 5: num_measures\n"
                    fp.write(line)
                    explain_entries = False
                line = f"""    [\"{entry["store"]}\", {entry["min_price_per_serving"]}, {entry["avg_price_per_serving"]}, {entry["max_price_per_serving"]}, {regular_per_serving}, {entry["num_measures"]}],\n"""
                fp.write(line)

        fp.write("  ]\n]\n]; // prices\n\n")

        fp.write("// </script>\n\n")


def main():
    with sqlite3.connect(CURRENT_DIR / "tmp" / "prices.db") as con:
        items_df = get_item_data(con)
        write_javascript_2(items_df)
        # df = get_min_prices(con)
        # write_javascript(df)


if __name__ == "__main__":
    main()
