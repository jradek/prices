import datetime

from pathlib import Path
import pandas as pd

import price_db

pd.set_option("display.max_rows", None)
pd.set_option("display.max_columns", None)
pd.set_option("display.width", None)
pd.set_option("display.max_colwidth", None)

CURRENT_DIR = Path(__file__).absolute().parent


def write_javascript(offers_df: pd.DataFrame):
    fn = CURRENT_DIR / "page" / "data.js"
    fn.parent.mkdir(exist_ok=True, parents=True)

    with open(fn, "w") as fp:
        fp.write("// <script>\n\n")
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


def get_offers(db: price_db.Database, today=None) -> pd.DataFrame:
    today = datetime.date.today() if today == None else today
    date = today.strftime("%Y-%m-%d")

    stmt = f"""
SELECT
     calc.*,
     min_price.min_store,
     min_price.min_start,
     min_price.min_price_per_serving,
     calc.price_per_serving < min_price.min_price_per_serving * 1.05 AS "is_deal",
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
WHERE "{date}" < calc."end"
  AND min_price.id = calc.item_id
  AND measures.id = calc.item_id
ORDER BY calc.store, calc."start", calc.name
    """

    df = pd.read_sql(stmt, db.get_connection())
    return df


def main():
    db = price_db.Database(CURRENT_DIR / "prices.db")
    offers_df = get_offers(db)
    write_javascript(offers_df)


if __name__ == "__main__":
    main()
