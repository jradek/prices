#! /usr/bin/env python3

import logging
import pandas as pd

from pathlib import Path

from price_db import Database

pd.set_option("display.max_rows", None)
pd.set_option("display.max_columns", None)
pd.set_option("display.width", None)
pd.set_option("display.max_colwidth", None)

CURRENT_DIR = Path(__file__).absolute().parent

LOGGER = logging.getLogger("gen_prices")


def get_min_prices(db: Database) -> pd.DataFrame:
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
		per_store.num_measures
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
        overall.category,
		overall.num_measures
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
    con = db.get_connection()
    df = pd.read_sql(stmt, con)
    return df


def write_javascript(prices_df: pd.DataFrame):
    fn = CURRENT_DIR / "page" / "prices_data.js"
    fn.parent.mkdir(exist_ok=True, parents=True)

    with open(fn, "w") as fp:
        fp.write("// <script>\n\n")

        # prices
        fp.write("g_prices = [\n")

        is_first = True
        for row in prices_df.iterrows():
            row_idx = row[0]
            series = row[1]

            if row_idx == 0:
                line = ", ".join(
                    [f"{idx}: {val}" for idx, val in enumerate(series.index)]
                )
                fp.write(f"// {line}\n")

            entry = row[1]

            if entry["store"] == "_all_stores_":
                line = ""
                if not is_first:
                    line = "]],\n"
                line += f"""[{entry['id']}, "{entry['name']}", {entry['min_price_per_serving']}, {entry['avg_price_per_serving']}, {entry['max_price_per_serving']}, {entry['serving_size']}, "{entry['unit']}", "{entry['category']}", {entry['num_measures']}, [\n"""
                fp.write(line)
                is_first = False
            else:
                line = f"""[\"{entry["store"]}\", {entry["min_price_per_serving"]}, {entry["avg_price_per_serving"]}, {entry["max_price_per_serving"]}, {entry["num_measures"]}],\n"""
                fp.write(line)

        fp.write("]]\n]; // prices\n\n")

        fp.write("// </script>\n\n")


def main():
    db = Database(CURRENT_DIR / "tmp" / "prices.db")
    df = get_min_prices(db)
    write_javascript(df)


if __name__ == "__main__":
    main()
