"""
Module CAdvisorUtil defines the CAdvisorUtil class. CAdvisorUtil is a class for collecting and
analyzing data from cAdvisor API.
"""
import json
import time
import subprocess
import os
from typing import Type, List
import docker
import requests
from src.type import State, Mode
from src.utils import logger
from .Util import Util, ParsedDataItem, CollectCommandArg, ReportCommandArg


class CAdvisorUtil(Util):
    """
    CAdvisorUtil is a class for collecting and analyzing data from cAdvisor API.
    
    Usage:

    ```sh
    TEST_NAME=example
    poetry run collect --test-name $TEST_NAME --utils cAdvisor
    poetry run report --test-name --utils cAdvisor --threshold-conf "./config"
    ```
    """

    # @TODO: add to variables
    __cAdvisor_endpoint: str = "http://127.0.0.1:8080/api/v1.1/subcontainers/docker/"
    __waf_container_name: str = "modsec2-apache"
    __cAdvisor_container_version: str = "v0.45.0"
    raw_filename: str = "cAdvisor.json"

    def collect(self, args: CollectCommandArg, state: State = None):
        # start cAdvisor container
        self.__start_cadvisor()

        # @TODO: better wrapping for different mode
        ftw_util_path = './ftw' if args.mode == Mode.PIPELINE.value else 'go-ftw'

        # start go-ftw in parallel
        proc_ftw_data_collector = subprocess.Popen(
            [f"{ftw_util_path} run -d {args.test_cases_dir} -o json"],
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
            )

        data_list, timestamp_set = [], set()
        url = f"{self.__cAdvisor_endpoint}{self.__get_waf_container_id()}"

        # cAdvisor API sends 60 recent dataset,
        # thus, the data requires to be filtered out duplicates
        while proc_ftw_data_collector.poll() is not None:
            self.fetch_data(data_list, timestamp_set, url)
            time.sleep(10)

        self.fetch_data(data_list, timestamp_set, url)
        self.save_json(f"{args.raw_output}/{state.value}_{self.raw_filename}", data_list)
        self.__stop_cadvisor()

    def text_report(self, args: ReportCommandArg):
        before_data = self.parse_data(f"{args.raw_output}/{State.BEFORE.value}_{self.raw_filename}")
        after_data = self.parse_data(f"{args.raw_output}/{State.AFTER.value}_{self.raw_filename}")

        for matrix in ["cpu_total", "cpu_user", "cpu_system", "memory_usage", "memory_cache"]:
            print(self.create_time_series_terminal_plot(matrix,
                                                        before_data[matrix],
                                                        after_data[matrix])
                  )

        if not args.threshold_conf:
            return

        thresholds = self._get_threshold(os.path.join(args.threshold_conf,
                                                      "cAdvisor.threshold.json")
                                         )

        for threshold in thresholds:
            threshold.inspect(before_data[threshold.metric_name], after_data[threshold.metric_name])

    # @TODO: impl
    def figure_report(self, args: ReportCommandArg):
        pass

    def parse_data(self, file_path: str)  -> dict[str, List[ParsedDataItem]]:
        """
        parse_data() parses the data from cAdvisor API to ParseDataItem.

        Args:
            file_path (str): path of the data file

        Returns:
            dict[str, List[ParsedDataItem]]: parsed data
        """
        res = {
            "cpu_total": [],
            "cpu_user": [],
            "cpu_system": [],
            "memory_usage": [],
            "memory_cache": []
        }

        with open(file_path, "r") as f:
            raw_data = json.load(f)

            for data in raw_data:
                # load data from corresponding field from cAdvisor API
                mp = {
                    "cpu_total": data["cpu"]["usage"]["total"],
                    "cpu_user": data["cpu"]["usage"]["user"],
                    "cpu_system": data["cpu"]["usage"]["system"],
                    "memory_usage": data["memory"]["usage"],
                    "memory_cache": data["memory"]["cache"]
                }

                for key in mp:
                    res[key].append(ParsedDataItem(data["timestamp"], mp[key]))

        f.close()
        return res

    def fetch_data(self, data_list: list, timestamp_set: set, url: str):
        """
        fetch_data() fetches data from cAdvisor API.

        Args:
            data_list (list): data list to be appended
            timestamp_set (set): set of timestamp of when the data is collected
            url (str): cAdvisor API url
        """
        try:
            response = requests.post(url, timeout=15)

            if response.status_code != 200:
                logger.error(f"Response status code is not 200: {response.status_code}")

            for stats in response.json()[0]["stats"]:
                timestamp = stats["timestamp"]
                if timestamp in timestamp_set:
                    continue

                timestamp_set.add(timestamp)
                data_list.append(stats)

            logger.info(f"Current data collected: {len(data_list)}")

        except Exception as e:
            logger.error(e)
            exit(1)

    def __get_waf_container_id(self) -> str:
        """
        __get_waf_container_id() gets the id of container of the WAF,
        the id is used for cAdvisor API.

        Returns:
            str: waf container id
        """
        try:
            client = docker.from_env()
            container = client.containers.get(self.__waf_container_name)
            return container.id
        except Exception as e:
            logger.error(e)
            exit(1)

    def __start_cadvisor(self):
        """
        start_cadvisor() starts the cAdvisor container.
        """

        try:
            cmd = f"""
            docker run \
            --volume=/:/rootfs:ro \
            --volume=/var/run:/var/run:ro \
            --volume=/sys:/sys:ro \
            --volume=/var/lib/docker/:/var/lib/docker:ro \
            --volume=/dev/disk/:/dev/disk:ro \
            --publish=8080:8080 \
            --detach=true \
            --name=cadvisor \
            --privileged \
            --device=/dev/kmsg \
            gcr.io/cadvisor/cadvisor:{self.__cAdvisor_container_version}
            """

            subprocess.run(cmd,
                           shell=True,
                           stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE,
                           check=True
                           )

            logger.info("Waiting for cAdvisor to be up... (~ 1 min)")
            cnt = 0
            while not self.container_is_healthy("cadvisor") and cnt < 6:
                time.sleep(10)
                cnt += 1
            time.sleep(60)

        except Exception as e:
            logger.error(e)
            exit(1)

    def __stop_cadvisor(self):
        """
        __stop_cadvisor() stops and removes the cAdvisor container.
        """
        cmd = "docker stop cadvisor && docker rm cadvisor"
        try:
            subprocess.run(cmd,
                           shell=True,
                           stdout=subprocess.DEVNULL,
                           stderr=subprocess.DEVNULL,
                           check=False
                           )
        except Exception as e:
            logger.error(e)
            exit(1)

    def save_json(self, dist_path: str, data: any, cls: Type[json.JSONEncoder] = None):
        """
        Desc: save data as a json file

        Args:
            dist_path (str): dist of the json file
            data (any): data to be saved
            cls (Type[json.JSONEncoder], optional): json encoder. Defaults to None.
        """

        os.makedirs(os.path.dirname(dist_path), exist_ok=True)

        with open(dist_path, "w+") as file:
            json.dump(data, file, indent=2, cls=cls)
        file.close()

    def container_is_healthy(self, name_or_id: str) -> bool:
        """
        container_is_healthy() checks if a container is healthy.

        Args:
            name_or_id (str): container name or id

        Returns:
            bool: true if the container is healthy, false otherwise
        """
        return docker.from_env().api.inspect_container(name_or_id)["State"]["Status"] == 'running'
