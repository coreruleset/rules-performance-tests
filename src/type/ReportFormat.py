"""
Module ReportFormat is an enum for representing the format of the report.
"""
from enum import Enum


class ReportFormat(Enum):
    """
    ReportFormat is an enum for representing the format of the report.

    Options:
        - `text`: output for text-based report
        - `img`: output for image-based report

    @TODO: impl http-based report
    """
    TEXT = "text",
    IMG = "img"
