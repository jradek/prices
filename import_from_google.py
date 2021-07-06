import pprint
import logging
from pathlib import Path
from re import A

import sqlalchemy as sqa  # type: ignore
from sqlalchemy.orm import sessionmaker  # type: ignore
import pandas as pd

DATA_DIR = Path(__file__).absolute().parent / "data"

LOGGER = logging.getLogger("Google Import")

metadata = sqa.MetaData()

discount_tbl = sqa.Table(
    "discount",
    metadata,
    sqa.Column("id", sqa.Integer, primary_key=True, autoincrement=True),
    sqa.Column("start", sqa.Text),
    sqa.Column("end", sqa.Text),
    sqa.Column("store", sqa.Text),
    sqa.Column("amount", sqa.Integer), # according to item unit
    sqa.Column("item_id", sqa.Integer),
    sqa.Column("price_cent", sqa.Integer), # in cent
)

item_tbl = sqa.Table(
    "item",
    metadata,
    sqa.Column("id", sqa.Integer, primary_key=True),
    sqa.Column("name", sqa.Text),
    sqa.Column("serving_size", sqa.Integer),
    sqa.Column("unit", sqa.Text),
    sqa.Column("category", sqa.Text),
)


class Database:
    def __init__(self, database_file_path: Path) -> None:
        self._database_file_path = database_file_path

        url = "sqlite:///%s" % database_file_path
        LOGGER.info("opening Database: %s", url)

        self._engine = sqa.create_engine(url)

        _Session = sessionmaker(bind=self._engine, autocommit=False)
        self._session = _Session()

    def create_tables(self):
        metadata.drop_all(self._engine)
        metadata.create_all(self._engine)
        self._session.commit()

    def commit(self):
        self._session.commit()

    def insert_items(self, items: dict):
        ins = item_tbl.insert()

        for k, v in items.items():
            unit = ""
            serving_size = ""
            if v["unit"] == "g":
                unit = "g"
                serving_size = "100"
            elif v["unit"] == "l":
                unit = "ml"
                serving_size = "1000"
            elif v["unit"] == "ml":
                unit = "ml"
                serving_size = "100"
            elif v["unit"] == "Stueck":
                unit = "Stueck"
                serving_size = "1"
            else:
                raise Exception(f"Unknwon serving size {v['unit']}")

            self._session.execute(
                ins,
                {
                    "id": v["id"],
                    "name": v["name"],
                    "serving_size": serving_size,
                    "unit": unit,
                    "category": v["category"],
                },
            )

        self._session.commit()

    def get_connection(self):
        return self._session.connection()


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

    db = Database("prices.db")
    db.create_tables()

    related_df.to_sql("discount", db.get_connection(), if_exists="replace", index=False)
    db.commit()
    db.insert_items(items)


if __name__ == "__main__":
    main()
