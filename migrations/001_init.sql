CREATE table documents (
  id BIGINT NOT NULL,
  title TEXT,
  PRIMARY KEY (id)
);
ALTER TABLE documents ORDER BY id;

CREATE TABLE tokens (
  id BIGINT NOT NULL AUTO_INCREMENT,
  token VARCHAR(200) CHARACTER SET ascii UNIQUE,
  PRIMARY KEY (id)
);
CREATE UNIQUE INDEX token_idx ON tokens (token);
ALTER TABLE tokens ORDER BY id;

CREATE TABLE token_counts (
  id BIGINT NOT NULL AUTO_INCREMENT,
  token INT,
  document INT,
  num INT DEFAULT 0,
  -- UNIQUE KEY tokdoc (token, document),
  -- TODO: re-enable?
  PRIMARY KEY (id)
);
CREATE INDEX document_idx ON token_counts(document);
CREATE INDEX token_idx ON token_counts(token);
ALTER TABLE token_counts ORDER BY id;
