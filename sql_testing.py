#!/usr/bin/env python

import functools
import sqlite3
import uuid

from typing import Optional


def log_execution(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        print(f"--- {func.__name__} ---")
        return func(*args, **kwargs)

    return wrapper


@log_execution
def having_conditions():
    SCRIPT = """
CREATE TABLE data(
    item TEXT,
    date TEXT,
    price INTEGER
);

INSERT INTO data 
    (item, date, price)
VALUES
    ("a", "2020", 100),
    ("a", "2021", 100),
    ("a", "2021", 120),
    ("bbb", "2021", 200),
    ("a", "2019", 100),
    ("bbb", "2020", 200)
;
    """

    QUERY = """
SELECT * FROM data
GROUP BY
    item
HAVING MIN(price * 5.0) AND MAX(date)
    """

    with sqlite3.connect(":memory:") as conn:
        conn.executescript(SCRIPT)

        for r in conn.execute(QUERY):
            print(r)


def str_lower(text: Optional[str]) -> Optional[str]:
    # print("hi")
    return None if text is None else text.casefold()


def uuid_bytes() -> bytes:
    return uuid.uuid4().bytes


@log_execution
def custom_function():
    QUERY = """
SELECT X_LOWER("This Is A Test"), X_UUID_B()
    """
    with sqlite3.connect(":memory:") as conn:
        conn.create_function("X_LOWER", narg=1, func=str_lower, deterministic=True)
        conn.create_function("X_UUID_B", narg=0, func=uuid_bytes, deterministic=False)

        for r in conn.execute(QUERY):
            print(r)


def main():
    having_conditions()
    custom_function()


if __name__ == "__main__":
    main()
