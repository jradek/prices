#! /usr/bin/env sh

rm -rf items.db
sqlite3 items.db < items.sql
