#! /usr/bin/env sh

# re-create database from sql dump

mkdir -p tmp
sqlite3 tmp/prices.db < data/prices.sql
