"""
Module CollectCommandArg is a class for storing the arguments for collect command,
it is used when the user wants to collect data with any util.
"""
import re
import os
from typing import List, Optional
from src.type import UtilType, Mode


class CollectCommandArg:
    """
    CollectCommandArg is a class for storing the arguments for collect command,
    it is used when the user wants to collect data with any util.
    @TODO: add more description
    
    Args:
        test_name (str): 
        utils (Optional[List[UtilType]]): Utilities to be used for collecting data. Default: all
        raw_output (Optional[str]): Raw data output folder. Default: ./data
        output (Optional[str]): Report output folder. Default: ./report
        before (Optional[str]): the state of the commit before the changes. Default: HEAD
        after (Optional[str]): the state of the commit after the changes. Default: . (on-prem location)
        waf_endpoint (Optional[str]): WAF endpoint. Default: http://localhost:80
        mode (Optional[Mode]): mode for running the command. Default: cli
    """
    test_name: str
    utils: List[UtilType]
    before: Optional[str]
    after: Optional[str]
    raw_output: Optional[str]
    output: Optional[str]
    waf_endpoint: Optional[str]
    mode: Optional[Mode]

    # auto-generated folder for storing temporary files
    tmp_dir: str = './tmp'
    before_rules_dir: str
    after_rules_dir: str
    test_cases_dir: str

    # @TODO: move to config
    modsec_version: str = 'modsec2-apache'

    def __init__(self,
                 test_name: str,
                 utils: Optional[List[UtilType]],
                 raw_output: Optional[str],
                 output: Optional[str],
                 before: Optional[str],
                 after: Optional[str],
                 waf_endpoint: Optional[str],
                 mode: Optional[Mode]
                 ):
        self.test_name = test_name
        self.utils = utils if (utils is not None and len(utils)) else [util for util in UtilType]
        self.before = before if before else "HEAD"
        self.after = after if after else "."
        self.mode = mode if mode else Mode.CLI

        if not self.__is_git_commit_hash(self.before) and not self.__is_git_commit_hash(self.after):
            raise ValueError("Invalid before/after: only one local folder is allowed")

        # check if the before/after is a git commit hash. -- is used for on-prem location.
        if not self.__is_git_commit_hash(self.after):
            self.after = f"-- {self.after}"

        self.raw_output = f"{raw_output}/{self.test_name}" if raw_output else f"./data/{self.test_name}"
        self.output = f"{output}/{self.test_name}" if output else f"./report/{self.test_name}"
        self.waf_endpoint = waf_endpoint if waf_endpoint else "http://localhost:80"

        self.tmp_dir = os.path.join(self.tmp_dir, self.test_name)
        self.before_rules_dir = os.path.join(self.tmp_dir, "before-rules")
        self.after_rules_dir = os.path.join(self.tmp_dir, "after-rules")
        self.test_cases_dir = os.path.join(self.tmp_dir, "test-cases")

    def __is_git_commit_hash(self, s: str) -> bool:
        """
        check if a string is a valid git commit hash

        Args:
            s (str): string to be checked

        Returns:
            bool: True if the string is a valid git commit hash
        """
        finder = re.compile(r'[0-9a-f]+')
        return s == "HEAD" or (len(s) <= 40 and finder.fullmatch(s))
