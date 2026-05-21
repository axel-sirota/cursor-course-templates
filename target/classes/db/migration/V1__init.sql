-- Phase 0 skeleton: full schema for the pub/sub broker.

CREATE TABLE topics (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name        TEXT NOT NULL UNIQUE,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE messages (
    id            BIGSERIAL PRIMARY KEY,
    topic_id      UUID NOT NULL REFERENCES topics(id) ON DELETE CASCADE,
    payload       JSONB NOT NULL,
    headers       JSONB NOT NULL DEFAULT '{}'::jsonb,
    published_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX idx_messages_topic_id_id ON messages(topic_id, id);

CREATE TABLE subscriptions (
    id                          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    topic_id                    UUID NOT NULL REFERENCES topics(id) ON DELETE CASCADE,
    name                        TEXT NOT NULL,
    webhook_url                 TEXT NOT NULL,
    last_delivered_message_id   BIGINT NOT NULL DEFAULT 0,
    active                      BOOLEAN NOT NULL DEFAULT TRUE,
    created_at                  TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (topic_id, name)
);
CREATE INDEX idx_subscriptions_active_topic ON subscriptions(active, topic_id);

CREATE TABLE delivery_attempts (
    id              BIGSERIAL PRIMARY KEY,
    subscription_id UUID NOT NULL REFERENCES subscriptions(id) ON DELETE CASCADE,
    message_id      BIGINT NOT NULL REFERENCES messages(id) ON DELETE CASCADE,
    attempt_no      INT NOT NULL,
    status          TEXT NOT NULL,           -- PENDING | SUCCESS | FAILED
    http_status     INT,
    error           TEXT,
    attempted_at    TIMESTAMPTZ,
    next_attempt_at TIMESTAMPTZ NOT NULL
);
CREATE INDEX idx_delivery_attempts_next ON delivery_attempts(status, next_attempt_at);

CREATE TABLE dead_letter (
    id              BIGSERIAL PRIMARY KEY,
    subscription_id UUID NOT NULL REFERENCES subscriptions(id) ON DELETE CASCADE,
    message_id      BIGINT NOT NULL REFERENCES messages(id) ON DELETE CASCADE,
    last_error      TEXT,
    moved_at        TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX idx_dead_letter_subscription ON dead_letter(subscription_id);
