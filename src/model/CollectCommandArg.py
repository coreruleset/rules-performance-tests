"""
Module CollectCommandArg is a class for storing the arguments for collect command,
it is used when the user wants to collect data with any util.
"""
import os
from typing import List, Optional
from src.type import UtilType, Mode


class CollectCommandArg:
    """
    CollectCommandArg is a class for storing the arguments for collect command,
    it is used when the user wants to collect data with any util.

    Args:
        test_name (str): Name of the test
        utils (Optional[List[UtilType]]): Utilities to be used for collecting data. Default: all
        raw_output (Optional[str]): Raw data output folder. Default: ./data
        output (Optional[str]): Report output folder. Default: ./report
        waf_endpoint (Optional[str]): WAF endpoint. Default: http://localhost:80
        mode (Optional[Mode]): mode for running the command. Default: cli
        rules_dir (Optional[str]): Directory containing WAF rules. Default: ./rules
        test_cases_dir (Optional[str]): Directory containing test cases. Default: ./tests/regression/tests
    """
    test_name: str
    utils: List[UtilType]
    raw_output: str
    output: str
    waf_endpoint: str
    mode: Mode
    rules_dir: str
    test_cases_dir: str

    # auto-generated folder for storing temporary files
    tmp_dir: str = './tmp'

    # @TODO: move to config
    modsec_version: str = 'modsec2-apache'

    def __init__(self,
                 test_name: str,
                 utils: Optional[List[UtilType]],
                 raw_output: Optional[str],
                 output: Optional[str],
                 waf_endpoint: Optional[str],
                 mode: Optional[Mode],
                 rules_dir: Optional[str],
                 test_cases_dir: Optional[str]
                 ):
        self.test_name = test_name
        self.utils = utils if (utils is not None and len(utils)) else [util for util in UtilType]
        self.mode = mode if mode else Mode.CLI

        self.raw_output = f"{raw_output}/{self.test_name}" if raw_output else f"./data/{self.test_name}"
        self.output = f"{output}/{self.test_name}" if output else f"./report/{self.test_name}"
        self.waf_endpoint = waf_endpoint if waf_endpoint else "http://localhost:80"
        self.rules_dir = rules_dir if rules_dir else "./rules"
        self.test_cases_dir = test_cases_dir if test_cases_dir else "./tests/regression/tests"

        self.tmp_dir = os.path.join(self.tmp_dir, self.test_name)
