
CREATE TABLE IF NOT EXISTS daily_logs (
    id SERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    log_date DATE NOT NULL DEFAULT CURRENT_DATE,
    mood SMALLINT CHECK (mood BETWEEN 1 AND 5),
    work_hours REAL CHECK (work_hours >= 0),
    sleep_hours REAL CHECK (sleep_hours >= 0),
    comment TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE (user_id, log_date)
);


CREATE INDEX IF NOT EXISTS idx_user_date ON daily_logs (user_id, log_date);