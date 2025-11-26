"""
Module FTWUtil is a class for collecting data from go-ftw, it utilizes the go-ftw for calling the testcases and parsing the data.
"""
import subprocess
import os
import json
import time
from typing import List
from src.type import Mode
from .Util import ParsedDataItem, Util, ReportCommandArg, CollectCommandArg


REPORT_PLAIN_TEXT_FORMAT: str = (
    " Test Name: {test_name}\n"
    "       Run: {run}\n"
    "   Success: {success}\n"
    "    Failed: {failed}\n"
    "   Skipped: {skipped}\n"
    "Total Time: {total_time}s\n"
)

class FTWUtil(Util):
    """
    FTWUtil is a class for collecting data from go-ftw, it utilizes the go-ftw
    for calling the testcases and parsing the data.

    Usage:
        ```sh
        poetry run collect --test-name example --utils ftw
        ```
    """

    raw_filename: str = "ftw.json"

    def collect(self, args: CollectCommandArg):
        # go-ftw requires time to spin up, otherwise the I/O might be timeout
        time.sleep(5)

        # @TODO: better wrapping for different mode
        ftw_util_path = './ftw' if args.mode == Mode.PIPELINE.value else 'go-ftw'

        output_file = f"{args.raw_output}/{self.raw_filename}"
        command = f'{ftw_util_path} run -d "{args.test_cases_dir}" -o json > "{output_file}"'

        f = open(output_file, "w")
        proc = subprocess.Popen([command], stdout=f, stderr=subprocess.PIPE, shell=True)
        if proc.returncode != 0:
            # @TODO: handle errors from go-ftw
            print(proc.stderr.read().decode())
        f.close()

    def text_report(self, args: ReportCommandArg):
        data = self.parse_data(f"{args.raw_output}/{self.raw_filename}")

        # generate report
        report = REPORT_PLAIN_TEXT_FORMAT.format(
            test_name=args.test_name,
            run=data["run"].value,
            success=len(data["success"]),
            failed=len(data["failed"]),
            skipped=len(data["skipped"]),
            total_time=data["totalTime"].value
        )

        print(report)

        if not args.threshold_conf:
            return

        thresholds = self._get_threshold(os.path.join(args.threshold_conf, "ftw.threshold.json"))

        for threshold in thresholds:
            threshold.inspect(data[threshold.metric_name])

    def figure_report(self, args: ReportCommandArg):
        pass

    def parse_data(self, file_path: str) -> dict[str, List[ParsedDataItem]]:
        """
        parse_data parses the raw data from go-ftw into a dict of ParsedDataItem

        Args:
            file_path (str): file path of the raw data

        Returns:
            dict[str, List[ParsedDataItem]]: data parsed from the file
        """
        res = { "run": None, "success": [], "failed": [], "skipped": [], "runtime": [] }

        with open(file_path, 'r') as f:
            raw_data = json.load(f)

            res["run"] = ParsedDataItem('run', raw_data['run'], [])
            res["success"] = [ParsedDataItem("caseID", rule, [rule]) for rule in raw_data["success"]]            
            res["failed"] = [ParsedDataItem("caseID", rule, [rule]) for rule in raw_data["failed"]]
            res["skipped"] = [ParsedDataItem("caseID", rule, [rule]) for rule in raw_data["skipped"]]
            res["runtime"] = [ParsedDataItem(rule, raw_data["runtime"][rule], [rule, rule.split("-")[0]]) for rule in raw_data["runtime"]]
            res["totalTime"] = ParsedDataItem("TotalTime", raw_data["TotalTime"], [])
        f.close()
        return res
