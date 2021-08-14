#! /usr/bin/env python

import datetime
import itertools
import sqlite3

import rich.console

from dataclasses import dataclass
from fuzzywuzzy import fuzz
from typing import Any, List, Mapping, Optional, Set, Tuple


@dataclass
class Item:
    item_id: int
    name: str
    serving_size: int
    unit: str

    def __str__(self):
        return f"({self.item_id}) {self.name} {self.serving_size}{self.unit}"


@dataclass
class Discount:
    start: str
    end: str
    store: str
    item_id: int
    amount: int
    price_cent: int


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


def alpha_items(items: Mapping[int, Item], start: str = None) -> List[Item]:
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


def parse_date(s: str) -> Tuple[str, datetime.datetime]:
    """
    raise ValueError
    """
    d = datetime.datetime.strptime(s, "%Y-%m-%d")
    return s, d


# =====================================================================
# INTERACTIVE
# =====================================================================


ITEMS: Mapping[int, Item] = {}
STORES: Set[str] = set()
LAST_BEST_MATCH_ITEM_ID: int = -1
LAST_STORE: Optional[str] = None
MONDAY: str
SATURDAY: str
LAST_START: str
LAST_END: str
DISCOUNTS: List[Discount] = []
CONSOLE: rich.console.Console = None


def i_show_current_values():
    """Displays current (saved) values"""

    global LAST_START, LAST_END, LAST_STORE, LAST_BEST_MATCH_ITEM_ID, ITEMS, CONSOLE

    s = ""
    if LAST_START is not None:
        s += f"{format_date(LAST_START)}"
    else:
        s += "?start?"

    s += " - "

    if LAST_END is not None:
        s += f"{format_date(LAST_END)}"
    else:
        s += "?end?"

    if LAST_STORE is not None:
        s += f", {LAST_STORE}"
    else:
        s += ", ?store?"

    if isinstance(LAST_BEST_MATCH_ITEM_ID, int):
        try:
            item = ITEMS[LAST_BEST_MATCH_ITEM_ID]
            s += f", {item.name} {item.serving_size}{item.unit}"
        except Exception:
            s += ", ?item?"
    else:
        s += ", ?item"

    CONSOLE.print(s)


def i_format_discount(d: Discount, con=CONSOLE) -> str:
    global ITEMS, STORES
    store_opt_start = ""
    store_opt_end = ""
    if d.store not in STORES:
        store_opt_start = "[bold red]"
        store_opt_end = "[/bold red]"
    item = ITEMS[d.item_id]
    price_euro = d.price_cent * 1.0 / 100.0
    s = f"""{format_date(d.start)} - {format_date(d.end)}: {store_opt_start}{d.store}{store_opt_end}, {item.name}, {d.amount}{item.unit}, {price_euro:.2f}€"""
    return s


def i_setup():
    global ITEMS, STORES, MONDAY, SATURDAY, CONSOLE, LAST_START, LAST_END
    ITEMS = get_items()
    STORES = get_stores()
    MONDAY, SATURDAY = get_monday_saturday()
    LAST_START = MONDAY
    LAST_END = SATURDAY
    CONSOLE = rich.console.Console()

    i_show_current_values()


def i_fz_search(name: str, **kwargs):
    """Fuzzy search the item list

    Best matching item is automatically cached and used for
    next discount, if not overwritten

    name : str
        portion to search in item name
    **kwargs :
        additional arguments for fz_search()
    """

    global ITEMS, LAST_BEST_MATCH_ITEM_ID
    results = fz_search(ITEMS, name, **kwargs)
    for idx, item in enumerate(results):
        if idx == 0:
            LAST_BEST_MATCH_ITEM_ID = item.item_id
            CONSOLE.print(f"* {item}")
        else:
            CONSOLE.print(f"  {item}")

    i_show_current_values()


