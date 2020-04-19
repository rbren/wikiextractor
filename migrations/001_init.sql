CREATE table documents (
  id INT NOT NULL PRIMARY KEY,
  title TEXT
);

CREATE TABLE tokens (
  id SERIAL PRIMARY KEY,
  token TEXT UNIQUE,
  dummy BOOLEAN
);

CREATE TABLE token_counts (
  id SERIAL,
  token INT REFERENCES tokens (id),
  document INT REFERENCES documents (id),
  num INT DEFAULT 0,
  UNIQUE(token, document)
);
