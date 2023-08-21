"""
Module State is an enum for representing the state of the test case.
"""

from enum import Enum


class State(Enum):
    """
    State is an enum for representing the state of the test case.
    A performance test is based on a comparison between the state before and after the change
    
    Option:
        - `before`: the state before the change
        - `after`: the state after the change
    """
    BEFORE = "before"
    AFTER = "after"
