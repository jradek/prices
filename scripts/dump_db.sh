#! /usr/bin/env sh

sqlite3 tmp/prices.db < scripts/dump_db.sql
