"""
Module Util is an abstract class for Utils, it is used to read data from a source and store it in a database.
Once the data is stored, it can be parsed and used for generating reports.
extend this class to implement your own data collector.
"""
from abc import ABC, abstractmethod
from typing import List
from enum import Enum
import os
import json
import shutil
import yaml
import asciichartpy as asciichart
import dateutil.parser as date_parser
from termcolor import colored
from astropy.table import Table
from src.utils import logger
from .CollectCommandArg import CollectCommandArg
from .ReportCommandArg  import ReportCommandArg


class ParsedDataItem:
    """
        ParsedDataItem is a class for representing a data item. It is used for generating reports.

        Args:
            - `key` (any): key is the identifier of the data item. Ideally, it will be the name of a matrix.
            - `value` (any): value is the value of the data item.
            - `labels` (List[str], optional): labels is useful when using Threshold. It can used for filter condition.
                Defaults to [].
        """
    key: any
    value: any
    labels: set

    def __init__(self, key: any, value: any, labels: List[str] = []):
        self.key = key
        self.value = value
        self.labels = set(labels)

class _ComparisonUnit(Enum):
    """
    comparison_unit is an enum for representing how the data will be compared between before and after.
    
    Options:
        - `EACH`: compare each data item in before and after
        - `AVERAGE`: compare the average value of before and after
        - `SUM`: compare the sum of before and after
        - `COUNT`: compare the count of before and after
    """
    EACH = 1
    AVERAGE = 2
    SUM = 3
    COUNT = 4

class _ComparisonMethod(Enum):
    """
    comparison_method is an enum for representing how the data will be compared between before and after.
    
    Options:
        - `EQ`: equal
        - `NE`: not equal
        - `GT`: greater than
        - `LT`: less than
        - `GE`: greater than or equal
        - `LE`: less than or equal
        
        @TODO: currently rate_fn only supports to compare with object before
        - `RATIO_GT`: greater than (ratio)
        - `RATIO_LT`: less than (ratio)
        - `RATIO_GE`: greater than or equal (ratio)
        - `RATIO_LE`: less than or equal (ratio)
    """
    EQ = 'eq'
    NE = 'ne'
    GT = 'gt'
    LT = 'le'
    GE = 'ge'
    LE = 'le'

    RATIO_GT = 'ratioGt'
    RATIO_LT = 'ratioLt'
    RATIO_GE = 'ratioGe'
    RATIO_LE = 'ratioLe'

_data_processing_fn = {
    _ComparisonMethod.EQ.value: lambda a, b: a == b,
    _ComparisonMethod.NE.value: lambda a, b: a != b,
    _ComparisonMethod.GT.value: lambda a, b: a > b,
    _ComparisonMethod.LT.value: lambda a, b: a < b,
    _ComparisonMethod.GE.value: lambda a, b: a >= b,
    _ComparisonMethod.LE.value: lambda a, b: a <= b,
    _ComparisonMethod.RATIO_GT.value: lambda a, b: a > b,
    _ComparisonMethod.RATIO_LT.value: lambda a, b: a < b,
    _ComparisonMethod.RATIO_GE.value: lambda a, b: a >= b,
    _ComparisonMethod.RATIO_LE.value: lambda a, b: a <= b,
}

class _ComparisonObject(Enum):
    """
    ComparisonObject is an enum for representing the object of comparison.
    (i.e., who compares with after-data)
    When the comparison_object is set to THRESHOLD, the comparison_method will be applied to the threshold value.
    Specifically, some comparison_method (e.g., RATIO_GT) only support THRESHOLD object.
    
    Options:
        - `BEFORE`: compare the after-data with the before data
        - `THRESHOLD`: compare the after-data with the threshold
    """
    THRESHOLD = 1,
    BEFORE = 2,

