import pprint
import logging
from pathlib import Path

import pandas as pd

import price_db

DATA_DIR = Path(__file__).absolute().parent / "data"

LOGGER = logging.getLogger("Google Import")


def read_prices() -> pd.DataFrame:
    def remove_euro(row: pd.Series):
        row_mod = row.copy()
        row_mod["price"] = float(row_mod["price"].replace("€", ""))
        # print(row_mod)
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
    # print(df.head())
    return df


def read_items() -> pd.DataFrame:
    file = DATA_DIR / "prices - items.csv"
    df = pd.read_csv(file, sep=",", header=0, index_col=False)
    return df


def items_to_dict(items_df: pd.DataFrame) -> dict:
    items = dict()
    for idx, row in enumerate(items_df.itertuples()):
        # print(row)
        desc = row[1]
        item = {
            "desc": desc,
            "id": idx,
            "name": row[3],
            "serving_size": row[4],
            "unit": row[5],
            "category": row[6],
        }
        # pprint.pprint(item)
        items[desc] = item

    # pprint.pprint(items)
    return items


def relate_items_to_prices(prices: pd.DataFrame, items: dict) -> pd.DataFrame:
    item_ids = []
    multipliers = []
    for row in prices.itertuples():
        desc = row[3]
        if desc not in items:
            raise Exception(f"could not find {desc}")

        item = items[desc]
        item_ids.append(item["id"])

        if item["unit"] == "g":
            multipliers.append(100)
        elif item["unit"] == "ml":
            multipliers.append(100)
        elif item["unit"] == "l":
            multipliers.append(1000)
        elif item["unit"] == "Stueck":
            multipliers.append(1)
        else:
            raise Exception(f"Unknown serving size {item['unit']}")

    df = prices.copy()
    df["item_id"] = item_ids
    df["mult"] = multipliers
    df["amount"] = df["num_servings"] * df["mult"]
    df["price_cent"] = df["price"] * 100
    df.amount = df.amount.astype(int)
    df.price_cent = df.price_cent.astype(int)
    df = df.drop(columns=["description", "mult", "num_servings", "price"])
    # print(df.head())
    return df


def main():
    items_df = read_items()
    items = items_to_dict(items_df)
    prices_df = read_prices()
    related_df = relate_items_to_prices(prices_df, items)

    db = price_db.Database("prices.db")
    db.create_tables()

    related_df.to_sql("discount", db.get_connection(), if_exists="replace", index=False)
    db.commit()
    db.insert_items(items)


if __name__ == "__main__":
    main()
