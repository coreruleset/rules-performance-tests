"""
Model package defines all the classes that are used to represent the data. Specifically,
following classes are defined:
- `ParsedDataItem`: a class that represents a single data item when generating a report.
- `Threshold`: a class that represents a threshold when generating a report.
- `Util`: a class that represents a utility. It is the base class for all the utilities.
- `CollectCommandArg`: a class that represents the arguments for collect command.
- `ReportCommandArg`: a class that represents the arguments for report command.
- `UtilMapper`: a dictionary that maps the UtilType to the Util class.
"""
from src.type import UtilType
from .Util import ParsedDataItem, Threshold, Util
from .CollectCommandArg import CollectCommandArg
from .ReportCommandArg import ReportCommandArg
from .FTWUtil import FTWUtil
from .LocustUtil import LocustUtil
from .CAdvisorUtil import CAdvisorUtil


# UtilMapper is a dictionary that maps the UtilType to the Util class
UtilMapper: dict[UtilType, Util] = {
    UtilType.FTW: FTWUtil,
    UtilType.CADVISOR: CAdvisorUtil,
    UtilType.LOCUST: LocustUtil
}


__all__ = [
    "ParsedDataItem",
    "Threshold",
    "Util",
    "CollectCommandArg",
    "ReportCommandArg",
    "UtilMapper"
]
