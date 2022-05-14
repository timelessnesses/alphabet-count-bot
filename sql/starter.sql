CREATE TABLE IF NOT EXISTS config(
    guild_id BIGSERIAL PRIMARY KEY,
    is_same_person BOOLEAN NOT NULL DEFAULT FALSE,
    already_setupped BOOLEAN NOT NULL DEFAULT FALSE,
    channel_id BIGINT NOT NULL
);
CREATE TABLE IF NOT EXISTS logger(
    id BIGSERIAL PRIMARY KEY,
    guild_id BIGINT NOT NULL,
    channel_id BIGINT NOT NULL,
    ruined_chain_id BIGINT NOT NULL,
    ruiner_id BIGINT NOT NULL,
    ruined_jump_url TEXT NOT NULL,
    ruined_content TEXT NOT NULL,
    when_ruined TIMESTAMP NOT NULL,
    reason TEXT NOT NULL,
    previous_chain_id BIGINT NOT NULL
);
CREATE TABLE IF NOT EXISTS counting(
    guild_id BIGSERIAL PRIMARY KEY,
    count_number BIGINT NOT NULL DEFAULT 0,
    count_channel_id BIGINT NOT NULL,
    previous_person BIGINT
);
CREATE TABLE IF NOT EXISTS user_stats(
    user_id BIGSERIAL PRIMARY KEY,
    alphabet_counts BIGINT NOT NULL DEFAULT 0,
    ruined_counts BIGINT NOT NULL DEFAULT 0
)