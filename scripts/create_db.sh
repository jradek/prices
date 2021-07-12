#! /usr/bin/env sh

mkdir -p tmp
sqlite3 tmp/prices.db < data/prices.sql
