import pytest
import sqlite3
import os
from unittest.mock import Mock
import tempfile
import json
from aiskus_app.services.report_processor import ReportProcessor
from aiskus_app import create_app
from aiskus_app.db import init_db, get_db
from aiskus_app.models.summary import Summary
import shutil

@pytest.fixture
def app_with_temp_db():
    """
    Creating pytest fixture of temp DB with dummy data
    Using a test application context
    """
    temp_dir = tempfile.mkdtemp()
    db_path = os.path.join(temp_dir, "test.sqlite3")  # Fixed: temp_dir instead of tempfile
    
    # Patching db config w/test db 
    app = create_app()
    app.config.update({"DATABASE": db_path})

    with app.app_context():
        init_db()
        yield app
    
    shutil.rmtree(temp_dir)

@pytest.fixture 
def test_question_objects():
    """Create test Summary objects with properly formatted themes_json"""
    summaryObj1 = Summary(
        first_question_time=1000,  # Before timestamp
        last_question_time=2000,
        themes=["theme1", "theme2", "theme3"],
        summary="sample summary paragraphs 1",
        queried=False
    )
    summaryObj2 = Summary(
        first_question_time=3000,  # Before timestamp  
        last_question_time=4000,
        themes=["theme4", "theme5", "theme6"],
        summary="sample summary paragraphs 2",
        queried=False
    )
    summaryObj3 = Summary(
        first_question_time=6000,  # After timestamp
        last_question_time=7000,
        themes=["theme7", "theme8"],
        summary="sample summary paragraphs 3",
        queried=False
    )
    yield [summaryObj1, summaryObj2, summaryObj3]

@pytest.fixture
def sample_ollama_response():
    """
    Mock Ollama response object that mimics the structure returned by ollama_client.chat()
    """
    mock_response = Mock()
    mock_response.message = Mock()
    mock_response.message.content = """
    Here is the analysis of the student questions:

    {
        "summary": "(1) Students demonstrate fundamental gaps in understanding derivative applications, particularly struggling with the chain rule when applied to composite functions and interpreting mathematical notation in complex expressions.\\n(2) Instructors should provide more step-by-step worked examples of chain rule applications, use visual representations of composite functions, and dedicate time to explaining mathematical notation conventions before introducing new derivative techniques.\\n(3) Students show high engagement but increasing frustration with notation complexity.",
        "themes": ["derivative applications", "chain rule confusion", "notation interpretation"],
        "number_of_questions": 20,
        "generated_time": 1672534800,
        "student_headspace": "The students are frustrated due around complicated concepts but eager to learn."
    }

    This analysis should help instructors understand the current learning challenges.
    """

    return mock_response


@pytest.fixture
def test_reports_processor():
    yield ReportProcessor()

def _insert_test_data(db_connection, summary_objects):
    """Helper function to insert test data into database"""
    cursor = db_connection.cursor()
    
    for summary in summary_objects:
        themes_json = json.dumps(summary.themes)  # Convert themes list to JSON string
        cursor.execute("""
            INSERT INTO themes_and_summaries 
            (first_question_time, last_question_time, themes, summary_str, queried)
            VALUES (?, ?, ?, ?, ?)
        """, (
            summary.first_question_time,
            summary.last_question_time,
            themes_json,
            summary.summary,
            1 if summary.queried else 0
        ))
    
    db_connection.commit()

def test_get_unprocessed_summaries(app_with_temp_db, test_question_objects):
    """
    Test that _get_unprocessed_summaries correctly:
    1. Retrieves only rows with first_question_time before the timestamp
    2. Retrieves only rows where queried = 0 (False)
    3. Orders results by first_question_time DESC
    4. Returns correct data structure
    """
    with app_with_temp_db.app_context():
        # Arrange
        db_connection = get_db()
        processor = ReportProcessor()
        request_timestamp = 5000  # Should get summaryObj1 and summaryObj2, not summaryObj3
        
        # Insert test data
        _insert_test_data(db_connection, test_question_objects)
        
        # Act
        result = processor._get_unprocessed_summaries(db_connection, request_timestamp)
        
        # Assert
        assert len(result) == 2, f"Expected 2 rows, got {len(result)}"
        
        # Verify correct rows returned (should be summaryObj2 first due to DESC order)
        assert result[0]['themes'] == json.dumps(["theme4", "theme5", "theme6"])  # themes_json
        assert result[0]['summary_str'] == "sample summary paragraphs 2"  # summary_str
        assert result[0][3] == 0  # queried should be 0 (False)
        
        assert result[1]['themes'] == json.dumps(["theme1", "theme2", "theme3"])  # themes_json  
        assert result[1]['summary_str'] == "sample summary paragraphs 1"  # summary_str
        assert result[1][3] == 0  # queried should be 0 (False)
        
        # Verify ordering (DESC by first_question_time)
        first_row_time = result[0][0] if hasattr(result[0], '__getitem__') else getattr(result[0], 'first_question_time', None)
        second_row_time = result[1][0] if hasattr(result[1], '__getitem__') else getattr(result[1], 'first_question_time', None)
        
        # Since we're selecting by index and the query orders by first_question_time DESC,
        # we need to check the actual timestamps from our test data
        # The result should have summaryObj2 (3000) first, then summaryObj1 (1000)
        assert result[0][1] == json.dumps(["theme4", "theme5", "theme6"])  # This confirms summaryObj2 is first
        assert result[1][1] == json.dumps(["theme1", "theme2", "theme3"])  # This confirms summaryObj1 is second

