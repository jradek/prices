import datetime

from pathlib import Path
import pandas as pd
import typing

import price_db

pd.set_option("display.max_rows", None)
pd.set_option("display.max_columns", None)
pd.set_option("display.width", None)
pd.set_option("display.max_colwidth", None)

CURRENT_DIR = Path(__file__).absolute().parent

_STORE_TO_COLOR = {
    # RBG, materialized name, text color
    "aldi": ["#01579b", "light-blue darken-4", "white-text"],
    "edeka": ["#ffff00", "yellow accent-2", "blue-text"],
    "edeka sander": ["#ffff00", "yellow accent-2", "blue-text"],
    "globus": ["#558b2f", "light-green darken-3", "black-text"],
    "kaufland": ["#f44336", "red", "white-text"],
    "lidl": ["#1976d2", "blue darken-2", "yellow-text"],
    "netto": ["#ff3d00", "deep-orange accent-3", "yellow-text text-lighten-2"],
    "norma": ["#f57f17", "yellow darken-4", "white-text"],
    "penny": ["#c62828", "red darken-3", "white-text"],
    "real": ["#fafafa", "grey lighten-5", "indigo-text text-darken-4"],
    "rewe": ["#b71c1c", "red darken-4", "white-text"],
    "tegut": ["#e65100", "orange darken-4", "white-text"],
    "thomas philipps": ["#fafafa", "grey lighten-5", "red-text text-darken-1"],
}


def _format_store_color(store: str) -> str:
    missing = ["#eceff1", "blue-grey lighten-5", "black-text"]
    colors = _STORE_TO_COLOR.get(store, missing)
    return f'"{store}": ["' + '", "'.join(colors) + '"]'


def write_javascript(offers_df: pd.DataFrame, stores: typing.List[str]):
    fn = CURRENT_DIR / "page" / "data.js"
    fn.parent.mkdir(exist_ok=True, parents=True)

    with open(fn, "w") as fp:
        fp.write("// <script>\n\n")

        # stores
        lines = ",\n".join(map(_format_store_color, stores))
        fp.write("g_storeToColor = {\n")
        fp.write(lines)
        fp.write("\n};\n\n")

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
                else:
                    items.append(str(val))
            fp.write(f'\t[{", ".join(items)}],\n')

        fp.write("]; // offers\n\n")
        fp.write("// </script>\n\n")


def get_stores(db: price_db.Database) -> typing.List[str]:
    stmt = "SELECT DISTINCT store FROM discount ORDER BY store"
    return [r[0] for r in db.execute_sql(stmt)]


def get_offers(db: price_db.Database, today=None) -> pd.DataFrame:
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
     measures.num_measures
FROM (SELECT
     d."start",
     d."end",
     STRFTIME('%s', d.end) - STRFTIME('%s', d.start) <= 2 * 24 * 3600 AS "is_short",
     d.store,
     i.name,
     i.id AS item_id,
     d.amount,
     d.price_cent,
     i.unit,
     i.serving_size,
     i.category,
     round(i.serving_size * d.price_cent * 1.0 / d.amount / 100.0, 2) AS "price_per_serving"
     FROM discount d
     INNER JOIN item i ON i.id = item_id
) AS calc
JOIN (SELECT
     i.id ,
     d.store AS "min_store",
     d."start" AS "min_start",
     round(i.serving_size * d.price_cent * 1.0 / d.amount / 100.0, 2) AS "min_price_per_serving"
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
WHERE "{date}" <= calc."end"
  AND min_price.id = calc.item_id
  AND measures.id = calc.item_id
ORDER BY calc.store, calc."start", calc.name
    """

    df = pd.read_sql(stmt, db.get_connection())
    return df


def main():
    db = price_db.Database(CURRENT_DIR / "prices.db")
    offers_df = get_offers(db)
    stores = get_stores(db)
    write_javascript(offers_df, stores)


if __name__ == "__main__":
    main()