class Threshold:
    """@TODO: doc"""
    id: int
    threshold_name: str
    threshold_desc: str
    comparison_unit: _ComparisonUnit
    comparison_method: _ComparisonMethod
    comparison_object: _ComparisonObject
    metric_name: str
    threshold: float

    # if include_labels is None, then include all labels
    # if include_labels not None, then the threshold inspection only applies to
    # the data with the labels in include_labels, it is a OR condition
    include_labels: set
    exclude_labels: set

    def __init__(self,
                 id: int,
                 threshold_name: str,
                 threshold_desc: str,
                 comparison_unit: _ComparisonUnit,
                 comparison_method: _ComparisonMethod,
                 comparison_object: _ComparisonObject,
                 metric_name: str,
                 threshold: float,
                 include_labels: List[str],
                 exclude_labels: List[str]
                 ):
        self.id = id
        self.threshold_name = threshold_name
        self.threshold_desc = threshold_desc
        self.comparison_unit = comparison_unit
        self.comparison_method = comparison_method
        self.comparison_object = comparison_object
        self.metric_name = metric_name
        self.threshold = threshold
        self.include_labels = set(include_labels) if include_labels else None
        self.exclude_labels = set(exclude_labels) if exclude_labels else None

    def inspect(self, before_data: List[ParsedDataItem], after_data: List[ParsedDataItem]):
        if not self.isPassed(before_data, after_data):
            print((f"Threshold: {self.threshold_name:24} {self.color_text('failed', 'red', True)}"))
        else:
            print((f"Threshold: {self.threshold_name:24} {self.color_text('passed', 'green', True)}"))

    def isPassed(self, before_data: List[ParsedDataItem], after_data: List[ParsedDataItem]) -> bool:
        if before_data is None or after_data is None:
            logger.error("before_data or after_data is None")
            return False

        if len(before_data) == 0 or len(after_data) == 0:
            logger.error("before_data or after_data is empty")
            return False

        before_val_type, after_val_type = type(before_data[0].value), type(after_data[0].value)

        if before_val_type != after_val_type:
            logger.error("before_data and after_data have different type")
            return False

        if (before_val_type in [str, bool]) and self.comparison_method not in ['eq', 'ne']:
            logger.error(f"str/bool type only support comparison method: EQ, NE")
            return False

        if not (before_val_type in [str, int, float, bool]):
            logger.error("current support data type: int, float, bool, str")
            return False

        if self.comparison_method in [7, 8, 9, 10] and self.comparison_object == _ComparisonObject.THRESHOLD:
            logger.error("rate comparison method only support with object: before")
            return False

        # filter data
        before_data = [data for data in before_data if self.__filter_by_labels(data)]
        after_data = [data for data in after_data if self.__filter_by_labels(data)]

        # process value by comparison_unit
        if self.comparison_unit == _ComparisonUnit.COUNT.name:
            before_data = [ParsedDataItem("cnt", len(before_data), [])]
            after_data = [ParsedDataItem("cnt", len(after_data), [])]
        elif self.comparison_unit == _ComparisonUnit.SUM.name:
            before_data = [ParsedDataItem("sum", sum([data.value for data in before_data]), [])]
            after_data = [ParsedDataItem("sum", sum([data.value for data in after_data]), [])]
        elif self.comparison_unit == _ComparisonUnit.AVERAGE.name:
            before_data = [ParsedDataItem("average", sum([data.value for data in before_data]) / len(before_data), [])]
            after_data = [ParsedDataItem("average", sum([data.value for data in after_data]) / len(after_data), [])]
        elif self.comparison_unit == _ComparisonUnit.EACH.name:
            pass

        # evaluate the value
        # @TODO: current only support same-length data
        # impl a non-length-sensitive version (e.g., time)
        if self.comparison_unit == _ComparisonUnit.EACH and len(before_data) != len(after_data):
            raise Exception("before_data and after_data have different length")

        passed, res = False, True
        for idx in range(len(after_data)):
            # @TODO: optimize enum issue
            if self.comparison_method in [_ComparisonMethod.RATIO_GT.value, _ComparisonMethod.RATIO_LT.value, _ComparisonMethod.RATIO_GE.value, _ComparisonMethod.RATIO_LE.value]:
                ratio = after_data[idx].value / before_data[idx].value
                passed = _data_processing_fn[self.comparison_method](self.threshold, ratio)
            else:
                passed = _data_processing_fn[self.comparison_method](before_data[idx].value, after_data[idx].value)
            
            if not passed:
                print(self.color_text((
                    f"\nThreshold {self.id} failed: \n"
                    f"threshold_name: {self.threshold_name}\n"
                    f"threshold_desc: {self.threshold_desc}\n"
                    f"        before: {before_data[idx].value}\n"
                    f"         after: {after_data[idx].value}\n\n"
                ), 'red', True))
                res = False

        return res

    def __filter_by_labels(self, data: ParsedDataItem) -> bool:
        # check include
        res = True

        if (self.include_labels is not None) and (len(self.include_labels) > 0):
            for label in data.labels:
                if label in self.include_labels:
                    res = True

        if not res: 
            return False

        # check exclude
        if (self.exclude_labels is not None) and (len(self.exclude_labels) > 0):
            for label in data.labels:
                if label in self.exclude_labels:
                    res = False

        return res

    def color_text(self, text: str, color: str, bold: bool = False):
        return colored(text, color, attrs=[] if not bold else ["bold"])

