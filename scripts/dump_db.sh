#! /usr/bin/env sh

# dump database to sql file

sqlite3 tmp/prices.db < scripts/dump_db.sql