def test_transform_rows_to_metadata(app_with_temp_db, test_question_objects, test_reports_processor):
    """
    Test that transform_rows_to_metadata correctly:
    1. Converts database rows to dictionary format
    2. Extracts id, themes, and summary_str fields
    3. Returns a list of metadata dictionaries
    4. Handles empty rows gracefully
    """
    with app_with_temp_db.app_context():
        # Arrange
        db_connection = get_db()
        request_timestamp = 5000  # Should get summaryObj1 and summaryObj2, not summaryObj3
        
        # Insert test data
        _insert_test_data(db_connection, test_question_objects)
        
        # Get rows from database
        rows = test_reports_processor._get_unprocessed_summaries(
            db_connection, request_timestamp
        )
        
        # Act
        metadata_list = test_reports_processor._transform_rows_to_metadata(rows)
        
        # Assert
        assert isinstance(metadata_list, list), "Should return a list"
        assert len(metadata_list) == 2, f"Expected 2 metadata objects, got {len(metadata_list)}"
        
        # Check first metadata object (summaryObj2 - highest timestamp due to DESC order)
        first_metadata = metadata_list[0]
        assert isinstance(first_metadata, dict), "Each metadata item should be a dictionary"
        assert 'id' in first_metadata, "Metadata should contain 'id' field"
        assert 'themes' in first_metadata, "Metadata should contain 'themes' field"
        assert 'summary_str' in first_metadata, "Metadata should contain 'summary_str' field"
        
        # Verify the actual data content
        assert first_metadata['themes'] == json.dumps(["theme4", "theme5", "theme6"])
        assert first_metadata['summary_str'] == "sample summary paragraphs 2"
        
        # Check second metadata object (summaryObj1)
        second_metadata = metadata_list[1]
        assert second_metadata['themes'] == json.dumps(["theme1", "theme2", "theme3"])
        assert second_metadata['summary_str'] == "sample summary paragraphs 1"
        
        # Verify all required fields are present in both objects
        for metadata in metadata_list:
            assert set(metadata.keys()) == {'id', 'themes', 'summary_str'}, \
                f"Metadata should have exactly 3 fields, got: {metadata.keys()}"
            
def test_parse_to_json(test_reports_processor,sample_ollama_response):

    parsed=test_reports_processor._parse_to_json(sample_ollama_response)

    assert parsed["summary"] is not None
    assert parsed["themes"] is not None
    assert parsed["number_of_questions"] is not None
    assert parsed["generated_time"] is not None
    assert parsed["student_headspace"] is not None

def test_generate_report(test_question_objects, app_with_temp_db, monkeypatch):
   
    with app_with_temp_db.app_context():
        #DUPLICATED because I'm need practice using mocks properly w/ollama client 
        """
        External dependencies to mockerooni
            1. mock db + insert data
            2. mock application ollama clinet + response
            3. mock the call to ollama client
        """
        #DB test data
        temp_db = get_db()
        _insert_test_data(temp_db, test_question_objects)
        request_timestamp = 5000  # Should get summaryObj1 and summaryObj2, not summaryObj3

        #mock client call + response
        mock_ollama_response = Mock()
        mock_ollama_response.message = Mock()
        mock_ollama_response.message.content = """
        Here is the analysis of student questions:
        
        {
            "summary": "Students demonstrate gaps in understanding derivatives and chain rule applications. Need more step-by-step examples.",
            "themes": ["derivative applications", "chain rule confusion", "notation interpretation"],
            "number_of_questions": 2,
            "generated_time": 1672534800,
            "student_headspace": "Students are frustrated but eager to learn."
        }
        
        This analysis should help instructors.
        """
        mock_ollama_client = Mock()
        mock_ollama_client.create_report.return_value= mock_ollama_response

        #patching the applicaiton runtime's ollama client w/ test client
        monkeypatch.setattr(app_with_temp_db, 'session_ollama_client', mock_ollama_client)
        
        #setting up test instance of report processor
        report_processor = ReportProcessor()

        result = report_processor.generate_report(request_timestamp)

        # Assert - Verify the results
        assert "report" in result, "Result should contain 'report' key"
        
        report = result["report"]
        assert isinstance(report, dict), "Report should be a dictionary"
        
        # Check all expected fields are present
        expected_fields = ["summary", "themes", "number_of_questions", "generated_time", "student_headspace"]
        for field in expected_fields:
            assert field in report, f"Report should contain '{field}' field"
        
        # Verify data types and content
        assert isinstance(report["themes"], list), "Themes should be a list"
        assert isinstance(report["number_of_questions"], int), "Number of questions should be an integer"
        assert isinstance(report["summary"], str), "Summary should be a string"
        assert len(report["themes"]) > 0, "Should have at least one theme"
        
        # Verify the Ollama client was called with correct data
        mock_ollama_client.create_report.assert_called_once()
        
        # Get the metadata that was passed to Ollama
        call_args = mock_ollama_client.create_report.call_args[0][0]
        assert isinstance(call_args, list), "Should pass list of metadata to Ollama"
        assert len(call_args) == 2, "Should pass 2 unprocessed summaries"
        
        # Verify metadata structure
        for metadata in call_args:
            assert "id" in metadata, "Metadata should contain id"
            assert "themes" in metadata, "Metadata should contain themes"
            assert "summary_str" in metadata, "Metadata should contain summary_str"