class _FTWTestInput:
    """@TODO: doc"""
    method: str = "GET"
    port: int = 80
    headers: dict = {}
    data: str = ""
    uri: str = "/"

    def __init__(self, dict: dict):
        for k, v in dict.items():
            setattr(self, k, v)

        HTTP_METHOD_LIST = ["GET", "HEAD", "POST", "PUT", "DELETE"
                            , "OPTIONS", "TRACE", "PATCH"]

        if self.method not in HTTP_METHOD_LIST:
            logger.warning(f"Invalid method in go-ftw yaml. Testcase: {self.method}, replace for 'GET to bypass'")
            self.method = "GET"

class _FTWTestSchema:
    """@TODO: doc"""
    test_title: str
    stages: List[_FTWTestInput]

    def __init__(self, test_title: str, stages: List[_FTWTestInput]):
        self.test_title = test_title
        self.stages = stages

class Util(ABC):
    """
    Util is an abstract class for Utils,
    it is used to read data from a source and store it in a database.
    extend this class to implement your own data collector.
    
    Generally, a collector perform the following steps in linear order:
    read_data() -> save_raw_data() -> parse_data()
    
    Noted that read_data() and save_raw_data() are optional if the raw data sources
    are provided. In this case, the data can be parsed directly.
    """

    @abstractmethod
    def collect(self, args: CollectCommandArg):
        """
        collect() is a method for collecting raw data from a source.

        Args:
            args (CollectCommandArg): the arguments for collecting data

        Raises:
            NotImplementedError: the method is not implemented
        """
        raise NotImplementedError

    @abstractmethod
    def text_report(self, args: ReportCommandArg):
        """_summary_
        text_report() is a method for generating a text-based report.

        Args:
            args (ReportCommandArg): the arguments for creating report

        Raises:
            NotImplementedError: the method is not implemented
        """
        raise NotImplementedError

    # @TODO: impl
    @abstractmethod
    def figure_report(self, args: ReportCommandArg):
        """
        figure_report() is a method for generating a figure-based report.
        
        Args:
            args (ReportCommandArg): the arguments for creating report
            
        Raises:
            NotImplementedError: the method is not implemented
        """
        raise NotImplementedError

    def _parse_ftw_test_file(self, file_path: str, case_limit: int) -> List[_FTWTestSchema]:
        if file_path is None:
            raise LookupError("file_path is None")

        data: List[_FTWTestSchema] = []

        # find filename which match the rule id
        for root, _, files in os.walk(file_path):
            for file_name in files:
                data += self.parse_go_ftw_yaml(os.path.join(root, file_name), case_limit)

        return data

    def parse_go_ftw_yaml(self, file_path: str, case_limit: int = 1e10) -> List[_FTWTestSchema]:
        """_summary_
        @TODO: documentation
        Args:
            file_path (str): _description_

        Returns:
            List[_FTWTestSchema]: _description_
        """
        with open(file_path, 'r') as file:
            data = yaml.safe_load(file)
        file.close()

        res, cnt = [], 0

        for data in data["tests"]:
            test_title = data['test_title']
            inputs: List[_FTWTestInput] = []
            for stage in data['stages']:
                inputs.append(_FTWTestInput(stage["stage"]["input"]))
                cnt += 1
                if cnt >= case_limit:
                    break
            test = _FTWTestSchema(test_title, inputs)
            res.append(test)
            if cnt >= case_limit:
                break

        return res
    def _get_threshold(self, file_path: str) -> List[Threshold]:
        with open(file_path, 'r') as f:
            raw_data = json.load(f)
            return [Threshold(**data) for data in raw_data["thresholds"]]

    def create_colored_text_by_value(self, value: any) -> str:
        """_summary_

        Args:
            value (any): _description_

        Raises:
            Exception: _description_

        Returns:
            str: _description_
        """
        color: str

        if type(value) == bool:
            color = "green" if value else "red"
        elif type(value) == float or type(value) == int:
            if value == 0:
                color = "light_grey"
            elif value > 0:
                color = "red"
                value = f"+{value}"
            else:
                color = "green"
        else:
            raise Exception("Invalid value type")

        return colored(str(value),color, attrs=["bold"])

    def create_time_series_terminal_plot(
        self,
        title: str,
        data: List[ParsedDataItem]) -> str:

        """
        Create a time series terminal plot for a single dataset

        Args:
            title (str): title of the plot
            data (List[ParsedDataItem]): data to plot

        Raises:
            Exception: if terminal size is too small

        Returns:
            str: formatted plot string
        """

        (column, line) = shutil.get_terminal_size((80, 20))
        if column < 120:
            raise Exception(f"Terminal column is too small, minimum requirement: 120 (current: {column})")
        if line < 12:
            raise Exception(f"Terminal line is too small, minimum requirement: 12 (current: {line})")

        config = {
            "colors": [asciichart.blue],
            "height": line - 7
        }
        def iso_time_str_to_unix_time(iso_time_str: str) -> float:
            return date_parser.parse(iso_time_str).timestamp()

        # flatten time series
        def flatten(list: List[ParsedDataItem]) -> list:
            start_time = iso_time_str_to_unix_time(list[0].key)
            end_time = iso_time_str_to_unix_time(list[-1].key)

            for data in list:
                compressed_time = (iso_time_str_to_unix_time(data.key) - start_time) / (end_time - start_time)
                data.key = round(compressed_time * 100)

            arr, cur = [], 0

            # filled
            for i in range(100):
                if cur >= len(list):
                    arr.append(arr[-1])
                if list[cur].key == i:
                    arr.append(list[cur].value)
                    cur += 1
                else:
                    arr.append(arr[-1])
            return arr

        f_data = flatten(data)

        # create title line
        spacer = (column - len(title) - 4) // 2
        title_line = "=" * spacer + f"  {title}  " + "=" * spacer

        return (
            f"{self.color_text(title_line, 'white', True)}\n" +
            f"{self.color_text('Warning: The text-chart only provides a simple visualization and it cannot depict the details.', 'yellow')}\n" +
            f"{self.color_text('Please use --format figure for better view. ', 'yellow')}\n\n" +
            asciichart.plot([f_data], config)
        )

    def create_data_terminal_table(self, data: dict[str, List[ParsedDataItem]],
                                    row: List[str]) -> Table:
        """
        Create a terminal table for displaying data without comparison

        Args:
            data (dict[str, List[ParsedDataItem]]): data to display
            row (List[str]): row headers

        Returns:
            Table: formatted astropy table
        """
        output = Table()
        output['Matrix'] = row

        for key in data.keys():
            cur_output = []
            for i in range(len(data[key][0].value)):
                out = f"{'{0:.4f}'.format(float(data[key][0].value[i]))}"
                cur_output.append(out)
            output[key] = cur_output
        return output

    # @TODO: make it generic
    def create_data_diff_terminal_table(self, before_data: dict[str, List[ParsedDataItem]],
                                        after_data: dict[str, List[ParsedDataItem]],
                                        row: List[str]) -> Table:

        key_set = set(before_data.keys())

        if before_data.keys() != after_data.keys():
            logger.error("The before and after data must have the same keys. The report will only show the shared keys.")
            key_set = [k for k in after_data.keys() if k in key_set]

        output = Table()
        output['Matrix'] = row

        for key in key_set:
            before, after, cur_output = before_data[key], after_data[key], []
            if len(before[0].value) != len(after[0].value):
                raise ValueError("The before and after data must have the same length")

            for i in range(len(before[0].value)):
                diff = round(float(before[0].value[i]) - float(after[0].value[i]), 4)
                out = (
                    f"{'{0:.4f}'.format(float(before[0].value[i]))}" +
                    f" ({self.create_colored_text_by_value(diff)})"
                )
                cur_output.append(out)
            output[key] = cur_output
        return output

    def color_text(self, text: str, color: str, bold: bool = False) -> str:
        """
        color_text() is a method for coloring a text with ANSI code.

        Args:
            text (str): the text to be colored
            color (str): the color of the text
            bold (bool, optional): bold font size. Defaults to False.

        Returns:
            str: the colored text
        """
        return colored(text, color, attrs=[] if not bold else ["bold"])
