"""
Module ReportCommandArg is a class for representing the arguments for report command.
"""
from typing import List
from src.type import UtilType, ReportFormat


class ReportCommandArg:
    """
    ReportCommandArg is a class for representing the arguments for report command.
    
    Args:
        - `test_name` (str): the name of the test case.
        - `utils` (List[UtilType]): the list of utils to be used. 
        - `raw_output` (str): raw output directory. Default: ./data.
        - `output` (str): output directory. Default: ./report.
        - `threshold_conf` (str): threshold configuration directory. Default: None.
        - `report_format` (ReportFormat): report format. Default: ReportFormat.TEXT.
    """
    test_name: str
    utils: List[UtilType]
    raw_output: str
    output: str
    threshold_conf: str
    report_format: ReportFormat

    def __init__(self,
                 test_name: str,
                 utils: List[UtilType],
                 raw_output: str,
                 output: str,
                 threshold_conf: str,
                 report_format: ReportFormat
                 ):
        self.test_name = test_name
        self.utils = utils
        self.raw_output = f"{raw_output}/{self.test_name}" if raw_output else f"./data/{self.test_name}"
        self.output = f"{output}/{self.test_name}" if output else f"./report/{self.test_name}"
        self.threshold_conf = threshold_conf if threshold_conf else None
        self.report_format = report_format if report_format else ReportFormat.TEXT