def i_add_discount(
    amount: int,
    price_cent: int,
    store: Optional[str] = None,
    item_id: Optional[int] = None,
    start: Optional[str] = None,
    end: Optional[str] = None,
):
    """Add new discount to list

    amount : int
        amount expressed in item unit
    price_cent : int
        price in cent
    item_id : int, optional
        item identifier, or last best match of 'i_fz_search'
    store : str, optional
        store to use, or last used one
    start : str, optional
        start deal date, or last monday. Format yyyy-mm-dd
    end : str, optional
        end deal date, or next saturday. Format yyyy-mm-dd or '+dd' as offset to start date
    """

    global MONDAY, SATURDAY, ITEMS, LAST_STORE, STORES, DISCOUNTS, CONSOLE, LAST_START, LAST_END

    # start date handling
    start_date_str, start_date = parse_date(MONDAY)
    end_date_str, end_date = parse_date(SATURDAY)
    if start is not None:
        start_date_str, start_date = parse_date(start)
    elif LAST_START is not None:
        start_date_str, start_date = parse_date(LAST_START)

    LAST_START = start_date_str

    # end date handling
    if end is not None:
        # offset
        if isinstance(end, str) and end.startswith("+"):
            end_date = start_date + datetime.timedelta(days=float(end[1:]))
            end_date_str = datetime.datetime.strftime(end_date, "%Y-%m-%d")
        else:
            end_date_str, end_date = parse_date(end)
    elif LAST_END is not None:
        end_date_str, end_date = parse_date(LAST_END)

    LAST_END = end_date_str

    # consistency
    if start_date_str > end_date_str:
        CONSOLE.print(
            f"Invalid date range {start_date_str} - {end_date_str}", style="red"
        )
        return

    # item handling
    item = None
    if item_id is not None:
        item = ITEMS[item_id]
    elif LAST_BEST_MATCH_ITEM_ID >= 0:
        item = ITEMS[LAST_BEST_MATCH_ITEM_ID]
    else:
        raise ValueError("No item_id given")

    # store handling
    if store is not None:
        LAST_STORE = store

    if LAST_STORE is None:
        raise ValueError("No store given")

    discount = Discount(
        LAST_START, LAST_END, LAST_STORE, item.item_id, amount, price_cent
    )
    CONSOLE.print(i_format_discount(discount))

    res = input("Is this correct [yN]? ")
    if res.lower() == "y":
        DISCOUNTS.append(discount)
        l = len(DISCOUNTS)
        CONSOLE.print(f"... discount added ({l} on list)", style="green")

    i_show_current_values()


def i_alpha_items(start: Optional[str] = None):
    """Show items in alphabetical order

    start : str, optional
        start with this letter
    """

    global ITEMS
    for idx, item in enumerate(alpha_items(ITEMS, start)):
        if (idx > 0) and (idx % 10 == 0):
            input("Continue ...")
        CONSOLE.print(f"{idx:03d}. {item}")


def i_show_discounts():
    global CONSOLE, DISCOUNTS
    for idx, d in enumerate(DISCOUNTS):
        CONSOLE.print(f"{idx:02d}: {i_format_discount(d)}")


def i_delete_discount(idx: Optional[int] = None):
    """Delete discount from list

    idx : int, optional
        delete discount at this position, or the last one
    """

    global CONSOLE, DISCOUNTS
    if idx is None and len(DISCOUNTS) > 0:
        last_item = DISCOUNTS[-1]
        CONSOLE.print(f"{i_format_discount(last_item)}")
        res = input("Delete this item [yN]? ")
        if res.lower() == "y":
            del DISCOUNTS[-1]

        return

    try:
        DISCOUNTS.pop(idx)
    except Exception as e:
        CONSOLE.print(f"Failed to remove index {idx}", style="red")


def i_dump_sql() -> None:
    """Dump discount list to file 'new_discounts.sql'

    The file contains the appropriate SQL INSERT statements
    """

    global DISCOUNTS, CONSOLE
    last_id = get_last_discount_id()

    lines = []
    for idx, entry in enumerate(DISCOUNTS):
        line = f"INSERT INTO discount VALUES({last_id + 1 + idx},'{entry.start}','{entry.end}','{entry.store}',{entry.item_id},{entry.amount},{entry.price_cent});"
        lines.append(line)

    content = "\n".join(lines)

    fn = "new_discounts.sql"
    with open(fn, "a") as fp:
        fp.write("\n\n\n")
        fp.write(content)
        CONSOLE.print(f"Wrote {fn}", style="green")


def i_create_demo():
    global MONDAY, SATURDAY, LAST_BEST_MATCH_ITEM_ID, LAST_STORE, DISCOUNTS, CONSOLE

    if len(DISCOUNTS) > 0:
        res = input("Discounts not empty. Overwrite with demo data [yN]?")
        if res.lower() != "y":
            return

    DISCOUNTS.clear()

    DISCOUNTS.append(Discount(MONDAY, SATURDAY, "lidl", 12, 10, 159))
    DISCOUNTS.append(Discount("2021-08-06", SATURDAY, "kaufland", 53, 500, 199))

    LAST_STORE = "kaufland"
    LAST_BEST_MATCH_ITEM_ID = 53
    MONDAY, SATURDAY = "2021-08-02", "2021-08-07"

    i_show_discounts()
    CONSOLE.print(f"{LAST_STORE=}")
    CONSOLE.print(f"{LAST_BEST_MATCH_ITEM_ID=}")
    CONSOLE.print(f"{MONDAY=}")
    CONSOLE.print(f"{SATURDAY=}")


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
