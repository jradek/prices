PRAGMA foreign_keys=OFF;
BEGIN TRANSACTION;

CREATE TABLE items (
	id INTEGER NOT NULL,
	date TEXT,
	price_cent INTEGER
);

INSERT INTO items VALUES(0, "2022-01-30", 100);
INSERT INTO items VALUES(0, "2022-01-30", 120);
INSERT INTO items VALUES(0, "2022-01-30", 140);
INSERT INTO items VALUES(1, "2022-01-29", 110);
INSERT INTO items VALUES(1, "2022-01-29", 100);

COMMIT;