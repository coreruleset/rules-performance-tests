"""
Module collect is a script to collect test cases for performance testing.

Usage:
    ```sh
    TEST_NAME=example
    poetry run collect --test-name $TEST_NAME --utils cAdvisor,ftw,locust
    ```
"""
import argparse
import os
import sys
import time
import subprocess
import requests
from typing import List
import docker
from src.model import CollectCommandArg, UtilMapper
from src.type import UtilType
from src.utils import logger


def get_test_command_arg(args: any) -> CollectCommandArg:
    """
    get test command arg from STDIN

    Returns:
        CollectCommandArg: collect command arg
    """
    parser = argparse.ArgumentParser(description='Collect Command Parser')
    parser.add_argument('--test-name', type=str, help='test name', required=True)
    parser.add_argument('--utils', type=str, help='utils')
    parser.add_argument('--raw-output', type=str, help='raw output')
    parser.add_argument('--output', type=str, help='output')
    parser.add_argument('--waf-endpoint', type=str, help='waf endpoint')
    parser.add_argument('--mode', type=str, help='mode')
    parser.add_argument('--rules-dir', type=str, help='rules directory')
    parser.add_argument('--test-cases-dir', type=str, help='test cases directory')

    parsed_args = parser.parse_args(args)

    return CollectCommandArg(
        test_name=parsed_args.test_name,
        utils=None if parsed_args.utils is None else parsed_args.utils.split(","),
        raw_output=parsed_args.raw_output,
        output=parsed_args.output,
        waf_endpoint=parsed_args.waf_endpoint,
        mode=parsed_args.mode,
        rules_dir=parsed_args.rules_dir,
        test_cases_dir=parsed_args.test_cases_dir
    )


def init(arg: CollectCommandArg):
    """
    initialize corresponding directory, service, etc.

    Args:
        arg (CollectCommandArg): collect command arg
    """

    # create folder for raw_output
    os.makedirs(arg.raw_output, exist_ok=True)

    # create folder for output
    os.makedirs(arg.output, exist_ok=True)

    # create folder for tmp
    os.makedirs(arg.tmp_dir, exist_ok=True)


def waf_server_is_up(waf_endpoint: str, modsec_version: str) -> bool:
    """
    check if waf server is up. Two conditions are inspected:
    1. docker container is up and running
    2. http server is up and running

    Args:
        waf_endpoint (str): waf endpoint
        modsec_version (str): modsec version

    Returns:
        bool: True if waf server is up, False otherwise
    """
    timeout, retry = 5, 0

    while retry < 3:
        try:
            container = docker.from_env().api.inspect_container(modsec_version)
            if container["State"]["Status"] == 'running':
                break
        except docker.errors.NotFound:
            logger.warning(f"Container {modsec_version} not found")
            return False
        retry += 1
        time.sleep(timeout)

    retry = 0

    while retry < 3:
        try:
            result = requests.get(waf_endpoint, timeout=5)
        except requests.exceptions.ConnectionError:
            result = None

        if result is None or not result:
            retry += 1
            time.sleep(timeout)
            continue
        else:
            return True

    return False


def runner(args: CollectCommandArg):
    """
    run test cases for performance testing.

    Args:
        args (CollectCommandArg): collect command arg
    """

    # start service with docker-compose
    cmd = f"docker-compose -f ./tests/docker-compose.yml up -d {args.modsec_version}"

    subprocess.run(cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, capture_output=False)

    # check it's up and running
    if not waf_server_is_up(args.waf_endpoint, args.modsec_version):
        logger.critical("WAF server is not up")
        exit(1)

    # run test cases
    for util in args.utils:
        logger.info(f"Running Test case: {args.test_name} using {util}")
        UtilMapper.get(UtilType(UtilType[util.upper()]))().collect(args)

    # stop service with docker-compose
    cmd = f"""
    docker-compose -f ./tests/docker-compose.yml stop &&
    docker-compose -f ./tests/docker-compose.yml down
    """
    subprocess.run(cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, capture_output=False)


def main(args: any = None):
    """
    script entrypoint of collect.py
    """

    if args is None:
        args = sys.argv[1:]

    # check the inputs
    command_args = get_test_command_arg(args)

    # create folder
    init(command_args)

    # run tests
    runner(command_args)

    logger.info(f"Test {command_args.test_name} completed successfully")
