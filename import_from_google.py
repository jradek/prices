#! /usr/bin/env python3

import logging
from pathlib import Path

import pandas as pd

import price_db

DATA_DIR = Path(__file__).absolute().parent / "google_export"

LOGGER = logging.getLogger("Google Import")


def read_prices() -> pd.DataFrame:
    def remove_euro(row: pd.Series):
        row_mod = row.copy()
        row_mod["price"] = float(row_mod["price"].replace("€", ""))
        return row_mod

    file = DATA_DIR / "prices - data.csv"
    df = pd.read_csv(file, sep=",", header=0, index_col=False)
    sel = ~df["until"].isna()
    df = df.loc[sel]
    df = df[["from", "until", "description", "store", "num servings", "price"]]
    df = df.rename(
        columns={"num servings": "num_servings", "from": "start", "until": "end"}
    )
    df = df.apply(remove_euro, axis=1)
    return df


def read_items() -> pd.DataFrame:
    file = DATA_DIR / "prices - items.csv"
    df = pd.read_csv(file, sep=",", header=0, index_col=False)
    return df


def items_to_dict(items_df: pd.DataFrame) -> dict:
    items = dict()
    for row in items_df.itertuples():
        # print(row)
        desc = row[1]
        item = {
            "desc": desc,
            "id": row[2],
            "name": row[3],
            "serving_size": row[4],
            "unit": row[5],
            "category": row[6],
        }
        # print(item)
        items[desc] = item

    return items


def relate_items_to_prices(prices: pd.DataFrame, items: dict) -> pd.DataFrame:
    item_ids = []
    multipliers = []
    for row in prices.itertuples():
        # replace item name with item id
        desc = row[3]
        if desc not in items:
            raise Exception(f"could not find {desc}")

        item = items[desc]
        item_ids.append(item["id"])

        # prepare serving size conversion
        converted_unit = price_db.Database.UNIT_CONVERSION[item["unit"]]
        multipliers.append(converted_unit["serving_size"])

    df = prices.copy()
    df["item_id"] = item_ids
    df["mult"] = multipliers
    df["amount"] = df["num_servings"] * df["mult"]
    df.amount = df.amount.astype(int)
    df["price_cent"] = df["price"] * 100
    df.price_cent = df.price_cent.astype(int)
    df = df.drop(columns=["description", "mult", "num_servings", "price"])

    df = df.sort_values(by=["start", "store"]).reset_index(drop=True)
    return df


def main():
    items_df = read_items()
    items = items_to_dict(items_df)
    prices_df = read_prices()
    related_df = relate_items_to_prices(prices_df, items)

    fn = Path("tmp") / "prices.db"
    fn.parent.mkdir(exist_ok=True, parents=True)

    if fn.exists:
        LOGGER.warning("Removing %s" % fn)
        fn.unlink()

    db = price_db.Database(fn)
    db.create_tables()

    related_df.to_sql(
        "discount",
        db.get_connection(),
        if_exists="append",
        index=True,
        index_label="id",
    )
    db.commit()
    db.insert_items(items)


if __name__ == "__main__":
    main()
