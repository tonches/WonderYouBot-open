CREATE TABLE IF NOT EXISTS numbers (
	    number BIGINT,
	    timestamp BIGINT
	);

CREATE TABLE IF NOT EXISTS reads  (date date);
CREATE TABLE IF NOT EXISTS names  (number BIGINT, name VARCHAR(10));
CREATE TABLE IF NOT EXISTS ids    (groupid BIGINT, id BIGINT);