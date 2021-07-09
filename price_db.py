from pathlib import Path

import logging
import sqlalchemy as sqa  # type: ignore
from sqlalchemy.orm import sessionmaker  # type: ignore

LOGGER = logging.getLogger("price_db")

metadata = sqa.MetaData()

discount_tbl = sqa.Table(
    "discount",
    metadata,
    sqa.Column("id", sqa.Integer, primary_key=True),
    sqa.Column("start", sqa.Text),
    sqa.Column("end", sqa.Text),
    sqa.Column("store", sqa.Text),
    sqa.Column("amount", sqa.Integer),  # according to item unit
    sqa.Column("item_id", sqa.Integer),
    sqa.Column("price_cent", sqa.Integer),
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

    def execute_sql(self, stmt: str):
        return self._session.execute(stmt)
