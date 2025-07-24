"""Test cases for SQLite database connection and schema setup."""
import json
import os
import shutil
import sqlite3
import tempfile

import pytest

from aiskus_app.db import get_db, close_db, init_db
from aiskus_app import create_app


# Setup and teardown

@pytest.fixture
def app_with_temp_db():
    """Create a Flask app with a temporary SQLite database."""
    # Create a temporary directory for the db
    temp_dir = tempfile.mkdtemp()
    db_path = os.path.join(temp_dir, "test.sqlite3")

    # Patch the app.config.DATABASE to point to our temp file
    app = create_app()
    app.config.update({"DATABASE": db_path})

    with app.app_context():
        init_db()

    yield app #per injection, test code runs until here. After finished, below code executes to cleanup
    # Clean up: remove temp directory after tests
    shutil.rmtree(temp_dir)

def test_db_connection(app_with_temp_db):
    """Test that the app can connect to the database."""
    with app_with_temp_db.app_context():
        db = get_db()
        assert db is not None, "Could not establish DB connection"
        close_db()

def test_table_exists(app_with_temp_db):
    """Test that the required table exists after initialization."""
    with app_with_temp_db.app_context():
        db = get_db()
        cursor = db.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='themes_and_summaries';"
        )
        table = cursor.fetchone()
        close_db()
        assert table is not None, "themes_and_summaries table does not exist"

def test_insert_and_fetch(app_with_temp_db):
    """Test inserting and fetching a summary record."""
    with app_with_temp_db.app_context():
        db = get_db()
        db.execute(
            "INSERT INTO themes_and_summaries "
            "(first_question_time, last_question_time, themes_json, summary_str, queried) "
            "VALUES (?, ?, ?, ?, ?)",
            (1623456000, 1623459600, json.dumps(["algorithms"]), "Batch summary example", 0)
        )
        db.commit()
        cursor = db.execute(
            "SELECT summary_str FROM themes_and_summaries WHERE summary_str = ?",
            ("Batch summary example",)
        )
        row = cursor.fetchone()
        close_db()
        assert row is not None and row["summary_str"] == "Batch summary example", "Insert/fetch failed"

def test_invalid_insert_and_fetch(app_with_temp_db):
    with app_with_temp_db.app_context():
        db = get_db()
        with pytest.raises(Exception) as execinfo:
            db.execute("INSERT INTO themes_and_summaries "
            "(first_question_time, last_question_time, themes_json, summary_str, queried) "
            "VALUES (?, ?, ?, ?, ?)",
            (1623456000, 1623459600,"Batch summary example", 0))
            db.commit()
        
        close_db()

    assert "Incorrect number of bindings supplied" in str(execinfo.value) or "incompatible" in str(execinfo.value).lower()


def test_invalid_db_path():
    """Test that connecting to an invalid path raises an error."""
    try:
        sqlite3.connect("/invalid/path/test_db.sqlite3")
        assert False, "Should not connect with invalid path"
    except sqlite3.OperationalError:
        assert True
