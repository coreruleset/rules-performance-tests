"""
Module Mode represents the mode for running the command. By default, command `collect` and `report` are run in CLI mode.
"""
from enum import Enum


class Mode(Enum):
    """
    Module Mode represents the mode for running the command. By default, command `collect` and `report` are run in CLI mode.
    the difference between CLI mode and pipeline mode is that CLI mode is run in the local machine, 
    while pipeline mode is run in the CI/CD pipeline (Primarily on GitHub Action). Thus, some of the commands are different.
    
    Options:
        - `pipeline`: run in the CI/CD pipeline
        - `cli`: run in the local machine
    """
    PIPELINE = "pipeline"
    CLI = "cli"
