import ollama
from ollama import Client
import pytest
import json
import time
from aiskus_app.models.question import Question
from aiskus_app.models.summary import Summary
from aiskus_app.clients.ollama_client import OllamaClient
from aiskus_app import create_app
from aiskus_app.services.questionProcessor import QuestionProcessor
import tempfile
import os
import shutil
import sqlite3

from aiskus_app.db import get_db, close_db, init_db
from aiskus_app import create_app


@pytest.fixture
def ollama_client():
    ollama_test_client= OllamaClient()
    yield ollama_test_client
@pytest.fixture
def question_processor():
    yield QuestionProcessor()
    # check how to do this with app context
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


def test_q(ollama_client, question_processor):
    question1=Question(question_body="What is the color of the moon?", question_asked_time=time.time())
    x = question_processor.processQuestion(question1)

def test_bigger(ollama_client, question_processor, app_with_temp_db):
    with app_with_temp_db.app_context():
        question1 = Question(
            question_body="Why do we need to sort the array before using the two pointer method?",
            question_asked_time=time.time()
        )
        question2 = Question(
            question_body="How do we choose the starting positions for the left and right pointers?",
            question_asked_time=time.time()
        )
        question3 = Question(
            question_body="Why can't we just use a single loop instead of two pointers?",
            question_asked_time=time.time()
        )
        question4 = Question(
            question_body="I'm confused about when to move the left pointer versus the right pointer.",
            question_asked_time=time.time()
        )
        question5 = Question(
            question_body="How does the two pointer approach help avoid checking duplicate pairs?",
            question_asked_time=time.time()
        )
        question6 = Question(
            question_body="I don't understand how incrementing works with the two points. How do they not overlap?",
            question_asked_time=time.time()
        )
        question7 = Question(
            question_body="Is the two pointer method only for arrays, or can it be used on linked lists too?",
            question_asked_time=time.time()
        )
        question8 = Question(
            question_body="How is the two pointer method different from using recursion?",
            question_asked_time=time.time()
        )
        question9 = Question(
            question_body="I'm getting stuck in an infinite loop when using two pointers. What might cause that?",
            question_asked_time=time.time()
        )
        question10 = Question(
            question_body="Why do we need to increment the poointers in opposite directions",
            question_asked_time=time.time()
        )

        question_objects_array = [
            question1,
            question2,
            question3,
            question4,
            question5,
            question6,
            question7,
            question8,
            question9,
            question10,
        ]

        for q in question_objects_array:
            summary_obj=question_processor.processQuestion(q)

        assert summary_obj.summary is not None 
        assert '(1)' in summary_obj.summary, "summary object missing (1) attribute"
        assert '(2)' in summary_obj.summary, "summary object missing (2) attribute"

        db = get_db()
        cursor = db.cursor()

            # Query the latest inserted row assuming queried=False and times matching those in the summary_obj
        cursor.execute("""
                SELECT first_question_time, last_question_time, themes, summary_str, queried
                FROM themes_and_summaries
                WHERE first_question_time = ? AND last_question_time = ?
                ORDER BY rowid DESC LIMIT 1
            """, (summary_obj.first_question_time, summary_obj.last_question_time))

        row = cursor.fetchone()
        cursor.close()

        assert row is not None, "Summary entry not found in the database."

            # Check each relevant field matches what we expect
        db_themes = json.loads(row["themes"])  # deserialize JSON
        db_summary = row["summary_str"]
        db_queried = row["queried"]

        assert db_themes == summary_obj.themes, "Themes stored in DB do not match."
        assert db_summary == summary_obj.summary, "Summary stored in DB does not match."
        assert db_queried == 0 or db_queried == False, "Queried flag should be False (0) initially."
