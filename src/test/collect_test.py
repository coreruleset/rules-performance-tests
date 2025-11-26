"""
Unit tests for the collect module.
These tests verify that the CollectCommandArg class and argument parsing work correctly.
"""
import pytest
from src.collect import get_test_command_arg
from src.model import CollectCommandArg
from src.type import UtilType


def test_collect_command_arg_parsing():
    """Test that command arguments are parsed correctly"""
    args = ["--test-name", "unit-test-ftw", "--utils", "ftw"]
    command_args = get_test_command_arg(args)

    assert command_args.test_name == "unit-test-ftw"
    assert command_args.utils == ["ftw"]
    assert command_args.raw_output == "./data/unit-test-ftw"
    assert command_args.output == "./report/unit-test-ftw"
    assert command_args.waf_endpoint == "http://localhost:80"


def test_collect_command_arg_multiple_utils():
    """Test parsing multiple utilities"""
    args = ["--test-name", "multi-util-test", "--utils", "ftw,locust,cAdvisor"]
    command_args = get_test_command_arg(args)

    assert command_args.test_name == "multi-util-test"
    assert command_args.utils == ["ftw", "locust", "cAdvisor"]


def test_collect_command_arg_custom_paths():
    """Test custom raw-output and output paths"""
    args = [
        "--test-name", "custom-path-test",
        "--utils", "ftw",
        "--raw-output", "/tmp/raw",
        "--output", "/tmp/output"
    ]
    command_args = get_test_command_arg(args)

    assert command_args.raw_output == "/tmp/raw/custom-path-test"
    assert command_args.output == "/tmp/output/custom-path-test"


def test_collect_command_arg_defaults():
    """Test that default values are set correctly"""
    args = ["--test-name", "defaults-test"]
    command_args = get_test_command_arg(args)

    # Should default to all utilities (ftw, locust, cAdvisor, eBPF)
    assert len(command_args.utils) >= 3  # At least ftw, locust, cAdvisor
    assert command_args.waf_endpoint == "http://localhost:80"
    assert command_args.rules_dir == "./rules"
    assert command_args.test_cases_dir == "./tests/regression/tests"
