"""
Module UtilType is an enum for representing the type of available utils
"""
from enum import Enum


class UtilType(Enum):
    """
    UtilType is an enum for representing the type of available utils
    
    Option:
        - `ftw`: go-ftw
        - `locust`: locust
        - `cAdvisor`: cAdvisor
        - `eBFF`: eBFF
    """
    FTW = "ftw",
    LOCUST = "locust",
    CADVISOR = "cAdvisor",

    # @TODO: impl
    EBPF = "eBFF"
