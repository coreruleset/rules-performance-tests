"""
Module report is a script to generate report from collected data.

Usage:
    ```sh
    TEST_NAME=example
    poetry run report --test-name $TEST_NAME --utils cAdvisor
    
    # use with multiple utils
    poetry run report --test-name $TEST_NAME --utils cAdvisor,ftw,locust
    
    # using with threshold
    poetry run report --test-name $TEST_NAME --utils cAdvisor --threshold-conf "./config"
"""
import argparse
import os
import sys
from src.model import ReportCommandArg, UtilMapper
from src.type import ReportFormat, UtilType
from src.utils import logger


def get_summary_command_arg(args: any) -> ReportCommandArg:
    """
    get summary command arg from STDIN

    Returns:
        ReportCommandArg: parsed args
    """
    parser = argparse.ArgumentParser(description='WAF Test Command Parser')
    parser.add_argument('--test-name', type=str, help='test name', required=True)
    parser.add_argument('--utils', type=str, help='utils')
    parser.add_argument('--output', type=str, help='output')
    parser.add_argument('--raw-output', type=str, help='raw output')
    parser.add_argument('--threshold-conf', type=str, help='threshold conf')
    parser.add_argument('--format', type=str, help='output')
    parsed_args = parser.parse_args(args)

    # @TODO: default with all utils
    return ReportCommandArg(
        test_name=parsed_args.test_name,
        utils=parsed_args.utils.split(',') if parsed_args.utils else [],
        output=parsed_args.output,
        raw_output=parsed_args.raw_output,
        threshold_conf=parsed_args.threshold_conf,
        report_format=parsed_args.format
    )

def init(args: ReportCommandArg):
    """
    initialize corresponding directory, service, etc.
    """
    os.makedirs(args.output, exist_ok=True)

def main(args: any = None):
    """
    script entrypoint of report.py
    """

    if args is None:
        args = sys.argv[1:]

    # check the inputs
    command_args = get_summary_command_arg(args)

    # create folder
    init(command_args)

    # build the report
    for util in command_args.utils:
        if command_args.report_format == ReportFormat.TEXT:
            UtilMapper.get(UtilType(UtilType[util.upper()]))().text_report(command_args)

        elif command_args.report_format == ReportFormat.IMG:
            UtilMapper.get(UtilType(UtilType[util.upper()]))().figure_report(command_args)

        else:
            logger.critical("--format support text or img")
            exit(1)
