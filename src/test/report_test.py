"""
Unit tests for the report module.
These tests verify that data parsing and report generation work correctly.
"""
import pytest
import json
import os
import tempfile
import shutil
from src.model import FTWUtil, ReportCommandArg
from src.type import ReportFormat


@pytest.fixture
def temp_data_dir():
    """Create a temporary directory for test data"""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)


@pytest.fixture
def ftw_test_data(temp_data_dir):
    """Create mock FTW test data"""
    test_name = "unit-test-ftw"
    data_dir = os.path.join(temp_data_dir, test_name)
    os.makedirs(data_dir, exist_ok=True)

    # Create mock FTW JSON data
    ftw_data = {
        "run": 10,
        "success": ["test-1", "test-2", "test-3"],
        "failed": ["test-4"],
        "skipped": ["test-5"],
        "runtime": {
            "test-1": 0.1,
            "test-2": 0.2,
            "test-3": 0.15
        },
        "TotalTime": 1.5
    }

    ftw_file = os.path.join(data_dir, "ftw.json")
    with open(ftw_file, 'w') as f:
        json.dump(ftw_data, f)

    return temp_data_dir, test_name


def test_ftw_util_parse_data(ftw_test_data):
    """Test FTW utility data parsing"""
    temp_dir, test_name = ftw_test_data

    util = FTWUtil()
    data = util.parse_data(f"{temp_dir}/{test_name}/ftw.json")

    assert data["run"].value == 10
    assert len(data["success"]) == 3
    assert len(data["failed"]) == 1
    assert len(data["skipped"]) == 1
    assert data["totalTime"].value == 1.5


def test_report_command_arg_creation():
    """Test ReportCommandArg creation with defaults"""
    args = ReportCommandArg(
        test_name="test-report",
        utils=["ftw"],
        raw_output="./data",
        output="./report",
        threshold_conf=None,
        report_format=ReportFormat.TEXT
    )

    assert args.test_name == "test-report"
    assert args.utils == ["ftw"]
    assert args.raw_output == "./data/test-report"
    assert args.output == "./report/test-report"
    assert args.threshold_conf is None
    assert args.report_format == ReportFormat.TEXT


def test_ftw_text_report_generates_output(ftw_test_data, capsys):
    """Test that FTW text report generates output"""
    temp_dir, test_name = ftw_test_data

    util = FTWUtil()
    args = ReportCommandArg(
        test_name=test_name,
        utils=["ftw"],
        raw_output=temp_dir,
        output=temp_dir,
        threshold_conf=None,
        report_format=ReportFormat.TEXT
    )

    util.text_report(args)

    # Capture the printed output
    captured = capsys.readouterr()
    assert "unit-test-ftw" in captured.out
    assert "Run:" in captured.out
    assert "Success:" in captured.out
    assert "Failed:" in captured.out
