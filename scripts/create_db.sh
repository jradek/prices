#! /usr/bin/env sh

# re-create database from sql dump

mkdir -p tmp
rm -rf tmp/prices.db
sqlite3 tmp/prices.db < data/prices.sql
