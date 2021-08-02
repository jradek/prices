#! /usr/bin/env python

import datetime
import itertools
import sqlite3

from dataclasses import dataclass
from fuzzywuzzy import fuzz
from typing import List, Mapping, Optional, Set, Tuple


@dataclass
class Item:
    item_id: int
    name: str
    serving_size: int
    unit: str

    def __str__(self):
        return f"({self.item_id}) {self.name} {self.serving_size}{self.unit}"


def get_items() -> Mapping[int, Item]:
    query = """
SELECT i.id, i.name, i.serving_size, i.unit
FROM item i
    """
    items = dict()
    with sqlite3.connect("tmp/prices.db") as con:
        cursor = con.cursor()
        for row in cursor.execute(query):
            item = Item(*row)
            items[item.item_id] = item
    return items


def alpha_items(items: List[Item], start: str = None) -> List[Item]:
    def check(s: str):
        if isinstance(start, str):
            return s.lower().startswith(start.lower())
        return True

    filtered = (i for _, i in items.items() if check(i.name))
    return sorted(filtered, key=lambda item: item.name)


def get_stores() -> Set[str]:
    query = """
SELECT DISTINCT d.store
FROM discount d
    """
    stores = set()
    with sqlite3.connect("tmp/prices.db") as con:
        cursor = con.cursor()
        for row in cursor.execute(query):
            stores.add(row[0])
    return stores


def get_last_discount_id() -> int:
    query = """
SELECT MAX(d.id)
FROM discount d
    """
    with sqlite3.connect("tmp/prices.db") as con:
        cursor = con.cursor()
        row = cursor.execute(query).fetchone()
        return row[0]


def fz_search(
    items: Mapping[int, Item], name: str, max_results=5, ignore_case=False
) -> List[Item]:
    def transform(s: str) -> str:
        if ignore_case:
            return s.lower()
        return s

    res = (
        (fuzz.ratio(transform(name), transform(item.name)), item)
        for _, item in items.items()
    )
    res = sorted(res, key=lambda t: t[0], reverse=True)
    res = [item for score, item in itertools.islice(res, max_results) if score > 0]
    return res


def get_monday_saturday() -> Tuple[str, str]:
    today = datetime.datetime.today()
    monday = today - datetime.timedelta(days=today.weekday())
    saturday = monday + datetime.timedelta(days=5)
    fmt = "%Y-%m-%d"
    return monday.strftime(fmt), saturday.strftime(fmt)


def format_date(s: str):
    """
    raise ValueError
    """
    d = datetime.datetime.strptime(s, "%Y-%m-%d")
    return d.strftime("%A (%Y-%m-%d)")


def parse_date(s: str):
    """
    raise ValueError
    """
    datetime.datetime.strptime(s, "%Y-%m-%d")
    return s


# =====================================================================
# INTERACTIVE
# =====================================================================


@dataclass
class Discount:
    start: str
    end: str
    store: str
    item_id: int
    amount: int
    price_cent: int

    def format(self) -> str:
        global ITEMS, STORES
        store_opt = ""
        if self.store not in STORES:
            store_opt = "!"
        item = ITEMS[self.item_id]
        price_euro = self.price_cent * 1.0 / 100.0
        s = f"""{format_date(self.start)} - {format_date(self.end)}: {self.store}{store_opt}, {item.name}, {self.amount}{item.unit}, {price_euro}€"""
        return s


ITEMS = {}
STORES = set()
LAST_BEST_MATCH_ITEM_ID = -1
LAST_STORE = None
MONDAY = ""
SATURDAY = ""
DISCOUNTS: List[Discount] = []


def i_setup():
    global ITEMS, STORES, MONDAY, SATURDAY
    ITEMS = get_items()
    STORES = get_stores()
    MONDAY, SATURDAY = get_monday_saturday()


def i_fz_search(name: str, **kwargs):
    global ITEMS
    global LAST_BEST_MATCH_ITEM_ID
    results = fz_search(ITEMS, name, **kwargs)
    for idx, item in enumerate(results):
        if idx == 0:
            LAST_BEST_MATCH_ITEM_ID = item.item_id
        print(item)


def i_discount(
    amount: int,
    price_cent: int,
    store: Optional[str] = None,
    item_id: Optional[int] = None,
    start: Optional[str] = None,
    end: Optional[str] = None,
):
    global MONDAY, SATURDAY, ITEMS, LAST_STORE, STORES, DISCOUNTS

    start_date = parse_date(MONDAY)
    end_date = parse_date(SATURDAY)
    if start is not None:
        start_date = parse_date(start)

    if end is not None:
        end_date = parse_date(end)

    item = None
    if item_id is not None:
        item = ITEMS[item_id]
    elif LAST_BEST_MATCH_ITEM_ID >= 0:
        item = ITEMS[LAST_BEST_MATCH_ITEM_ID]
    else:
        raise ValueError("No itemid given")

    if store is None and LAST_STORE is not None:
        store = LAST_STORE

    if store not in STORES:
        print(f"\nWARNING: unknown store '{store}'\n")

    LAST_STORE = store

    discount = Discount(start_date, end_date, store, item.item_id, amount, price_cent)
    print(discount.format())

    res = input("Is this correct [yN]? ")
    if res.lower() == "y":
        print("... discount added")
        DISCOUNTS.append(discount)
    else:
        print("... discount rejected")


def i_alpha_items(start: Optional[str] = None):
    global ITEMS
    for idx, item in enumerate(alpha_items(ITEMS, start)):
        if (idx > 0) and (idx % 10 == 0):
            input("Continue ...")
        print(f"{idx:03d}. {item}")


def i_show_discounts():
    global DISCOUNTS
    for idx, d in enumerate(DISCOUNTS):
        print(f"= {idx:02d}")
        print(d.format())


def i_dump_sql() -> str:
    last_id = get_last_discount_id()

    lines = []
    global DISCOUNTS
    for idx, entry in enumerate(DISCOUNTS):
        line = f"INSERT INTO discount VALUES({last_id + 1 + idx},'{entry.start}','{entry.end}','{entry.store}',{entry.item_id},{entry.amount},{entry.price_cent});"
        lines.append(line)

    lines = "\n".join(lines)

    with open("new_discounts.sql", "a") as fp:
        fp.write(lines)


def main():
    items = get_items()
    res = fz_search(items, "jack daniels", ignore_case=False)
    print(list(res))
    print(get_monday_saturday())
    print(format_date("2021-08-01"))
    print(get_stores())
    print(alpha_items(items, start="b"))
    print(get_last_discount_id())
    pass


if __name__ == "__main__":
    main()
else:
    i_setup()
