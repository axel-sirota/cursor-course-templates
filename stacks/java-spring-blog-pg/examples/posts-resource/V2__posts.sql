CREATE TABLE posts (
    id         UUID         PRIMARY KEY,
    title      VARCHAR(200) NOT NULL,
    body       TEXT         NOT NULL,
    author     VARCHAR(200) NOT NULL,
    created_at TIMESTAMPTZ  NOT NULL
);

CREATE INDEX posts_created_at_idx ON posts (created_at DESC);
