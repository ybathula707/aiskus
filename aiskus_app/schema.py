CREATE_SCHEMA_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS themes_and_summaries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    first_question_time REAL NOT NULL,
    last_question_time REAL NOT NULL,
    themes_json TEXT NOT NULL,
    summary_str TEXT NOT NULL,
    queried INTEGER NOT NULL DEFAULT 0
);
"""
